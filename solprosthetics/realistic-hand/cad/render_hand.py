"""Posed full hand for renders. usage: render_hand.py out_dir finger_curl thumb_swing_fraction"""
import sys, os, json, numpy as np, trimesh
from scipy.spatial.transform import Rotation as Rot
from rlib import to_tm
from pose import load, pose_finger, ORDER
out, curl, sw = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); os.makedirs(out, exist_ok=True)
J, segs = load(); TS = json.load(open('build/thumb_solution.json'))
names = []
for n in ORDER:
    for k, s in enumerate(pose_finger(J, segs, n, curl)):
        to_tm(s).export(f'{out}/{n}-{k+1}.stl'); names.append(f'{n}-{k+1}')
th = trimesh.load('build/thumb.stl'); p = np.array(TS['pivot'])
R = Rot.from_rotvec(np.array(TS['hinge_axis']) * np.radians(TS['swing_deg'] * sw)) * Rot.from_quat(TS['open_quat'])
M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = p - R.as_matrix() @ p; th.apply_transform(M); th.export(f'{out}/thumb.stl')
for part in ('palm_back', 'palm_flap'): trimesh.load(f'build/{part}.stl').export(f'{out}/{part}.stl')
print(','.join(['palm_back', 'palm_flap', 'thumb'] + names))
trimesh.load('build/cuff.stl').export(f'{out}/cuff.stl')
