"""Stage 2 (v3.1): finger segments built as smooth distance fields.
Joint seams, cups, tongues, slots and the palm-side creases are all smooth booleans (rounded edges,
filleted roots); thin rims are removed with an opening; then screw holes, line channels and the knot
pocket are cut exactly. Joint layout (axes, radii, screws) is the v3 layout in build_v3/joints.json.
Writes build/fingers/*.stl, build/joints.json, build/finger_channels.json."""
import json, os, sys, numpy as np, manifold3d as mf
from rlib import to_tm, frame_matrix
from sdf import Grid, to_manifold, smin, smax, seg_dist
from sdfparts import Skin, JointSDF, local, opening, sweep_carve, GAP, chain_field
from fingerskin import FingerSkin
from joints import Joint, cyl_x, cyl_x_span, BIG
import fingers as FG
from lib_grid import load_skin
from scipy.interpolate import RegularGridInterpolator

ORDER = ['index', 'middle', 'ring', 'little']
FLEX = [80, 85, 65]
HEAD = FG.HEAD
J3 = json.load(open('build_v3/joints.json'))
PITCH = 0.15
ARM_MIN = 2.6        # PETG left under a screw head or around a pilot (mm)
HEAD_H = 1.65        # M3 button head (ISO 7380) height
FG.MIN_SKIN = 1.1
R_FLEX, R_RET = 1.0, 1.0    # v3.2c line channels: 2.0 mm where they cross a joint (slim there) ...
R_MID = 1.25                 # ... 2.5 mm along the rest of each segment
R_MOUTH = 1.5                # 3 mm funnel at every mouth
HOOD_MIN = 0.9       # cup hood thinner than 2 x this is trimmed away (local opening radius)
OUT = 'build'; os.makedirs(f'{OUT}/fingers', exist_ok=True)

# v3.2: the index, middle and ring knuckles share ONE straight axle (a long M3 screw put in from the index
# side), because a separate screw can't be put in between two knuckles. Their MCP axes were already within
# 0.35 mm / 3 deg of a common line: they are moved onto it. The little finger keeps its own screw (outside).
AXLE = ('index', 'middle', 'ring')
INS_R, INS_D = 2.0, 5.5          # heat-set insert pocket (M3 x 4-5 mm long, 4.2 mm OD): 4.0 mm hole, 5.5 deep
INS_MIN = 4.3                    # arm needed for an insert (else a plain 2.6 mm pilot)
AXLE_LENGTHS = (30, 35, 40, 45, 50)
TIP_KEEP = 3.0                   # v3.2: full rounded fingertip kept beyond the grip pad
NAIL_FREE, NAIL_LEN = 2.4, 7.0   # nail ends 2.4 mm short of the tip, 7 mm long


def _axle_line():
    O = np.array([J3[n]['joints'][0]['O'] for n in AXLE]); X = np.array([J3[n]['joints'][0]['x'] for n in AXLE])
    c = O.mean(0); a = np.linalg.svd(O - c)[2][0]
    a = a if a @ X.mean(0) > 0 else -a
    return c, a / np.linalg.norm(a)


AX_C, AX_A = _axle_line()
for _n in AXLE:
    _inf = J3[_n]['joints'][0]; _O = np.array(_inf['O'])
    _Op = AX_C + AX_A * ((_O - AX_C) @ AX_A)
    _d = np.array(_inf['d']); _d = _d - AX_A * (_d @ AX_A); _d /= np.linalg.norm(_d)
    _z = np.cross(AX_A, _d); _z = _z if _z @ np.array(_inf['z']) > 0 else -_z
    print(f'axle: {_n} MCP moved {np.linalg.norm(_Op - _O):.2f} mm, axis turned '
          f'{np.degrees(np.arccos(np.clip(AX_A @ np.array(_inf["x"]), -1, 1))):.1f} deg', flush=True)
    _inf.update(O=_Op.tolist(), x=AX_A.tolist(), d=_d.tolist(), z=_z.tolist())
