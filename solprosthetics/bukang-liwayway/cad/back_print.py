"""Make palm_back_print.stl: palm_back plus a snip-off support wall under the floating wrist-end rim.

In print orientation (standing on the wrist end) palm_back touches the bed only under the two wrist ears;
the rim across the back of the hand floats ~8 mm up and the line tunnels exit through its underside.
This adds a thin wall that follows the rim's centre line on a 0.6 mm sole, joined to the rim only by
small necked tabs that sit on solid plastic between the tunnel exits (never in a hole).
Also writes <dst stem>_support_blocker.stl, a support blocker for the slicer (same coordinates): every hole,
tunnel and narrow slot of the part (holes under ~5.5 mm filled by a 2.75 mm closing) plus the space under the rim.

usage: python3 back_print.py stl/palm_back.stl stl/palm_back_print.stl
"""
import sys, numpy as np, trimesh, manifold3d as mf
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from skimage import measure

src, dst = sys.argv[1], sys.argv[2]
G = 0.1                         # grid step
WALL_W, NECK_W = 1.6, 0.8       # wall (4 lines) and tab neck widths
GAP = 0.8                       # air between wall top and rim between tabs (= neck height)
BITE = 0.3                      # tab reaches this far into the rim
TAB_L, TAB_PITCH = 1.4, 3.5     # tab length along the wall, spacing
HOLE_CLEAR_WALL, HOLE_CLEAR_TAB = 0.9, 1.3
SOLE_T, SOLE_W, SOLE_CLEAR = 0.6, 7.0, 0.35
part = trimesh.load(src)

# ---- underside height map of the rim region
xs = np.arange(-17, 33, G); ys = np.arange(-27, -6, G); X, Y = np.meshgrid(xs, ys, indexing='ij')
org = np.c_[X.ravel(), Y.ravel(), np.full(X.size, -1.0)]
tri, ray, loc = part.ray.intersects_id(org, np.tile([0, 0, 1.], (len(org), 1)), multiple_hits=False, return_locations=True)
h = np.full(X.size, np.inf); nz = np.zeros(X.size); h[ray] = loc[:, 2]; nz[ray] = part.face_normals[tri, 2]
h = h.reshape(X.shape); nz = nz.reshape(X.shape)

over = (h > 1.0) & (h < 14) & (nz < -0.707)
band = ndi.binary_fill_holes(ndi.binary_closing(over, iterations=6))
lab, n = ndi.label(band); band = lab == (1 + np.argmax(ndi.sum(band, lab, range(1, n + 1))))
hm = np.where(np.isfinite(h), h, 99)
med = ndi.median_filter(hm, size=int(4 / G))
holes = band & (~over | (hm - med > 0.6) | ~np.isfinite(h))
holes = ndi.binary_opening(holes, iterations=2)
dhole = ndi.distance_transform_edt(~holes, sampling=G)
print('rim band %.0f mm2, tunnel-exit area %.1f mm2' % (band.sum() * G * G, holes.sum() * G * G))

# ---- centre line of the band (smooth), trimmed 1.5 mm short of the ends
sk = skeletonize(ndi.binary_erosion(band, iterations=3))
pts = np.argwhere(sk)
# order along x (the rim is a shallow U, one y per x is enough); smooth
order = np.argsort(pts[:, 0]); pts = pts[order]
cx = xs[pts[:, 0]]; cy = ys[pts[:, 1]]
bx = np.arange(cx.min() + 1.5, cx.max() - 1.5, 0.25)
byy = np.array([np.median(cy[np.abs(cx - x) < 1.0]) for x in bx])
byy = ndi.gaussian_filter1d(byy, 6)
line = np.c_[bx, byy]
seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))]
print('wall line x %.1f..%.1f, %.1f mm long' % (bx[0], bx[-1], seg[-1]))

# distance of each grid cell to the line, and arc position of the nearest line point
from scipy.spatial import cKDTree
dense = np.c_[np.interp(np.arange(0, seg[-1], 0.05), seg, line[:, 0]), np.interp(np.arange(0, seg[-1], 0.05), seg, line[:, 1])]
s_dense = np.arange(0, seg[-1], 0.05)
dist, ii = cKDTree(dense).query(np.c_[X.ravel(), Y.ravel()])
dist = dist.reshape(X.shape); sarc = s_dense[ii].reshape(X.shape)
at_end = (ii == 0) | (ii == len(dense) - 1)
dist = np.where(at_end.reshape(X.shape), np.inf, dist)

dedge = ndi.distance_transform_edt(band, sampling=G)
NECK_R, POST_R, LOW_GAP, POST_GAP, SPACING = 0.4, 0.8, 2.0, GAP, 2.6
safe = band & (dhole > NECK_R + 0.5) & (dedge > NECK_R + 0.35) & np.isfinite(h)
# rim must be locally flat-ish under the neck
hloc = np.where(np.isfinite(h), h, 99)
flat = (ndi.maximum_filter(hloc, size=9) - ndi.minimum_filter(hloc, size=9)) < 0.5
safe &= flat
score = np.minimum(dhole - NECK_R - 0.5, dedge - NECK_R - 0.35)
cand = np.argwhere(safe); cand = cand[np.argsort(-score[safe])]
posts = []
for i, j in cand:
    p = np.array([xs[i], ys[j]])
    if all(np.linalg.norm(p - q[:2]) >= SPACING for q in posts): posts.append((p[0], p[1], h[i, j]))
