"""
Kodigo KD-05 companion glasses frame - parametric CadQuery model.
Designer: Hoofie Puppet. License CC BY-NC-SA 4.0.

Wear coordinates (mm): X = across (+X = wearer's RIGHT), Y = up, Z = toward the ears.
Front face of the frame at Z = 0.
"""
import math, os, sys
import cadquery as cq

# ---- size (52-18-140) ----
LENS_W, BRIDGE, ARM_L = 50.0, 20.0, 140.0
LENS_H = 42.0
N_TOP, N_BOT = 3.0, 2.3  # superellipse exponents: flatter brow, rounder bottom (panto)
RIM = 3.6                # rim border width (thinner = softer look)
FRONT_T = 4.0            # front thickness (Z)

# ---- hinge ----
PIN_D_FRONT, PIN_D_ARM = 1.8, 1.95   # 1.75 mm filament pin: snug in front, free in arm
HY0, HY1 = 12.0, 21.0               # hinge block height range (Y) - top corners
_HC = (HY0 + HY1) / 2
BAND = (_HC - 1.7, _HC + 1.7)        # middle slot (arm knuckle) Y range in the lug
ARM_KN = (_HC - 1.5, _HC + 1.5)      # arm knuckle Y range
KN_R = 3.0                           # arm knuckle radius
LUG_Z0 = 5.8                         # slot starts behind this Z
AXIS_Z = 9.5

# ---- arms ----
ARM_T = 4.0
ARM_H_FRONT, ARM_H_BACK = 7.0, 5.0
BEND_AT = 100.0          # straight length from hinge axis
BEND_ANG = 35.0          # ear bend, degrees down

# ---- Kodigo rail v1 (shared with KD-04 clip-on) ----
RAIL_Z0, RAIL_Z1 = 16.0, 56.0
RAIL_BASE_W, RAIL_TOP_W, RAIL_H = 5.0, 7.0, 2.0
RAIL_ZONE_H = 10.0       # right arm is taller where the rail is

SIG = "HP-KD05"
SIG_DEPTH = 0.4

# derived
OPEN_CX = BRIDGE / 2 + LENS_W / 2
OUT_W, OUT_H = LENS_W + 2 * RIM, LENS_H + 2 * RIM
HINGE_X = OPEN_CX + OUT_W / 2 + 1.5    # hinge axis X (right side)
HY_C = (HY0 + HY1) / 2


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_y(x, z, y0, y1, d):
    return cq.Workplane("XZ", origin=(0, y0, 0)).center(x, z).circle(d / 2).extrude(-(y1 - y0))


def rrect(cx, cy, w, h, r, z0, z1):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(cx, cy).rect(w, h).extrude(z1 - z0).edges("|Z").fillet(r)


def engrave(origin, xdir, normal, txt, size):
    o = cq.Vector(*origin) - cq.Vector(*normal).normalized() * SIG_DEPTH
    pl = cq.Plane(origin=o.toTuple(), xDir=xdir, normal=normal)
    return cq.Workplane(pl).text(txt, size, SIG_DEPTH + 0.01, kind="bold", halign="center", valign="center")


def lug(side):
    """Hinge lug on the front; side=+1 right, -1 left. Built for right then mirrored."""
    hx = HINGE_X
    L = box(hx - 3.5, hx + 3.5, HY0, HY1, 0, AXIS_Z + 3.5)
    L = L.cut(box(hx - 5, hx + 5, BAND[0], BAND[1], LUG_Z0, 30))                 # slot for arm knuckle
    # round the inner-back corner so the arm can fold inward
    corner = box(hx - 6, hx, HY0 - 1, HY1 + 1, AXIS_Z, AXIS_Z + 6).cut(cyl_y(hx, AXIS_Z, HY0 - 2, HY1 + 2, 7.0))
    L = L.cut(corner)
    L = L.cut(cyl_y(hx, AXIS_Z, HY0 - 1, HY1 + 1, PIN_D_FRONT))
    # endpiece joining lug to the rim
    # endpiece joining lug to the rim (right side, where the HUD hangs, is beefier)
    ep_y0 = HY0 - (2.0 if side > 0 else 0.0)
    ep = box(OPEN_CX + OUT_W / 2 - 9, hx + 3.5, ep_y0, HY1, 0, FRONT_T + (1.0 if side > 0 else 0.0))
    try:
        ep = ep.edges("|Z").fillet(1.5)
    except Exception:
        pass
    L = L.union(ep.cut(outline_solid(opening_pts(OPEN_CX, 0.0), -1, FRONT_T + 3)))
    if side < 0:
        L = L.mirror("YZ")
    return L


