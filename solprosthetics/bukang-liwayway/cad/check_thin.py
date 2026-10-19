"""Thin-feature check on the print STLs: from points spread over each surface, a ray goes straight in
(against the surface normal); the distance to where it comes out again is the local material thickness.
Reports the share of surface thinner than 0.45 mm (about one 0.4 mm nozzle line) and where it is."""
import sys, glob, numpy as np, trimesh
from trimesh.ray.ray_pyembree import RayMeshIntersector
from scipy.cluster.vq import kmeans2
for f in sys.argv[1:] or sorted(glob.glob('stl/*.stl')):
    t = trimesh.load(f); ri = RayMeshIntersector(t)
    n = 40000
    P, fi = trimesh.sample.sample_surface(t, n, seed=2)
    N = t.face_normals[fi]
    O = P - N * 1e-3
    loc, ir, _ = ri.intersects_location(O, -N, multiple_hits=False)
    th = np.full(n, np.inf); th[ir] = np.linalg.norm(loc - O[ir], axis=1)
    thin = th < 0.45
    msg = f'{f}: thinner than 0.45 mm on {100 * thin.mean():.2f}% of the surface ({thin.sum()} of {n} samples)'
    if thin.sum() >= 8:
        c, lab = kmeans2(P[thin], min(6, thin.sum() // 4), seed=1, minit='++')
        sizes = np.bincount(lab)
        msg += '; clusters ' + ', '.join(f'{c[k].round(0).tolist()} x{sizes[k]}' for k in np.argsort(-sizes)[:6])
    print(msg, flush=True)
