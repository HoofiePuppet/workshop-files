"""Collision check: palm vs finger segments and segment vs segment at several curl angles."""
import sys, numpy as np, trimesh
from rlib import to_mf
from pose import load, pose_finger, ORDER
J, segs = load()
palm = to_mf(trimesh.load('build/palm_back.stl'))
angles = [float(a) for a in sys.argv[1:]] or [-4, 0, 20, 45, 70]
for n in ORDER:
    row = []
    for a in angles:
        s = pose_finger(J, segs, n, a)
        v = [(palm ^ s[0]).volume()] + [(s[k] ^ s[k + 1]).volume() for k in range(len(s) - 1)]
        v += [(palm ^ s[k]).volume() for k in range(1, len(s))]
        row.append(f'{a:>4.0f}: ' + ' '.join(f'{x:6.1f}' for x in v))
    print(n, ' | '.join(row))