AXLE_RECESS = float(os.environ.get('AXLE_RECESS', '2.25'))   # head recess on the index side (default: full)
LITTLE_HEAD_EXTRA = {0: 2.4, 1: 1.2}   # v3.3: little finger joints thicker on the outside (nearly all of it stays after smoothing) so both take M3 x 12, like the other fingers
AXLE_HEAD_EXTRA = 2.4            # index knuckle thicker on the outside (about 1.2 mm after smoothing) so a stock M3 x 45 ends inside the ring


def joint_params(n, j):
    small = n == 'little'
    return dict(barrel='D' if j == 0 else 'P', wt=4.8 if small else 5.6, ws=5.4 if small else 6.2,
                hn=2.6 if (j == 2 or small) else 3.0, flex=(-6, FLEX[j] + 4))


def planes():
    O_ = {n: FG.frame(n) for n in ORDER}; out = []
    for a, b in zip(ORDER[:-1], ORDER[1:]):
        Oa, xa, da, _ = O_[a]; Ob, xb, db, _ = O_[b]
        nrm = xa + xb; out.append(((Oa + da * 25 + Ob + db * 25) / 2, nrm / np.linalg.norm(nrm)))
    return out


PL = planes()


def column(P, i, shrink=0.3):
    f = np.full(len(P), -1e3, np.float32)
    if i < 3:
        p0, nr = PL[i]; f = np.maximum(f, (P - p0) @ nr + shrink)
    if i > 0:
        p0, nr = PL[i - 1]; f = np.maximum(f, -((P - p0) @ nr) + shrink)
    return f


def surface_extent(S, c, dirv, lo=-15, hi=15):
    t = np.arange(lo, hi, 0.05); v = S(c[None] + t[:, None] * dirv[None]); ins = t[v < 0]
    return ins.min(), ins.max()


