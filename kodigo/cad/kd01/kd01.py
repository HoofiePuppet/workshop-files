"""
Kodigo KD-01 optics test rig - parametric CadQuery model.
Designer: Hoofie Puppet. License CC BY-NC-SA 4.0.

Assembly coordinates (mm):
  +X = light direction (OLED -> lens -> splitter), Y = sideways (eye on -Y side),
  Z = up. Base-plate top is Z = 0. Optical axis is at Z = AXIS_Z, Y = 0.
  Lens centre plane is at X = 0. Scale on the base reads distance from the lens.
"""
import math, os, sys
import cadquery as cq

# ---------------- parameters ----------------
SIG_LONG = "KODIGO KD-01 HOOFIE PUPPET"   # hidden mark (placeholder wording)
SIG = "HP-KD01"                             # short hidden mark for small parts
SIG_DEPTH = 0.4

AXIS_Z = 32.0          # optical axis height above base top
M3_CLR, M3_TAP = 3.4, 2.6
M2_CLR = 2.4
CB_D, CB_DEPTH = 6.4, 3.5     # M3 counterbore

# base rail
B_X0, B_X1 = -80.0, 80.0
B_W = 64.0             # y from -32..+32
B_T = 10.0
KEY_W = 10.0
SLOT_W = M3_CLR
SLOT_X0, SLOT_X1 = -72.0, 72.0
NUT_W, NUT_T = 6.0, 6.0        # nut channel width (M3 nut 5.5 flats), height from bottom
TICK_Y0 = -21.0                # ticks run from y=-21 toward -y

# feet
FOOT_T = 8.0
KEY_H = 1.8                     # raised key on rail top
GROOVE_W, GROOVE_H = KEY_W + 0.4, KEY_H + 0.2   # groove under feet
FOOT_Y0, FOOT_Y1 = -8.0, 16.0

# lens
LENS_D = 25.0
LENS_POCKET_D = 25.6
LENS_POCKET_DEPTH = 4.5
LENS_LIP_D = 23.0
LENS_EDGE = 2.5        # guessed lens edge thickness (centre plane offset)
LENS_LIP_T = 3.5

# splitter piece (1 x 1-3/8 in)
PIECE_L, PIECE_H = 35.0, 25.0
PIECE_CLR = 0.6
FR_BORDER = 4.0
FR_LIP = 1.4
COVER_T = 1.2
PEG_D, PEG_HOLE_D = 2.4, 2.65
TAB_W, TAB_L, TAB_T = 10.0, 6.0, 3.0

# turret / pedestal
DISC_D, DISC_T = 30.0, 3.0
POCKET_D = 30.5
PED_D = 38.0
DISC_Z0 = FOOT_T - 2.0             # disc pocket floor (sunk into foot)
PED_TOP = DISC_Z0 + DISC_T          # ring top flush with disc top

# OLED carriage
GLASS_T, PCB_T, STANDOFF_H, ADAPT_T, UPR_T = 1.5, 1.6, 3.0, 3.0, 4.0
ADAPT_W, ADAPT_H = 50.0, 42.0
ADAPT_SCREW_Y = 19.5
UPR_W = 48.0
UPR_TOP = 60.0

OLEDS = {
    # name: (pcb_w, pcb_h, hole_dx, hole_dy, screw clearance)
    "13":  (35.4, 33.5, 30.4, 28.5, M2_CLR),   # 1.3" SH1106 I2C (typical, MEASURE)
    "096": (27.3, 27.8, 23.5, 23.8, M2_CLR),   # 0.96" SSD1306 I2C (typical, MEASURE)
}

# ---------------- helpers ----------------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def cyl_z(x, y, z0, h, d):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(d / 2).extrude(h)

def cyl_x(x0, y, z, L, d):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(d / 2).extrude(L)

def cyl_y(y0, x, z, L, d):
    # XZ plane normal is -Y; extrude negative to go +Y
    return cq.Workplane("XZ", origin=(0, y0, 0)).center(x, z).circle(d / 2).extrude(-L)

def text_under(x, y, zbot, txt, size, rot=0):
    """Engraving solid that reads correctly when looking at a bottom face at z=zbot."""
    pl = cq.Plane(origin=(x, y, zbot + SIG_DEPTH), xDir=(math.cos(math.radians(rot)), math.sin(math.radians(rot)), 0), normal=(0, 0, -1))
    return cq.Workplane(pl).text(txt, size, SIG_DEPTH + 0.01, kind="bold", halign="center", valign="center")

