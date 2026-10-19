"""Stage 4: forearm cuff (PETG). Follows the MakeHuman forearm with a 1.5 mm liner gap and a 3 mm wall,
open along the palm side for putting it on, two strap slots per strap, oval vents, hinge ears that sit
outside the palm's ear pads, and a smooth tensioner bump on top with 4 screw line clamps.
Writes build/cuff.stl and build/cuff.json"""
import json, numpy as np, trimesh, manifold3d as mf
from rlib import to_tm, smooth, frame_matrix
from sdf import Grid, sdf, to_manifold, smin, smax, seg_dist
from joints import cyl_x_span, bx, BIG
from scipy.interpolate import RegularGridInterpolator

PJ = json.load(open('build/palm.json'))
W = np.array(PJ['wrist']); EARS = PJ['ears_x']
LINER, WALL = 1.5, 3.0
Y_END = -102.0                 # elbow end
OPEN_HALF = 62.0               # deg either side of straight palm-side: open for donning
PSI_DORSAL, PSI_PALMAR = 122.0, -135.0   # wrist clearance: palm swings 25 deg up, 40 deg down
STRAPS_Y = (-36.0, -84.0); STRAP_W = 27.0
FLEX_EXITS = [PJ['line_exits_x'][i] for i in (0, 2, 4, 6)]