def main(only=None):
    d_, g0 = load_skin()
    FG.FIELD = RegularGridInterpolator(g0.axes(), d_['outer'], bounds_error=False, fill_value=10)
    joints_out = {}
    for i, n in enumerate(ORDER):
        if only and n != only:
            joints_out[n] = json.load(open(f'{OUT}/joints.json'))[n] if os.path.exists(f'{OUT}/joints.json') else J3[n]; continue
        info = J3[n]['joints']; nj = len(info)
        for inf_ in info:          # thicker tongue ring round its bore (wall = Rt - 1.7)
            inf_['Rt'] = float(max(inf_['Rt'], min(inf_['R'] - 1.1, 4.0)))
        JS = [JointSDF(info[j], **joint_params(n, j)) for j in range(nj)]
        O, x, d, z = FG.frame(n); L = J3[n]['L']
        import trimesh
        bb = np.array([trimesh.load(f'build_v3/fingers/{n}-{k+1}.stl').bounds for k in range(nj)])
        S = FingerSkin(n, bb[:, 0].min(0) - 4, bb[:, 1].max(0) + 4)          # this finger's own skin
        FG.FIELD = RegularGridInterpolator(S.g.axes(), S.f, bounds_error=False, fill_value=10)   # channels follow this finger's skin
        F = [np.array(p) for p in J3[n]['flexor']]; Rr = [np.array(p) for p in J3[n]['return']]

        def basic(P, k):
            """Segment k without slots or carves: skin ∩ column ∩ joint sides (+ its tongue)."""
            sk = S(P)
            # barrel ends grown sideways (rounded) so each arm can keep ARM_MIN under a flush screw head
            for jj in ([0] if k == 0 else []) + ([k + 1] if k < nj - 1 else []):
                Jt = JS[jj]; u, v, w = Jt.loc(P)
                hw_ = Jt.ws / 2 + ARM_MIN + HEAD_H
                if jj == 0 and n == AXLE[0]:       # axle head side (outside of the hand) grown a little
                    side_ = np.maximum(u - hw_, -u - (hw_ + AXLE_HEAD_EXTRA))
                elif n == 'little' and jj in LITTLE_HEAD_EXTRA:   # screw-head side (outside of the hand, +u) grown
                    side_ = np.maximum(u - (hw_ + LITTLE_HEAD_EXTRA[jj]), -u - hw_)
                else:
                    side_ = np.abs(u) - hw_
                boss = smax(np.sqrt(v * v + w * w) - (Jt.R - 0.2), side_, 1.2)
                sk = smin(sk, boss, 1.5)
            f = smax(sk, column(P, i), 2.0)
            f = smax(f, JS[k].side(P, 'D'), 0.8)
            if k < nj - 1:
                f = smax(f, JS[k + 1].side(P, 'P'), 0.8)
            if JS[k].barrel == 'P':
                f = smin(f, JS[k].tongue(P), 1.0)
            return f

        # fingertip: knot pocket and grip pocket position (pad on the palm side, 7 mm back from the tip)
        # grip pocket must stay clear of the last joint's cup: fit it between the cup rim and the tip
        last = info[-1]; s_rim = last['s'] + last['R'] + GAP + 1.8
        PB = float(np.clip(((L - TIP_KEEP) - s_rim) / 2, 3.2, 4.6))     # pocket half length (outer, lip edge)
        s_pad = (L - TIP_KEEP) - PB
        ctip = O + d * s_pad
        zmin_t, zmax_t = surface_extent(S, ctip, z)
        tip_pad = ctip + z * zmin_t
        segs = []
        for k in range(nj):
            src = f'build_v3/fingers/{n}-{k+1}.stl'
            import trimesh
            b = trimesh.load(src).bounds
            g = Grid(b[0] - 2.5, b[1] + 2.5, PITCH)
            X, Y, Z = g.points(); P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1); shape = X.shape; del X, Y, Z
            f = basic(P, k)
            # slots through the barrels this segment owns (MCP for k = 0, and the joint at its far end)
            for jj in ([0] if k == 0 else []) + ([k + 1] if k < nj - 1 else []):
                Jt = JS[jj]
                m = Jt.cyl(P, Jt.R + 0.6) < 0
                tongue = lambda Q, Jt=Jt: Jt.tongue(Q) - 0.15        # allow for the tongue's root fillet
                slot = Jt.slot_from(P[m], tongue)
                f[m] = smax(f[m], -slot, 0.4)
            # palm-side crease: carve what the next segment sweeps through as the joint flexes
            if k < nj - 1:
                Jn = JS[k + 1]
                u, v, w = Jn.loc(P)
                m = (np.sqrt(v * v + w * w) < Jn.R + 13) & (f < 1.0)
                zone = lambda Q, Jn=Jn: smax(smax(GAP / 2 - 0.35 - Jn.loc(Q)[1], Jn.loc(Q)[1] - (Jn.R + 10), 0.0),
                                             -Jn.cyl(Q, Jn.R + 0.05), 0.0)
                nxt = lambda Q, k=k, zone=zone: smax(basic(Q, k + 1), zone(Q), 0.0)
                sw = sweep_carve(P[m], Jn.O, Jn.x, nxt, np.arange(0, FLEX[k + 1] + 0.1, 2.5), grow=0.35)
                f[m] = smax(f[m], -sw, 0.6)
            # line channels, cut in the field: every exit gets a rounded mouth (smooth subtraction) instead
            # of a hard cut edge; the paths are relaxed to keep >= 0.9 mm of skin over them
            if k < nj - 1:
                paths = [(FG.relax([F[k], F[k + 1]], R_MID), R_FLEX), (FG.relax([Rr[k], Rr[k + 1]], R_MID), R_RET)]
            else:
                zmid = (zmin_t + zmax_t) / 2
                paths = [(FG.relax(FG.spline([F[-1], O + d * (L - 11) + z * (zmin_t + 2.6), tip_pad + z * 1.2, tip_pad - z * 2], 14), R_MID), R_FLEX),
                         (FG.relax(FG.spline([Rr[-1], O + d * (L - 7) + z * (zmax_t - 2.4), O + d * (L - 2.5) + z * zmid,
                                              O + d * (L - 5.5) + z * (zmin_t + 1.6), tip_pad - z * 2], 18), R_MID), R_RET)]
            ch = np.full(len(P), 1e3, np.float32)
            for pts, r in paths:
                FG.CHANNELS.append({'r': r, 'pts': [list(map(float, p)) for p in pts]})
                ch = np.minimum(ch, chain_field(P, pts, r))
                # wider (2.5 mm) along the middle of the segment, 3 mm or more from either end
                A_ = np.asarray(pts, float); sl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(A_, axis=0), axis=1))]
                if sl[-1] > 7.0:
                    mid_ = A_[(sl >= 3.0) & (sl <= sl[-1] - 3.0)]
                    if len(mid_) >= 2:
                        # biggest that fits: up to 2.5 mm, keeping >= 0.9 mm of skin over the channel
                        rr_ = np.clip(-S(mid_) - 0.9, R_FLEX, R_MID)
                        for a_, b_, ra_, rb_ in zip(mid_[:-1], mid_[1:], rr_[:-1], rr_[1:]):
                            ch = np.minimum(ch, seg_dist(P, a_, b_) - min(ra_, rb_))
                        FG.CHANNELS[-1]['r_mid'] = [float(v_) for v_ in rr_]
                for e0, e1 in ((pts[0], pts[1]), (pts[-1], pts[-2])):      # 3 mm funnel at each end
                    e0 = np.asarray(e0, float); dv = np.asarray(e1, float) - e0; dv /= np.linalg.norm(dv) + 1e-9
                    ch = np.minimum(ch, seg_dist(P, e0 - dv * 0.6, e0 + dv * 0.6) - R_MOUTH)
                    ch = np.minimum(ch, seg_dist(P, e0, e0 + dv * 1.6) - (r + 0.25))
            if k == nj - 1:
                # knot pocket under the pad, and the grip recess: 1.0 mm deep, following the skin, rounded rim;
                # the inner-tube pad is glued in with contact cement
                ch = np.minimum(ch, seg_dist(P, tip_pad - z * 4.0, tip_pad + z * 1.5) - 1.5)
                u, v, w = local(P, tip_pad, x, d, z)
                sk = S(P)
                ell_b = (np.sqrt((u / 3.6) ** 2 + (v / PB) ** 2) - 1.0) * 3.6
                rec = np.maximum(np.maximum(ell_b, -(sk + 1.0)), np.abs(w) - 6.0)   # smooth limit (a hard cut-off left a jagged rim)
                ch = np.minimum(ch, rec); del rec, ell_b
                # fingernail (v3.2): a rounded-square nail plate set back from the tip (a full fingertip stays
                # in front of it), sunk 0.55 mm at the cuticle and fading to 0.15 mm at the free edge
                s_n = L - NAIL_FREE - NAIL_LEN / 2; hl_n = NAIL_LEN / 2
                zt_n = surface_extent(S, O + d * s_n, z)[1]
                nail_c = O + d * s_n + z * zt_n
                un, vn, wn = local(P, nail_c, x, d, z)
                ex_n = surface_extent(S, O + d * s_n + z * (zt_n - 1.5), x); hw_n = 0.33 * (ex_n[1] - ex_n[0])
                pe = 2.6
                nail = ((np.abs(un) / hw_n) ** pe + (np.abs(vn) / hl_n) ** pe) ** (1 / pe) - 1.0
                nail = nail * min(hw_n, hl_n)
                dep = 0.275 * (1 - np.clip(vn / hl_n, -1, 1))      # 0.55 at the cuticle, flush at the free edge
                ch = np.minimum(ch, np.maximum(np.maximum(nail, -(sk + dep)), np.abs(wn) - 4.0)); del sk, un, vn, wn, nail, dep
            f = f.reshape(shape)
            if k >= 1 and JS[k].barrel == 'P':       # this segment holds the cup at joint k: trim thin hood
                Jc = JS[k]
                wz = np.clip(1 - (Jc.cyl(P, Jc.R + GAP + 3.0)) / 1.5, 0, 1).reshape(shape).astype(np.float32)
                fo = opening(f, g, HOOD_MIN)
                f = f + wz * (np.maximum(f, fo) - f); del fo, wz
            f = opening(f, g, 0.65)                     # no rim or blade thinner than ~1.3 mm, every convex edge rounded
            # channels, knot pocket and grip recess after the opening (it would eat the 1.1 mm roof over a
            # channel); the smooth subtraction still gives every mouth and rim a rounded edge
            from scipy import ndimage as _nd
            ch = _nd.gaussian_filter(ch.reshape(shape), 0.3 / g.p)          # soft cut: rims of recesses and mouths come out smooth
            f = smax(f, -ch, 0.6); del ch
            M = to_manifold(f, g, 0.0, simplify=0.01)
            M = max(M.decompose(), key=lambda p: p.volume())
            # exact cuts: screw holes, tongue bore, channels, knot pocket
            for jj in ([0] if k == 0 else []) + ([k + 1] if k < nj - 1 else []):
                inf = info[jj]; jt = Joint(inf['R'], Rt=inf['Rt'], ws=JS[jj].ws)
                Mj = frame_matrix(np.array(inf['O']), np.array(inf['x']), np.array(inf['d']), np.array(inf['z']))
                # measure the barrel's real width on this smooth part, then size the head recess so at least
                # 1.2 mm of arm stays under the screw head, and pick the screw that fits
                tmM = to_tm(M); Oj, xj = np.array(inf['O']), np.array(inf['x'])
                ext = []
                for sgn in (-1, 1):            # outermost skin crossing along the screw axis on each side
                    loc, _, _ = tmM.ray.intersects_location([Oj], [sgn * xj], multiple_hits=True)
                    dd = (loc - Oj) @ (sgn * xj); dd = dd[(dd > 0) & (dd < 15)]
                    ext.append(sgn * float(dd.max()) if len(dd) else sgn * 3.1)
                xmin, xmax = ext
                w2 = JS[jj].ws / 2
                arm_n, arm_p = -xmin - w2, xmax - w2
                hs = -1 if arm_n > arm_p else 1                  # head on the side with the thicker arm
                xh, xf = (xmin, xmax) if hs < 0 else (xmax, xmin)
                arm_h = abs(xh) - w2; arm_f = abs(xf) - w2
                recess = float(np.clip(arm_h - ARM_MIN, 0.0, HEAD_H + 0.1))
                seat = xh - hs * recess
                span = abs(xf - seat) - 0.3                      # through pilot: tip may reach the far face
                screw = max([L_ for L_ in (6, 8, 10, 12, 16) if L_ <= span] or [0])
                proud = max(0.0, HEAD_H - recess)
                print(f'  {n} joint {jj}: width {xmax - xmin:.1f} arms {arm_h:.2f}/{arm_f:.2f} recess {recess:.2f} head proud {proud:.2f} screw {screw}', flush=True)
                inf.update(xmin=xmin, xmax=xmax, recess=recess, screw_len=screw, arm=float(min(arm_h, arm_f)), width=float(xmax - xmin), head_side=hs, head_proud=proud)
                if jj == 0 and n in AXLE:
                    # shared axle: 3.4 mm clearance right through; head recess on the index's outer side;
                    # heat-set insert (or a pilot) in the ring finger's far arm, where the axle ends
                    hole = cyl_x_span(1.7, -BIG, BIG)
                    role = {'index': 'head', 'middle': 'pass', 'ring': 'end'}[n]
                    if role == 'head':
                        # head recess on the outside of the hand; the axle threads into a heat-set insert in
                        # the index's own inner arm, so it turns with the index and is a plain pin for the others
                        rc = AXLE_RECESS if np.isfinite(AXLE_RECESS) else min(HEAD_H + 0.1, max(0.0, -xmin - w2 - ARM_MIN))
                        hole = hole + cyl_x_span(3.1, -BIG, xmin + rc)
                        # v3.3 (test print: tightening the axle squeezed the two index arms onto the palm tongue
                        # and the finger seized): the insert moves to the OUTER arm, right under the head. Head and
                        # thread now grip the same arm, nothing pulls the arms together, and the inner arm turns
                        # freely on the screw (plain 3.4 mm hole). The insert goes in from outside, flush in the
                        # head recess; its hole runs through to the slot so the displaced plastic can escape.
                        arm_out = -(xmin + rc) - w2; dpt = min(INS_D, arm_out)
                        if dpt >= 4.0:
                            hole = hole + cyl_x_span(INS_R, -BIG, -w2)
                        else:
                            hole = cyl_x_span(1.7, -BIG, w2) + cyl_x_span(1.3, -BIG, BIG) + cyl_x_span(3.1, -BIG, xmin + rc)
                        inf.update(axle_role=role, recess=float(rc), seat=float(xmin + rc), screw_len=0,
                                   insert=bool(dpt >= 4.0), insert_depth=float(dpt), insert_arm='outer')
                        print(f'  axle head: recess {rc:.2f}; outer arm under the head {arm_out:.2f} -> insert {dpt >= 4.0} ({dpt:.2f} deep, through)', flush=True)
                    elif role == 'end':
                        inf.update(axle_role=role, screw_len=0, far_arm=float(xmax - w2))
                        print(f'  axle end: far arm {xmax - w2:.2f} (the axle tip rests in it)', flush=True)
                    else:
                        inf.update(axle_role=role, screw_len=0)
                    M = M - hole.transform(Mj)
                    continue
                if hs < 0:
                    hole = cyl_x_span(3.1, -BIG, seat) + cyl_x_span(1.7, -BIG, w2) + cyl_x_span(1.3, -BIG, BIG)     # pilot goes right through
                else:
                    hole = cyl_x_span(3.1, seat, BIG) + cyl_x_span(1.7, -w2, BIG) + cyl_x_span(1.3, -BIG, BIG)
                M = M - hole.transform(Mj)
            if JS[k].barrel == 'P':
                inf = info[k]; Mj = frame_matrix(np.array(inf['O']), np.array(inf['x']), np.array(inf['d']), np.array(inf['z']))
                M = M - cyl_x(1.7).transform(Mj)
            parts = M.decompose(); M = max(parts, key=lambda p: p.volume())
            to_tm(M).export(f'{OUT}/fingers/{n}-{k+1}.stl')
            print(n, k + 1, 'vol', round(M.volume()), 'grid', g.n.tolist(), flush=True)
        joints_out[n] = dict(J3[n]); joints_out[n]['tip_pad'] = tip_pad.tolist(); joints_out[n]['pad_half_len'] = PB
    # axle length: from the head seat on the index side to inside the ring finger's insert (or pilot)
    try:
        t = {n: float((np.array(joints_out[n]['joints'][0]['O']) - AX_C) @ AX_A) for n in AXLE}
        hi_ = joints_out['index']['joints'][0]; ri_ = joints_out['ring']['joints'][0]
        t_seat = t['index'] + hi_['seat']; t_far = t['ring'] + ri_['xmax'] - 0.3; t_min = t['ring'] + ri_['xmax'] - ri_['far_arm'] + 0.8
        fits = [L_ for L_ in AXLE_LENGTHS if t_min <= t_seat + L_ <= t_far]
        need = [(L_, round(t_seat + L_ - t_min, 2), round(t_far - t_seat - L_, 2)) for L_ in AXLE_LENGTHS]
        print(f'axle span seat->far {t_far - t_seat:.2f} mm, min {t_min - t_seat:.2f}; fits {fits}; (len, grip-margin, tip-room) {need}', flush=True)
        joints_out['axle'] = {'c': AX_C.tolist(), 'a': AX_A.tolist(), 'fits': fits, 'screw_len': max(fits) if fits else 0,
                              't_seat': t_seat, 't_far': t_far + 0.3, 't_index_min': t['index'] + hi_['xmin'] - 1.0}
    except KeyError as e:
        print('axle length not computed (partial build)', e, flush=True)
    json.dump(joints_out, open(f'{OUT}/joints.json', 'w'), indent=1)
    json.dump(FG.CHANNELS, open(f'{OUT}/finger_channels.json', 'w'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