def opening_pts(cx, grow=0.0, n=160):
    """Panto/round lens outline (superellipse), optionally grown outward by `grow`."""
    a, bb = LENS_W / 2 + grow, LENS_H / 2 + grow
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s_ = math.cos(t), math.sin(t)
        e = N_TOP if s_ > 0 else N_BOT
        x = a * math.copysign(abs(c) ** (2 / e), c)
        y = bb * math.copysign(abs(s_) ** (2 / e), s_)
        pts.append((cx + x, y))
    return pts


def outline_solid(pts, z0, z1):
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(z1 - z0)


def inner_edge_x(y):
    """x of the nose-side edge of the right opening at height y."""
    a, bb = LENS_W / 2, LENS_H / 2
    e = N_TOP if y > 0 else N_BOT
    sy = min(abs(y) / bb, 0.999)
    # |y/b|^(e/2) = |sin t|  -> |cos t| = sqrt(1-sin^2);  x = a*|cos t|^(2/e)
    st = sy ** (e / 2)
    ct = math.sqrt(max(0.0, 1 - st * st))
    return OPEN_CX - a * ct ** (2 / e)


ARCH_Y0, ARCH_RISE, ARCH_HALF = 6.0, 5.5, 2.3


def arch_xin():
    return inner_edge_x(6.0) + 0.8


def arch_yc(x):
    u = x / arch_xin()
    return ARCH_Y0 + ARCH_RISE * (1 - u * u)


# ---- snap-in nose piece ----
PEG_X, PEG_D, PEG_H = 4.5, 2.0, 2.6
PEG_HOLE_D, PEG_HOLE_DEPTH = 2.15, 2.9
NOSE_WALL = 2.4
NOSE_FRONTAL = 22.0       # nose side angle from vertical, front view (deg)
NOSE_SPLAY = 35.0         # nose side angle from straight-back, top view (deg)
NOSE_SIZES = {            # nose width 10 mm below the ridge (full width)
    "narrow": 15.0, "medium": 17.0, "wide": 19.0}
NOSE_HEIGHTS = {          # (tunnel top y at the frame, saddle depth) ; lower top = frame rides higher
    "standard": (5.0, 8.0), "lowbridge": (1.5, 11.0)}


def keyhole_bridge():
    x_in = arch_xin()                        # where the bridge meets the rims
    pts_top, pts_bot = [], []
    n = 30
    for i in range(n + 1):
        x = (-1 + 2 * i / n) * x_in
        pts_top.append((x, arch_yc(x) + ARCH_HALF))
        pts_bot.append((x, arch_yc(x) - ARCH_HALF))
    return cq.Workplane("XY").polyline(pts_top + pts_bot[::-1]).close().extrude(FRONT_T)


def front():
    f = None
    for sx in (-1, 1):
        o = outline_solid(opening_pts(sx * OPEN_CX, RIM), 0, FRONT_T)
        f = o if f is None else f.union(o)
    f = f.union(keyhole_bridge())
    for sx in (-1, 1):
        f = f.cut(outline_solid(opening_pts(sx * OPEN_CX, 0.0), -1, FRONT_T + 1))
    # pegs on the bridge back for the snap-in nose piece
    for sx in (-1, 1):
        px = sx * PEG_X
        f = f.union(cq.Workplane("XY", origin=(0, 0, FRONT_T - 0.01)).center(px, arch_yc(abs(px))).circle(PEG_D / 2).extrude(PEG_H)
                    .faces(">Z").edges().chamfer(0.3))
    for sx in (-1, 1):
        f = f.union(lug(sx))
    try:
        f = f.faces("<Z").edges().fillet(0.8)
    except Exception:
        pass
    # hidden mark: back face, lower LEFT rim
    f = f.cut(engrave((-OPEN_CX, -LENS_H / 2 - RIM / 2, FRONT_T), (-1, 0, 0), (0, 0, 1), SIG, 2.2))
    return f


def nose_outline(hw0, top, bottom, n_top=14):
    """Inverted-U nose silhouette (front view): rounded top, sides at NOSE_FRONTAL."""
    t = math.tan(math.radians(NOSE_FRONTAL))
    pts = []
    for i in range(n_top + 1):
        x = -hw0 + 2 * hw0 * i / n_top
        pts.append((x, top - 1.6 * (x / hw0) ** 2))
    yb = top - 1.6
    pts.append((hw0 + (yb - bottom) * t, bottom))
    pts.append((-(hw0 + (yb - bottom) * t), bottom))
    # reorder: left-bottom -> top curve -> right-bottom (closed by polyline)
    return [pts[-1]] + pts[:n_top + 1] + [pts[-2]]


def loft_outline(p_front, p_back, z0, z1):
    w0 = cq.Wire.makePolygon([cq.Vector(x, y, z0) for x, y in p_front], close=True)
    w1 = cq.Wire.makePolygon([cq.Vector(x, y, z1) for x, y in p_back], close=True)
    return cq.Workplane("XY").add(cq.Solid.makeLoft([w0, w1], True))


