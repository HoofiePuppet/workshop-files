"""Blunt knife edges: morphological opening of every part with a 0.22 mm ball.
Where a joint cup or a clearance cut meets the skin at a shallow angle the boolean leaves a feather edge
that tapers to nothing: too thin to print well and the first thing to chip. Opening (erode, then grow
back) removes any material thinner than 0.44 mm and rounds convex edges to 0.22 mm, while everything
thicker keeps its surface (final field = max(original, opened), remeshed on a 0.12-0.18 mm grid; typical
deviation 0.01 mm, far below a 0.2 mm layer). Concave corners, holes and slots keep their size.
Rewrites build/*.stl in place."""
import sys, glob, numpy as np, trimesh
from scipy import ndimage
from sdf import Grid, sdf, to_manifold
from rlib import to_tm

R = 0.22


def open_part(path, pitch):
    tm = trimesh.load(path)
    lo, hi = tm.bounds[0] - 1.5, tm.bounds[1] + 1.5
    g = Grid(lo, hi, pitch)
    f = sdf(tm, g, band=1.5, spacing=min(0.08, pitch * 0.5))
    eroded = f < -R
    h = ndimage.distance_transform_edt(~eroded).astype(np.float32) * pitch - pitch / 2 - R
    final = np.maximum(f, h)
    # light smoothing of the sampled distance takes out sub-0.05 mm sampling ripple before meshing
    final = ndimage.gaussian_filter(final, 0.6)
    m = to_manifold(final, g, 0.0, simplify=0.004)
    parts = m.decompose(); m = max(parts, key=lambda p: p.volume())
    v0 = tm.volume
    to_tm(m).export(path)
    print(f'{path}: {v0:.0f} -> {m.volume():.0f} mm3 ({m.volume() - v0:+.1f}), grid {g.n.tolist()}', flush=True)


if __name__ == '__main__':
    files = sys.argv[1:] or (sorted(glob.glob('build/fingers/*.stl')) + ['build/thumb.stl', 'build/palm_flap.stl', 'build/palm_back.stl', 'build/cuff.stl'])
    for f in files:
        open_part(f, 0.12 if ('fingers' in f or 'thumb' in f) else 0.18)
