"""Rotate an exported posed set about the wrist axis (everything but the cuff). usage: render_wrist.py dir deg"""
import sys, glob, json, os, numpy as np, trimesh
d, a = sys.argv[1], float(sys.argv[2]); W = np.array(json.load(open('build/palm.json'))['wrist'])
R = trimesh.transformations.rotation_matrix(np.radians(a), [1, 0, 0], W)
for f in glob.glob(f'{d}/*.stl'):
    if os.path.basename(f) == 'cuff.stl': continue
    m = trimesh.load(f); m.apply_transform(R); m.export(f)
