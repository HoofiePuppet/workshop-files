import os
"""Stage 3 (v3.1): back of the hand (PETG), palm flap (TPU) and thumb, built as smooth distance fields.
Same layout as v3 (palm.py) but every cut is a smooth boolean: rounded seams and wrist end, filleted
thumb barrel and knuckle tongues, rounded vents, tabs and knobs. Tunnels, screw holes and the logo are cut
exactly afterwards. Writes build/palm_back.stl, build/palm_flap.stl, build/thumb.stl, build/palm.json,
build/palm_channels.json"""
import json, numpy as np, trimesh, manifold3d as mf, shapely
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.transform import Rotation as Rot
from rlib import to_tm, frame_matrix
from sdf import Grid, to_manifold, smin, smax, seg_dist
from lib_grid import load_skin
from cavity import cavity_field
from joints import Joint, cyl_x, cyl_x_span, BIG
from sdfparts import Skin, JointSDF, local, opening, opening_true, closing, sweep_carve, rot_points, box2, GAP, chain_field
from fingerskin import FingerSkin
from skin import knuckle_y
import fingers as FG
import fingers2 as F2
from thumb_solve import thumb_rest_field, pad_target
import palm as P3                       # v3 helpers (chan, dorsal_point, surface_point) and constants

ORDER = ['index', 'middle', 'ring', 'little']
J = json.load(open('build/joints.json')); TS = json.load(open('build/thumb_solution.json'))
OUT = 'build'
Z_SEAM, RAY_X, WRIST, EAR_R, TUNNEL_DEPTH = P3.Z_SEAM, P3.RAY_X, P3.WRIST, P3.EAR_R, P3.TUNNEL_DEPTH
LOGO_C, LOGO_SCALE = P3.LOGO_C, P3.LOGO_SCALE
PITCH = 0.3
R_FLEX, R_RET = 0.75, 0.75  # line tunnel radii: 1.5 mm flexor and return cord
WALL_MIN = 3.2              # shell wall round the hand cavity before smoothing (about 2.5 mm finished)
# flap closure (v3.1b): flush lap joints. The TPU flap's edge laps into a recessed step of the back.
# Little-finger side: 3 flush M3 x 4 countersunk screws (the TPU there acts as the hinge).
# Under the knuckles and on the thumb side: thin adhesive hook-and-loop between the lap and a recessed land.
SCREWS_Y = (16.0, 26.0, 36.0)
# v3.1e palm cover: TPU cover = the palm face; its edge (COV_T thick, COV_L wide) lies flush in one even
# recessed step round the opening; 3 flush M3 x 4 screws on the little-finger side, TPU snap bumps elsewhere
COV_T, COV_L = 1.6, 6.0
WALL_COVER = 2.7                    # cover thickness before smoothing (about 2 mm finished)
WALL_RIM, WALL_BOSS = 4.6, 6.2      # shell before smoothing in the band round the opening / at the screws
SNAP_R, SNAP_GAP = 0.7, 11.0        # snap bump radius and spacing
EAR_EXT = 0.0                       # (v3.1e had 2.1; v3.1f trims the hand flat at the ears instead)
OPEN_X, OPEN_Y, OPEN_R = (-10.0, 17.0), (4.0, 42.0), 9.0   # palm opening: symmetric rounded rectangle (x, y, corner r)
SCREW_X = 20.0                      # cover screws on the palm face, along the little-finger edge


class Sampler:
    """Cubic-spline sampler for any grid field."""
    def __init__(self, f, g):
        self.g = g; self.c = ndimage.spline_filter(f.astype(np.float64), order=3).astype(np.float32)

    def __call__(self, P):
        idx = ((np.asarray(P, np.float64) - self.g.o) / self.g.p).T
        return ndimage.map_coordinates(self.c, np.atleast_2d(idx), order=3, mode='nearest', prefilter=False).astype(np.float32)


def chan_pts(pts, r, fields, need=(1.0, 0.8)):
    """Tunnel centre line kept >= need[0] mm under the skin and >= need[1] mm off the cavity (as palm.chan)."""
    pts = [np.asarray(p, float) for p in pts]
    dense = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        k = max(2, int(np.linalg.norm(b - a) / 1.5))
        dense += [a + (b - a) * t for t in np.linspace(0, 1, k + 1)[1:]]
    P = np.array(dense); FO, FC = fields; h = 0.15
    for _ in range(12):
        wo = -FO(P[1:-1]) - r; wc = FC(P[1:-1]) - r
        no = np.clip(need[0] - wo, 0, 3); nc = np.clip(need[1] - wc, 0, 3)
        if max(no.max(), nc.max()) < 0.02: break
        go = np.stack([(FO(P[1:-1] + h * e) - FO(P[1:-1] - h * e)) / (2 * h) for e in np.eye(3)], 1)
        gc_ = np.stack([(FC(P[1:-1] + h * e) - FC(P[1:-1] - h * e)) / (2 * h) for e in np.eye(3)], 1)
        go /= np.linalg.norm(go, axis=1, keepdims=True) + 1e-9; gc_ /= np.linalg.norm(gc_, axis=1, keepdims=True) + 1e-9
        P[1:-1] += -go * no[:, None] + gc_ * nc[:, None]
        P[2:-2] = (P[1:-3] + 2 * P[2:-2] + P[3:-1]) / 4
    P3.CHANNELS.append({'r': r, 'pts': P.tolist()})
    return P


try:                                    # optional local step, not part of the published source
    from finish_private import finish_thumb
except ImportError:
    finish_thumb = None


def cyl_axis(P, O, a, r):
    a = np.asarray(a, float); a = a / np.linalg.norm(a); Q = P - O
    return np.linalg.norm(Q - np.outer(Q @ a, a), axis=1) - r


