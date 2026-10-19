"""Stage 1: outer skin and child cavity as signed-distance grids (hand region, thumb removed).
Outer = MakeHuman hand grown by 3.5 mm over the palm (shell wall + liner), easing to 0.8 mm on the fingers.
Fingers get their own distance fields and a slight natural splay so neighbours don't fuse when grown.
Cavity = child's hand + 1.0 mm liner gap, palm only, ending in a rounded face behind the knuckle block."""
import json, numpy as np, trimesh
from rlib import to_mf, to_tm, box, smooth, rot_about
from sdf import Grid, sdf, smax, smin

CFG = json.load(open('src/config.json')); AX = json.load(open('src/finger_axes.json'))
ORDER = ['index', 'middle', 'ring', 'little']
PALM_OFF, FING_OFF, LINER = 3.5, 0.8, 1.0
DORSAL_EXTRA = 1.2      # back of the palm: thicker wall for the hidden line tunnels under the logo
FING_DORSAL = 1.1       # fingers: extra on the back for the return-cord channel above each knuckle
KB = 14.0                      # knuckle block length behind each MCP joint (cavity stops here)
SPLAY = {'index': -2.0, 'middle': 0.0, 'ring': 3.0, 'little': 9.0}   # deg about the knuckle, + = toward little finger
COL_START = 6.0                # finger fields start this far behind the MCP line
PALM_OVER = 2.0                # palm field runs this far past the MCP line (overlap hides the join)


def knuckle_y(x):
    xs = [AX[n]['center'][0] for n in ORDER]; ys = [CFG['MCP_Y'][n] for n in ORDER]
    return np.interp(x, xs, ys)


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


def mcp_point(n):
    t = np.array(AX[n]['tip']); d = np.array(AX[n]['dir']); d /= np.linalg.norm(d)
    return t + d * (CFG['MCP_Y'][n] - t[1]) / d[1]


def splay_axes():
    out = {}
    for n in ORDER:
        R = trimesh.transformations.rotation_matrix(np.radians(-SPLAY[n]), [0, 0, 1], mcp_point(n))
        tip = (R @ np.r_[AX[n]['tip'], 1])[:3]; d = R[:3, :3] @ np.array(AX[n]['dir'])
        out[n] = {'tip': tip.tolist(), 'dir': (d / np.linalg.norm(d)).tolist(), 'mcp': mcp_point(n).tolist(),
                  'L': float(np.linalg.norm(tip - mcp_point(n)))}
    return out


def columns(H):
    cx = [AX[n]['center'][0] for n in ORDER]; cols = {}
    for i, n in enumerate(ORDER):
        l = -60 if i == 0 else (cx[i - 1] + cx[i]) / 2
        r = 60 if i == 3 else (cx[i] + cx[i + 1]) / 2
        cols[n] = box(l, r, CFG['MCP_Y'][n] - COL_START, 200, -40, 40)
    return cols


if __name__ == '__main__':
    arm = smooth(trimesh.load('src/right-arm-oriented.stl'), 1, 6)
    H = to_mf(arm) - box(*CFG['thumb_box'])
    cols = columns(H)
    palm = H
    for n, c in cols.items(): palm = palm - c.translate([0, COL_START + PALM_OVER, 0])
    g = Grid([-48, -24, -36], [40, 140, 36], 0.3)
    X, Y, Z = g.points()
    yk = knuckle_y(X)
    f_palm = sdf(to_tm(palm), g)
    tr = smoothstep(yk - 24, yk + 6, Y)
    off = (PALM_OFF + DORSAL_EXTRA * smoothstep(9, 15, Z)) * (1 - tr) + FING_OFF * tr
    outer = f_palm - off
    f_hand = f_palm.copy()
    for n in ORDER:
        fin = rot_about(H ^ cols[n], [0, 0, 1], -SPLAY[n], mcp_point(n))
        ff = sdf(to_tm(fin), g)
        A = splay_axes()[n]; d = np.array(A['dir']); xl = np.cross(d, [0, 0, 1]); xl /= np.linalg.norm(xl)
        zl = np.cross(xl, d); zl = zl if zl[2] > 0 else -zl
        zloc = (X - A['mcp'][0]) * zl[0] + (Y - A['mcp'][1]) * zl[1] + (Z - A['mcp'][2]) * zl[2]
        offn = off + FING_DORSAL * smoothstep(0, 5, zloc) * smoothstep(yk - 3, yk + 5, Y)
        outer = smin(outer, ff - offn, 1.5)
        f_hand = np.minimum(f_hand, ff)
        print('finger', n, 'done', flush=True)
    cav = smax(f_palm - LINER, Y - (yk - KB), 4.0)
    np.savez_compressed('src/skin.npz', outer=outer.astype(np.float32), cav=cav.astype(np.float32),
                        hand=f_hand.astype(np.float32), o=g.o, p=g.p, n=g.n)
    json.dump(splay_axes(), open('src/finger_axes_splay.json', 'w'), indent=1)
    print('saved skin grid', g.n)
