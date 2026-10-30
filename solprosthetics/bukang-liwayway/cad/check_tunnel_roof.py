"""v3.3: plastic between every palm line tunnel and the OUTSIDE. Rays from the tunnel centre line: a ray that meets
no wall within r + 0.4 has escaped = a hole; a ray that meets the tunnel wall, then one more surface and then nothing
has crossed the outer skin, and that wall thickness is the roof. (Rays that meet more surfaces are crossing into the
neighbouring tunnel or the hand cavity: not the outside.) The last 5 mm at each end (the mouths) are skipped.
usage: python3 check_tunnel_roof.py [run_dir]"""
import json, sys, numpy as np, trimesh
from trimesh.ray.ray_pyembree import RayMeshIntersector
d = sys.argv[1] if len(sys.argv) > 1 else '.'
m = trimesh.load(d + '/stl/palm_back.stl'); T = np.array(json.load(open(d + '/build/orient.json'))['palm_back']['matrix']); Ti = np.linalg.inv(T)
ch = json.load(open(d + '/build/palm_channels.json'))
names = ['index flexor', 'index return', 'middle flexor', 'middle return', 'ring flexor', 'ring return', 'little flexor', 'little return']
ri = RayMeshIntersector(m); worst = 99; holes_all = 0
for i, c in enumerate(ch):
    P = np.array(c['pts']) @ T[:3, :3].T + T[:3, 3]; r = c['r']
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    O, D = [], []
    for a, b, la in zip(P[:-1], P[1:], L[:-1]):
        t_ = (b - a) / np.linalg.norm(b - a)
        u = np.cross(t_, [0, 0, 1.0]); u = u if np.linalg.norm(u) > 0.1 else np.cross(t_, [1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(t_, u)
        for f in np.linspace(0, 1, 5, endpoint=False):
            if la + f * np.linalg.norm(b - a) < 5 or la + f * np.linalg.norm(b - a) > L[-1] - 5: continue
            p = a + f * (b - a)
            for ang in np.linspace(0, 2 * np.pi, 36, endpoint=False):
                O.append(p); D.append(np.cos(ang) * u + np.sin(ang) * v)
    O, D = np.array(O), np.array(D)
    loc, ir, _ = ri.intersects_location(O, D, multiple_hits=True)
    dist = np.linalg.norm(loc - O[ir], axis=1)
    order = np.lexsort((dist, ir)); ir, dist = ir[order], dist[order]
    starts = np.searchsorted(ir, np.arange(len(O))); ends = np.searchsorted(ir, np.arange(len(O)), side='right')
    roof = []; holes = []
    for k in range(len(O)):
        dk = dist[starts[k]:ends[k]]
        if len(dk) == 0 or dk[0] > r + 0.4: holes.append(k); continue
        if len(dk) == 2: roof.append((dk[1] - dk[0], k))
    holes_all += len(holes)
    th, k = min(roof) if roof else (99, 0)
    worst = min(worst, th)
    hp = (Ti[:3, :3] @ O[holes[0]] + Ti[:3, 3]).round(1) if holes else ''
    print(f'{names[i]:14s} thinnest roof {th:.2f} mm at {(Ti[:3, :3] @ O[k] + Ti[:3, 3]).round(1)}; under 0.8: {sum(1 for t, _ in roof if t < 0.8)}; HOLES {len(holes)} {hp}')
print('THINNEST ROOF %.2f mm, holes %d' % (worst, holes_all))