def ellipsoid(P, c, axes, radii):
    Q = P - c
    q = np.stack([Q @ np.asarray(ax) / r for ax, r in zip(axes, radii)], 1)
    return (np.linalg.norm(q, axis=1) - 1.0) * min(radii)


def main():
    d, g0 = load_skin()
    Sk = Skin()
    cav0 = cavity_field(d, g0)
    Cv = Sampler(cav0, g0)
    FO0 = RegularGridInterpolator(g0.axes(), d['outer'], bounds_error=False, fill_value=20)
    pivot = np.array(TS['pivot'])

    # ---------------- outer2: skin + thenar boss + ear pads + line hump (all smooth unions)
    ears = []
    for sx in (-1, 1):
        xs = np.arange(-40, 45, 0.1)
        v = FO0(np.stack([xs, np.full_like(xs, WRIST[1]), np.full_like(xs, WRIST[2])], 1))
        inside = xs[v < 0]; ears.append(inside.min() if sx < 0 else inside.max())
    hx = WRIST[0] - 3.9
    ztop = P3.dorsal_point(FO0, hx, 1.0, 0.0)[2]

    def outer2(P):
        f = Sk(P)
        f = smin(f, np.linalg.norm(P - pivot, axis=1) - 10.0, 5.0)
        for xw in ears:
            ext = EAR_EXT if xw < WRIST[0] else 0.0                # thumb-side pad reaches 2.1 mm further out to meet the cuff arm
            xc_, hw_ = xw - np.sign(WRIST[0] - xw) * ext / 2, 2.0 + ext / 2
            pad = smax(np.sqrt((P[:, 1] - WRIST[1]) ** 2 + (P[:, 2] - WRIST[2]) ** 2) - EAR_R, np.abs(P[:, 0] - xc_) - hw_, 1.0)
            f = smin(f, pad, 3.5)
        # line guide: a broad, low swelling of the back at the wrist end (was a separate hump)
        bell = 2.6 * np.exp(-((P[:, 0] - hx) / 16.0) ** 2 - ((P[:, 1] - 2.0) / 10.0) ** 2)
        top = np.clip((P[:, 2] - (ztop - 10.0)) / 6.0, 0, 1)
        return f - bell * top

    # ---------------- grid
    bb = np.array([trimesh.load(f'build_v3/{p}.stl').bounds for p in ('palm_back', 'palm_flap')])
    g = Grid(bb[:, 0].min(0) - 3, bb[:, 1].max(0) + 3, PITCH)
    X, Y, Z = g.points(); shape = X.shape
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(np.float32); del X, Y, Z
    O2 = outer2(P)
    FO = Sampler(O2.reshape(shape), g)                      # outer2 as a sampler (tunnels, logo)
    # ---------------- flap seam (needed early: the closure laps need a slightly thicker wall along it)
    from skin import smoothstep
    xs = np.linspace(-60, 60, 241); yk_x = knuckle_y(xs)
    top = [(x, min(yt, 22.0) if x < RAY_X else yt) for x, yt in zip(xs, yk_x - 15.0)]
    poly = shapely.Polygon([(-60, -1.0)] + top + [(60, -1.0)])
    gx = g.o[0] + g.p * np.arange(g.n[0]); gy = g.o[1] + g.p * np.arange(g.n[1])
    GX, GY = np.meshgrid(gx, gy, indexing='ij')
    pts2 = shapely.points(GX.ravel(), GY.ravel())
    d2 = shapely.distance(pts2, poly.exterior).reshape(GX.shape)
    d2 = np.where(shapely.contains(poly, pts2).reshape(GX.shape), -d2, d2).astype(np.float32)
    del pts2, GX, GY
    D2 = np.broadcast_to(d2[:, :, None], shape).ravel()
    region = smax(D2, P[:, 2] - Z_SEAM, 0.8)
    rw = np.sqrt((P[:, 1] - WRIST[1]) ** 2 + (P[:, 2] - WRIST[2]) ** 2)
    earz = rw - (EAR_R + 1.85)
    def rrect(x0, x1, y0, y1, r):
        cx_, cy_, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
        dx = np.abs(P[:, 0] - cx_) - hx; dy = np.abs(P[:, 1] - cy_) - hy
        return (np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) + np.minimum(np.maximum(dx, dy), 0) - r).astype(np.float32)
    s0 = smax(rrect(OPEN_X[0], OPEN_X[1], OPEN_Y[0], OPEN_Y[1], OPEN_R), P[:, 2] - (Z_SEAM - 4.0), 1.0)   # < 0 inside the opening
    s_open = s0.copy()
    screw_pts = [P3.surface_point(FO, np.array([SCREW_X, yy, -40.0]), np.array([0, 0, -1.0]), lo=-45, hi=0) for yy in SCREWS_Y]
    # v3.1e: no seam swelling. Wall minimum all round the cavity, thicker in a band round the opening (cover
    # lip + ledge; wide enough for wherever the final edge lands) and locally round the three hinge screws
    cvP = Cv(P)
    rim = (1 - smoothstep(COV_L + 2.0, COV_L + 12.0, np.abs(s0 - COV_L / 2))).astype(np.float32)
    boss = np.zeros(len(P), np.float32)
    for yy in SCREWS_Y:
        boss = np.maximum(boss, np.clip(1 - (np.linalg.norm(P - screw_pts[SCREWS_Y.index(yy)], axis=1) - 5.0) / 3.0, 0, 1))
    base = WALL_MIN + (WALL_COVER - WALL_MIN) * smoothstep(-2.0, -10.0, s0)   # thinner inside the opening (the cover)
    wall = base + (WALL_RIM - base) * rim; del base
    wall = wall + (WALL_BOSS - wall) * boss
    wall_ok = smoothstep(3.0, 7.0, earz)                    # not at the wrist ears (cuff clearance)
    O2s = (wall_ok * smin(O2, cvP - wall, 1.5) + (1 - wall_ok) * O2).astype(np.float32)
    del wall_ok, rim, boss, wall, s0
    FS2 = Sampler(O2s.reshape(shape), g)
    shell = smax(O2s, -cvP, 0.8); del cvP
    print('shell field done', flush=True)

    # ---------------- knuckles: palm stops at each MCP joint (cup + tongue), carved for segment 1's swing
    kc = np.full(len(P), 15.0, np.float32)         # finger swing carve, collected then smoothed
    for i, n in enumerate(ORDER):
        J0 = JointSDF(J[n]['joints'][0], **F2.joint_params(n, 0))
        near = J0.cyl(P, J0.R + 16) < 0
        Pn = P[near]
        removal = np.maximum(F2.column(Pn, i, shrink=-0.3), -J0.side(Pn, 'P'))      # all but the palm's cup side
        s = smax(shell[near], -removal, 1.4)
        s = smin(s, J0.tongue(Pn), 1.0)
        info = J[n]['joints']
        bbf = np.array([trimesh.load(f'build_v3/fingers/{n}-1.stl').bounds])
        Sf = FingerSkin(n, bbf[:, 0].min(0) - 4, bbf[:, 1].max(0) + 4)
        J1 = JointSDF(info[1], **F2.joint_params(n, 1))
        def seg1(Q, J0=J0, J1=J1, Sf=Sf, i=i):
            f = smax(Sf(Q), F2.column(Q, i), 2.0)
            f = smax(f, J0.side(Q, 'D'), 0.8)
            return smax(f, J1.side(Q, 'P'), 0.8)
        def zone(Q, J0=J0):
            u, v, w = J0.loc(Q)
            return smax(smax(GAP / 2 - 0.35 - v, v - (J0.R + 10), 0.0), -(np.sqrt(v * v + w * w) - (J0.R + 0.05)), 0.0)
        m = (J0.cyl(Pn, J0.R + 13) < 0) & (s < 1.0)
        sw = sweep_carve(Pn[m], J0.O, J0.x, lambda Q: smax(seg1(Q), zone(Q), 0.0), np.arange(0, F2.FLEX[0] + 4.1, 2.5), grow=0.35)
        idx = np.nonzero(near)[0][m]
        kc[idx] = np.minimum(kc[idx], np.clip(sw, -15, 15))
        shell[near] = s
        print('knuckle', n, flush=True)

    # the discrete swing steps leave fine ridges: smooth the carve before cutting with it
    kc = ndimage.gaussian_filter(kc.reshape(shape), 0.45 / g.p).ravel()
    shell = smax(shell, -kc, 0.6)
    # ---------------- thumb hinge: palm owns a slotted barrel; the swept thumb is carved out first
    ax_w = np.array(TS['hinge_axis']); R_open = Rot.from_quat(TS['open_quat'])
    xj = -ax_w / np.linalg.norm(ax_w)
    tf, tg, t_scaled = thumb_rest_field(pivot)
    tf = ndimage.gaussian_filter(tf, 0.35 / tg.p)
    TF = Sampler(tf, tg)
    pad_r = t_scaled.vertices[np.argmax(np.linalg.norm(t_scaled.vertices - pivot, axis=1))]
    mid = Rot.from_rotvec(ax_w * np.radians(TS['swing_deg'] / 2)) * R_open
    yj = mid.apply(pad_r - pivot); yj -= xj * (yj @ xj); yj /= np.linalg.norm(yj); zj = np.cross(xj, yj)
    Rinv = R_open.inv()
    xr, yr, zr = Rinv.apply(xj), Rinv.apply(yj), Rinv.apply(zj)
    tinfo_w = dict(O=pivot.tolist(), x=xj.tolist(), d=yj.tolist(), z=zj.tolist(), R=6.5, Rt=4.5)
    tinfo_r = dict(O=pivot.tolist(), x=xr.tolist(), d=yr.tolist(), z=zr.tolist(), R=6.5, Rt=4.5)
    TJw = JointSDF(tinfo_w, 'P', 6.0, 7.5, 3.4, (-6, TS['swing_deg'] + 6))
    TJr = JointSDF(tinfo_r, 'P', 6.0, 7.5, 3.4, (-6, TS['swing_deg'] + 6))
    LB = 15.0

    def big_thumb_rest(Q):
        u, v, w = TJr.loc(Q)
        neck = np.maximum(box2(v - (TJr.R + GAP + 5.0) / 2, w, (TJr.R + GAP + 5.0) / 2, 3.4 + 0.35), np.abs(u) - 7.5 / 2)   # matches the thumb's long neck
        f = np.minimum(TF(Q) - 0.5, neck)
        return np.maximum(f, -(np.sqrt(v * v + w * w) - (TJr.R - 0.03)))

    m = (np.linalg.norm(P - pivot, axis=1) < 60) & (shell < 1.0)
    Pm = P[m]; sw = np.full(len(Pm), 1e3, np.float32)
    for fr in np.linspace(-0.05, 1.05, 34):
        R = Rot.from_rotvec(ax_w * np.radians(TS['swing_deg'] * fr)) * R_open
        Q = R.inv().apply(Pm - pivot) + pivot
        sw = np.minimum(sw, big_thumb_rest(Q))
    tsw = np.full(len(P), 15.0, np.float32); tsw[m] = np.clip(sw, -15, 15)
    tsw = ndimage.gaussian_filter(tsw.reshape(shape), 0.45 / g.p).ravel()   # smooth swing carve
    shell = smax(shell, -tsw, 0.8)
    u, v, w = TJw.loc(P)
    barrel = smax(np.sqrt(v * v + w * w) - TJw.R, np.abs(u) - LB / 2, 1.2)
    shell = smin(shell, barrel, 1.5)
    shell = smax(shell, -tsw, 0.4)          # re-carve: the barrel fillet must not bridge into the thumb's path
    # webs left standing between the thumb's path and the index finger's path: material within 2 mm of
    # both carves is too thin to be useful and looks like stray struts, so it goes (barrels excluded)
    web = np.maximum(kc, tsw) - 2.0
    keepz = TJw.cyl(P, TJw.R + 1.5)
    for n in ORDER:
        keepz = np.minimum(keepz, JointSDF(J[n]['joints'][0], **F2.joint_params(n, 0)).cyl(P, 7.5))
    web = np.maximum(web, -keepz)
    shell = smax(shell, -web, 0.6)
    del web, keepz
    mb = TJw.cyl(P, TJw.R + 0.6) < 0
    slot = TJw.slot_from(P[mb], lambda Q: TJw.tongue(Q) - 0.15, step=3.0)
    shell[mb] = smax(shell[mb], -slot, 0.4)
    slot_full = np.full(len(P), 5.0, np.float32); slot_full[mb] = slot
    print('thumb mount done', flush=True)

    # ---------------- wrist end: keep the hand side of y = -1 plus the hinge ear discs, rounded
    rw = np.sqrt((P[:, 1] - WRIST[1]) ** 2 + (P[:, 2] - WRIST[2]) ** 2)
    disc = np.maximum(rw - EAR_R, np.maximum(-14 - P[:, 1], P[:, 1] - 0.0))
    keep = smin(-1.0 - P[:, 1], disc, 1.5)
    shell = smax(shell, keep, 0.9)
    del disc, barrel, u, v, w, mb, slot, m, Pm, sw
    import gc; gc.collect()

    # ---------------- drain (rounded)
    xd = (np.array(J['middle']['joints'][0]['O'])[0] + np.array(J['ring']['joints'][0]['O'])[0]) / 2
    ykd = knuckle_y(xd)
    dpts = [np.array([xd, ykd - 17, 2.0]), np.array([xd, ykd - 9, -8]), np.array([xd, ykd - 6, -22])]
    drain = np.minimum(seg_dist(P, dpts[0], dpts[1]), seg_dist(P, dpts[1], dpts[2])) - 1.3
    shell = smax(shell, -drain, 0.5)
    drain_f = drain

    # ---------------- split: the TPU cover is the palm face inside the opening; the opening keeps
    # COV_L + 2 mm away from the finger and thumb swing carves, so its edge (and the step under it) only
    # ever runs over smooth skin
    flap_reg = s_open; del s_open
    band = (flap_reg > -1.0) & (flap_reg < COV_L + 1.0)
    print('opening band clearance: min thumb-swing', round(float(tsw[band].min()), 2), 'min finger-swing', round(float(kc[band].min()), 2), flush=True)
    flap = smax(shell, flap_reg + 0.15, 0.7)
    back = smax(shell, -(flap_reg - 0.15), 0.7)
    back = opening(back.reshape(shape), g, 0.45).ravel()
    flap = opening(flap.reshape(shape), g, 0.45).ravel()
    # the knuckle block / thumb mount junction: close slits, then cut the functional clearances again
    back = closing(back.reshape(shape), g, 0.9).ravel()
    back = smax(back, -kc, 0.6)
    back = smax(back, -tsw, 0.4)
    for i, n in enumerate(ORDER):
        J0 = JointSDF(J[n]['joints'][0], **F2.joint_params(n, 0))
        near = J0.cyl(P, J0.R + 16) < 0
        Pn = P[near]
        b = smax(back[near], -np.maximum(F2.column(Pn, i, shrink=-0.3), -J0.side(Pn, 'P')), 0.8)
        back[near] = smin(b, J0.tongue(Pn), 1.0)
    back = smax(back, -slot_full, 0.4)
    back = smax(back, -drain_f, 0.5)
    back = smax(back, keep, 0.9)
    back = smax(back, -(flap_reg - 0.15), 0.7)
    del slot_full
    wz = (smoothstep(-2.0, -8.0, P[:, 0]) * smoothstep(36.0, 42.0, P[:, 1]) * smoothstep(66.0, 60.0, P[:, 1])
          * smoothstep(3.0, -1.0, P[:, 2])).astype(np.float32)
    opened = opening(back.reshape(shape), g, 1.0).ravel()
    back = back + wz * (opened - back)
    del opened, wz, D2, region, shell
    del d, Sk, cav0, FO0
    gc.collect()
    print('split done', flush=True)

    # ---------------- polish (not at the working features)
    def keep_w():
        w = np.zeros(len(P), np.float32)
        for n in ORDER:
            J0 = JointSDF(J[n]['joints'][0], **F2.joint_params(n, 0))
            u0, v0, w0 = J0.loc(P)
            d0 = np.maximum(np.sqrt(v0 * v0 + w0 * w0) - (J0.R + 1.5), np.abs(u0) - 9.0)
            w = np.maximum(w, np.clip(1 - d0 / 2.0, 0, 1))
        ut, vt, wt_ = TJw.loc(P)
        dt = np.maximum(np.sqrt(vt * vt + wt_ * wt_) - (TJw.R + 2.0), np.abs(ut) - (LB / 2 + 2.0))
        w = np.maximum(w, np.clip(1 - dt / 2.0, 0, 1))
        de = np.sqrt((P[:, 1] - WRIST[1]) ** 2 + (P[:, 2] - WRIST[2]) ** 2) - (EAR_R + 1.0)
        w = np.maximum(w, np.clip(1 - de / 2.0, 0, 1) * (np.minimum(np.abs(P[:, 0] - ears[0]), np.abs(P[:, 0] - ears[1])) < 6))
        return w
    wk = keep_w()
    back = wk * back + (1 - wk) * ndimage.gaussian_filter(back.reshape(shape), 0.9 / g.p).ravel()
    flap = wk * flap + (1 - wk) * ndimage.gaussian_filter(flap.reshape(shape), 0.9 / g.p).ravel()
    del wk

    # ---------------- cover edge: one even lip (COV_T thick) all round, lying flush in a matching step of the
    # back (the ledge under it is what the snaps and screws hold on to)
    s = flap_reg
    band_out = np.maximum(s - COV_L, -s - 3.0)                          # 3 mm overlap into the cover: one piece
    band_out = np.maximum(np.maximum(band_out, 5.0 - earz), P[:, 2] - (Z_SEAM - 7.0))   # lip only on the palm face
    lip = smax(smax(O2s, -(O2s + COV_T), 0.3), band_out, 0.5)
    lip = smax(lip, keep, 0.5)
    flap = smin(flap, lip, 0.6)
    step = np.maximum(-(O2s + COV_T + 0.15), np.maximum(s - (COV_L + 0.25), -s - 1.0))
    step = np.maximum(np.maximum(step, 4.7 - earz), P[:, 2] - (Z_SEAM - 7.3))
    back = smax(back, -step, 0.4)
    # snap points along the middle of the lip (not on the screwed little-finger side)
    near_mid = (np.abs(s - COV_L / 2) < 0.25) & (np.abs(O2s + COV_T) < 0.25) & (earz > 7.0) & (np.min([np.linalg.norm(P - sp_, axis=1) for sp_ in screw_pts], axis=0) > 7.0)
    cand = P[near_mid]
    snaps = []
    for c_ in cand[np.argsort(cand[:, 1])]:
        if all(np.linalg.norm(c_ - q_) > SNAP_GAP for q_ in snaps):
            snaps.append(c_)
    print('snaps', len(snaps), flush=True)
    lip_keep = lip.astype(np.float32)       # the lip is only 1.5 mm: the cover's 0.6 opening would erase it
    del lip, step, band_out, near_mid, cand
    gc.collect()

    # ---------------- raised oval grip on the cover: an egg shape, wider toward the fingers, raised 0.8 mm
    # and blended in smoothly (no step)
    ex, ey = P[:, 0] - 4.0, P[:, 1] - 24.0
    eb = np.where(ey > 0, 12.0, 9.0)
    egg = np.sqrt((ex / 15.0) ** 2 + (ey / eb) ** 2) - 1.0
    hgt = (0.8 * (1 - smoothstep(-0.35, 0.0, egg)) * smoothstep(Z_SEAM - 3.0, Z_SEAM - 7.0, P[:, 2])
           * smoothstep(-2.0, -6.0, flap_reg)).astype(np.float32)          # every factor smooth: no seam
    raised = np.maximum(np.maximum(O2s - hgt, -(O2s + 1.2)), flap_reg + 2.0)
    flap = np.minimum(flap, raised)
    del ex, ey, eb, egg, hgt, raised
    print('cover done', flush=True)

    # ---------------- line tunnels, cut in the field so every mouth is a rounded flare (no hard cut edges)
    P3.CHANNELS.clear()
    exits = np.linspace(WRIST[0] - 9.1, WRIST[0] + 9.1, 8)
    tun = np.full(len(P), 1e3, np.float32)
    k = 0
    for n in ORDER:
        info = J[n]['joints'][0]; O0 = np.array(info['O']); xf, df = np.array(info['x']), np.array(info['d'])
        R0 = info['R']; F0 = np.array(J[n]['flexor'][0]); Rr0 = np.array(J[n]['return'][0])
        for kind, start, lat in (('flex', F0, -1.3), ('ret', Rr0, 1.3)):
            r = R_FLEX if kind == 'flex' else R_RET
            q = O0 - df * 16 + xf * lat
            D = P3.dorsal_point(FO, q[0], q[1], TUNNEL_DEPTH)
            if kind == 'flex':
                A = start - df * (R0 + 1.0); B = A - df * 3.5
                climb = FG.spline([A, B, D + df * 3.0, D], 14)            # starts behind the tongue
            else:
                climb = FG.spline([start - df * (R0 + 1.0), start - df * (R0 + 4.0), D + df * 3.0, D], 12)
            run = [P3.dorsal_point(FO, D[0] + (exits[k] - D[0]) * t, D[1] + (-2.0 - D[1]) * t, TUNNEL_DEPTH) for t in np.linspace(0, 1, 26)[1:]]
            path = chan_pts(climb + run[:-1] + [run[-1] - np.array([0, 3.0, 0])], r, (FO, Cv))
            tun = np.minimum(tun, chain_field(P, path, r))
            for e0, e1 in ((path[0], path[1]), (path[-1], path[-2])):      # flared mouths
                dv = e1 - e0; dv /= np.linalg.norm(dv) + 1e-9
                tun = np.minimum(tun, seg_dist(P, e0 - dv * 1.0, e0 + dv * 1.8) - (r + 0.45))
            if kind == 'ret':                                    # knot counterbore at the wrist end
                e = run[-1]
                tun = np.minimum(tun, seg_dist(P, np.array([e[0], 0.8, e[2]]), np.array([e[0], -3.0, e[2]])) - 1.6)
            k += 1
    print('tunnels routed', flush=True)
    cvl = Cv(P)
    inner = np.maximum(np.maximum(cvl - 2.0, -cvl), np.maximum(np.maximum(0.8 - tsw, 0.8 - kc), np.maximum(0.8 - drain_f, keep)))
    inner = np.maximum(inner, -(flap_reg - 1.0))                                  # not under the cover
    inner = np.maximum(inner, -(TJw.cyl(P, TJw.R + 1.0)))                         # not in the thumb barrel
    back = smin(back, inner, 0.4); del cvl, inner
    # flat faces at the wrist ears: nothing of the hand beyond the ear pads' outer faces near the hinge axis,
    # so the cuff arms sit close and clear
    rwe = np.sqrt((P[:, 1] - WRIST[1]) ** 2 + (P[:, 2] - WRIST[2]) ** 2)
    fade = (1 - smoothstep(EAR_R + 3.0, EAR_R + 7.0, rwe)).astype(np.float32)
    for xw in ears:
        sx_ = -1 if xw < WRIST[0] else 1
        beyond = sx_ * (P[:, 0] - (xw + sx_ * 2.0))
        back = np.where(fade > 0, smax(back, beyond - 10.0 * (1 - fade), 0.6), back)
    del rwe, fade, beyond
    del O2s, kc, tsw, s, flap_reg, keep, drain_f, drain, rw, earz
    gc.collect()

    # ---------------- final rounding
    ends_ = np.array([pivot + xj * LB / 2, pivot - xj * LB / 2])
    hs_ = 1 if Cv(ends_)[0] > Cv(ends_)[1] else -1
    acc = seg_dist(P, pivot + hs_ * xj * (LB / 2 - 1.5), pivot + hs_ * xj * 45.0) - 3.4
    back = smax(back, -acc, 0.6); del acc
    back = opening_true(back.reshape(shape), g, 0.9).ravel()      # nothing under 1.8 mm on the PETG back
    flap = opening_true(flap.reshape(shape), g, 0.6).ravel()      # nothing under 1.2 mm on the TPU cover
    flap = smin(flap, lip_keep, 0.3); del lip_keep                 # ...except the even edge lip, put back
    # tunnels after the rounding (it would eat the thin roof over a tunnel); smooth subtraction rounds the mouths
    back = smax(back, -tun, 0.4); del tun
    # snaps: a 0.7 mm TPU bump under the cover's lip clicks into a matching dimple in the ledge
    print('final rounding done', flush=True)

    # ---------------- mesh, then exact cuts
    Mback = max(to_manifold(back.reshape(shape), g, 0.0, simplify=0.01).decompose(), key=lambda p: p.volume())
    _fp = to_manifold(flap.reshape(shape), g, 0.0, simplify=0.01).decompose()
    print('flap pieces', sorted([round(q.volume()) for q in _fp], reverse=True)[:5], flush=True)
    Mflap = max(_fp, key=lambda p: p.volume())
    del back, flap, _fp, P
    gc.collect()
    # flap screws (little-finger side): countersink in the TPU lip, blind pilot in the PETG step; the
    # screw length is picked from the PETG measured under each screw so the tip stays clear of the cavity
    flap_screws = []
    tmB = to_tm(Mback)
    for yy in SCREWS_Y:
        p = P3.surface_point(FS2, np.array([SCREW_X, yy, -40.0]), np.array([0, 0, -1.0]), lo=-45, hi=0)
        e = 0.2; gr = np.array([(FS2((p + dv)[None])[0] - FS2((p - dv)[None])[0]) / (2 * e) for dv in np.eye(3) * e])
        n_ = gr / np.linalg.norm(gr)
        loc, _, _ = tmB.ray.intersects_location([p - n_ * (COV_T + 0.3)], [-n_], multiple_hits=True)
        dd = np.sort((p - n_ * (COV_T + 0.3) - loc) @ n_) if len(loc) else np.array([0.0])
        petg = float(dd[0] + 0.3 - 0.1) if len(dd) else 0.0      # PETG from the step floor to the cavity
        L_s = max([L_ for L_ in (4, 5, 6, 8) if L_ - COV_T + 0.4 <= petg] or [4])
        u_ = np.cross(n_, [0, 1, 0]); u_ /= np.linalg.norm(u_); w_ = np.cross(n_, u_)
        Ms = frame_matrix(p, u_, w_, n_)
        csk = mf.Manifold.cylinder(1.5, 1.55, 2.95, 32).translate([0, 0, -1.45]) + mf.Manifold.cylinder(0.6, 2.95, 2.95, 32).translate([0, 0, 0.0])
        thru = mf.Manifold.cylinder(COV_T + 0.6, 1.7, 1.7, 24).translate([0, 0, -COV_T - 0.4])
        pilot = mf.Manifold.cylinder(L_s - COV_T + 0.4, 1.3, 1.3, 24).translate([0, 0, -(L_s + 0.3)])
        Mflap = Mflap - (csk + thru).transform(Ms)
        Mback = Mback - csk.transform(Ms)                     # the head may sit a little into the ledge
        Mback = Mback - pilot.transform(Ms)
        flap_screws.append({'p': p.round(2).tolist(), 'n': n_.round(3).tolist(), 'petg_under_step': round(petg, 2), 'screw_len': L_s})
        print('flap screw', flap_screws[-1], flush=True)
    # through-snaps (v3.1f): a TPU peg under the cover's lip pushes through a hole in the PETG step; its
    # cone head pops out into a counterbore on the inside and holds. Flush on the inside, nothing to see outside.
    snap_info = []
    for c_ in snaps:
        e = 0.2; gr = np.array([(FS2((c_ + dv)[None])[0] - FS2((c_ - dv)[None])[0]) / (2 * e) for dv in np.eye(3) * e])
        n_ = gr / np.linalg.norm(gr)
        p0 = c_ - n_ * 0.3
        loc, _, _ = tmB.ray.intersects_location([p0], [-n_], multiple_hits=True)
        dd = np.sort((p0 - loc) @ n_) if len(loc) else np.array([])
        t = float(dd[0] + 0.3) if len(dd) else 0.0        # PETG thickness from the step floor to the cavity
        if t < 2.6:
            print('snap skipped (PETG', round(t, 2), ')', flush=True); continue
        cb = min(1.2, t - 1.4)                              # counterbore depth on the cavity side
        u_ = np.cross(n_, [0, 1, 0]); u_ /= np.linalg.norm(u_); w_ = np.cross(n_, u_)
        Ms = frame_matrix(c_, u_, w_, -n_)                  # local +z points into the part, 0 = step floor
        shaft = mf.Manifold.cylinder(t - cb + 0.5, 1.4, 1.4, 32).translate([0, 0, -0.5])
        head = mf.Manifold.cylinder(cb - 0.15, 2.0, 1.15, 32).translate([0, 0, t - cb])
        hole = mf.Manifold.cylinder(t + 1.0, 1.6, 1.6, 32).translate([0, 0, -0.5])
        cbore = mf.Manifold.cylinder(cb + 1.0, 2.45, 2.45, 32).translate([0, 0, t - cb])
        Mflap = Mflap + (shaft + head).transform(Ms)
        Mback = Mback - (hole + cbore).transform(Ms)
        snap_info.append({'p': np.round(c_, 2).tolist(), 'petg': round(t, 2), 'counterbore': round(cb, 2)})
    print('through-snaps', len(snap_info), [s_['petg'] for s_ in snap_info], flush=True)
    del tmB
    # knuckle tongues: an exact round ring round each bore (the field tongue had bites taken out of it,
    # which made the bores look off-centre); inset so it never grows past the tongue the finger was fitted to
    for n in ORDER:
        inf = J[n]['joints'][0]; jp = F2.joint_params(n, 0)
        Mt = frame_matrix(np.array(inf['O']), np.array(inf['x']), np.array(inf['d']), np.array(inf['z']))
        hw = jp['wt'] / 2 - 0.35
        ring = cyl_x_span(inf['Rt'] - 0.25, -hw, hw)
        reach = inf['R'] + GAP + 2.0
        neck = mf.Manifold.cube([2 * hw, reach, 2 * (jp['hn'] - 0.35)]).translate([-hw, -reach, -(jp['hn'] - 0.35)])
        Mback = Mback + (ring + neck).transform(Mt)
    Wm = frame_matrix(WRIST, np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.]))
    Mw = frame_matrix(pivot, xj, yj, zj)
    # thumb screw: head on the end farther from the cavity, blind pilot in the other arm
    ends = [pivot + xj * LB / 2, pivot - xj * LB / 2]
    headside = 1 if Cv(np.array(ends))[0] > Cv(np.array(ends))[1] else -1
    w = 7.5 / 2
    if headside > 0:
        sc = cyl_x_span(3.1, LB / 2 - 1.5, BIG) + cyl_x_span(1.7, -w, BIG) + cyl_x_span(1.3, -LB / 2 + 0.8, -w + 0.01)
    else:
        sc = cyl_x_span(3.1, -BIG, -LB / 2 + 1.5) + cyl_x_span(1.7, -BIG, w) + cyl_x_span(1.3, w - 0.01, LB / 2 - 0.8)
    Mback = Mback - sc.transform(Mw)
    # MCP joints: the palm owns the tongues; each needs its 3.4 mm bore for the knuckle screw
    for n in ORDER:
        inf = J[n]['joints'][0]
        hb = F2.joint_params(n, 0)['wt'] / 2 + 2.5          # only through this tongue (an endless bore cut into the neighbours)
        Mback = Mback - cyl_x_span(1.7, -hb, hb).transform(frame_matrix(np.array(inf['O']), np.array(inf['x']), np.array(inf['d']), np.array(inf['z'])))
    for sx, xw in zip((-1, 1), ears):
        x_out = xw + sx * (2.0 + (EAR_EXT if sx < 0 else 0.0))
        xl = x_out - WRIST[0]                                 # the frame below is centred on the wrist axis
        hole = cyl_x_span(1.3, xl - 1, xl + 4.0) if sx < 0 else cyl_x_span(1.3, xl - 4.0, xl + 1)
        Mback = Mback - hole.transform(Wm)
    # logo, pressed 0.8 mm into the curved back
    rects = json.load(open('src/logo_rects.json'))
    # centre the logo across the back of the hand (midway between the side walls, measured just under
    # the top of the back) and along it between the wrist swelling and the knuckles
    ycen = 35.0
    xs_ = np.arange(-45, 45, 0.1); zt = P3.dorsal_point(FO, -3.0, ycen, 0.0)[2]
    vv = FO(np.stack([xs_, np.full_like(xs_, ycen), np.full_like(xs_, zt - 4.0)], 1)); xin = xs_[vv < 0]
    LOGO_C = ((xin.min() + xin.max()) / 2, ycen); LOGO_SCALE = 0.72
    print('logo centre', np.round(LOGO_C, 1), flush=True)
    polys = [[(LOGO_C[0] + x * LOGO_SCALE, LOGO_C[1] + y * LOGO_SCALE) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))] for x0, x1, y0, y1 in rects]
    cs = mf.CrossSection.batch_boolean([mf.CrossSection([p]) for p in polys], mf.OpType.Add)
    logo = cs.offset(0.06, mf.JoinType.Miter).extrude(40).translate([0, 0, 5])
    ins08 = to_manifold((O2 + 0.8).reshape(shape), g, 0.0, simplify=0.01)
    Mback = Mback - (logo - ins08)
    del ins08, O2, FS2
    gc.collect()

    # ---------------- thumb part (rest pose): cup + tongue, rubber pocket, opening
    tgf = Grid(tg.o, tg.o + tg.p * (tg.n - 1), 0.15)          # finer grid for the thumb (crisp pocket lip)
    X, Y, Z = tgf.points(); tshape = X.shape
    T = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(np.float32); del X, Y, Z
    TFv = TF(T)
    ft = TFv.copy()
    ft = smax(ft, -(TJr.cyl(T, TJr.R + GAP)), 0.6)
    ft = smax(ft, TJr.side(T, 'D'), 0.6)          # nothing of the thumb wraps past the hinge axis
    ft = smax(ft, -TJr.cyl(T, TJr.R + GAP + 1.6), 0.8)   # no thin hood round the palm's barrel: the tongue alone carries the hinge
    ft = smin(ft, TJr.tongue(T), 1.0)
    # the tongue's neck runs 5 mm into the thumb body and is filleted in, so the hinge eye is part of the thumb
    ut_, vt_, wt2 = TJr.loc(T)
    reach2 = TJr.R + GAP + 5.0
    neck2 = smax(box2(vt_ - reach2 / 2, wt2, reach2 / 2, TJr.hn), np.abs(ut_) - TJr.wt / 2, 0.6)
    ft = smin(ft, neck2, 2.0); del ut_, vt_, wt2, neck2
    # the cup hood round the palm's barrel thins to a knife edge: trim anything under 1.8 mm there
    wzt = np.clip(1 - TJr.cyl(T, TJr.R + GAP + 3.0) / 1.5, 0, 1).astype(np.float32)
    fo = opening(ft.reshape(tshape), tgf, 0.9).ravel()
    ft = ft + wzt * (np.maximum(ft, fo) - ft); del fo, wzt
    ft = opening(ft.reshape(tshape), tgf, 0.45).ravel()
    Rp = Rot.from_rotvec(TS['pinch_rotvec'])
    tip_w = Rp.apply(pad_r - pivot) + pivot
    tgt = pad_target(TS['pinch_curl_deg'])
    n_rest = Rp.inv().apply((tgt - tip_w) / np.linalg.norm(tgt - tip_w))
    c0 = pad_r + (pivot - pad_r) / np.linalg.norm(pivot - pad_r) * 6.0
    c_s = P3.surface_point(TF, c0, n_rest, lo=-12, hi=12)
    t_ax = (pad_r - pivot) / np.linalg.norm(pad_r - pivot)
    nn = -n_rest; uu_ = t_ax - nn * (t_ax @ nn); uu_ /= np.linalg.norm(uu_); vv_ = np.cross(nn, uu_)
    Q = T - c_s; a1 = Q @ uu_; b1 = Q @ vv_; w1 = Q @ nn
    eb = (np.sqrt((a1 / 5.4) ** 2 + (b1 / 4.0) ** 2) - 1) * 4.0
    rem = np.maximum(eb, -(TFv + 1.0))                      # 1.0 mm recess, pad glued in
    ft = smax(ft, -np.maximum(rem, np.abs(w1) - 6.0), 0.4)
    del Q, a1, b1, w1, eb, rem
    gc.collect()
    # fingernail: a shallow nail bed (0.45 mm) on the back of the thumb tip, for looks or to paint
    cn0 = pad_r + (pivot - pad_r) / np.linalg.norm(pad_r - pivot) * 5.5
    cn = P3.surface_point(TF, cn0, -n_rest, lo=-12, hi=12)
    Qn = T - cn; an = Qn @ uu_; bn = Qn @ vv_; wn = Qn @ nn
    nail = (np.sqrt((an / 4.2) ** 2 + (bn / 3.3) ** 2) - 1.0) * 3.3
    ft = smax(ft, -np.maximum(np.maximum(nail, -(TFv + 0.45)), np.abs(wn) - 4.0), 0.5)
    del Qn, an, bn, wn, nail
    ft = opening(ft.reshape(tshape), tgf, 0.6).ravel()      # final rounding, as the other parts
    Mth = max(to_manifold(ft.reshape(tshape), tgf, 0.0, simplify=0.01).decompose(), key=lambda p: p.volume())
    Mr = frame_matrix(pivot, xr, yr, zr)
    Mth = Mth - cyl_x(1.7).transform(Mr)
    # optional private finishing step
    if finish_thumb is not None:
        Mth = finish_thumb(Mth, xr)

    for name, m in (('palm_back', Mback), ('palm_flap', Mflap), ('thumb', Mth)):
        parts = m.decompose(); mp = max(parts, key=lambda p: p.volume())
        if m.volume() < mp.volume() - 0.1 and len([q_ for q_ in parts if q_.volume() > 1.0]) == 1: mp = m   # keep sealed internal voids
        to_tm(mp).export(f'{OUT}/{name}.stl'); print(name, 'vol', round(mp.volume()), 'genus', mp.genus(), flush=True)
    json.dump({'wrist': WRIST.tolist(), 'ears_x': ears, 'thumb_frame': {'pivot': pivot.tolist(), 'x': xj.tolist(), 'y': yj.tolist(), 'z': zj.tolist()},
               'thumb_head': headside, 'line_exits_x': exits.tolist(), 'flap_screws': flap_screws}, open(f'{OUT}/palm.json', 'w'), indent=1)
    json.dump(P3.CHANNELS, open(f'{OUT}/palm_channels.json', 'w'))


if __name__ == '__main__':
    main()
