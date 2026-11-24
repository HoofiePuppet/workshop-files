"""
Kodigo KD-07 carrying case - parametric CadQuery model.
Designer: Hoofie Puppet. License CC BY-NC-SA 4.0.

Parts (print each once):
  KD07-A_case_base   rigid box (PETG/PLA), open top up, with hinge knuckles and two rubber-band lugs
  KD07-B_case_lid    rigid lid (PETG/PLA), print TOP FACE DOWN: big logo-chip pocket, hinge knuckles, two rubber-band lugs, finger-lift tab
  KD07-C_tpu_insert  soft insert (TPU): pockets shaped like the glasses (arms folded), the KD-06 bracelet,
                     spare nose pieces and a coil of USB-C cable
  KD07-D_logo_chip   two-colour logo chip (the bracelet logo scaled up, reads left-to-right on the lid)
Hinge pin: ONE piece of 1.75 mm filament, about 90 mm long, through all 5 knuckles (trim flush).

Coordinates (mm): X across, Y front(-) to back(+, hinge side), Z up. Base bottom is Z = 0.
Needs the sibling scripts ../kd05/kd05.py and ../kd06/kd06.py (the pockets are cut from the real parts).
"""
import math, os, sys
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("kd05", "kd06"):
    p = os.path.join(HERE, "..", sub)
    if p not in sys.path:
        sys.path.insert(0, p)
import kd05, kd06

# ---------------- parameters ----------------
WALL = 2.4
FLOOR = 2.4
CLR = 0.3                    # gap between the insert and the base walls, per side
POCKET_CLR = 0.6             # clearance around each shaped pocket
EDGE = 7.0                   # insert edge margin
GAP = 8.0                    # space between pockets
CORNER_R = 6.0

INS_FLOOR = 3.0              # TPU under the deepest pockets
INS_POCKET = 14.0            # pocket depth (items stick out above; the lid clears them)
INS_H = INS_FLOOR + INS_POCKET
INNER_H = 34.0               # inside height of the base (tallest item: folded arm at about 30 mm)
BH = FLOOR + INNER_H         # rim height of the base

LID_T = 8.0                  # lid plate thickness (also the thickness of the lid lugs)
LIP_H, LIP_W, LIP_CLR = 4.0, 1.6, 0.4   # alignment lip that drops into the base

# hinge
KN_R = 3.0                   # knuckle radius
PIN_D_BASE, PIN_D_LID = 1.8, 1.95
KN_L, KN_GAP = 18.0, 0.5     # knuckle length, gap between knuckles

# rubber-band lugs (front wall): one pair (lid lug + box lug) at each of x = +/-LUG_X
LUG_X = 42.0                 # distance of each pair from the centre
LUG_W, LUG_D = 20.0, 16.0    # lug width (X) and how far it sticks out of the wall (Y)
LUG_TIP = 6.0                # box-lug thickness at the tip (the 45 degree gusset under it makes it thicker at the wall)
LUG_HOLE = 7.0               # eyelet hole for the band
LUG_HOLE_OFF = 9.5           # hole centre, measured out from the wall
LUG_DROP = 14.4              # top face of the box lug sits this far below the rim (band stretches across this)
PULL_W, PULL_D = 26.0, 10.0  # finger-lift tab on the lid, front centre

# logo chip pocket (same size as the KD-06 lid)
CHIP_SCALE = 2.5             # logo chip = the bracelet chip x this (32 x 16 mm -> 80 x 40 mm)
CHIP_W, CHIP_H = kd06.CHIP_W * CHIP_SCALE, kd06.CHIP_H * CHIP_SCALE
CHIP_CLR, POCKET_DEPTH = kd06.CHIP_CLR, kd06.POCKET_DEPTH

