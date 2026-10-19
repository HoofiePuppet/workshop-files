"""Stage 2: cut the realistic outer skin into palm + 4 x 3 finger segments with real hinge joints.
Writes build/fingers/*.stl, build/palm_raw.stl (palm with MCP tongues, before shell work) and build/joints.json."""
import json, os, numpy as np, trimesh, manifold3d as mf
from rlib import to_mf, to_tm, frame_matrix
from sdf import to_manifold
from lib_grid import load_skin
from joints import Joint, cyl_x, bx, BIG, GAP

CFG = json.load(open('src/config.json')); AX = json.load(open('src/finger_axes_splay.json'))
ORDER = ['index', 'middle', 'ring', 'little']
FLEX = [80, 85, 65]      # max flexion per joint (MCP, PIP, DIP), deg
HEAD = {'index': -1, 'middle': -1, 'ring': 1, 'little': 1}   # screw head side (local x): outside of the hand first
OUT = 'build'; os.makedirs(f'{OUT}/fingers', exist_ok=True)


def frame(n):
    d = np.array(AX[n]['dir']); d /= np.linalg.norm(d)
    x = np.cross(d, [0, 0, 1]); x /= np.linalg.norm(x); x = -x if x[0] < 0 else x
    z = np.cross(x, d); z = z if z[2] > 0 else -z
    return np.array(AX[n]['mcp']), x, d, z


def halfspace(p0, nrm, keep_negative=True):
    nrm = nrm / np.linalg.norm(nrm)
    u = np.cross(nrm, [0, 0, 1]); u /= np.linalg.norm(u); v = np.cross(nrm, u)
    b = bx(-BIG, 0, -BIG, BIG, -BIG, BIG) if keep_negative else bx(0, BIG, -BIG, BIG, -BIG, BIG)
    return b.transform(frame_matrix(p0, nrm, u, v))


CHANNELS = []
FIELD = None          # outer-skin interpolator, set in main()
MIN_SKIN = 0.9


def relax(pts, r, n_per=2.0):
    """Resample a channel and push interior points inward wherever the skin over it is thinner than MIN_SKIN."""
    pts = [np.asarray(p, float) for p in pts]
    dense = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        k = max(2, int(np.linalg.norm(b - a) / n_per))
        dense += [a + (b - a) * t for t in np.linspace(0, 1, k + 1)[1:]]
    P = np.array(dense)
    if FIELD is None or len(P) < 4: return list(P)
    h = 0.15
    for _ in range(8):
        v = FIELD(P[1:-1]); wall = -v - r
        need = np.clip(MIN_SKIN - wall, 0, 3)
        if need.max() < 0.02: break
        gr = np.stack([(FIELD(P[1:-1] + h * e) - FIELD(P[1:-1] - h * e)) / (2 * h) for e in np.eye(3)], 1)
        gr /= np.linalg.norm(gr, axis=1, keepdims=True) + 1e-9
        P[1:-1] -= gr * need[:, None]
        P[1:-1] = (P[:-2] + 2 * P[1:-1] + P[2:]) / 4 if len(P) > 4 else P[1:-1]
    return list(P)


def capsule_chain(pts, r, fit=True):
    if fit: pts = relax(pts, r)
    CHANNELS.append({'r': r, 'pts': [list(map(float, p)) for p in pts]})
    sph = [mf.Manifold.sphere(r, 24).translate(list(p)) for p in pts]
    return mf.Manifold.batch_boolean([mf.Manifold.batch_hull([a, b]) for a, b in zip(sph[:-1], sph[1:])], mf.OpType.Add)


def spline(ctrl, n=12):
    """Quadratic Bezier chain through the end points, smooth in between."""
    ctrl = [np.asarray(c, float) for c in ctrl]
    if len(ctrl) == 2: return ctrl
    out = []
    for t in np.linspace(0, 1, n):
        P = ctrl
        while len(P) > 1:
            P = [(1 - t) * a + t * b for a, b in zip(P[:-1], P[1:])]
        out.append(P[0])
    return out


def local_bounds(piece_tm, O, x, d, z, s):
    """Section of a finger piece at distance s along the axis: (xmin, xmax, zmin, zmax) relative to O + d*s."""
    c = O + d * s
    sec = piece_tm.section(plane_origin=c, plane_normal=d)
    loops = sec.discrete
    l = min(loops, key=lambda l: np.linalg.norm(l.mean(0) - c))
    q = l - c
    return (q @ x).min(), (q @ x).max(), (q @ z).min(), (q @ z).max()