def main():
    arm = smooth(trimesh.load('src/right-arm-oriented.stl'), 1, 6)
    g = Grid([-34, -112, -28], [46, 10, 44], 0.4)
    f = sdf(arm, g)
    X, Y, Z = g.points()
    # forearm axis (centre of each section), for the palm-side opening
    ys = np.array([-140, -110, -100, -80, -60, -40, -20, -5.0])
    cxs = np.array([10.4, 10.4, 10.3, 9.8, 9.0, 7.8, 6.6, 5.7]); czs = np.array([0.3, 1.8, 2.5, 3.9, 5.2, 6.3, 7.0, 7.3])
    CX = np.interp(Y, ys, cxs); CZ = np.interp(Y, ys, czs)
    r_ax = np.sqrt((X - CX) ** 2 + (Z - CZ) ** 2) + 1e-6
    theta = np.degrees(np.arctan2(X - CX, -(Z - CZ)))           # 0 = straight down the palm side
    shell = smax(f - LINER - WALL, -(f - LINER), 0.6)
    # palm-side opening, elbow end and wrist end, all with rounded edges
    open_f = (OPEN_HALF - np.abs(theta)) * np.radians(1) * r_ax
    shell = smax(shell, open_f, 1.5)
    shell = smax(shell, Y_END - Y, 1.5)
    yw, zw = Y - W[1], Z - W[2]
    rw = np.sqrt(yw ** 2 + zw ** 2) + 1e-6; psi = np.degrees(np.arctan2(zw, yw))
    wedge = np.minimum(psi - PSI_PALMAR, PSI_DORSAL - psi) * np.radians(1) * rw
    shell = smax(shell, wedge, 1.5)
    # tensioner bump on top
    ax_ = g.axes(); ix = np.argmin(np.abs(ax_[0] - np.mean(FLEX_EXITS))); iy = np.argmin(np.abs(ax_[1] + 28))
    zt = float(ax_[2][np.nonzero(shell[ix, iy, :] < 0)[0].max()])          # top of the cuff wall there
    bc = np.array([np.mean(FLEX_EXITS) - 1.0, -29.0, zt + 2.0])
    q = np.stack([(X - bc[0]) / 15.0, (Y - bc[1]) / 17.5, (Z - bc[2]) / 7.0], -1)
    bump = (np.linalg.norm(q, axis=-1) - 1.0) * 7.0
    shell = smin(shell, smax(bump, -(f - LINER), 0.5), 3.0)
    # hinge ear plates outside the palm's ear pads
    for xw in EARS:
        sx = 1 if xw > W[0] else -1
        x_out = xw + sx * (2.3 + 3.4)
        hw = np.interp(Y, ys, np.array([49.3, 45.6, 44.2, 41.2, 38.4, 36.2, 34.3, 35.0]) / 2)
        sb = np.clip((-6.0 - Y) / 14.0, 0, 1); sb = sb * sb * (3 - 2 * sb)     # 0 at the ear, 1 where it joins the cuff
        x_in = (xw + sx * 2.3) * (1 - sb) + (CX + sx * (hw + LINER + WALL - 1.2)) * sb
        cap = seg_dist(np.stack([np.zeros_like(Y), yw, zw], -1), np.array([0, 0, 0.0]), np.array([0, -17.0, 0.0])) - 7.5
        plate = smax(smax(sx * (x_in - X), sx * (X - x_out), 1.4), cap, 1.8)
        shell = smin(shell, plate, 4.0)
        # keep clear of the palm's ear pad and wall: nothing inside the pad face within 9.6 of the axis
        inner = sx * (xw + sx * 2.3) - sx * X        # positive on the palm side of the plate's inner face
        shell = smax(shell, np.minimum(9.6 - rw, inner), 0.4)
    np.save('build/cuff_field.npy', shell)
    cuff = to_manifold(shell, g)
    Wm = frame_matrix(W, np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.]))
    for xw in EARS:
        sx = 1 if xw > W[0] else -1
        x_out = xw + sx * (2.3 + 3.4)
        if sx > 0:
            h = cyl_x_span(1.7, x_out - 4.5, x_out + 2) + cyl_x_span(3.1, x_out - 1.5, x_out + 5)
        else:
            h = cyl_x_span(1.7, x_out - 2, x_out + 4.5) + cyl_x_span(3.1, x_out - 5, x_out + 1.5)
        cuff = cuff - h.translate([0, W[1], W[2]])
    # tensioner: 4 line channels front to back, each pinned by an M3 x 6 screw from the top
    FS = RegularGridInterpolator(g.axes(), shell, bounds_error=False, fill_value=10)
    zc = zt + 3.6
    clamps = []
    for x in FLEX_EXITS:
        a = mf.Manifold.cylinder(40, 0.75, 0.75, 24).rotate([90, 0, 0]).translate([x, -8.0, zc])     # y -8 .. -48
        cuff = cuff - a
        zs = np.arange(zc + 12, zc, -0.05); v = FS(np.stack([np.full_like(zs, x), np.full_like(zs, -30.0), zs], 1))
        ztop = zs[np.argmax(v < 0)]
        cuff = cuff - mf.Manifold.cylinder(ztop - zc + 2.5, 1.3, 1.3, 24).translate([x, -30.0, zc - 1.3])
        clamps.append({'x': x, 'top': float(ztop), 'line_z': float(zc), 'pilot_depth': float(ztop - zc + 1.3)})
    # strap slots: one each side of the opening per strap
    def rad_frame(y, th):
        cx, cz = np.interp(y, ys, cxs), np.interp(y, ys, czs)
        nrm = np.array([np.sin(np.radians(th)), 0, -np.cos(np.radians(th))])
        return np.array([cx, y, cz]), nrm
    for ys_ in STRAPS_Y:
        for th in (OPEN_HALF + 16, -(OPEN_HALF + 16)):
            c, nrm = rad_frame(ys_, th)
            u = np.array([0, 1.0, 0]); v = np.cross(nrm, u)
            M = frame_matrix(c, u, v, nrm)
            a = mf.Manifold.cylinder(40, 2.3, 2.3, 24).translate([-STRAP_W / 2 + 2.3, 0, 0])
            b = mf.Manifold.cylinder(40, 2.3, 2.3, 24).translate([STRAP_W / 2 - 2.3, 0, 0])
            cuff = cuff - mf.Manifold.batch_hull([a, b]).transform(M)
    # oval vents on the upper sides, between the straps
    for ys_ in (-52.0, -68.0):
        for th in (130.0, -130.0, 160.0, -160.0):
            if abs(th) == 160 and ys_ > -60: continue
            c, nrm = rad_frame(ys_, th)
            u = np.array([0, 1.0, 0]); v = np.cross(nrm, u)
            cuff = cuff - mf.Manifold.cylinder(40, 1, 1, 48).scale([6.0, 3.2, 1]).transform(frame_matrix(c, u, v, nrm))
    parts = cuff.decompose(); main = max(parts, key=lambda p: p.volume())
    if len(parts) > 1: print('cuff loose bits', len(parts) - 1, round(sum(p.volume() for p in parts) - main.volume(), 1))
    to_tm(main).export('build/cuff.stl'); print('cuff vol', round(main.volume()), 'genus', main.genus())
    json.dump({'clamps': clamps, 'bump_top': zt, 'straps_y': STRAPS_Y}, open('build/cuff.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
