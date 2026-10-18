"""Sol Prosthetics - Model 1 "Bukang-liwayway" (Sunrise), v2: organic shapes, 100% scale.

Same mechanism and hardware as v1 (M3 screw joints, wrist-driven flexor lines), with
human-like shapes: oval fingers that narrow between rounded knuckles, domed fingertips,
a softly rounded palm with the Sol Prosthetics logo pressed into the back, hidden line
tunnels, and a tapered gauntlet with a smooth tensioner bump, rounded ears and edges.

Frame: X across the hand (thumb side = -X, right hand), Y toward the fingertips,
Z up from the palm side to the back of the hand. Units mm.

Run:  python3 bukang_liwayway_v2.py <out_dir>
"""
import json
import math
import sys
from pathlib import Path

import cadquery as cq

V = cq.Vector
HERE = Path(__file__).resolve().parent


# ---------- helpers ----------
def B(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def capX(x0, x1, y, z, r):
    return cq.Solid.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def capY(y0, y1, x, z, r):
    return cq.Solid.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def capZ(z0, z1, x, y, r):
    return cq.Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def fuse(a, *others):
    for o in others:
        a = a.fuse(o)
    return a.clean()


def cut(a, *others):
    for o in others:
        a = a.cut(o)
    return a.clean()


def rot(shape, axis, deg, pivot=(0, 0, 0)):
    p = V(*pivot)
    return shape.rotate(p, p + V(*axis), deg)


def ellipsoid(cx, cy, cz, a, b, c):
    s = cq.Solid.makeSphere(1.0, angleDegrees1=-90, angleDegrees2=90)
    m = cq.Matrix([[a, 0, 0, 0], [0, b, 0, 0], [0, 0, c, 0]])
    return s.transformGeometry(m).translate(V(cx, cy, cz))


def y_loft(sections):
    """Loft through ellipses in planes normal to +Y. sections = [(y, a_x, b_z), ...]."""
    y0 = sections[0][0]
    wp = cq.Workplane(cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, 1, 0)))
    wp = wp.ellipse(sections[0][1], sections[0][2])
    prev = y0
    for y, a, b in sections[1:]:
        wp = wp.workplane(offset=y - prev).ellipse(a, b)
        prev = y
    return wp.loft(ruled=False).val()


def rounded_box(x0, x1, y0, y1, z0, z1, r):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False) \
        .translate((x0, y0, z0)).edges().fillet(r).val()


FILLET_LOG = []


def try_fillet(shape, r, selector):
    """Fillet the edges chosen by selector(edge) -> bool; fall back to smaller radii."""
    edges = [e for e in shape.Edges() if selector(e)]
    if not edges:
        return shape
    for rr in (r, r * 0.7, r * 0.5):
        try:
            out = shape.fillet(rr, edges)
            if out.isValid():
                if rr != r:
                    FILLET_LOG.append(f"reduced {r}->{rr} on {len(edges)} edges")
                return out
        except Exception:
            pass
    FILLET_LOG.append(f"FAILED r={r} on {len(edges)} edges")
    return shape


def in_box(x0, x1, y0, y1, z0, z1):
    def sel(e):
        c = e.Center()
        return x0 <= c.x <= x1 and y0 <= c.y <= y1 and z0 <= c.z <= z1
    return sel


CLR = 1.7   # M3 clearance radius (3.4)
PIL = 1.3   # M3 pilot radius (2.6), screw threads into PETG
HEAD = 3.0  # M3 head recess radius (6.0), 2 mm deep
FLAT = -5.3  # flat on the palm side of fingers and thumb, so they print flat


# ---------- finger segment ----------
def knuckle_cap():
    """Smooth dome over the fork: bridges the slot to hide the tongue, and stops the joint
    bending backwards. Merges into the knuckle barrel below z = 6."""
    return ellipsoid(0, 0.4, 0, 6.9, 7.4, 7.2).intersect(B(-8, 8, -8, 8, 4.5, 9))


