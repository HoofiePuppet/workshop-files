"""Thumb: palm/finger collisions along the swing, and the pinch contact with the fingers curled."""
import json, numpy as np, trimesh, manifold3d as mf
from scipy.spatial.transform import Rotation as Rot
from rlib import to_mf, to_tm
from pose import load, pose_finger
TS = json.load(open('build/thumb_solution.json')); p = np.array(TS['pivot'])
th = to_mf(trimesh.load('build/thumb.stl'))
parts = {k: to_mf(trimesh.load(f'build/{k}.stl')) for k in ('palm_back', 'palm_flap')}
J, segs = load()
def thumb_at(f):
    R = Rot.from_rotvec(np.array(TS['hinge_axis']) * np.radians(TS['swing_deg'] * f)) * Rot.from_quat(TS['open_quat'])
    M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = p - R.as_matrix() @ p
    return th.transform(M[:3, :])
for f in (0, 0.25, 0.5, 0.75, 1.0):
    t = thumb_at(f); print('swing', f, {k: round((t ^ m).volume(), 1) for k, m in parts.items()})
t = thumb_at(1.0)
for curl in (40, 45, 49, 55):
    out = []
    for n in ('index', 'middle'):
        s = pose_finger(J, segs, n, curl)[-1]
        ov = (t ^ s).volume()
        gap = t.min_gap(s, 10.0) if ov == 0 else 0.0
        out.append(f'{n}: overlap {ov:.1f} mm3, gap {gap:.2f} mm')
    print('curl', curl, ' | '.join(out))
