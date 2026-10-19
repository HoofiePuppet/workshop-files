"""Child cavity used by the shell parts: skin.npz cavity minus the thumb ray.
This hand is for a child without a usable thumb, so the thumb metacarpal zone is free for the thumb mount.
(A thumb-hole variant for children who have a thumb is a separate job.)"""
import numpy as np
from sdf import smax

RAY = dict(x1=-21.0, z1=-2.0, y0=27.0, k=4.0)


def ray_field(X, Y, Z):
    # negative inside the region x < x1, z < z1, y > y0 (rounded edges)
    a = X - RAY['x1']; b = Z - RAY['z1']; c = RAY['y0'] - Y
    return smax(smax(a, b, RAY['k']), c, RAY['k'])


def cavity_field(d, g):
    X, Y, Z = g.points()
    return smax(d['cav'], -ray_field(X, Y, Z), 2.0).astype(np.float32)