def nose_piece(width, height):
    """Snap-in saddle; front face sits on the bridge back (z = FRONT_T)."""
    w10 = NOSE_SIZES[width]
    y_top, depth = NOSE_HEIGHTS[height]
    t = math.tan(math.radians(NOSE_FRONTAL))
    hw0 = w10 / 2 - 10 * t
    dx = depth * math.tan(math.radians(NOSE_SPLAY))   # widening toward the face
    rise = depth * 0.45                                # nasal bridge rises toward the forehead
    z0, z1 = FRONT_T, FRONT_T + depth
    y_bot = y_top - 14.0
    outer = loft_outline(nose_outline(hw0 + NOSE_WALL, y_top + NOSE_WALL, y_bot),
                         nose_outline(hw0 + NOSE_WALL + dx, y_top + NOSE_WALL + rise, y_bot), z0, z1)
    # tab behind the bridge carrying the peg holes (hidden behind the arch from the front)
    xt = PEG_X + 3.0
    pts = [(-xt, y_top)]
    for i in range(21):
        x = -xt + 2 * xt * i / 20
        pts.append((x, arch_yc(abs(x)) + ARCH_HALF - 0.4))
    pts.append((xt, y_top))
    tab = cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(3.4)
    p = outer.union(tab)
    tunnel = loft_outline(nose_outline(hw0, y_top, y_bot - 20),
                          nose_outline(hw0 + dx + 0.6, y_top + rise, y_bot - 20), z0 - 0.5, z1 + 0.5)
    p = p.cut(tunnel)
    for sx in (-1, 1):
        px = sx * PEG_X
        p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 0.1)).center(px, arch_yc(PEG_X)).circle(PEG_HOLE_D / 2).extrude(PEG_HOLE_DEPTH + 0.1))
    try:
        p = p.faces(">Z").edges().fillet(0.8)
    except Exception as e:
        print("nose fillet skipped", e)
    # size code + hidden mark on the front face (against the frame, unseen), both inside the solid tab
    code = width[0].upper() + ("-LB" if height == "lowbridge" else "")
    y_a = arch_yc(0) + ARCH_HALF - 0.4          # top edge of the tab
    y_b = y_top + 0.3                            # top of the tunnel
    hp_y = y_b + (y_a - y_b) * 0.66
    code_y = y_b + (y_a - y_b) * 0.28
    p = p.cut(engrave((0, hp_y, z0), (-1, 0, 0), (0, 0, -1), "HP", 1.7))
    p = p.cut(engrave((0, code_y, z0), (-1, 0, 0), (0, 0, -1), code, 1.4))
    return p


def arm_profile_solid(x0, x1, rail):
    """Side-profile arm (YZ) extruded across X from x0..x1. Right-arm coordinates."""
    hz = AXIS_Z
    z_full = hz + 4.5          # full height starts here (clear of lug when folding)
    z_bend = hz + BEND_AT
    z_tip_len = ARM_L - BEND_AT
    yc = HY_C
    pts = [(z_full, yc + ARM_H_FRONT / 2), (z_bend, yc + ARM_H_BACK / 2),
           (z_bend, yc - ARM_H_BACK / 2), (z_full, yc - ARM_H_FRONT / 2)]
    wp = cq.Workplane("YZ", origin=(x0, 0, 0))
    body = wp.polyline([(y, z) for (z, y) in pts]).close().extrude(x1 - x0)
    # ear bend
    a = math.radians(BEND_ANG)
    ez, ey = z_bend + z_tip_len * math.cos(a), yc - z_tip_len * math.sin(a)
    nz, ny = math.sin(a) * ARM_H_BACK / 2, math.cos(a) * ARM_H_BACK / 2
    tip = [(z_bend + nz * 0, yc + ARM_H_BACK / 2), (ez + nz, ey + ny), (ez - nz, ey - ny), (z_bend, yc - ARM_H_BACK / 2)]
    body = body.union(cq.Workplane("YZ", origin=(x0, 0, 0)).polyline([(y, z) for (z, y) in tip]).close().extrude(x1 - x0))
    body = body.union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(yc, z_bend).circle(ARM_H_BACK / 2).extrude(x1 - x0))
    body = body.union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(ey, ez).circle(ARM_H_BACK / 2 + 0.3).extrude(x1 - x0))
    try:
        body = body.edges("not |X").fillet(1.2)
    except Exception as e:
        print("arm fillet skipped:", e)
    if rail:
        # taller zone under the rail, blending back to normal height
        zone = (cq.Workplane("YZ", origin=(x0, 0, 0))
                .polyline([(yc + RAIL_ZONE_H / 2, z_full), (yc + RAIL_ZONE_H / 2, RAIL_Z1 + 2),
                           (yc + ARM_H_FRONT / 2 - 0.4, RAIL_Z1 + 16), (yc - ARM_H_FRONT / 2 + 0.4, RAIL_Z1 + 16),
                           (yc - RAIL_ZONE_H / 2, RAIL_Z1 + 2), (yc - RAIL_ZONE_H / 2, z_full)]).close().extrude(x1 - x0))
        try:
            zone = zone.edges("not |X").fillet(1.2)
        except Exception as e:
            print("zone fillet skipped:", e)
        body = body.union(zone)
    return body


