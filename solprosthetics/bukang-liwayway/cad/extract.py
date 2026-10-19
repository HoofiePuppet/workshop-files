"""Extract and orient the right forearm + hand from a MakeHuman T-pose body STL."""
import sys, json, numpy as np, trimesh
src, scale = sys.argv[1], float(sys.argv[2])
m = trimesh.load(src); m.apply_scale(scale)
body = max(m.split(only_watertight=False), key=lambda p: len(p.faces))
half = -body.bounds[0][0]
arm = body.slice_plane(plane_origin=[-0.523 * half, 0, 0], plane_normal=[-1, 0, 0], cap=True)
R = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], float); T = np.eye(4); T[:3, :3] = R; arm.apply_transform(T)
v = arm.vertices; y0, y1 = v[:, 1].min(), v[:, 1].max()
# wrist = narrowest section in the 55-80 % band of the arm length
best = None
for y in np.linspace(y0 + 0.55 * (y1 - y0), y0 + 0.80 * (y1 - y0), 60):
    s = arm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is None: continue
    b = s.bounds; w = (b[1][0] - b[0][0]) * (b[1][2] - b[0][2])
    if best is None or w < best[0]: best = (w, y)
b = arm.bounds; c = (b[0] + b[1]) / 2
arm.apply_translation([-c[0], -best[1], -c[2]])
print('arm faces', len(arm.faces), 'watertight', arm.is_watertight, 'wrist at', round(best[1], 1), 'bounds', arm.bounds.round(1))
arm.export('src/right-arm-oriented.stl')
# finger axes
a = arm; v = a.vertices
secs = {}
for y in np.arange(40, a.bounds[1][1], 2):
    s = a.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is not None: secs[round(y, 1)] = [e for e in s.discrete]
counts = {y: len(l) for y, l in secs.items()}
print('loops per section (y:count):', {k: v_ for k, v_ in list(counts.items())[::3]})
json.dump({str(k): [[float(e[:, 0].min()), float(e[:, 0].max()), float(e[:, 2].min()), float(e[:, 2].max())] for e in l] for k, l in secs.items()}, open('src/sections.json', 'w'))