def text_on(plane_origin, xdir, normal, txt, size, depth=SIG_DEPTH):
    """Engraving solid into a face whose outward normal is `normal`."""
    o = cq.Vector(*plane_origin) - cq.Vector(*normal).normalized() * depth
    pl = cq.Plane(origin=o.toTuple(), xDir=xdir, normal=normal)
    return cq.Workplane(pl).text(txt, size, depth + 0.01, kind="bold", halign="center", valign="center")

def foot(x0, x1, screw_x, ref_x, y0=FOOT_Y0, y1=FOOT_Y1):
    """Sliding foot: plate + tongue + counterbored M3 + pointer tab at ref_x."""
    f = box(x0, x1, y0, y1, 0, FOOT_T)
    f = f.cut(box(x0 - 1, x1 + 1, -GROOVE_W / 2, GROOVE_W / 2, -0.1, GROOVE_H))
    # pointer tab reaching over the scale (thin, triangular tip at ref_x)
    tip_y = TICK_Y0 - 0.5
    tab = (cq.Workplane("XY").polyline([(ref_x - 5, y0 + 0.01), (ref_x + 5, y0 + 0.01),
                                        (ref_x + 5, tip_y + 4), (ref_x, tip_y), (ref_x - 5, tip_y + 4)])
           .close().extrude(1.6))
    f = f.union(tab)
    # engraved line on the tab top showing the exact reference
    f = f.cut(box(ref_x - 0.3, ref_x + 0.3, tip_y, y0, 1.0, 1.7))
    # screw
    f = f.cut(cyl_z(screw_x, 0, -1, FOOT_T + 2, M3_CLR))
    f = f.cut(cyl_z(screw_x, 0, FOOT_T - CB_DEPTH, CB_DEPTH + 1, CB_D))
    return f

def groove_cut(p):
    return p.cut(box(-300, 300, -GROOVE_W / 2, GROOVE_W / 2, -0.1, GROOVE_H))

# ---------------- parts ----------------
def base_rail():
    b = box(B_X0, B_X1, -B_W / 2, B_W / 2, -B_T, 0)
    b = b.edges("|Z").fillet(4)
    b = b.union(box(B_X0 + 2, B_X1 - 2, -KEY_W / 2, KEY_W / 2, -0.01, KEY_H))     # raised key
    b = b.cut(box(SLOT_X0, SLOT_X1, -SLOT_W / 2, SLOT_W / 2, -B_T - 1, KEY_H + 1))      # through slot
    b = b.cut(box(SLOT_X0 - 3, SLOT_X1 + 3, -NUT_W / 2, NUT_W / 2, -B_T - 1, -B_T + NUT_T))  # nut channel
    # scale: ticks every 1 mm from -65..+60, labels every 10 (distance from lens)
    cuts = []
    for i in range(-65, 61):
        L = 5.0 if i % 10 == 0 else (3.5 if i % 5 == 0 else 2.0)
        w = 0.6 if i % 5 == 0 else 0.45
        cuts.append(box(i - w / 2, i + w / 2, TICK_Y0 - L, TICK_Y0, -0.6, 0.1))
    for i in range(-60, 61, 10):
        t = cq.Workplane("XY", origin=(i, TICK_Y0 - 7.8, -0.6)).text(str(abs(i)), 3.6, 0.7, kind="bold",
                                                                         halign="center", valign="center")
        cuts.append(t)
    # arrows/words
    cuts.append(cq.Workplane("XY", origin=(-35, 24, -0.6)).text("SCREEN  <-  mm  ->  LENS", 3.2, 0.7, halign="center", valign="center"))
    cuts.append(cq.Workplane("XY", origin=(35, 24, -0.6)).text("LENS  ->  mm  ->  SPLITTER", 3.2, 0.7, halign="center", valign="center"))
    cuts.append(cq.Workplane("XY", origin=(0, 24, -0.6)).text("KODIGO KD-01", 3.6, 0.7, kind="bold", halign="center", valign="center"))
    for c in cuts:
        b = b.cut(c)
    # hidden mark underneath
    b = b.cut(text_under(-40, -18, -B_T, SIG_LONG, 3.0))
    return b