def phalanx(L, tip, mid_w=12.4, mid_h=11.0, tip_w=12.6, tip_h=10.6):
    """Joint axis on local X at the origin; segment runs +Y. Fork at the joint, tongue or domed tip at L."""
    knuckle = try_fillet(capX(-7, 7, 0, 0, 6), 1.8, lambda e: True)        # rounded knuckle barrel
    if tip:
        body = y_loft([(1.0, 6.9, 5.9), (L * 0.55, mid_w / 2, mid_h / 2), (L, tip_w / 2, tip_h / 2)])
        dome = ellipsoid(0, L, 0, tip_w / 2, 6.8, tip_h / 2)                 # rounded fingertip
        s = fuse(knuckle, body, dome)
    else:
        body = y_loft([(1.0, 6.9, 5.9), (L - 6.5, mid_w / 2, mid_h / 2)])
        tongue = try_fillet(B(-2.8, 2.8, L - 7.5, L, -5.6, 5.6), 1.4, lambda e: abs(e.tangentAt(0).y) > 0.9)
        tongue = fuse(tongue, capX(-2.8, 2.8, L, 0, 5.6))
        s = fuse(knuckle, body, tongue)
    s = cut(
        fuse(s, knuckle_cap()),
        B(-10, 10, -10, L + 12, -20, FLAT),         # palm-side flat (finger pad)
        B(-3.1, 3.1, -7, 6.8, -8, 6.3),             # fork slot (6.2 wide for a 5.6 tongue), capped on top
        capX(-8, -3, 0, 0, CLR),                    # screw clearance, near arm
        capX(-8, -5, 0, 0, HEAD),                   # head recess
        capX(-4, 8, 0, 0, PIL),                     # pilot, far arm
        capY(-8, L + 4, 0, -3.2, 1.1),              # flexor line channel (palm side)
        capY(-8, L + 4, 0, 3.2, 1.1),               # return channel (back side)
    )
    if not tip:
        s = cut(s, capX(-3, 3, L, 0, CLR))          # tongue hole
    return s


def thumb():
    knuckle = try_fillet(capX(-7, 7, 0, 0, 6), 1.8, lambda e: True)
    body = y_loft([(1.0, 6.9, 5.9), (14, 6.6, 5.6), (26, 6.4, 5.4)])
    dome = ellipsoid(0, 26, 0, 6.4, 7.0, 5.4)
    t = fuse(knuckle, body, dome, knuckle_cap())
    return cut(t, B(-10, 10, -10, 40, -20, FLAT), B(-3.1, 3.1, -7, 6.8, -8, 6.3),
               capX(-8, -3, 0, 0, CLR), capX(-8, -5, 0, 0, HEAD), capX(-4, 8, 0, 0, PIL))


# ---------- palm ----------
FX = [-23.25, -7.75, 7.75, 23.25]     # index, middle, ring, little
KY, KZ = 62, 15                       # knuckle axis
TP = (-33, 18, 8)                     # thumb mount pivot
LINE_Z = 26.5                         # hidden line tunnels in the back wall
LOGO_C = (0.0, 27.75)                 # logo centre on the back of the hand
LOGO_DEPTH = 0.8


def logo_cutter(z_top):
    rects = json.loads((HERE / "logo_rects.json").read_text())
    cx, cy = LOGO_C
    tool = None
    for x0, x1, y0, y1 in rects:
        b = B(cx + x0, cx + x1, cy + y0, cy + y1, z_top - LOGO_DEPTH, z_top + 1)
        tool = b if tool is None else tool.fuse(b)
    return tool.clean()


def rounded_rect_wire(y, xc, zc, w, h, r):
    """Rounded rectangle in the plane y = const (normal +Y), centred at (xc, zc)."""
    pl = cq.Plane(origin=(xc, y, zc), xDir=(1, 0, 0), normal=(0, 1, 0))
    hw, hh = w / 2, h / 2
    k = r * (1 - 1 / math.sqrt(2))
    wp = (cq.Workplane(pl).moveTo(-hw + r, -hh).lineTo(hw - r, -hh)
          .threePointArc((hw - k, -hh + k), (hw, -hh + r)).lineTo(hw, hh - r)
          .threePointArc((hw - k, hh - k), (hw - r, hh)).lineTo(-hw + r, hh)
          .threePointArc((-hw + k, hh - k), (-hw, hh - r)).lineTo(-hw, -hh + r)
          .threePointArc((-hw + k, -hh + k), (-hw + r, -hh)).close())
    return wp.wire().val()


def wrist_ear(side):
    """Rounded stadium-shaped hinge ear on the side of the palm (hinge at the rear circle)."""
    s = 1 if side > 0 else -1
    x0 = 28.5 if s > 0 else -37
    pl = cq.Plane(origin=(x0, 0, 12), xDir=(0, 1, 0), normal=(1, 0, 0))
    ear = cq.Workplane(pl).slot2D(28, 12, 0).extrude(8.5).val()   # y -14..14, circle centres at y = -8 and 8
    outer = 37 * s
    return try_fillet(ear, 1.5, lambda e: abs(e.Center().x - outer) < 0.01)