# contents
RING_OD, RING_ID = 66.0, 42.0      # USB-C cable coil groove
SPARE_W, SPARE_D = 44.0, 26.0      # spare nose pieces (stack 2 or 3)
# KD-02 module pocket: PLACEHOLDER size until KD-02 is designed. Change these 3 numbers and reprint only the insert.
MOD_W, MOD_D, MOD_H = 60.0, 40.0, 30.0   # module footprint (X, Y) and height; keep MOD_H - 14 < 17 (headroom)

SIG = "HP-KD07-26"
SIG_DEPTH = 0.4


# ---------------- helpers ----------------
def rr(w, h, r, z0, z1, cx=0.0, cy=0.0):
    return (cq.Workplane("XY", origin=(0, 0, z0)).center(cx, cy).rect(w, h)
            .extrude(z1 - z0).edges("|Z").fillet(r))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_z(x, y, z0, z1, d):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(d / 2).extrude(z1 - z0)


def cyl_x(x0, x1, y, z, d):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(d / 2).extrude(x1 - x0)


def prism_x(pts_yz, x0, x1):
    """Polygon given in (y, z), extruded along X from x0 to x1."""
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts_yz).close().extrude(x1 - x0)


def engrave_up(origin, txt, size):
    o = (origin[0], origin[1], origin[2] - SIG_DEPTH)
    return cq.Workplane(cq.Plane(origin=o, xDir=(1, 0, 0), normal=(0, 0, 1))).text(
        txt, size, SIG_DEPTH + 0.01, kind="bold", halign="center", valign="center")


def engrave_down(origin, txt, size):
    """Text cut into a downward-facing surface at origin (reads when viewed from below)."""
    o = (origin[0], origin[1], origin[2] - 0.01)
    return cq.Workplane(cq.Plane(origin=o, xDir=(-1, 0, 0), normal=(0, 0, 1))).text(
        txt, size, SIG_DEPTH + 0.01, kind="bold", halign="center", valign="center")


# ---------------- silhouettes of the real parts (foam-style pockets) ----------------
def _mesh_of(solid, tol=0.05):
    import tempfile, trimesh
    f = tempfile.mktemp(suffix=".stl")
    cq.exporters.export(solid, f, tolerance=tol, angularTolerance=0.3)
    m = trimesh.load(f)
    os.remove(f)
    return m


