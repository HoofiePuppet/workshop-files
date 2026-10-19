"""Write a posed set of STLs for the browser renderer. usage: render_set.py out_dir curl [palm_stl]"""
import sys, os, trimesh
from rlib import to_tm
from pose import load, pose_finger, ORDER
out, curl = sys.argv[1], float(sys.argv[2]); os.makedirs(out, exist_ok=True)
palm = sys.argv[3] if len(sys.argv) > 3 else 'build/palm_raw.stl'
J, segs = load()
names = []
for n in ORDER:
    for k, s in enumerate(pose_finger(J, segs, n, curl)):
        to_tm(s).export(f'{out}/{n}-{k+1}.stl'); names.append(f'{n}-{k+1}')
trimesh.load(palm).export(f'{out}/palm.stl')
print(','.join(names))