posts = sorted(posts)
print('%d posts at x %s' % (len(posts), [round(p[0], 1) for p in posts]))
P = np.c_[X.ravel(), Y.ravel()]
neck = np.zeros(X.size, bool); post = np.zeros(X.size, bool); link = np.zeros(X.size, bool)
for (px, py, ph) in posts:
    dd = np.hypot(P[:, 0] - px, P[:, 1] - py)
    neck |= dd <= NECK_R; post |= dd <= POST_R
    k = np.argmin(np.hypot(dense[:, 0] - px, dense[:, 1] - py)); c = dense[k]
    v = c - [px, py]; L = np.linalg.norm(v) + 1e-9; t_ = np.clip(((P - [px, py]) @ v) / L**2, 0, 1)
    link |= np.hypot(*(P - ([px, py] + t_[:, None] * v)).T) <= 0.6
neck, post, link = (m.reshape(X.shape) for m in (neck, post, link))
wall = ((dist <= WALL_W / 2) | link) & band
hb = np.where(band & np.isfinite(h), h, 99)
low_top = ndi.minimum_filter(hb, size=int(4 / G)) - LOW_GAP          # low wall stays 2 mm under the rim
tab = neck

zt = np.arange(0, 14.5, G)
Hc = np.where(np.isfinite(h), h, 0)
dwall = ndi.distance_transform_edt(~(wall | post), sampling=G)
sole = (dwall <= SOLE_W / 2) & (~np.isfinite(h) | (h > SOLE_T + SOLE_CLEAR))
V = np.zeros(X.shape + (len(zt),), bool)
zz = zt[None, None, :]
V |= wall[..., None] & (zz <= low_top[..., None])
V |= post[..., None] & (zz <= (Hc - POST_GAP)[..., None])
V |= neck[..., None] & (zz <= (Hc + BITE)[..., None])
V |= sole[..., None] & (zz <= SOLE_T)
# blocker for the slicer: the whole rim footprint, bed to just above the rim (keeps slicer supports out of
# the tunnel exits and the space the jig already holds)
bfoot = ndi.binary_dilation(band, iterations=5)
gapV = bfoot[..., None] & (zz < (np.where(np.isfinite(h), h, 0) + 0.4)[..., None]) & (zz < 14)
def mc(vol, name):
    v, f, _, _ = measure.marching_cubes(np.pad(vol, 1).astype(np.float32), 0.5)
    v = (v - 1) * G + [xs[0], ys[0], zt[0]]
    m = trimesh.Trimesh(v, f[:, ::-1]); 
    if m.volume < 0: m.invert()
    return m

jig = mc(V, 'jig')
jig.vertices[:, 2] = np.maximum(jig.vertices[:, 2], 0.0)      # flat on the bed
to_mf = lambda tm: mf.Manifold(mf.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
J = to_mf(jig); print('jig manifold status', J.status(), 'vol %.0f mm3' % J.volume())
out = (J + to_mf(part)).to_mesh()
res = trimesh.Trimesh(out.vert_properties[:, :3], out.tri_verts)
bodies = res.split(only_watertight=False)
print('watertight', res.is_watertight, 'bodies', len(bodies), 'bounds', res.bounds.round(2).tolist())
res.export(dst)

# ---- support blocker: holes / tunnels / narrow slots of the whole part + the rim space
def hole_blocker(m, R_CLOSE=2.75, GROW=0.4, H=0.2):
    from skimage.draw import polygon as rpoly
    lo, hi = m.bounds[0] - 4, m.bounds[1] + 4
    nx, ny, nz = np.ceil((hi - lo) / H).astype(int) + 1
    zs = lo[2] + np.arange(nz) * H
    solid = np.zeros((nx, ny, nz), bool)
    for k, sct in enumerate(m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs + H * 0.01))):
        if sct is None: continue
        T = sct.metadata['to_3D']
        def rast(coords):
            c = np.c_[np.asarray(coords), np.zeros(len(coords)), np.ones(len(coords))] @ T.T
            return rpoly((c[:, 0] - lo[0]) / H, (c[:, 1] - lo[1]) / H, (nx, ny))
        for Pg in sct.polygons_full:
            rr, cc = rast(Pg.exterior.coords); solid[rr, cc, k] = True
            for I in Pg.interiors:
                rr, cc = rast(I.coords); solid[rr, cc, k] = False
    dil = ndi.distance_transform_edt(~solid, sampling=H) <= R_CLOSE
    holes_ = (ndi.distance_transform_edt(dil, sampling=H) > R_CLOSE) & ~solid
    del dil, solid
    lab, n = ndi.label(holes_); sizes = ndi.sum(holes_, lab, range(1, n + 1))
    keep = np.isin(lab, 1 + np.where(sizes * H ** 3 > 0.3)[0])
    blk = ndi.binary_opening(ndi.distance_transform_edt(~keep, sampling=H) <= GROW, iterations=1)
    v, f, _, _ = measure.marching_cubes(np.pad(blk, 1).astype(np.float32), 0.5)
    b = trimesh.Trimesh((v - 1) * H + lo, f)
    b = trimesh.smoothing.filter_taubin(b, iterations=10)
    if b.volume < 0: b.invert()
    return b

blk = to_mf(hole_blocker(part)) + to_mf(mc(gapV, 'gap'))
bm = blk.to_mesh(); bt = trimesh.Trimesh(bm.vert_properties[:, :3], bm.tri_verts)
if bt.bounds[0, 2] < 0.2: bt = bt.slice_plane([0, 0, 0.2], [0, 0, 1], cap=True)   # never below the bed line
bt.export(dst.replace('.stl', '_support_blocker.stl'))
print('support blocker watertight', bt.is_watertight, 'bounds', bt.bounds.round(1).tolist())
print('bed contact before %.0f mm2, after %.0f mm2' % (
    part.area_faces[(part.triangles_center[:, 2] < 0.05) & (part.face_normals[:, 2] < -0.9)].sum(),
    res.area_faces[(res.triangles_center[:, 2] < 0.05) & (res.face_normals[:, 2] < -0.9)].sum()))
