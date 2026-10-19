"""Stage 3: thumb + palm shell.
PETG back of the hand (knuckle block, thumb mount, wrist ears, hidden line tunnels, logo, knobs)
+ TPU palm flap (crease vents, rubber-pad pockets, tabs, distal tuck tongue) + thumb with friction hinge.
Writes build/palm_back.stl, build/palm_flap.stl, build/thumb.stl (rest frame), build/palm.json"""
import json, numpy as np, trimesh, manifold3d as mf
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.transform import Rotation as Rot
from rlib import to_mf, to_tm, frame_matrix, box
from sdf import to_manifold, smin
from lib_grid import load_skin
from cavity import cavity_field
from joints import Joint, GAP, cyl_x, cyl_x_span, bx, BIG
from fingers import spline, frame as finger_frame
from skin import knuckle_y
import fingers as FG
from thumb_solve import thumb_rest_field

ORDER = ['index', 'middle', 'ring', 'little']
J = json.load(open('build/joints.json')); TS = json.load(open('build/thumb_solution.json'))
OUT = 'build'
Z_SEAM = 3.0                     # PETG back above, TPU flap below (side walls)
RAY_X = -21.0                    # flap stays medial of the thumb mount zone
WRIST = np.array([4.75, 0.0, 7.6])
EAR_R = 9.0
TUNNEL_DEPTH = 2.2
LOGO_C, LOGO_SCALE, LOGO_DEPTH = (-2.0, 26.0), 1.0, 0.8
CHANNELS = []


def chan(pts, r, fields, need=(0.9, 0.8)):
    """Channel along pts kept >= need[0] mm under the skin and >= need[1] mm off the cavity."""
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
        gc = np.stack([(FC(P[1:-1] + h * e) - FC(P[1:-1] - h * e)) / (2 * h) for e in np.eye(3)], 1)
        go /= np.linalg.norm(go, axis=1, keepdims=True) + 1e-9; gc /= np.linalg.norm(gc, axis=1, keepdims=True) + 1e-9
        P[1:-1] += -go * no[:, None] + gc * nc[:, None]
        P[2:-2] = (P[1:-3] + 2 * P[2:-2] + P[3:-1]) / 4
    CHANNELS.append({'r': r, 'pts': P.tolist()})
    return FG.capsule_chain(list(P), r, fit=False)


def dorsal_point(FO, x, y, depth):
    zs = np.arange(36, -10, -0.1)
    v = FO(np.stack([np.full_like(zs, x), np.full_like(zs, y), zs], 1))
    i = np.argmax(v < -depth)
    return np.array([x, y, zs[i]])


def surface_point(FO, p, n, lo=-15, hi=15):
    """First point along p + t*n (t from hi down to lo) where the outer skin is crossed."""
    ts = np.arange(hi, lo, -0.05)
    v = FO(np.asarray(p) + ts[:, None] * np.asarray(n))
    return np.asarray(p) + ts[np.argmax(v < 0)] * np.asarray(n)


def ellipse_prism(c, ax_u, ax_v, a, b, z0=-40, z1=40, nrm=(0, 0, 1)):
    nrm = np.asarray(nrm, float); u = np.asarray(ax_u, float); u -= nrm * (u @ nrm); u /= np.linalg.norm(u)
    v = np.cross(nrm, u)
    m = mf.Manifold.cylinder(z1 - z0, 1, 1, 72).scale([a, b, 1]).translate([0, 0, z0])
    return m.transform(frame_matrix(np.asarray(c, float), u, v, nrm))