def palm():
    # tapered: narrower and thinner at the wrist, flat back (logo face, prints on it)
    w0 = rounded_rect_wire(0, 0, 16, 58, 28, 9)         # wrist end: z 2..30
    w1 = rounded_rect_wire(55.5, 0, 15, 66, 30, 10)     # knuckles: z 0..30
    p = cq.Solid.makeLoft([w0, w1], True)
    # curved knuckle line: the middle knuckles sit furthest forward, like a real hand
    p = p.intersect(cq.Solid.makeCylinder(120, 60, V(0, -65.5, -10), V(0, 0, 1)))
    on_arc = lambda e: abs(math.hypot(e.Center().x, e.Center().y + 65.5) - 120) < 0.3
    p = try_fillet(p, 7, on_arc)                                      # round the knuckle edge
    p = try_fillet(p, 4, lambda e: e.Center().y < 0.1)                # soften the wrist edge
    for x in FX:
        t = try_fillet(B(x - 2.8, x + 2.8, 50, KY, KZ - 5.5, KZ + 5.5), 1.4, lambda e: abs(e.tangentAt(0).y) > 0.9)
        p = fuse(p, t, capX(x - 2.8, x + 2.8, KY, KZ, 5.5))
    p = fuse(p, wrist_ear(+1), wrist_ear(-1),
             ellipsoid(-28.5, 23, 11, 5.5, 17, 9),     # thumb-side muscle pad (thenar)
             ellipsoid(29.5, 27, 10, 4.5, 18, 8))      # little-finger side (hypothenar)

    def diag(x):
        a, b = (x, 56.5, 11.8), (x, 48.5, LINE_Z)
        d = (0, b[1] - a[1], b[2] - a[2])
        ln = math.hypot(d[1], d[2])
        u = (0, d[1] / ln, d[2] / ln)
        return cq.Solid.makeCylinder(1.15, ln + 4, V(a[0], a[1] - 2.5 * u[1], a[2] - 2.5 * u[2]), V(*u))

    strap = lambda xa, xb: try_fillet(B(xa, xb, 29, 47, 5, 9), 1.9, lambda e: abs(e.tangentAt(0).x) > 0.9)
    p = cut(
        p,
        rounded_box(-28, 28, -8, 48, 4.5, 24, 4),               # hand cavity, open at the wrist
        rounded_box(-24, 24, -8, 44, -6, 5, 3),                 # open palm side, U-shaped
        strap(-34, -27), strap(27, 34),                         # palm strap slots (16 mm strap)
        *[capX(x - 3.5, x + 3.5, KY, KZ, CLR) for x in FX],     # knuckle screw holes
        *[capY(53, KY + 8, x, KZ - 3.2, 1.1) for x in FX],      # flexor line through each tongue
        *[diag(x) for x in FX],                                  # line up into the back wall
        *[capY(-3, 49.5, x, LINE_Z, 1.15) for x in FX],         # hidden tunnel to the wrist
        capX(30, 38, -8, 12, PIL), capX(-38, -30, -8, 12, PIL), # wrist screw pilots
        logo_cutter(30),                                         # Sol Prosthetics logo, pressed in
    )
    tongue = cut(fuse(B(-44, -29.5, 15.2, 20.8, 2.5, 13.5), capY(15.2, 20.8, -44, 8, 5.5)),
                 capY(14, 22, -44, 8, CLR))
    tongue = try_fillet(tongue, 1.2, lambda e: abs(e.Center().y - 15.2) < 0.01 or abs(e.Center().y - 20.8) < 0.01)
    return fuse(p, rot(tongue, (0, 0, 1), -35, TP))


# ---------- gauntlet ----------
GZ = 12
TX = [-12, -4, 4, 12]
G_Y0, G_Y1 = -112, -17                # elbow end, wrist end
R_ELBOW, R_WRIST, WALL = 34.0, 31.8, 3.0


def outer_r(y):
    t = (y - G_Y0) / (G_Y1 - G_Y0)
    return R_ELBOW + (R_WRIST - R_ELBOW) * t


def gauntlet_ear(side):
    """Smooth lobe from the cuff out to the wrist hinge; curved underside (prints standing up)."""
    s = 1 if side > 0 else -1
    pts = lambda P: [(s * x, y) for x, y in P]
    wp = (cq.Workplane("XY").moveTo(*pts([(29.5, -54)])[0])
          .spline(pts([(35.5, -45), (40, -35), (41.3, -25)]), includeCurrent=True)
          .lineTo(*pts([(41.3, -8)])[0]).lineTo(*pts([(37.3, -8)])[0]).lineTo(*pts([(37.3, -15.5)])[0])
          .spline(pts([(34, -17.6), (29.5, -18.2)]), includeCurrent=True).close())
    ear = wp.extrude(12).val().translate(V(0, 0, 6))
    ear = try_fillet(ear, 2.5, lambda e: abs(e.Center().x) > 31 and
                     (abs(e.Center().z - 6) < 0.01 or abs(e.Center().z - 18) < 0.01))
    hinge = capX(37.3, 41.3, -8, 12, 6) if s > 0 else capX(-41.3, -37.3, -8, 12, 6)
    hinge = try_fillet(hinge, 1.5, lambda e: abs(e.Center().x - 41.3 * s) < 0.01)
    return fuse(ear, hinge)