def silhouette(solids, grow=POCKET_CLR):
    """XY footprint (shapely) of the solids, grown by `grow`."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = []
    for s in solids:
        m = _mesh_of(s)
        for tri in m.triangles:
            p = Polygon(tri[:, :2])
            if p.area > 1e-6:
                polys.append(p)
    g = unary_union(polys).buffer(grow, join_style=1).simplify(0.12)
    return g


def poly_solid(geom, z0, z1):
    """shapely Polygon / MultiPolygon -> CadQuery solid (holes stay as islands of material)."""
    geoms = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
    out = None
    for g in geoms:
        s = cq.Workplane("XY", origin=(0, 0, z0)).polyline(list(g.exterior.coords)[:-1]).close().extrude(z1 - z0)
        for ring in g.interiors:
            isl = cq.Workplane("XY", origin=(0, 0, z0 - 0.1)).polyline(list(ring.coords)[:-1]).close().extrude(z1 - z0 + 0.2)
            s = s.cut(isl)
        out = s if out is None else out.union(s)
    return out


def folded_glasses():
    """Glasses lying front-down, arms folded (right arm 90 deg, left arm ~82 deg, resting on top)."""
    P = kd05.build()
    hx, az = kd05.HINGE_X, kd05.AXIS_Z
    right = P["KD05-B_arm_right_rail"].rotate((hx, 0, az), (hx, 1, az), -90)
    left = P["KD05-C_arm_left"].rotate((-hx, 0, az), (-hx, 1, az), 82)
    return [P["KD05-A_front"], right, left, P["KD05-D_nose_medium_standard"]]


def bracelet_parts():
    return [kd06.base(), kd06.lid()]


def layout():
    """Work out the insert size and where every pocket goes. Returns a dict."""
    from shapely import affinity
    g_sil = silhouette(folded_glasses())
    b_sil = affinity.rotate(silhouette(bracelet_parts()), 90, origin=(0, 0))   # lay it along X to save depth
    gx0, gy0, gx1, gy1 = g_sil.bounds
    bx0, by0, bx1, by1 = b_sil.bounds
    gw, gd = gx1 - gx0, gy1 - gy0
    bw, bd = bx1 - bx0, by1 - by0
    col_w = max(bw, MOD_W)
    col_h = max(RING_OD + GAP + SPARE_D, bd + GAP + MOD_D)
    row2_w = RING_OD + GAP + col_w
    row2_h = col_h
    IW = max(gw, row2_w) + 2 * EDGE
    ID = EDGE + gd + GAP + row2_h + EDGE
    top_y = ID / 2 - EDGE                        # back edge of the glasses pocket
    g_cx, g_cy = 0.0, top_y - gd / 2
    row2_top = top_y - gd - GAP
    ring_c = (-IW / 2 + EDGE + RING_OD / 2 + (IW - 2 * EDGE - row2_w) / 2, row2_top - RING_OD / 2)
    col_x0 = ring_c[0] + RING_OD / 2 + GAP
    brace_c = (col_x0 + bw / 2, row2_top - bd / 2)
    spare_c = (ring_c[0], row2_top - RING_OD - GAP - SPARE_D / 2)      # spare noses under the cable ring
    mod_c = (brace_c[0], row2_top - bd - GAP - MOD_D / 2)               # KD-02 module under the bracelet
    return dict(g_sil=g_sil, b_sil=b_sil, IW=IW, ID=ID, g_c=(g_cx, g_cy), g_bb=(gx0, gy0, gx1, gy1),
                b_bb=(bx0, by0, bx1, by1), ring_c=ring_c, brace_c=brace_c, spare_c=spare_c, mod_c=mod_c)


# ---------------- parts ----------------
def dims(L):
    OW = L["IW"] + 2 * (CLR + WALL)
    OD = L["ID"] + 2 * (CLR + WALL)
    return OW, OD


def knuckle_layout(OW):
    """x ranges of the 5 knuckles (centered): base, lid, base, lid, base."""
    n = 5
    total = n * KN_L + (n - 1) * KN_GAP
    x = -total / 2
    out = []
    for i in range(n):
        out.append((x, x + KN_L, "base" if i % 2 == 0 else "lid"))
        x += KN_L + KN_GAP
    return out


def base(L):
    OW, OD = dims(L)
    b = rr(OW, OD, CORNER_R, 0, BH)
    b = b.cut(rr(OW - 2 * WALL, OD - 2 * WALL, CORNER_R - WALL, FLOOR, BH + 1))
    yc, zc = OD / 2 + KN_R, BH + LID_T / 2
    yw = OD / 2
    for (x0, x1, who) in knuckle_layout(OW):
        if who != "base":
            continue
        k = cyl_x(x0, x1, yc, zc, 2 * KN_R)
        gus = prism_x([(yw - 1.2, zc), (yc, zc), (yc, zc - KN_R), (yw, zc - KN_R - (yc - yw)), (yw - 1.2, zc - KN_R - (yc - yw))], x0, x1)
        b = b.union(k).union(gus)
    # pin hole through all base knuckles
    b = b.cut(cyl_x(-OW / 2, OW / 2, yc, zc, PIN_D_BASE))
    # rubber-band lugs on the front wall: flat top, 45 degree gusset underneath (prints without supports)
    y0 = -OD / 2
    for sx in (-1, 1):
        zt = BH - LUG_DROP
        prof = [(y0 + 1.5, zt), (y0 - LUG_D, zt), (y0 - LUG_D, zt - LUG_TIP),
                (y0, zt - LUG_TIP - LUG_D), (y0 + 1.5, zt - LUG_TIP - LUG_D - 1.5)]
        lug = prism_x(prof, sx * LUG_X - LUG_W / 2, sx * LUG_X + LUG_W / 2)
        lug = lug.intersect(rr(LUG_W, 2 * LUG_D, 4.0, 0.0, zt + 1, sx * LUG_X, y0))   # round the tip corners
        lug = lug.cut(cyl_z(sx * LUG_X, y0 - LUG_HOLE_OFF, -1.0, zt + 1, LUG_HOLE))
        lug = lug.faces(">Z").edges("%CIRCLE").chamfer(0.8)
        b = b.union(lug)
    # hidden mark on the floor under the insert
    b = b.cut(engrave_up((0, -OD / 2 + 14, FLOOR), SIG, 5.0))
    return b


def lid(L):
    OW, OD = dims(L)
    zc = BH + LID_T / 2
    yc = OD / 2 + KN_R
    l = rr(OW, OD, CORNER_R, BH, BH + LID_T)
    # alignment lip: drops inside the base walls
    iw, idp = OW - 2 * WALL - 2 * LIP_CLR, OD - 2 * WALL - 2 * LIP_CLR
    lip = rr(iw, idp, CORNER_R - WALL - LIP_CLR, BH - LIP_H, BH).cut(
        rr(iw - 2 * LIP_W, idp - 2 * LIP_W, max(CORNER_R - WALL - LIP_CLR - LIP_W, 1.0), BH - LIP_H - 1, BH + 1))
    l = l.union(lip)
    # notches in the plate where the base knuckles swing through, knuckles of the lid
    for (x0, x1, who) in knuckle_layout(OW):
        if who == "base":
            l = l.cut(box(x0 - KN_GAP, x1 + KN_GAP, OD / 2 - 3.0, OD / 2 + 1, BH - 0.1, BH + LID_T + 0.1))
        else:
            k = cyl_x(x0, x1, yc, zc, 2 * KN_R)
            web = box(x0, x1, OD / 2 - 3.0, yc, BH, BH + LID_T)
            l = l.union(k).union(web)
    l = l.cut(cyl_x(-OW / 2, OW / 2, yc, zc, PIN_D_LID))
    # rubber-band lugs + finger-lift tab: flat plates the full thickness of the lid, flat on the bed when printed top-down
    y0 = -OD / 2
    for sx in (-1, 1):
        lug = rr(LUG_W, 2 * LUG_D, 4.0, BH, BH + LID_T, sx * LUG_X, y0).intersect(box(sx * LUG_X - LUG_W, sx * LUG_X + LUG_W, y0 - LUG_D, y0 + 1.5, BH, BH + LID_T))
        lug = lug.cut(cyl_z(sx * LUG_X, y0 - LUG_HOLE_OFF, BH - 1, BH + LID_T + 1, LUG_HOLE))
        lug = lug.faces(">Z").edges("%CIRCLE").chamfer(0.8).faces("<Z").edges("%CIRCLE").chamfer(0.8)
        l = l.union(lug)
    pull = rr(PULL_W, 2 * PULL_D, 4.0, BH, BH + LID_T, 0, y0).intersect(box(-PULL_W, PULL_W, y0 - PULL_D, y0 + 1.5, BH, BH + LID_T))
    l = l.union(pull)
    # logo chip pocket (top face, resin-filled like the bracelet)
    l = l.cut(rr(CHIP_W + 2 * CHIP_CLR, CHIP_H + 2 * CHIP_CLR, 1.7 * CHIP_SCALE, BH + LID_T - POCKET_DEPTH, BH + LID_T + 1, 0, 0))
    # hidden mark on the underside, inside the lip
    l = l.cut(engrave_down((0, OD / 2 - 14, BH), SIG, 5.0))
    return l


def insert(L):
    from shapely import affinity
    IW, ID = L["IW"], L["ID"]
    ins = rr(IW, ID, CORNER_R - 1.0, 0, INS_H)
    z0 = INS_FLOOR
    top = INS_H + 1
    # glasses
    g = affinity.translate(L["g_sil"], L["g_c"][0] - (L["g_bb"][0] + L["g_bb"][2]) / 2,
                           L["g_c"][1] - (L["g_bb"][1] + L["g_bb"][3]) / 2)
    ins = ins.cut(poly_solid(g, z0, top))
    gx0, gy0, gx1, gy1 = g.bounds
    for sx in (-1, 1):                                  # thumb scoops on the front edge
        ins = ins.cut(cyl_z(sx * kd05.OPEN_CX, gy0 + 2.0, z0, top, 16.0))
    # bracelet (laid along X)
    b = affinity.translate(L["b_sil"], L["brace_c"][0] - (L["b_bb"][0] + L["b_bb"][2]) / 2,
                           L["brace_c"][1] - (L["b_bb"][1] + L["b_bb"][3]) / 2)
    ins = ins.cut(poly_solid(b, z0, top))
    bx0, by0, bx1, by1 = b.bounds
    ins = ins.cut(cyl_z((bx0 + bx1) / 2, by0 + 2.0, z0, top, 16.0))
    # spare nose pieces
    sx_, sy_ = L["spare_c"]
    ins = ins.cut(rr(SPARE_W, SPARE_D, 3.0, z0, top, sx_, sy_))
    ins = ins.cut(cyl_z(sx_, sy_ - SPARE_D / 2 + 2.0, z0, top, 14.0))
    # KD-02 module (placeholder size)
    mx, my = L["mod_c"]
    ins = ins.cut(rr(MOD_W, MOD_D, 4.0, z0, top, mx, my))
    ins = ins.cut(cyl_z(mx, my - MOD_D / 2 + 2.0, z0, top, 16.0))
    # cable coil groove
    rc = L["ring_c"]
    ring = cyl_z(rc[0], rc[1], z0, top, RING_OD).cut(cyl_z(rc[0], rc[1], z0 - 1, top + 1, RING_ID))
    ins = ins.cut(ring)
    ins = ins.cut(box(rc[0] + RING_ID / 2 - 1, rc[0] + RING_OD / 2 + 2, rc[1] - 6, rc[1] + 6, z0 + 6.0, top))   # cable exit
    # hidden mark under the insert
    ins = ins.cut(engrave_down((0, -ID / 2 + 14, 0.0), SIG, 6.0))
    return ins


def logo_chip():
    # kd06's chip is turned 90 degrees to read along the strap; turn it back so it reads along X
    c = kd06.logo_chip().rotate((0, 0, 0), (0, 0, 1), -90)
    m = cq.Matrix([[CHIP_SCALE, 0, 0, 0], [0, CHIP_SCALE, 0, 0], [0, 0, 1, 0]])   # grow X and Y only, keep 1.0 mm thick
    return cq.Workplane("XY").newObject([c.val().transformGeometry(m)])


def build():
    L = layout()
    return L, {"KD07-A_case_base": base(L), "KD07-B_case_lid": lid(L),
               "KD07-C_tpu_insert": insert(L), "KD07-D_logo_chip": logo_chip()}


def print_pose(name, p, L):
    if name == "KD07-B_case_lid":
        s = p.rotate((0, 0, 0), (1, 0, 0), 180)          # top face down on the bed
    else:
        s = p
    bb = s.val().BoundingBox()
    return s.translate((-bb.center.x, -bb.center.y, -bb.zmin))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    L, parts = build()
    OW, OD = dims(L)
    print("insert %.1f x %.1f x %.1f | case outside %.1f x %.1f x %.1f (closed %.1f)" %
          (L["IW"], L["ID"], INS_H, OW, OD, BH, BH + LID_T))
    for n, p in parts.items():
        s = print_pose(n, p, L)
        cq.exporters.export(s, os.path.join(out, n + ".stl"), tolerance=0.02, angularTolerance=0.15)
        bb = s.val().BoundingBox()
        print("%-22s valid=%s  %.1f x %.1f x %.1f" % (n, s.val().isValid(), bb.xlen, bb.ylen, bb.zlen))
    print("ok")
