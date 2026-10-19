"""Pose the realistic finger segments: every joint flexed by the given angle (deg)."""
import json, numpy as np, trimesh
from rlib import to_mf, to_tm

ORDER = ['index', 'middle', 'ring', 'little']


def load(build='build'):
    J = json.load(open(f'{build}/joints.json'))
    segs = {n: [to_mf(trimesh.load(f'{build}/fingers/{n}-{k+1}.stl')) for k in range(len(J[n]['joints']))] for n in ORDER}
    return J, segs


def pose_finger(J, segs, n, curl):
    info = J[n]['joints']
    curl = curl if np.ndim(curl) else [curl] * len(info)
    out = list(segs[n]); P = [np.array(i['O']) for i in info]; X = [np.array(i['x']) for i in info]
    for j in range(len(info)):
        R = trimesh.transformations.rotation_matrix(np.radians(-curl[j]), X[j], P[j])
        for k in range(j, len(out)):
            out[k] = out[k].transform(R[:3, :])
        for k in range(j + 1, len(info)):
            P[k] = (R @ np.r_[P[k], 1])[:3]; X[k] = R[:3, :3] @ X[k]
    return out
