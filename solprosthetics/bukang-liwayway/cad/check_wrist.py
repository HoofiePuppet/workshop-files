"""Palm vs cuff collisions over the wrist range (palm turns about the wrist axis)."""
import json, numpy as np, trimesh
from rlib import to_mf
W = np.array(json.load(open('build/palm.json'))['wrist'])
cuff = to_mf(trimesh.load('build/cuff.stl'))
parts = {p: to_mf(trimesh.load(f'build/{p}.stl')) for p in ('palm_back', 'palm_flap')}
for a in (-55, -50, -45, -40, -20, 0, 15, 25, 30):
    R = trimesh.transformations.rotation_matrix(np.radians(a), [1, 0, 0], W)
    v = {k: round((m.transform(R[:3, :]) ^ cuff).volume(), 1) for k, m in parts.items()}
    print(f'wrist {a:+d} deg (+ = bent back):', v)
