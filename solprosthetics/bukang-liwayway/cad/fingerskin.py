"""One finger's own outer skin (no webbing, no neighbours), on its own grid, same growth rules as skin.py.
The finger segments are cut from this instead of the blended hand skin, so their sides stay clean."""
import functools, numpy as np, trimesh
from scipy import ndimage
from rlib import to_mf, to_tm, box, smooth, rot_about
from sdf import Grid, sdf
import skin as SK


@functools.lru_cache(maxsize=1)
def _hand():
    arm = smooth(trimesh.load('src/right-arm-oriented.stl'), 1, 6)
    H = to_mf(arm) - box(*SK.CFG['thumb_box'])
    return H, SK.columns(H)


def finger_outer(n, lo, hi, pitch=0.3):
    H, cols = _hand()
    g = Grid(lo, hi, pitch)
    X, Y, Z = g.points()
    yk = SK.knuckle_y(X)
    fin = rot_about(H ^ cols[n], [0, 0, 1], -SK.SPLAY[n], SK.mcp_point(n))
    ff = sdf(to_tm(fin), g, smooth_sigma=0.25)
    tr = SK.smoothstep(yk - 24, yk + 6, Y)
    off = (SK.PALM_OFF + SK.DORSAL_EXTRA * SK.smoothstep(9, 15, Z)) * (1 - tr) + SK.FING_OFF * tr
    A = SK.splay_axes()[n]; d = np.array(A['dir']); xl = np.cross(d, [0, 0, 1]); xl /= np.linalg.norm(xl)
    zl = np.cross(xl, d); zl = zl if zl[2] > 0 else -zl
    zloc = (X - A['mcp'][0]) * zl[0] + (Y - A['mcp'][1]) * zl[1] + (Z - A['mcp'][2]) * zl[2]
    offn = off + SK.FING_DORSAL * SK.smoothstep(0, 5, zloc) * SK.smoothstep(yk - 3, yk + 5, Y)
    f = ndimage.gaussian_filter(ff - offn, 0.35 / pitch)
    return f.astype(np.float32), g


class FingerSkin:
    def __init__(self, n, lo, hi):
        f, self.g = finger_outer(n, lo, hi)
        self.f = f
        self.c = ndimage.spline_filter(f.astype(np.float64), order=3).astype(np.float32)

    def __call__(self, P):
        idx = ((np.asarray(P, np.float64) - self.g.o) / self.g.p).T
        return ndimage.map_coordinates(self.c, idx, order=3, mode='nearest', prefilter=False).astype(np.float32)
