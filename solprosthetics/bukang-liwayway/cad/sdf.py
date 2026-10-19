"""Signed-distance grids from meshes (parity voxeliser + EDT) and meshes back from grids."""
import numpy as np, trimesh, manifold3d as mf
from scipy import ndimage
from skimage.measure import marching_cubes


class Grid:
    def __init__(self, lo, hi, pitch):
        self.p = pitch
        # small irrational shift keeps rays off mesh vertices and edges
        self.o = np.asarray(lo, float) + pitch * np.array([0.1234, 0.2345, 0.0])
        self.n = np.ceil((np.asarray(hi, float) - self.o) / pitch).astype(int) + 1

    def axes(self):
        return [self.o[i] + self.p * np.arange(self.n[i]) for i in range(3)]

    def points(self, sl=None):
        X, Y, Z = np.meshgrid(*self.axes(), indexing='ij')
        return X, Y, Z


def inside(tm, g):
    """Occupancy by z-ray parity: +1 at every crossing, cumulative sum along z, odd = inside."""
    tri = tm.vertices[tm.faces]
    p, o, n = g.p, g.o, g.n
    xy = tri[:, :, :2]
    lo = np.ceil((xy.min(1) - o[:2]) / p).astype(int)
    hi = np.floor((xy.max(1) - o[:2]) / p).astype(int)
    lo = np.clip(lo, 0, n[:2] - 1); hi = np.clip(hi, -1, n[:2] - 1)
    nx = np.maximum(hi[:, 0] - lo[:, 0] + 1, 0); ny = np.maximum(hi[:, 1] - lo[:, 1] + 1, 0)
    cnt = nx * ny
    ti = np.repeat(np.arange(len(tri)), cnt)
    start = np.repeat(np.cumsum(cnt) - cnt, cnt)
    k = np.arange(cnt.sum()) - start
    ix = lo[ti, 0] + k % nx[ti]; iy = lo[ti, 1] + k // nx[ti]
    px = o[0] + ix * p; py = o[1] + iy * p
    a, b, c = tri[ti, 0], tri[ti, 1], tri[ti, 2]
    v0 = b[:, :2] - a[:, :2]; v1 = c[:, :2] - a[:, :2]; v2 = np.stack([px, py], 1) - a[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-12
    den = np.where(ok, den, 1)
    l1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    l2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    l0 = 1 - l1 - l2
    hit = ok & (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
    z = l0 * a[:, 2] + l1 * b[:, 2] + l2 * c[:, 2]
    iz = np.ceil((z - o[2]) / p).astype(int)
    hit &= (iz < n[2])
    iz = np.clip(iz, 0, n[2] - 1)
    acc = np.zeros(n, np.int16)
    np.add.at(acc, (ix[hit], iy[hit], iz[hit]), 1)
    return (np.cumsum(acc, axis=2) % 2).astype(bool)


def sdf(tm, g, band=7.0, spacing=0.12):
    """EDT gives the coarse field; inside a band around the surface the distance is replaced by an
    exact-enough nearest-surface-sample distance (dense surface samples + KD-tree)."""
    from scipy.spatial import cKDTree
    occ = inside(tm, g)
    d_out = ndimage.distance_transform_edt(~occ).astype(np.float32)
    d_in = ndimage.distance_transform_edt(occ).astype(np.float32)
    f = (np.where(occ, -(d_in - 0.5), d_out - 0.5)) * g.p
    n_s = int(tm.area / spacing ** 2)
    pts, _ = trimesh.sample.sample_surface_even(tm, n_s) if False else trimesh.sample.sample_surface(tm, n_s, seed=1)
    tree = cKDTree(pts)
    idx = np.nonzero(np.abs(f) < band)
    P = np.stack([g.o[i] + g.p * idx[i] for i in range(3)], 1)
    dist, _ = tree.query(P, workers=-1)
    f[idx] = np.where(occ[idx], -dist, dist)
    return f.astype(np.float32)


def to_manifold(field, g, level=0.0, simplify=0.02):
    f = np.pad(field, 1, constant_values=1e3)
    v, faces, _, _ = marching_cubes(f, level=level, spacing=(g.p,) * 3)
    v = v + g.o - g.p
    faces = np.ascontiguousarray(faces)
    m = mf.Manifold(mf.Mesh(vert_properties=v.astype(np.float32), tri_verts=faces.astype(np.uint32)))
    if m.status() != mf.Error.NoError:
        raise RuntimeError(f'marching cubes mesh not manifold: {m.status()}')
    if m.volume() < 0:
        raise RuntimeError('inverted mesh')
    return m.simplify(simplify) if simplify else m


def smin(a, b, k):
    """Polynomial smooth minimum (smooth union for SDFs)."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def seg_dist(P, a, b):
    """Distance from points P (...,3) to segment ab."""
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[..., None] * ab), axis=-1)