def teardrop(x, y, r=3.6):
    """Teardrop vent: round with a 45-degree point toward +Y (up when printing)."""
    d = r * math.sqrt(2)
    tip = cq.Workplane("XY").polyline([(-r / math.sqrt(2), r / math.sqrt(2)), (0, d), (r / math.sqrt(2), r / math.sqrt(2)), (0, 0)]).close().extrude(22).val()
    return fuse(capZ(0, 22, 0, 0, r), tip).translate(V(x, y, 28))


OPEN_DEG = 100   # open underside, centred on -Z


def cuff_shell():
    """Tapered C-shaped cuff, revolved from a profile with rounded corners, so both ends
    and the open underside have soft edges."""
    prof = [(R_ELBOW - WALL, G_Y0), (R_ELBOW, G_Y0), (R_WRIST, G_Y1), (R_WRIST - WALL, G_Y1)]
    sk = cq.Sketch().polygon(prof + [prof[0]]).vertices().fillet(1.2)
    sweep = 360 - OPEN_DEG
    shell = cq.Workplane("XY").placeSketch(sk).revolve(sweep, (0, 0, 0), (0, 1, 0)).val()
    # turn the cuff so its solid back (centroid) points up and the gap faces -Z
    c = shell.Center()
    for th in (math.degrees(math.atan2(-c.x, c.z)), -math.degrees(math.atan2(-c.x, c.z))):
        cand = rot(shell, (0, 1, 0), th)
        cc = cand.Center()
        if abs(cc.x) < 0.05 and cc.z > 0:
            shell = cand
            break
    shell = try_fillet(shell, 1.2, lambda e: e.Center().z < -8 and abs(e.tangentAt(0).y) > 0.5)
    return shell.translate(V(0, 0, GZ))


def gauntlet():
    hump = ellipsoid(0, -46, 43, 20, 24, 9)                    # smooth tensioner bump
    inner = cq.Solid.makeCone(R_ELBOW - WALL, R_WRIST - WALL, G_Y1 - G_Y0 + 2, V(0, G_Y0 - 1, GZ), V(0, 1, 0))
    hump = cut(hump, inner)
    g = fuse(cuff_shell(), hump, gauntlet_ear(+1), gauntlet_ear(-1))
    slot = lambda xa, xb, ya, yb: try_fillet(B(xa, xb, ya, yb, -6, -2), 1.9, lambda e: abs(e.tangentAt(0).x) > 0.9)
    g = cut(
        g,
        inner,                                                   # keep the forearm space clear
        capX(37, 42, -8, 12, CLR), capX(39.3, 42, -8, 12, HEAD), # wrist screws
        capX(-42, -37, -8, 12, CLR), capX(-42, -39.3, -8, 12, HEAD),
        *[capZ(42.6, 54, x, -50, PIL) for x in TX],              # tension screws (clamp the lines)
        *[capY(-52, -18, x, 46.5, 0.8) for x in TX],             # line tunnels into each screw hole
        slot(-32, -23, -52, -25), slot(23, 32, -52, -25),        # strap slots (25 mm)
        slot(-33, -24, -102, -75), slot(24, 33, -102, -75),
        *[teardrop(x, y) for x in (-13, 0, 13) for y in (-104, -94, -84, -74)],
    )
    return g


# ---------- print layout ----------
LEN = {"index-and-ring": (22, 15.5, 13), "middle": (24, 16.5, 14), "little": (18, 15.5, 12)}


def seat(shape):
    bb = shape.BoundingBox()
    return shape.translate(V(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def finger_set(lengths):
    p, m, d = lengths
    parts = [phalanx(p, False), phalanx(m, False).translate(V(20, 0, 0)), phalanx(d, True).translate(V(40, 0, 0))]
    return seat(cq.Compound.makeCompound(parts))


def print_parts():
    out = {
        "SP1-01_palm_back-side-down": seat(rot(palm(), (1, 0, 0), 180)),
        "SP1-03_gauntlet_stand-on-forearm-end": seat(rot(gauntlet(), (1, 0, 0), 90)),
        "SP1-06_thumb": seat(thumb()),
    }
    for name, lens in LEN.items():
        qty = "_print-x2" if name == "index-and-ring" else ""
        out[f"SP1-02_finger-{name}{qty}"] = finger_set(lens)
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "stl")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, shape in print_parts().items():
        bb = shape.BoundingBox()
        print(f"{name}: valid={shape.isValid()} vol={shape.Volume():.0f} mm3 "
              f"size={bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        cq.exporters.export(shape, str(out_dir / f"{name}.stl"), tolerance=0.05, angularTolerance=0.2)
