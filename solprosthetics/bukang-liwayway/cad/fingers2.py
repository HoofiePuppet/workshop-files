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
R_FLEX, R_RET = 0.75, 0.8   # line channel radii: 1.5 mm flexor, 1.6 mm return cord
HOOD_MIN = 0.9       # cup hood thinner than 2 x this is trimmed away (local opening radius)
OUT = 'build'; os.makedirs(f'{OUT}/fingers', exist_ok=True)


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
                boss = smax(np.sqrt(v * v + w * w) - (Jt.R - 0.2), np.abs(u) - (Jt.ws / 2 + ARM_MIN + HEAD_H), 1.2)
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
        PB = float(np.clip(((L - 2.0) - s_rim) / 2, 3.2, 4.6))          # pocket half length (outer, lip edge)
        s_pad = (L - 2.0) - PB
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
                paths = [(FG.relax([F[k], F[k + 1]], R_FLEX), R_FLEX), (FG.relax([Rr[k], Rr[k + 1]], R_RET), R_RET)]
            else:
                zmid = (zmin_t + zmax_t) / 2
                paths = [(FG.relax(FG.spline([F[-1], O + d * (L - 11) + z * (zmin_t + 2.6), tip_pad + z * 1.2, tip_pad - z * 2], 14), R_FLEX), R_FLEX),
                         (FG.relax(FG.spline([Rr[-1], O + d * (L - 7) + z * (zmax_t - 2.4), O + d * (L - 2.5) + z * zmid,
                                              O + d * (L - 5.5) + z * (zmin_t + 1.6), tip_pad - z * 2], 18), R_RET), R_RET)]
            ch = np.full(len(P), 1e3, np.float32)
            for pts, r in paths:
                FG.CHANNELS.append({'r': r, 'pts': [list(map(float, p)) for p in pts]})
                ch = np.minimum(ch, chain_field(P, pts, r))
                for e0, e1 in ((pts[0], pts[1]), (pts[-1], pts[-2])):      # flared mouth at each end
                    e0 = np.asarray(e0, float); dv = np.asarray(e1, float) - e0; dv /= np.linalg.norm(dv) + 1e-9
                    ch = np.minimum(ch, seg_dist(P, e0 - dv * 0.6, e0 + dv * 1.0) - (r + 0.25))
            if k == nj - 1:
                # knot pocket under the pad, and the grip recess: 1.0 mm deep, following the skin, rounded rim;
                # the inner-tube pad is glued in with contact cement
                ch = np.minimum(ch, seg_dist(P, tip_pad - z * 4.0, tip_pad + z * 1.5) - 1.5)
                u, v, w = local(P, tip_pad, x, d, z)
                sk = S(P)
                ell_b = (np.sqrt((u / 3.6) ** 2 + (v / PB) ** 2) - 1.0) * 3.6
                rec = np.maximum(np.maximum(ell_b, -(sk + 1.0)), np.abs(w) - 6.0)   # smooth limit (a hard cut-off left a jagged rim)
                ch = np.minimum(ch, rec); del rec, ell_b
                # fingernail: shallow nail bed (0.45 mm) on the back of the fingertip, for looks or to paint
                zt_n = surface_extent(S, O + d * (L - 4.0), z)[1]
                nail_c = O + d * (L - 4.0) + z * zt_n
                un, vn, wn = local(P, nail_c, x, d, z)
                ex_n = surface_extent(S, O + d * (L - 4.0) + z * (zt_n - 1.5), x); hw_n = 0.36 * (ex_n[1] - ex_n[0])
                nail = (np.sqrt((un / hw_n) ** 2 + (vn / 3.5) ** 2) - 1.0) * min(hw_n, 3.5)
                ch = np.minimum(ch, np.maximum(np.maximum(nail, -(sk + 0.45)), np.abs(wn) - 4.0)); del sk, un, vn, wn, nail
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
    json.dump(joints_out, open(f'{OUT}/joints.json', 'w'), indent=1)
    json.dump(FG.CHANNELS, open(f'{OUT}/finger_channels.json', 'w'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
