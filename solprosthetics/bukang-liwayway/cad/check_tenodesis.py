"""How far the fingers close as the wrist bends down (line pull = change in exit-to-clamp distance)."""
import json, numpy as np, trimesh, manifold3d as mf
from rlib import to_mf
W = np.array(json.load(open('build/palm.json'))['wrist'])
ch = json.load(open('build/palm_channels.json')); C = json.load(open('build/cuff.json'))['clamps']
J = json.load(open('build/joints.json'))
cuff = to_mf(trimesh.load('build/cuff.stl'))
names = ['index', 'middle', 'ring', 'little']
flex = [ch[i] for i in (0, 2, 4, 6)]
for n, c, cl in zip(names, flex, C):
    e = np.array(c['pts'][-2]); t = np.array([cl['x'], -8.0, cl['line_z']])
    zf = [j['zf'] for j in J[n]['joints']]
    out = []
    for a in (0, -20, -30, -40):
        R = trimesh.transformations.rotation_matrix(np.radians(a), [1, 0, 0], W)
        e2 = (R @ np.r_[e, 1])[:3]; pull = np.linalg.norm(e2 - t) - np.linalg.norm(e - t)
        curl = np.degrees(pull / sum(zf))          # equal curl at every joint
        # does the free line span touch the cuff?
        seg = [e2 + (t - e2) * s for s in np.linspace(0.02, 0.98, 40)]
        hit = sum((cuff ^ mf.Manifold.sphere(0.5, 8).translate(list(p))).volume() > 0.01 for p in seg) if False else 0
        out.append(f'{a:+d}: pull {pull:4.1f} mm -> {curl:4.0f} deg/joint')
    print(n, ' | '.join(out))
