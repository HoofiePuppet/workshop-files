"""Real wall thickness round every palm line tunnel, measured on the finished PETG back:
rays out from the tunnel centre line, first hit = tunnel wall, second hit = the other side of the wall."""
import json, numpy as np, trimesh
# measured on the cleaned print file (build/ still holds zero-volume boolean slivers that fake double hits)
m = trimesh.load('stl/palm_back.stl')
T = np.array(json.load(open('build/orient.json'))['palm_back']['matrix'])
from trimesh.ray.ray_pyembree import RayMeshIntersector
ri = RayMeshIntersector(m)
ch = json.load(open('build/palm_channels.json'))
names = ['index flexor', 'index return', 'middle flexor', 'middle return', 'ring flexor', 'ring return', 'little flexor', 'little return']
for i, c in enumerate(ch):
    P = np.array(c['pts']) @ T[:3, :3].T + T[:3, 3]; seg, tan = [], []
    for a, b in zip(P[:-1], P[1:]):
        for t in np.linspace(0, 1, 6, endpoint=False): seg.append(a + t * (b - a)); tan.append((b - a) / np.linalg.norm(b - a))
    seg, tan = np.array(seg), np.array(tan)
    dend = np.minimum(np.linalg.norm(seg - P[-1], axis=1), np.linalg.norm(seg - P[0], axis=1))
    seg, tan = seg[dend > 8], tan[dend > 8]
    O, D = [], []
    for p, t in zip(seg, tan):
        u = np.cross(t, [0, 0, 1.0]); u = u if np.linalg.norm(u) > 0.1 else np.cross(t, [1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(t, u)
        for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            O.append(p); D.append(np.cos(a) * u + np.sin(a) * v)
    O, D = np.array(O), np.array(D)
    loc, ir, _ = ri.intersects_location(O, D, multiple_hits=True)
    dist = np.linalg.norm(loc - O[ir], axis=1)
    th = np.full(len(O), np.inf)
    for k in range(len(O)):
        dk = np.sort(dist[ir == k])
        if len(dk) >= 2: th[k] = dk[1] - dk[0]
    k = np.argmin(th)
    print(f'{names[i]:14s} thinnest wall {th[k]:.2f} mm at {O[k].round(1)}; 5th percentile {np.percentile(th, 5):.2f} mm')