def lens_holder():
    lip_face = LENS_EDGE / 2                # lens centre plane at x=0
    ux0 = lip_face - LENS_POCKET_DEPTH
    ux1 = lip_face + LENS_LIP_T
    up = cq.Workplane("YZ", origin=(ux0, 0, 0)).moveTo(-18, 0).lineTo(18, 0).lineTo(18, AXIS_Z) \
        .threePointArc((0, AXIS_Z + 18), (-18, AXIS_Z)).close().extrude(ux1 - ux0)
    f = foot(-15, ux1, -10, 0.0)
    p = f.union(up)
    p = p.cut(cyl_x(ux0 - 1, 0, AXIS_Z, ux1 - ux0 + 2, LENS_LIP_D))
    p = p.cut(cyl_x(ux0 - 1, 0, AXIS_Z, LENS_POCKET_DEPTH + 1, LENS_POCKET_D))
    # finger notches to lift the lens/retainer out
    p = p.cut(cyl_x(ux0 - 1, 0, AXIS_Z + LENS_POCKET_D / 2, LENS_POCKET_DEPTH - 1 + 1, 6))
    p = groove_cut(p)
    p = p.cut(text_under(-7, 11, 0, SIG, 2.4))
    return p

def lens_retainer():
    od, idd, t, gap = LENS_POCKET_D + 0.5, 21.5, 1.6, 2.5
    r = cq.Workplane("XY").circle(od / 2).circle(idd / 2).extrude(t)
    r = r.cut(box(-gap / 2, gap / 2, 0, od, -1, t + 1))
    return r

def frame_dims(sheet_t):
    pl, ph = PIECE_L + PIECE_CLR, PIECE_H + PIECE_CLR
    ow, oh = pl + 2 * FR_BORDER, ph + 2 * FR_BORDER
    base_t = FR_LIP + sheet_t + 0.1
    return pl, ph, ow, oh, base_t

def peg_positions(sheet_t):
    pl, ph, ow, oh, _ = frame_dims(sheet_t)
    px, py = (pl / 2 + ow / 2) / 2, (ph / 2 + oh / 2) / 2
    return [(sx * px, sy * py) for sx in (-1, 1) for sy in (-1, 1)]

def splitter_frame(sheet_t):
    """Local: piece in XY (long side = X), lip at z=0..FR_LIP, pocket open toward +z."""
    pl, ph, ow, oh, base_t = frame_dims(sheet_t)
    win_l, win_h = PIECE_L - 2.0, PIECE_H - 2.0
    f = cq.Workplane("XY").rect(ow, oh).extrude(base_t).edges("|Z").fillet(2)
    f = f.cut(box(-pl / 2, pl / 2, -ph / 2, ph / 2, FR_LIP, base_t + 1))
    f = f.cut(box(-win_l / 2, win_l / 2, -win_h / 2, win_h / 2, -1, base_t + 1))
    for (x, y) in peg_positions(sheet_t):
        f = f.union(cyl_z(x, y, base_t, COVER_T, PEG_D))
    # bottom tab for the turret socket
    f = f.union(box(-TAB_W / 2, TAB_W / 2, -oh / 2 - TAB_L, -oh / 2 + 0.01, 0, TAB_T))
    # fingernail notch on top edge to pry the cover off
    f = f.cut(box(-4, 4, oh / 2 - 1.2, oh / 2 + 1, base_t - 0.8, base_t + 1))
    # hidden mark: on the tab back face (inside the socket when assembled)
    f = f.cut(text_on((0, -oh / 2 - TAB_L / 2 - 0.3, 0), (1, 0, 0), (0, 0, -1), "HP", 2.6))
    return f

def splitter_cover(sheet_t):
    pl, ph, ow, oh, base_t = frame_dims(sheet_t)
    win_l, win_h = PIECE_L - 2.0, PIECE_H - 2.0
    c = cq.Workplane("XY").rect(ow, oh).extrude(COVER_T).edges("|Z").fillet(2)
    c = c.cut(box(-win_l / 2, win_l / 2, -win_h / 2, win_h / 2, -1, COVER_T + 1))
    for (x, y) in peg_positions(sheet_t):
        c = c.cut(cyl_z(x, y, -1, COVER_T + 2, PEG_HOLE_D))
    return c

