"""Stage 4 (v3.1): forearm cuff (PETG) as a smooth distance field.
Follows the forearm with a 1.5 mm liner gap and a 3 mm wall, open along the palm side, rounded edges,
rounded strap slots and vents, hinge ear plates outside the palm's ear pads. The tensioner is now a low,
symmetric swelling of the wall (2.8 mm at its crown) centred on the top of the forearm; the four lines run
inside it and are pinned by M3 x 4 countersunk (flat-head) screws that sit flush.
Writes build/cuff.stl and build/cuff.json"""
import json, numpy as np, trimesh, manifold3d as mf
from scipy import ndimage
from rlib import to_tm, smooth, frame_matrix
from sdf import Grid, sdf, to_manifold, smin, smax, seg_dist
from joints import cyl_x_span
from sdfparts import opening

PJ = json.load(open('build/palm.json'))
W = np.array(PJ['wrist']); EARS = PJ['ears_x']
LINER, WALL = 1.5, 3.0
Y_END = -102.0
OPEN_HALF = 62.0
PSI_DORSAL, PSI_PALMAR = 122.0, -150.0
EAR_EXT = 2.2               # v3.3: thumb-side arm 2.2 mm further out (the hand's ear pad is thicker for an insert)
EAR_EXT_R = 1.0             # v3.3: little-finger-side arm 1.0 mm further out
STRAPS_Y = (-36.0, -84.0); STRAP_W = 27.0
FLEX_EXITS = [PJ['line_exits_x'][i] for i in (0, 2, 4, 6)]
BUMP_H, BUMP_Y, BUMP_LEN, BUMP_WID = 2.8, -29.0, 17.0, 16.0
SCREW_LEN = 4.0             # default clamp screw (M3 x 4 flat head); v3.2c picks 4/5/6 per clamp
CUFF_R = 1.5                # v3.2c: 3 mm line channels


