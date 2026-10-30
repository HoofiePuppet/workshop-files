"""v3.3: pinholes and slits in the outer skin of the back of the hand. Depth maps from six directions; a pit is a
spot more than 0.8 mm deeper than the lowest point of a 1.2 mm ring round it (surface all round = not an edge).
Design features that are holes on purpose (screw holes, tunnel exits, logo strokes) are listed with what is near.
usage: python3 check_pits.py [palm_back.stl in the hand frame]"""
import sys, json, numpy as np, trimesh
from trimesh.ray.ray_pyembree import RayMeshIntersector
from scipy import ndimage
f = sys.argv[1] if len(sys.argv) > 1 else 'build/palm_back.stl'
m = trimesh.load(f); ri = RayMeshIntersector(m); lo, hi = m.bounds
res = 0.08; R = int(1.2 / res)
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]; ring = np.abs(np.hypot(xx, yy) - R) < 1.0
found = []
for ax in range(3):
    for sgn in (1, -1):
        a, b = [k for k in range(3) if k != ax]
        A = np.arange(lo[a], hi[a], res); Bv = np.arange(lo[b], hi[b], res); AA, BB = np.meshgrid(A, Bv)
        O = np.zeros((AA.size, 3)); O[:, a] = AA.ravel(); O[:, b] = BB.ravel(); O[:, ax] = hi[ax] + 5 if sgn > 0 else lo[ax] - 5
        D = np.zeros(3); D[ax] = -sgn
        loc, ir, _ = ri.intersects_location(O, np.tile(D, (len(O), 1)), multiple_hits=False)
        Z = np.full(len(O), np.nan); Z[ir] = loc[:, ax] * sgn; Z = Z.reshape(AA.shape)
        Zf = np.nan_to_num(Z, nan=-1e3)
        mn = ndimage.minimum_filter(Zf, footprint=ring, mode='constant', cval=-1e3)
        pit = np.where((mn > -500) & (Zf > -500), mn - Zf, 0)
        lab, nl = ndimage.label(pit > 0.8)
        for i in range(1, nl + 1):
            w = np.where(lab == i); k = np.argmax(pit[w])
            p = np.zeros(3); p[a] = AA[w][k]; p[b] = BB[w][k]; p[ax] = mn[w][k] * sgn
            found.append((p, pit[w][k], len(w[0]) * res * res, 'xyz'[ax] + ('+' if sgn > 0 else '-')))
# merge duplicates seen from two sides
out = []
for p, dpt, area, v in sorted(found, key=lambda t: -t[2]):
    if all(np.linalg.norm(p - q[0]) > 2.0 for q in out): out.append((p, dpt, area, v))
for p, dpt, area, v in out:
    print('pit at %s seen from %s: %.2f mm deep, %.2f mm2' % (p.round(1), v, dpt, area))
print('PITS', len(out))