def arm(rail):
    hx = HINGE_X
    x0, x1 = hx - ARM_T / 2, hx + ARM_T / 2
    a = arm_profile_solid(x0, x1, rail)
    # knuckle band joining hinge to body
    a = a.union(box(x0, x1, ARM_KN[0], ARM_KN[1], AXIS_Z, AXIS_Z + 5.0))
    a = a.union(cyl_y(hx, AXIS_Z, ARM_KN[0], ARM_KN[1], 2 * KN_R))
    # open-stop: square the outer-front quadrant of the knuckle (hits the lug when opened past straight)
    a = a.union(box(hx, x1, ARM_KN[0], ARM_KN[1], LUG_Z0 + 0.25, AXIS_Z))
    a = a.cut(cyl_y(hx, AXIS_Z, ARM_KN[0] - 1, ARM_KN[1] + 1, PIN_D_ARM))
    if rail:
        yc = HY_C
        prof = [(yc - RAIL_BASE_W / 2, 0), (yc + RAIL_BASE_W / 2, 0), (yc + RAIL_TOP_W / 2, RAIL_H), (yc - RAIL_TOP_W / 2, RAIL_H)]
        # dovetail on the outer face (+X), running along Z
        d = (cq.Workplane("XY", origin=(0, 0, RAIL_Z0))
             .polyline([(x1 - 0.01 + h, y) for (y, h) in prof]).close().extrude(RAIL_Z1 - RAIL_Z0))
        a = a.union(d)
        # front stop for the module
        a = a.union(box(x1 - 0.01, x1 + RAIL_H + 1.0, yc - RAIL_ZONE_H / 2, yc + RAIL_ZONE_H / 2, RAIL_Z0 - 2.5, RAIL_Z0))
        # detent bump near the back end of the rail (module snaps over it)
        a = a.union(box(x1 + RAIL_H - 0.2, x1 + RAIL_H + 0.5, yc - 2.5, yc + 2.5, RAIL_Z1 - 3.6, RAIL_Z1 - 2.6).edges("|Y").chamfer(0.3))
    # hidden mark on the inner face near the ear (against the head)
    z_m = AXIS_Z + 80
    a = a.cut(engrave((x0, HY_C, z_m), (0, 0, -1), (-1, 0, 0), SIG, 2.4))
    return a


def build():
    parts = {
        "KD05-A_front": front(),
        "KD05-B_arm_right_rail": arm(True),
        "KD05-C_arm_left": arm(False).mirror("YZ"),
    }
    for w in NOSE_SIZES:
        for h in NOSE_HEIGHTS:
            parts["KD05-D_nose_%s_%s" % (w, h)] = nose_piece(w, h)
    return parts


def print_pose(name, p):
    if name == "KD05-A_front":
        s = p                                   # front face down (Z=0 on bed)
    elif name == "KD05-B_arm_right_rail":
        s = p.rotate((0, 0, 0), (0, 1, 0), -90)  # inner face down, rail up
    elif name.startswith("KD05-D"):
        s = p                                   # front face (against bridge) down
    else:
        s = p.rotate((0, 0, 0), (0, 1, 0), 90)  # left arm lying on its side
    bb = s.val().BoundingBox()
    s = s.translate((-bb.center.x, -bb.center.y, -bb.zmin))
    if name.startswith("KD05-B") or name.startswith("KD05-C"):
        # the ear tip bends ~1 mm past the flat inner face and would be the only thing touching the bed
        # (everything else floats, so slicers ask for supports). Trim it so the flat face sits on the bed.
        bb = s.val().BoundingBox()
        mid = cq.Workplane("XY").box(bb.xlen - 30.0, bb.ylen + 2, bb.zlen + 2, centered=(True, True, False)).translate((0, 0, -1))
        zflat = s.intersect(mid).val().BoundingBox().zmin
        if zflat > 0.05:
            keep = cq.Workplane("XY").box(bb.xlen + 2, bb.ylen + 2, bb.zlen + 2, centered=(True, True, False)).translate((0, 0, zflat))
            s = s.intersect(keep).translate((0, 0, -zflat))
    return s


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    parts = build()
    for n, p in parts.items():
        cq.exporters.export(print_pose(n, p), os.path.join(out, n + ".stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(p, os.path.join(out, "_asm_" + n + ".stl"), tolerance=0.05, angularTolerance=0.3)
    print("ok")