def main():
    global FIELD
    d_, g = load_skin()
    from scipy.interpolate import RegularGridInterpolator
    FIELD = RegularGridInterpolator(g.axes(), d_['outer'], bounds_error=False, fill_value=10)
    Mo = to_manifold(d_['outer'], g)
    insets = {k: to_manifold(d_['outer'] + k, g) for k in (0.5, 1.0)}
    Mo_g = to_manifold(d_['outer'] - 0.35, g)
    fr = {}
    O_ = {n: frame(n) for n in ORDER}
    # bisector planes between neighbouring fingers
    planes = []
    for a, b in zip(ORDER[:-1], ORDER[1:]):
        Oa, xa, da, _ = O_[a]; Ob, xb, db, _ = O_[b]
        planes.append(((Oa + da * 25 + Ob + db * 25) / 2, xa + xb))
    for i, n in enumerate(ORDER):
        def region(sh):
            r = mf.Manifold.cube([1, 1, 1]).scale([2 * BIG] * 3).translate([-BIG] * 3)
            if i < 3: r = r ^ halfspace(planes[i][0] - sh * planes[i][1] / np.linalg.norm(planes[i][1]), planes[i][1], True)
            if i > 0: r = r ^ halfspace(planes[i - 1][0] + sh * planes[i - 1][1] / np.linalg.norm(planes[i - 1][1]), planes[i - 1][1], False)
            return r
        fr[n] = (region(0.3), region(0.0), region(-0.3))   # (part, exact, grown past the bisector)

    palm = Mo
    joints_out = {}
    for n in ORDER:
        O, x, d, z = O_[n]; L = AX[n]['L']; fp, fm = CFG['SPLIT'][n]
        piece = to_tm(Mo ^ fr[n][0])
        small = n == 'little'
        st = [0.0, fp * L] if small else [0.0, fp * L, (fp + fm) * L]   # little finger: DIP fused (too slim for a third screw)
        nj = len(st)
        J, F, Rr, info = [], [], [], []
        for j, s in enumerate(st):
            x0, x1, zmin, zmax = local_bounds(piece, O, x, d, z, s if j else 8.0)
            T = zmax - zmin
            Rt = 3.1 if j == 2 else (3.2 if small else 3.4)
            zf = Rt + 1.1
            zc = max(zmin + 0.43 * T, zmin + zf + 1.4)
            if j == 0:
                zmax = min(zmax, local_bounds(piece, O, x, d, z, 0.0)[3])
            dors = zmax - zc
            R = float(np.clip(dors - 2.3, Rt + 1.35, 6.0))
            jt = Joint(R, Rt=Rt, wt=4.8 if small else 5.6, ws=5.4 if small else 6.2, hn=2.6 if (j == 2 or small) else 3.0,
                       barrel='D' if j == 0 else 'P', split=(0, 22), flex=(-6, FLEX[j] + 4))
            Oj = O + d * s + z * zc
            M = frame_matrix(Oj, x, d, z)
            J.append((jt, M, Oj))
            F.append(Oj - z * zf); Rr.append(Oj + z * (R + 0.95))
            # screw: outer surface along the axis
            ax_hits = to_tm((Mo ^ cyl_x(0.3).transform(M)) ^ fr[n][1]).vertices - Oj
            xs = ax_hits @ x
            arm = (xs.max() - xs.min()) / 2 - jt.ws / 2
            recess = float(min(2.2, arm - 1.4))
            span = float(xs.max() - xs.min() - recess)
            screw = max(L_ for L_ in (6, 8, 10, 12, 16) if L_ <= span - 0.3)
            info.append({'recess': recess, 'screw_len': screw, 'arm': float(arm), 's': s, 'zc': zc, 'R': R, 'Rt': Rt, 'zf': zf, 'T': float(T), 'dorsal_room': float(dors - (R + 1.55)),
                         'palmar_room': float(zc - zmin - zf - 0.65), 'width': float(xs.max() - xs.min()),
                         'xmin': float(xs.min()), 'xmax': float(xs.max()), 'O': Oj.tolist(), 'x': x.tolist(), 'd': d.tolist(), 'z': z.tolist()})
        # tip geometry for the line anchor (knot pocket under the nail) and the grip pad
        _, _, zmin_t, zmax_t = local_bounds(piece, O, x, d, z, L - 7)
        tip_pad = O + d * (L - 7) + z * zmin_t
        segs = []
        for k in range(nj):
            reg = Mo ^ fr[n][0]
            jp, Mp, _ = J[k]
            reg = reg ^ jp.dist_region().transform(Mp)
            if k < nj - 1:
                jn, Mn, _ = J[k + 1]
                reg = reg ^ jn.prox_region().transform(Mn)
            reg = reg - jp.wedge_dist().transform(Mp)
            # tongue from the proximal joint when its barrel is on the proximal side
            if jp.barrel == 'P':
                reg = reg + (jp.tongue().transform(Mp) ^ insets[0.5])
            # barrel cuts
            if jp.barrel == 'D':
                reg = reg - jp.slot().transform(Mp) - jp.screw_holes(HEAD[n], info[k]['xmin'] if HEAD[n] < 0 else info[k]['xmax'], 0, info[k]['recess']).transform(Mp)
            if k < nj - 1:
                jn, Mn, _ = J[k + 1]
                reg = reg - jn.slot().transform(Mn) - jn.screw_holes(HEAD[n], info[k + 1]['xmin'] if HEAD[n] < 0 else info[k + 1]['xmax'], 0, info[k + 1]['recess']).transform(Mn)
                reg = reg - capsule_chain([F[k], F[k + 1]], 0.65) - capsule_chain([Rr[k], Rr[k + 1]], 0.6)
            else:
                # flexor and return cord both end in a knot pocket under the rubber fingertip pad (hidden)
                zmid = (zmin_t + zmax_t) / 2
                reg = reg - capsule_chain(spline([F[-1], O + d * (L - 11) + z * (zmin_t + 2.6), tip_pad + z * 1.2, tip_pad - z * 2], 14), 0.65)
                reg = reg - capsule_chain(spline([Rr[-1], O + d * (L - 7) + z * (zmax_t - 1.8), O + d * (L - 2.5) + z * zmid,
                                                  O + d * (L - 5.5) + z * (zmin_t + 1.6), tip_pad - z * 2], 18), 0.6)
                reg = reg - mf.Manifold.cylinder(5, 1.5, 1.5, 32).translate([0, 0, -1.0]).transform(frame_matrix(tip_pad + z * 1.0, x, d, z))
                # grip pocket for the rubber insert: 1.0 deep, 0.5 mm undercut lip all round
                Mpad = frame_matrix(tip_pad, x, d, z)
                big = mf.Manifold.cylinder(12, 1, 1, 64).scale([3.6, 4.6, 1]).translate([0, 0, -6]).transform(Mpad)
                sml = mf.Manifold.cylinder(12, 1, 1, 64).scale([3.1, 4.1, 1]).translate([0, 0, -6]).transform(Mpad)
                pocket = ((Mo - insets[0.5]) ^ sml) + ((insets[0.5] - insets[1.0]) ^ big)
                reg = reg - pocket
            segs.append(reg)
        # palm side of the MCP joint
        j0, M0, _ = J[0]
        # grown 0.3 mm past the bisector planes so neighbouring fingers' cuts overlap: cuts that only met
        # at the plane left paper-thin fins of palm standing between the knuckles
        palm = palm - (fr[n][2] - j0.prox_region().transform(M0))
        palm = palm + (j0.tongue().transform(M0) ^ insets[0.5])
        # rounded palm-side clearance ('crease'): carve from each proximal part exactly what the distal part
        # (grown 0.35 mm) sweeps through over its flex range
        for j in range(nj):
            jt, Mj, Oj = J[j]
            loc = bx(-BIG, BIG, GAP / 2 - 0.35, jt.R + 10, -BIG, BIG) - cyl_x(jt.R + 0.05)
            Dg = (Mo_g ^ (fr[n][2] if j == 0 else fr[n][1])) ^ loc.transform(Mj)
            xa = np.array(info[j]['x'])
            cop = []
            for a in np.arange(0, FLEX[j] + 0.1, 2.5):
                Rm = trimesh.transformations.rotation_matrix(np.radians(-a), xa, Oj)
                cop.append(Dg.transform(Rm[:3, :]))
            sw = mf.Manifold.batch_boolean(cop, mf.OpType.Add)
            if j == 0:
                palm = palm - sw
            else:
                segs[j - 1] = segs[j - 1] - sw
        for k, s_ in enumerate(segs):
            parts = s_.decompose()
            main_part = max(parts, key=lambda p: p.volume())
            if len(parts) > 1:
                print(f'  {n}-{k+1}: dropped {len(parts)-1} loose bits ({sum(p.volume() for p in parts)-main_part.volume():.1f} mm3)')
            to_tm(main_part).export(f'{OUT}/fingers/{n}-{k+1}.stl')
            print(n, k + 1, 'vol', round(main_part.volume()), 'genus', main_part.genus())
        joints_out[n] = {'joints': info, 'flexor': [f.tolist() for f in F], 'return': [r.tolist() for r in Rr],
                         'head': HEAD[n], 'tip_pad': tip_pad.tolist(), 'L': L}
        for j, inf in enumerate(info):
            print(f"  joint {j}: R {inf['R']:.1f} T {inf['T']:.1f} width {inf['width']:.1f} dorsal room {inf['dorsal_room']:.2f} palmar room {inf['palmar_room']:.2f}")
    to_tm(palm).export(f'{OUT}/palm_raw.stl')
    json.dump(joints_out, open(f'{OUT}/joints.json', 'w'), indent=1)
    json.dump(CHANNELS, open(f'{OUT}/finger_channels.json', 'w'))


if __name__ == '__main__':
    main()