def turret(sheet_t=1.5):
    """Local: disc centred on origin, z=0..DISC_T; socket long axis along X."""
    _, _, _, _, base_t = frame_dims(sheet_t)
    sock_t = TAB_T + 0.35   # same tab on both frames
    t = cq.Workplane("XY").circle(DISC_D / 2).extrude(DISC_T)
    boss_top = DISC_T + 6.0
    t = t.union(box(-(TAB_W / 2 + 2.5), TAB_W / 2 + 2.5, -(sock_t / 2 + 2.2), sock_t / 2 + 2.2, DISC_T - 0.01, boss_top))
    t = t.cut(box(-(TAB_W + 0.4) / 2, (TAB_W + 0.4) / 2, -sock_t / 2, sock_t / 2, DISC_T + 0.2, boss_top + 1))
    # pointer line on disc top along the socket (= splitter plane) both ends
    for s in (-1, 1):
        t = t.cut(box(min(s * 9, s * 14.6), max(s * 9, s * 14.6), -0.35, 0.35, DISC_T - 0.5, DISC_T + 0.1))
    # grip knurls on the edge
    for k in range(24):
        a = 2 * math.pi * k / 24
        t = t.cut(cyl_z(DISC_D / 2 * math.cos(a), DISC_D / 2 * math.sin(a), -1, DISC_T + 2, 1.2))
    t = t.cut(text_under(0, 7.5, 0, SIG, 2.4))
    return t, boss_top

def splitter_foot():
    """Local: pivot at x=0 (pointer), foot along X."""
    f = foot(-20, 30, 24.5, 0.0)
    ped = cyl_z(0, 0, 0, PED_TOP, PED_D)
    f = f.union(ped)
    f = f.union(box(-4.5, 4.5, 0, 24, 0, PED_TOP))                          # lock-screw boss (+Y)
    f = f.cut(cyl_z(0, 0, DISC_Z0, PED_TOP, POCKET_D))
    f = f.cut(cyl_y(10, 0, DISC_Z0 + DISC_T / 2, 20, M3_TAP))               # radial M3 thread-forming hole
    # re-cut the clamp screw (pedestal may cover nothing, but keep tidy)
    f = f.cut(cyl_z(24.5, 0, -1, PED_TOP + 3, M3_CLR))
    # degree marks on ring top around -45 deg (front-right), 5 deg steps
    r0, r1 = POCKET_D / 2 + 0.6, PED_D / 2 - 0.4
    for k in range(-3, 4):
        a = math.radians(-45 + 5 * k)
        L = r1 - r0 if k == 0 else (r1 - r0) * 0.55
        w = 0.7 if k == 0 else 0.45
        mark = box(r0, r0 + L, -w / 2, w / 2, PED_TOP - 0.5, PED_TOP + 0.1).rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        f = f.cut(mark)
    f = groove_cut(f)
    f = f.cut(text_under(-12, 11, 0, SIG, 2.4))
    return f

def oled_carriage():
    """Local: x=0 is the OLED glass front face (pointer)."""
    x_adapt_front = -(GLASS_T + PCB_T + STANDOFF_H)
    x_upr_front = x_adapt_front - ADAPT_T
    x_upr_back = x_upr_front - UPR_T
    f = foot(-26, 1.0, -19.5, 0.0)
    u = box(x_upr_back, x_upr_front, -UPR_W / 2, UPR_W / 2, 0, UPR_TOP)
    u = u.edges("|X").fillet(3)
    p = f.union(u)
    p = p.cut(box(x_upr_back - 1, x_upr_front + 1, -14, 14, 18, UPR_TOP - 3))           # wire window
    for s in (-1, 1):
        p = p.cut(cq.Workplane("YZ", origin=(x_upr_back - 1, 0, 0)).center(s * ADAPT_SCREW_Y, AXIS_Z)
                  .slot2D(12 + M3_CLR, M3_CLR, 90).extrude(UPR_T + 2))
    p = groove_cut(p)
    p = p.cut(text_under(-10, 11, 0, SIG, 2.4))
    return p, x_adapt_front

def oled_adapter(kind):
    """Local: plate in YZ, front face (toward lens) at x=0, centred on axis (y=0,z=0)."""
    pcb_w, pcb_h, hdx, hdy, clr = OLEDS[kind]
    a = box(-ADAPT_T, 0, -ADAPT_W / 2, ADAPT_W / 2, -ADAPT_H / 2, ADAPT_H / 2).edges("|X").fillet(3)
    for sy in (-1, 1):
        for sz in (-1, 1):
            y, z = sy * hdx / 2, sz * hdy / 2
            ang = math.degrees(math.atan2(z, y))
            boss = (cq.Workplane("YZ", origin=(0, 0, 0)).center(y, z).slot2D(6 + 5.5, 5.5, ang).extrude(STANDOFF_H))
            a = a.union(boss)
            a = a.cut(cq.Workplane("YZ", origin=(-ADAPT_T - 1, 0, 0)).center(y, z)
                      .slot2D(4 + clr, clr, ang).extrude(ADAPT_T + STANDOFF_H + 2))
    a = a.cut(box(-ADAPT_T - 1, 1, -9, 9, 9, 17.0))                                 # header pins window (top)
    for s in (-1, 1):
        a = a.cut(cq.Workplane("YZ", origin=(-ADAPT_T - 1, 0, 0)).center(s * ADAPT_SCREW_Y, 0)
                  .slot2D(3 + M3_CLR, M3_CLR, 0).extrude(ADAPT_T + 2))
    # label on the back (visible), hidden mark on the front under the board
    lbl = '1.3"' if kind == "13" else '0.96"'
    a = a.cut(text_on((-ADAPT_T, 0, -15), (0, -1, 0), (-1, 0, 0), lbl + " TOP ^", 3.0))
    a = a.cut(text_on((0, 0, -4), (0, 1, 0), (1, 0, 0), SIG, 2.4))
    return a