def main():
    d, g = load_skin()
    FO = RegularGridInterpolator(g.axes(), d['outer'], bounds_error=False, fill_value=20)
    cav = cavity_field(d, g)
    FC = RegularGridInterpolator(g.axes(), cav, bounds_error=False, fill_value=20)
    X, Y, Z = g.points()
    pivot = np.array(TS['pivot'])
    # ---- outer skin with the thenar mount boss and the wrist-ear pads
    sph = np.sqrt((X - pivot[0]) ** 2 + (Y - pivot[1]) ** 2 + (Z - pivot[2]) ** 2) - 10.0
    outer2 = smin(d['outer'], sph, 5.0)
    ears = []
    for sx in (-1, 1):
        # find the side wall at the wrist axis height, then a 2 mm pad there for the hinge screw
        xs = np.arange(-40, 45, 0.1)
        v = FO(np.stack([xs, np.full_like(xs, WRIST[1]), np.full_like(xs, WRIST[2])], 1))
        inside = xs[v < 0]; xw = inside.min() if sx < 0 else inside.max()
        ears.append(xw)
        pad = np.sqrt((Y - WRIST[1]) ** 2 + (Z - WRIST[2]) ** 2) - EAR_R
        pad = np.maximum(pad, np.abs(X - xw) - 2.0)
        outer2 = smin(outer2, np.maximum(pad, sx * (xw - X) - 0.0) , 2.0) if False else smin(outer2, pad, 2.0)
    # line guide hump at the wrist end of the back (raises the line exits for a stronger tenodesis pull)
    hx = WRIST[0] - 3.9            # over the middle-finger line: index and middle exits ride highest
    ztop = dorsal_point(FO, hx, 1.0, 0.0)[2]
    hump = (np.sqrt(((X - hx) / 18.0) ** 2 + ((Y - 1.0) / 9.0) ** 2 + ((Z - (ztop - 1.0)) / 5.5) ** 2) - 1.0) * 5.5
    outer2 = smin(outer2, hump, 4.0)
    FO = RegularGridInterpolator(g.axes(), outer2, bounds_error=False, fill_value=20)
    Mo = to_manifold(d['outer'], g)
    Mo2 = to_manifold(outer2, g)
    ins = {k: to_manifold(outer2 + k, g) for k in (0.5, 0.6, 0.8, 1.0, 1.9, 2.1)}
    Cav = to_manifold(cav, g)
    palm_raw = to_mf(trimesh.load(f'{OUT}/palm_raw.stl'))
    zone = mf.Manifold.sphere(17, 48).translate(list(pivot)) + bx(hx - 24, hx + 24, -2, 14, ztop - 8, ztop + 10)
    for xw in ears:
        zone = zone + bx(xw - 6, xw + 6, WRIST[1] - 12, WRIST[1] + 12, WRIST[2] - 12, WRIST[2] + 12)
    shell = (palm_raw + ((Mo2 - Mo) ^ zone)) - Cav
    # wrist: keep the hand side of y = -1 plus the two hinge ears (inside a 9 mm disc round the axis)
    Wm = frame_matrix(WRIST, np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.]))
    keep = bx(-BIG, BIG, -1.0, BIG, -BIG, BIG) + (cyl_x(EAR_R).transform(Wm) ^ bx(-BIG, BIG, -14, 0, -BIG, BIG))
    shell = shell ^ keep
    # ---- thumb with friction hinge (palm owns the slotted barrel, thumb the tongue; inner-tube washers each side)
    ax_w = np.array(TS['hinge_axis']); R_open = Rot.from_quat(TS['open_quat'])
    xj = -ax_w / np.linalg.norm(ax_w)
    tf, tg, t_scaled = thumb_rest_field(pivot)
    thumb_rest = to_manifold(tf, tg)
    pad_r = t_scaled.vertices[np.argmax(np.linalg.norm(t_scaled.vertices - pivot, axis=1))]
    mid = Rot.from_rotvec(ax_w * np.radians(TS['swing_deg'] / 2)) * R_open
    yj = mid.apply(pad_r - pivot); yj -= xj * (yj @ xj); yj /= np.linalg.norm(yj); zj = np.cross(xj, yj)
    Mw = frame_matrix(pivot, xj, yj, zj)
    Rinv = R_open.inv()
    Mr = frame_matrix(pivot, Rinv.apply(xj), Rinv.apply(yj), Rinv.apply(zj))   # same frame, in the thumb's rest pose
    TJ = Joint(6.5, Rt=4.5, wt=6.0, ws=7.5, hn=3.4, barrel='P', flex=(-6, TS['swing_deg'] + 6))
    LB = 15.0
    barrel = cyl_x(TJ.R) ^ bx(-LB / 2, LB / 2, -BIG, BIG, -BIG, BIG)
    thumb = thumb_rest - cyl_x(TJ.R + GAP).transform(Mr)
    thumb = thumb + TJ.tongue().transform(Mr)
    # rubber pad pocket on the thumb tip, facing the fingertips at the pinch setting
    from thumb_solve import pad_target
    Rp = Rot.from_rotvec(TS['pinch_rotvec'])
    tip_w = Rp.apply(pad_r - pivot) + pivot
    n_rest = Rp.inv().apply((pad_target(TS['pinch_curl_deg']) - tip_w) / np.linalg.norm(pad_target(TS['pinch_curl_deg']) - tip_w))
    FT = RegularGridInterpolator(tg.axes(), tf, bounds_error=False, fill_value=20)
    c0 = pad_r + (pivot - pad_r) / np.linalg.norm(pivot - pad_r) * 6.0
    c_s = surface_point(FT, c0, n_rest, lo=-12, hi=12)
    t_ax = (pad_r - pivot) / np.linalg.norm(pad_r - pivot)
    ti5, ti10 = to_manifold(tf + 0.5, tg), to_manifold(tf + 1.0, tg)
    tb = ellipse_prism(c_s, t_ax, None, 5.4, 4.0, -6, 6, -n_rest); ts_ = ellipse_prism(c_s, t_ax, None, 4.9, 3.5, -6, 6, -n_rest)
    thumb = thumb - ((ts_ - ti5) + ((tb ^ ti5) - ti10))
    # the thumb never hits the palm anywhere in its swing: carve the swept (0.5 mm grown) thumb out of the palm
    big_thumb = (to_manifold(tf - 0.5, tg) + TJ._neck(extra=0.35, reach=TJ.R + GAP + 2.0).transform(Mr)) - cyl_x(TJ.R - 0.03).transform(Mr)
    sweep = []
    for f in np.linspace(-0.05, 1.05, 24):
        R = Rot.from_rotvec(ax_w * np.radians(TS['swing_deg'] * f)) * R_open
        M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = pivot - R.as_matrix() @ pivot
        sweep.append(big_thumb.transform(M[:3, :]))
    shell = shell - mf.Manifold.batch_boolean(sweep, mf.OpType.Add)
    shell = shell + barrel.transform(Mw)
    shell = shell - TJ.slot().transform(Mw)
    # screw: head on the end of the axis farther from the cavity, blind pilot in the other arm
    ends = [pivot + xj * LB / 2, pivot - xj * LB / 2]
    head = 1 if FC([ends[0]])[0] > FC([ends[1]])[0] else -1
    w = TJ.ws / 2
    if head > 0:
        sc = cyl_x_span(3.1, LB / 2 - 1.5, BIG) + cyl_x_span(1.7, -w, BIG) + cyl_x_span(1.3, -LB / 2 + 0.8, -w + 0.01)
    else:
        sc = cyl_x_span(3.1, -BIG, -LB / 2 + 1.5) + cyl_x_span(1.7, -BIG, w) + cyl_x_span(1.3, w - 0.01, LB / 2 - 0.8)
    shell = shell - sc.transform(Mw)
    # ---- wrist ear screw holes (pilot 2.6, 4.0 deep from the outside, blind)
    for sx, xw in zip((-1, 1), ears):
        x_out = xw + sx * 2.0
        if sx < 0:
            hole = cyl_x_span(1.3, x_out - 1, x_out + 4.0)
        else:
            hole = cyl_x_span(1.3, x_out - 4.0, x_out + 1)
        shell = shell - hole.transform(Wm)
    # ---- line tunnels: knuckle climb, then hidden in the back wall to the wrist edge
    exits = np.linspace(WRIST[0] - 9.1, WRIST[0] + 9.1, 8)
    k = 0
    fields = (FO, FC)
    for n in ORDER:
        info = J[n]['joints'][0]; O0 = np.array(info['O']); xf, df, zf = (np.array(info[a]) for a in 'xdz')
        R0 = info['R']; F0 = np.array(J[n]['flexor'][0]); Rr0 = np.array(J[n]['return'][0])
        for kind, start, lat in (('flex', F0, -1.3), ('ret', Rr0, 1.3)):
            q = O0 - df * 16 + xf * lat
            D = dorsal_point(FO, q[0], q[1], TUNNEL_DEPTH)
            if kind == 'flex':
                A = start - df * (R0 + 1.0); B = A - df * 3.5
                climb = spline([start, A, B, D + df * 3.0, D], 16)
            else:
                climb = spline([start, start - df * 4.0, D + df * 3.0, D], 12)
            run = []
            ex = exits[k]
            for t in np.linspace(0, 1, 26)[1:]:
                yy = D[1] + (-2.0 - D[1]) * t; xx = D[0] + (ex - D[0]) * t
                run.append(dorsal_point(FO, xx, yy, TUNNEL_DEPTH))
            path = climb + run[:-1] + [run[-1] - np.array([0, 3.0, 0])]
            shell = shell - chan(path, 0.65 if kind == 'flex' else 0.6, fields)
            if kind == 'ret':   # knot counterbore in the wrist end face
                e = run[-1]
                shell = shell - mf.Manifold.cylinder(2.2, 1.4, 1.4, 32).rotate([90, 0, 0]).translate([e[0], -1.0 + 1.6, e[2]])
            k += 1
    # ---- drain at the front of the cavity (hand hanging down), between middle and ring
    xd = (np.array(J['middle']['joints'][0]['O'])[0] + np.array(J['ring']['joints'][0]['O'])[0]) / 2
    yk = knuckle_y(xd)
    shell = shell - FG.capsule_chain([np.array([xd, yk - 17, 2.0]), np.array([xd, yk - 9, -8]), np.array([xd, yk - 6, -22])], 1.3, fit=False)
    # ---- logo pressed 0.8 mm into the back of the hand
    rects = json.load(open('../logo/logo_rects.json'))
    # union the pixel cells in 2D and grow them 0.06 mm so diagonal pixels overlap instead of
    # touching at a corner (corner contacts leave non-manifold edges in the STL)
    polys = [[(LOGO_C[0] + x * LOGO_SCALE, LOGO_C[1] + y * LOGO_SCALE) for x, y in
              ((x0, y0), (x1, y0), (x1, y1), (x0, y1))] for x0, x1, y0, y1 in rects]
    cs = mf.CrossSection.batch_boolean([mf.CrossSection([p]) for p in polys], mf.OpType.Add)
    logo = cs.offset(0.06, mf.JoinType.Miter).extrude(40).translate([0, 0, 5])
    ins08 = ins[0.8]
    shell = shell - (logo - ins08)
    # ---- split: TPU flap (palm side) / PETG back
    xs = np.linspace(-60, 60, 241)
    yk_x = knuckle_y(xs)
    def flap_poly(grow):
        top = []
        for x, yt in zip(xs, yk_x - 15.0):
            if x < RAY_X: yt = min(yt, 22.0)
            top.append((x, yt))
        poly = ([(-60, -1.0)] + top + [(60, -1.0)])[::-1]        # counter-clockwise
        cs = mf.CrossSection([poly]).offset(grow, mf.JoinType.Round)
        return cs.extrude(80).translate([0, 0, -80 + Z_SEAM + grow])
    reg_flap = flap_poly(-0.15); reg_cut = flap_poly(0.15)
    # radial side above the mount: the flap edge runs along x = RAY_X on the palm face
    ray_block = bx(-BIG, RAY_X - 0.15, 22.0, BIG, -BIG, BIG)
    reg_flap = reg_flap - bx(-BIG, RAY_X + 0.15, 22.0, BIG, -BIG, BIG)
    ear_zone = cyl_x(EAR_R + 2.0).transform(Wm)
    reg_flap = reg_flap - ear_zone
    reg_cut = reg_cut - cyl_x(EAR_R + 1.7).transform(Wm)
    flap = shell ^ reg_flap
    back = shell - (reg_cut - ray_block)
    # distal tuck tongue on the flap, matching slot in the knuckle block
    band = lambda a, b: ins[a] - ins[b]
    def ystrip(y0, y1, grow=0.0):
        poly = [(x, yt + y0) for x, yt in zip(xs, yk_x)] + [(x, yt + y1) for x, yt in zip(xs[::-1], yk_x[::-1])]
        cs = mf.CrossSection([poly])
        return cs.extrude(80).translate([0, 0, -80 + Z_SEAM - 1.5])
    tongue_r = (band(0.8, 1.9) ^ ystrip(-15.4, -11.0)) - bx(-BIG, RAY_X + 0.6, -BIG, BIG, -BIG, BIG)
    slot_r = (band(0.6, 2.1) ^ ystrip(-15.4, -10.7)) - bx(-BIG, RAY_X + 0.3, -BIG, BIG, -BIG, BIG)
    flap = flap + tongue_r
    back = back - slot_r
    # ---- knobs on the PETG and tabs on the flap (watch-band closure; nothing can come loose)
    L16 = to_manifold(outer2 - 1.6, g) - Mo2
    knobs = []
    for side, yy in ((1, 15.5), (1, 38.0), (-1, 14.5)):
        xs_ = np.arange(-45, 45, 0.1)
        v = FO(np.stack([xs_, np.full_like(xs_, yy), np.full_like(xs_, Z_SEAM + 4.5)], 1))
        xin = xs_[v < 0]; xk = xin.max() if side > 0 else xin.min()
        p = np.array([xk, yy, Z_SEAM + 4.5]); nrm = np.array([side, 0, 0.25]); nrm /= np.linalg.norm(nrm)
        seamp = np.array([xk, yy, Z_SEAM - 3.0])
        knobs.append((p, nrm, seamp))
    # radial knob on the palm face of the thumb-mount zone (flap edge runs along x = RAY_X there):
    # first spot where the PETG under it survived the thumb's swing carve
    for yy in (28.0, 25.0, 31.0, 34.0):
        p = surface_point(FO, np.array([RAY_X - 3.6, yy, -40.0]), np.array([0, 0, -1.0]), lo=-45, hi=0)
        probe = mf.Manifold.cube([1.6, 1.6, 1.6]).translate(list(p + np.array([-0.8, -0.8, 0.6])))
        if (back ^ probe).volume() > 3.5:
            knobs.append((p, np.array([0, 0, -1.0]), np.array([RAY_X + 4.0, yy, p[2] - 0.5]))); break
    else:
        print('no room for the radial knob')
    for p, nrm, seamp in knobs:
        u = np.cross(nrm, [0, 1, 0]); u = u if np.linalg.norm(u) > 0.1 else np.cross(nrm, [1, 0, 0]); u /= np.linalg.norm(u)
        Mk = frame_matrix(p, u, np.cross(nrm, u), nrm)
        stem = mf.Manifold.cylinder(1.6 + 1.0, 1.5, 1.5, 32).translate([0, 0, -1.0])
        headm = mf.Manifold.sphere(1, 32).scale([2.4, 2.4, 1.2]).translate([0, 0, 1.6])
        back = back + (stem + (headm ^ bx(-5, 5, -5, 5, 1.6, 5))).transform(Mk)
        sph_a = mf.Manifold.sphere(4.6, 32).translate(list(p)); sph_b = mf.Manifold.sphere(4.6, 32).translate(list(seamp))
        tab = (mf.Manifold.batch_hull([sph_a, sph_b]) ^ L16) - mf.Manifold.cylinder(10, 1.4, 1.4, 32).translate([0, 0, -5]).transform(Mk)
        flap = flap + tab
    # ---- flap: crease vents (dashed slots along the palm creases) and rubber-pad pockets
    creases = [[(-26, 41), (-10, 38), (6, 35), (19, 33)],                          # head line
               [(-15, 40), (-11, 30), (-9, 20), (-8, 10), (-6, 3)]]                # life line (round the thenar)
    vents = []
    for cr in creases:
        pts = np.array(spline([np.array([x, y, 0.0]) for x, y in cr], 60))
        sl = np.cumsum(np.r_[0, np.linalg.norm(np.diff(pts, axis=0), axis=1)])
        for s0 in np.arange(2.0, sl[-1] - 6, 10.0):
            a = pts[np.searchsorted(sl, s0)]; b = pts[np.searchsorted(sl, s0 + 6)]
            ca = mf.Manifold.cylinder(60, 0.9, 0.9, 24).translate([a[0], a[1], -50])
            cb = mf.Manifold.cylinder(60, 0.9, 0.9, 24).translate([b[0], b[1], -50])
            vents.append(mf.Manifold.batch_hull([ca, cb]))
    vent = mf.Manifold.batch_boolean(vents, mf.OpType.Add) ^ bx(-BIG, BIG, -BIG, BIG, -BIG, Z_SEAM - 2)
    flap = flap - vent
    def pocket(part, c, u, a, b, nrm=(0, 0, -1)):
        big = ellipse_prism(c, u, None or np.cross(nrm, u), a, b, -15, 15, nrm)
        sml = ellipse_prism(c, u, None, a - 0.5, b - 0.5, -15, 15, nrm)
        return part - ((sml - ins[0.5]) + ((big ^ ins[0.5]) - ins[1.0]))
    flap = pocket(flap, (17, 20, -5), (0, 1, 0), 10.0, 6.0)        # hypothenar pad
    flap = pocket(flap, (-14, 22, -5), (0, 1, 0), 8.0, 5.0)        # thenar side pad
    yk0 = knuckle_y(-1.0)
    back = pocket(back, (-1, yk0 - 10.5, -5), (1, 0, 0), 19.0, 3.4)   # distal palm pad under the knuckles
    # ---- export
    for name, m in (('palm_back', back), ('palm_flap', flap), ('thumb', thumb)):
        parts = m.decompose(); main_p = max(parts, key=lambda p: p.volume())
        if len(parts) > 1:
            print(f'{name}: {len(parts)-1} loose bits dropped ({sum(p.volume() for p in parts) - main_p.volume():.1f} mm3)')
        to_tm(main_p).export(f'{OUT}/{name}.stl'); print(name, 'vol', round(main_p.volume()), 'genus', main_p.genus())
    json.dump({'wrist': WRIST.tolist(), 'ears_x': ears, 'thumb_frame': {'pivot': pivot.tolist(), 'x': xj.tolist(), 'y': yj.tolist(), 'z': zj.tolist()},
               'thumb_head': head, 'line_exits_x': exits.tolist()}, open(f'{OUT}/palm.json', 'w'), indent=1)
    json.dump(CHANNELS, open(f'{OUT}/palm_channels.json', 'w'))


if __name__ == '__main__':
    main()