def main():
    arm = smooth(trimesh.load('src/right-arm-oriented.stl'), 1, 6)
    g = Grid([-34, -112, -28], [46, 10, 44], 0.35)
    f = sdf(arm, g, smooth_sigma=0.25)
    f = ndimage.gaussian_filter(f, 0.6 / g.p)
    X, Y, Z = (a.astype(np.float32) for a in g.points())
    f = f.astype(np.float32)
    ys = np.array([-140, -110, -100, -80, -60, -40, -20, -5.0])
    cxs = np.array([10.4, 10.4, 10.3, 9.8, 9.0, 7.8, 6.6, 5.7]); czs = np.array([0.3, 1.8, 2.5, 3.9, 5.2, 6.3, 7.0, 7.3])
    CX = np.interp(Y, ys, cxs); CZ = np.interp(Y, ys, czs)
    r_ax = np.sqrt((X - CX) ** 2 + (Z - CZ) ** 2) + 1e-6
    theta = np.degrees(np.arctan2(X - CX, -(Z - CZ)))           # 0 = straight down the palm side, 180 = top
    # tensioner swelling: a low bell raised on the wall itself, centred on the top of the forearm (theta = 180),
    # so it follows the cuff's curve and sits straight
    dth = (theta - 180 + 540) % 360 - 180
    s_arc = np.radians(dth) * r_ax
    bell = BUMP_H * np.exp(-(s_arc / BUMP_WID) ** 2 - ((Y - BUMP_Y) / BUMP_LEN) ** 2)
    outer = f - LINER - WALL - bell
    shell = smax(outer, -(f - LINER), 0.6)
    open_f = (OPEN_HALF - np.abs(theta)) * np.radians(1) * r_ax
    shell = smax(shell, open_f, 1.5)
    shell = smax(shell, Y_END - Y, 1.5)
    yw, zw = Y - W[1], Z - W[2]
    rw = np.sqrt(yw ** 2 + zw ** 2) + 1e-6; psi = np.degrees(np.arctan2(zw, yw))
    wedge = np.minimum(psi - PSI_PALMAR, PSI_DORSAL - psi) * np.radians(1) * rw
    shell = smax(shell, wedge, 1.5)
    for xw in EARS:
        sx = 1 if xw > W[0] else -1
        ext = EAR_EXT if sx < 0 else EAR_EXT_R
        x_out = xw + sx * (2.3 + ext + 3.4)
        hw = np.interp(Y, ys, np.array([49.3, 45.6, 44.2, 41.2, 38.4, 36.2, 34.3, 35.0]) / 2)
        sb = np.clip((-5.0 - Y) / 6.0, 0, 1); sb = sb * sb * (3 - 2 * sb)      # arm joins the cuff wall from y = -5 back (wrist clearance)
        x_in = (xw + sx * (2.3 + ext)) * (1 - sb) + (CX + sx * (hw + LINER + WALL - 1.2)) * sb
        cap = seg_dist(np.stack([np.zeros_like(Y), yw, zw], -1), np.array([0, 0, 0.0]), np.array([0, -17.0, 0.0])) - 7.5
        plate = smax(smax(sx * (x_in - X), sx * (X - x_out), 1.4), cap, 1.8)
        shell = smin(shell, plate, 4.0)
    # clearance for the hand's hinge pads: only between the two arms' inner faces (one bounded cut; a cut per
    # ear ran across the whole cuff and took the front of the thumb-side arm away)
    between = np.minimum((EARS[1] + 2.3 + EAR_EXT_R) - X, X - (EARS[0] - 2.3 - EAR_EXT))
    shell = smax(shell, np.minimum(9.6 - rw, between), 0.4); del between
    # rounded strap slots and vents (cut in the field so their edges are rounded)
    def radial_slot(y0, th, half_len, r, along='y'):
        """Rounded slot through the wall, centred at (y0, angle th), long axis along y or around the arm."""
        s = np.radians(((theta - th + 540) % 360) - 180) * r_ax
        if along == 'y':
            a, b = Y - y0, s
        else:
            a, b = s, Y - y0
        return np.sqrt(np.maximum(np.abs(a) - half_len, 0) ** 2 + b ** 2) - r
    cut = np.full(shell.shape, 1e3, np.float32)
    for ys_ in STRAPS_Y:
        for th in (OPEN_HALF + 16, -(OPEN_HALF + 16)):
            cut = np.minimum(cut, radial_slot(ys_, th, STRAP_W / 2 - 2.3, 2.3, along='y'))
    for ys_ in (-52.0, -70.0):                     # one clean vent slot each side, well apart (no doubled holes)
        for th in (140.0, -140.0):
            cut = np.minimum(cut, radial_slot(ys_, th, 3.5, 3.0, along='y'))
    shell = smax(shell, -cut, 0.6)
    # the hand swings about the wrist axis between the arms: trim the arms to its swept volume + 0.4 mm
    # v3.2d: the palm AND the cover sweep past the arms. Each gets its own distance field (one combined mesh
    # confused the inside/outside test where the two meet and left ragged spikes), 1-degree steps, and the
    # swept field is smoothed before it trims, so the trimmed faces come out clean and rounded.
    tms = [trimesh.load('build/palm_back.stl'), trimesh.load('build/palm_flap.stl')]
    from scipy.interpolate import RegularGridInterpolator as RGI
    from scipy import ndimage as _nd
    for lo_, hi_ in (([-32.0, -16.0, -6.0], [-8.0, 12.0, 22.0]), ([21.0, -16.0, -6.0], [40.0, 12.0, 22.0])):
        gl = Grid(lo_, hi_, 0.3)
        FPs = [RGI(gl.axes(), sdf(m_, gl, band=3.0, spacing=0.15), bounds_error=False, fill_value=10.0) for m_ in tms]
        msk = (X >= lo_[0]) & (X <= hi_[0]) & (Y >= lo_[1]) & (Y <= hi_[1]) & (Z >= lo_[2]) & (Z <= hi_[2])
        Q = np.stack([X[msk], Y[msk], Z[msk]], 1)
        swp = np.full(len(Q), 10.0, np.float32)
        for a_ in np.arange(-58.0, 30.6, 1.0):
            Rm = trimesh.transformations.rotation_matrix(np.radians(-a_), [1, 0, 0], W)[:3, :3]
            Qr = (Q - W) @ Rm.T + W                          # point in the hand's own frame at wrist angle a_
            for FP in FPs:
                swp = np.minimum(swp, FP(Qr))
        full = np.full(shell.shape, 10.0, np.float32); full[msk] = np.clip(swp, -10, 10)
        full = _nd.gaussian_filter(full, 0.45 / g.p)
        shell[msk] = smax(shell[msk], -(full[msk] - 0.4), 0.5)
        del FPs, Q, swp, msk, full
    shell = opening(shell, g, 0.45)
    # tensioner line channels (1.8 mm), cut in the field with flared mouths where they leave the swelling
    from scipy.interpolate import RegularGridInterpolator
    FS0 = RegularGridInterpolator(g.axes(), shell, bounds_error=False, fill_value=10)
    cx_b = float(np.interp(BUMP_Y, ys, cxs))
    PP = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    tube = np.full(len(PP), 1e3, np.float32); chans = []
    pc = json.load(open('build/palm_channels.json'))
    sp_ = 4.7 / (FLEX_EXITS[1] - FLEX_EXITS[0])                # lines 4.7 mm apart in the cuff whatever the palm exits
    for e_x, x in zip(FLEX_EXITS, [cx_b + sp_ * (e - np.mean(FLEX_EXITS)) for e in FLEX_EXITS]):
        zs = np.arange(40, -5, -0.05)
        v = FS0(np.stack([np.full_like(zs, x), np.full_like(zs, BUMP_Y), zs], 1))
        inside = zs[v < 0]
        ztop, zbot = inside.max(), inside[inside > inside.max() - 12].min()
        zc = ztop - min(2.7, (ztop - zbot) / 2)
        # the channel follows the middle of the thick wall inside the swelling, and turns out through the
        # front and back slopes at a steep angle (rounded flares there), so it never grazes the top
        def zs_at(y):
            zz = np.arange(40, -5, -0.05); vv_ = FS0(np.stack([np.full_like(zz, x), np.full_like(zz, y), zz], 1))
            ins = zz[vv_ < 0]; top_ = ins.max(); bot_ = ins[ins > top_ - 12].min(); return top_, bot_
        # the line enters through the cuff's front end face (not the top), runs in the middle of the wall to
        # its clamp, and leaves into the inside of the cuff behind the swelling: only the clamp seats show on top
        # v3.2d: 3 mm channel under the clamps (thick swelling, 2.5 mm deep so the floor is where the M3 x 4 tip lands);
        # toward the front end the wall is only ~3 mm, so the channel narrows (down to 2 mm) and keeps to the middle
        mids, rads = [], []
        for y in np.arange(-6.0, -41.1, -2.0):
            try:
                t_, b_ = zs_at(y)
            except ValueError:
                continue                                   # in front of the cuff's front face
            wall_ = t_ - b_
            if abs(y - BUMP_Y) <= 6.5:
                r_ = CUFF_R; dep_ = CUFF_R + 1.0
            else:
                r_ = float(np.clip(wall_ / 2 - 0.6, 1.0, CUFF_R)); dep_ = float(np.clip(wall_ / 2, r_ + 0.6, CUFF_R + 1.0))
            mids.append(np.array([x, y, t_ - dep_])); rads.append(r_)
        tb_, bb_ = zs_at(-46.0)
        path = [np.array([x, -4.0, mids[0][2]])] + mids + [np.array([x, -45.0, bb_ + 0.4]), np.array([x, -47.0, bb_ - 2.0])]
        prad = [rads[0]] + rads + [rads[-1], rads[-1]]
        for a0, a1, r0, r1 in zip(path[:-1], path[1:], prad[:-1], prad[1:]):
            tube = np.minimum(tube, seg_dist(PP, a0, a1) - min(r0, r1))
        for e0, e1, re_ in ((path[0], path[1], prad[0]), (path[-1], path[-2], prad[-1])):
            dv = (e1 - e0) / np.linalg.norm(e1 - e0)
            tt = np.arange(0, np.linalg.norm(e1 - e0), 0.05); seg = e0[None] + tt[:, None] * dv[None]
            i = int(np.argmax(FS0(seg) < 0)); e = seg[i]
            tube = np.minimum(tube, seg_dist(PP, e - dv * 0.6, e + dv * 1.0) - (re_ + 0.25))
        print('cuff line', round(float(x), 1), 'radii', [round(r__, 2) for r__ in rads], flush=True)
        zc = float(np.interp(-BUMP_Y, -np.array([m_[1] for m_ in mids]), [m_[2] for m_ in mids]))
        chans.append((x, ztop, zbot, zc, mids))
    shell = smax(shell, -tube.reshape(shell.shape), 0.4); del tube, PP
    np.save('build/cuff_field.npy', shell)
    cuff = to_manifold(shell, g, 0.0, simplify=0.01)
    _pcs = cuff.decompose(); print('cuff pieces', sorted([round(p_.volume()) for p_ in _pcs], reverse=True)[:6], flush=True)
    cuff = max(_pcs, key=lambda p: p.volume())
    # hinge holes (clearance + head recess in the ear plates)
    for xw in EARS:
        sx = 1 if xw > W[0] else -1
        ext = EAR_EXT if sx < 0 else EAR_EXT_R
        x_out = xw + sx * (2.3 + ext + 3.4)
        if sx > 0:
            h = cyl_x_span(1.7, x_out - 4.5, x_out + 2) + cyl_x_span(3.1, x_out - 1.5, x_out + 5)
        else:
            h = cyl_x_span(1.7, x_out - 2, x_out + 4.5) + cyl_x_span(3.1, x_out - 5, x_out + 1.5)
        cuff = cuff - h.translate([0, W[1], W[2]])
    # tensioner clamps: countersink for a flat-head M3 (head 5.6 mm), pilot 2.6 to SCREW_LEN below the top
    clamps = []
    for k_, (x, ztop, zbot, zc, mids) in enumerate(chans):
        # neighbouring lines are 4.7 mm apart but a countersink is 5.9 wide: stagger the seats front/back
        # (7 mm apart) so each one is a separate clean round seat
        yc = BUMP_Y + (3.5 if k_ % 2 == 0 else -3.5)
        zz = np.arange(40, -5, -0.05); vv_ = FS0(np.stack([np.full_like(zz, x), np.full_like(zz, yc), zz], 1))
        ins = zz[vv_ < 0]; ztop = ins.max(); zbot = ins[ins > ztop - 12].min()
        zc = float(np.interp(-yc, -np.array([m_[1] for m_ in mids]), [m_[2] for m_ in mids]))
        t = ztop - zbot
        # countersink and pilot square to the swelling's surface (drilled straight down they looked like half-moons)
        p0 = np.array([x, yc, ztop]); e = 0.2
        gr = np.array([(FS0((p0 + dv)[None])[0] - FS0((p0 - dv)[None])[0]) / (2 * e) for dv in np.eye(3) * e]); nz = gr / np.linalg.norm(gr)
        ux = np.cross(nz, [0, 1.0, 0]); ux /= np.linalg.norm(ux); uy = np.cross(nz, ux)
        Mc = frame_matrix(p0, ux, uy, nz)
        cs = mf.Manifold.cylinder(1.75, 1.5, 2.95, 32).translate([0, 0, -1.7]) + mf.Manifold.cylinder(1.0, 2.95, 2.95, 32)
        depth_ = ztop - zc                                  # channel centre below the top
        need_ = depth_ + CUFF_R - 0.3                       # tip must reach the line lying on the channel floor
        L_ = next((L0 for L0 in (4, 5, 6) if L0 >= need_ and L0 <= t - 0.8), min(6, int(t - 0.8)))
        pilot = mf.Manifold.cylinder(L_ + 0.3, 1.3, 1.3, 24).translate([0, 0, -L_ - 0.3])
        cuff = cuff - cs.transform(Mc) - pilot.transform(Mc)
        clamps.append({'x': float(x), 'y': float(yc), 'top': float(ztop), 'line_z': float(zc), 'wall': float(t), 'screw_len': int(L_), 'channel_floor_depth': float(depth_ + CUFF_R), 'floor_below_screw': float(t - L_ - 0.3)})
    parts = cuff.decompose(); main_p = max(parts, key=lambda p: p.volume())
    to_tm(main_p).export('build/cuff.stl'); print('cuff vol', round(main_p.volume()), 'genus', main_p.genus())
    json.dump({'clamps': clamps, 'bump_y': BUMP_Y, 'bump_height': BUMP_H, 'straps_y': STRAPS_Y}, open('build/cuff.json', 'w'), indent=1)
    for c in clamps: print(c)


if __name__ == '__main__':
    main()