# ---------------- build + export ----------------
def place_frame(fr, S, sheet_t, turret_boss_top):
    _, _, ow, oh, base_t = frame_dims(sheet_t)
    # centre base thickness on pivot; tab bottom sits on socket floor (DISC_T+0.2) on top of foot
    f = fr.translate((0, 0, -TAB_T / 2))
    f = f.rotate((0, 0, 0), (1, 0, 0), 90)            # y->z, z->-y ; normal now -Y
    tab_bottom_local = -oh / 2 - TAB_L
    f = f.translate((0, 0, DISC_Z0 + DISC_T + 0.2 - tab_bottom_local))
    f = f.rotate((0, 0, 0), (0, 0, 1), -45)
    return f.translate((S, 0, 0))

def build(outdir, D=36.0, S=30.0):
    os.makedirs(outdir, exist_ok=True)
    parts = {}
    parts["KD01-A_base_rail"] = base_rail()
    parts["KD01-B_lens_holder"] = lens_holder()
    parts["KD01-C_lens_retainer_ring"] = lens_retainer()
    parts["KD01-D1_splitter_frame_acrylic1.5"] = splitter_frame(1.5)
    parts["KD01-D2_splitter_frame_filmonly"] = splitter_frame(0.3)
    parts["KD01-E1_splitter_cover_acrylic1.5"] = splitter_cover(1.5)
    parts["KD01-E2_splitter_cover_filmonly"] = splitter_cover(0.3)
    tur, boss_top = turret()
    parts["KD01-F_splitter_turret"] = tur
    parts["KD01-G_splitter_foot"] = splitter_foot()
    car, x_adapt = oled_carriage()
    parts["KD01-H_oled_carriage"] = car
    parts["KD01-J1_oled_adapter_1.3in"] = oled_adapter("13")
    parts["KD01-J2_oled_adapter_0.96in"] = oled_adapter("096")

    # assembly (for preview / interference checks)
    asm = {
        "base": parts["KD01-A_base_rail"],
        "lens": parts["KD01-B_lens_holder"],
        "sfoot": parts["KD01-G_splitter_foot"].translate((S, 0, 0)),
        "turret": tur.rotate((0, 0, 0), (0, 0, 1), -45).translate((S, 0, DISC_Z0)),
        "frame": place_frame(parts["KD01-D1_splitter_frame_acrylic1.5"], S, 1.5, boss_top),
        "carriage": car.translate((-D, 0, 0)),
        "adapter": parts["KD01-J1_oled_adapter_1.3in"].translate((x_adapt - D, 0, AXIS_Z)),
    }
    return parts, asm

PRINT_ORIENT = {
    # rotations (axis, deg) applied so the best face is on the bed
    "KD01-B_lens_holder": [((0, 1, 0), 90)],       # lip face on bed, pocket opens up
    # carriage, feet, base, turret: print as assembled (flat bottom)
    "KD01-J1_oled_adapter_1.3in": [((0, 1, 0), -90)],   # back face down, standoffs up
    "KD01-J2_oled_adapter_0.96in": [((0, 1, 0), -90)],
}

def export_all(parts, outdir):
    for name, p in parts.items():
        s = p
        for ax, deg in PRINT_ORIENT.get(name, []):
            s = s.rotate((0, 0, 0), ax, deg)
        bb = s.val().BoundingBox()
        s = s.translate((-bb.center.x, -bb.center.y, -bb.zmin))
        cq.exporters.export(s, os.path.join(outdir, name + ".stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(s, os.path.join(outdir, name + ".step"))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    parts, asm = build(out)
    export_all(parts, out)
    for n, p in asm.items():
        cq.exporters.export(p, os.path.join(out, "_asm_" + n + ".stl"), tolerance=0.05, angularTolerance=0.3)
    print("ok")
