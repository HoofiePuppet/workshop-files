"""Sol Prosthetics - Model 1 "Bukang-liwayway" (Sunrise), v1 test print, 100% scale.

CadQuery port of bukang-liwayway.kcad.ts (same numbers, same frame) used to export
print-ready STLs. Frame: X across the hand (thumb side = -X, right hand),
Y toward the fingertips, Z up from the palm side to the back of the hand. Units mm.

Run:  python3 bukang_liwayway.py <out_dir>
"""
import math
import sys
from pathlib import Path

import cadquery as cq

V = cq.Vector


def B(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def capX(x0, x1, y, z, r):
    return cq.Solid.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def capY(y0, y1, x, z, r):
    return cq.Solid.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def capZ(z0, z1, x, y, r):
    return cq.Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def poly(points, depth):
    """Closed polygon in XY, extruded +Z from z = 0."""
    return cq.Workplane("XY").polyline(points).close().extrude(depth).val()


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


CLR = 1.7   # M3 clearance radius (3.4)
PIL = 1.3   # M3 pilot radius (2.6), screw threads into PETG
HEAD = 3.0  # M3 head recess radius (6.0), 2 mm deep


# ---------- One finger segment ----------
def phalanx(L, tip):
    body_end = L if tip else L - 6.5
    s = fuse(capX(-7, 7, 0, 0, 6), B(-7, 7, 0, body_end, -6, 6))
    if tip:
        s = fuse(s, capX(-7, 7, L, 0, 6))
    else:
        s = fuse(s, B(-2.8, 2.8, L - 7, L, -6, 6), capX(-2.8, 2.8, L, 0, 6))
    s = cut(
        s,
        B(-3.1, 3.1, -7, 6.8, -7, 7),        # fork slot (6.2 wide for a 5.6 tongue)
        capX(-8, -3, 0, 0, CLR),              # screw clearance, near arm
        capX(-8, -5, 0, 0, HEAD),             # head recess
        capX(-4, 8, 0, 0, PIL),               # pilot, far arm
        capY(-8, L + 8, 0, -3.2, 1.1),        # flexor line channel (palm side)
        capY(-8, L + 8, 0, 3.2, 1.1),         # return channel (back side)
    )
    if not tip:
        s = cut(s, capX(-3, 3, L, 0, CLR))    # tongue hole
    return s


# ---------- Palm ----------
FX = [-23.25, -7.75, 7.75, 23.25]             # index, middle, ring, little
KY, KZ = 62, 15                               # knuckle axis
TP = (-33, 18, 8)                             # thumb mount pivot


def palm():
    p = cq.Workplane("XY").box(66, 55.5, 30, centered=False).translate((-33, 0, 0)).edges().fillet(3).val()
    for x in FX:
        p = fuse(p, B(x - 2.8, x + 2.8, 55, KY, KZ - 5.5, KZ + 5.5), capX(x - 2.8, x + 2.8, KY, KZ, 5.5))
    p = fuse(
        p,
        B(32, 37, -8, 8, 6, 18), capX(32, 37, -8, 12, 6),       # wrist ear, right
        B(-37, -32, -8, 8, 6, 18), capX(-37, -32, -8, 12, 6),   # wrist ear, left
    )

    def diag(x):
        a, b = (x, 56.5, 11.8), (x, 49, 31)
        d = (0, b[1] - a[1], b[2] - a[2])
        ln = math.hypot(d[1], d[2])
        u = (0, d[1] / ln, d[2] / ln)
        start = V(a[0], a[1] - 3 * u[1], a[2] - 3 * u[2])
        return cq.Solid.makeCylinder(1.1, ln + 6, start, V(*u))

    vents = [capZ(24, 31, x, y, 3) for x in (-15.5, 0, 15.5) for y in (12, 24, 36)]
    p = cut(
        p,
        B(-28, 28, -1, 48, 4, 25),                               # hand cavity, open at the wrist
        B(-24, 24, -1, 44, -1, 5),                               # open palm side, U-shaped
        B(-34, -27, 29, 47, 5, 9), B(27, 34, 29, 47, 5, 9),      # palm strap slots (16 mm strap)
        *[capX(x - 3.5, x + 3.5, KY, KZ, CLR) for x in FX],      # knuckle screw holes
        *[capY(54, KY + 8, x, KZ - 3.2, 1.1) for x in FX],       # flexor line through each tongue
        *[diag(x) for x in FX],                                   # line up to the back of the hand
        *[B(x - 1.25, x + 1.25, -1, 50, 28.2, 31) for x in FX],  # line grooves on the back
        *vents,
        capX(30, 38, -8, 12, PIL), capX(-38, -30, -8, 12, PIL),  # wrist screw pilots
    )
    tongue = cut(fuse(B(-44, -30, 15.2, 20.8, 2.5, 13.5), capY(15.2, 20.8, -44, 8, 5.5)),
                 capY(14, 22, -44, 8, CLR))
    return fuse(p, rot(tongue, (0, 0, 1), -35, TP))


# ---------- Thumb ----------
def thumb():
    t = fuse(capX(-7, 7, 0, 0, 6), B(-7, 7, 0, 26, -6, 6), capX(-7, 7, 26, 0, 6))
    return cut(t, B(-3.1, 3.1, -7, 6.8, -7, 7), capX(-8, -3, 0, 0, CLR),
               capX(-8, -5, 0, 0, HEAD), capX(-4, 8, 0, 0, PIL))


# ---------- Gauntlet ----------
GZ = 12
TX = [-15, -5, 5, 15]


def gauntlet():
    tens = rot(poly([(-32, 36), (-32, 50), (-55, 50), (-69, 36)], 40), (1, 1, 1), 120).translate(V(-20, 0, 0))
    g = fuse(
        capY(-112, -17, 0, GZ, 32.5),
        tens,
        poly([(31, -40.3), (41.3, -30), (41.3, -15), (31, -15)], 12).translate(V(0, 0, 6)),
        B(37.3, 41.3, -15.5, -8, 6, 18), capX(37.3, 41.3, -8, 12, 6),
        poly([(-31, -15), (-41.3, -15), (-41.3, -30), (-31, -40.3)], 12).translate(V(0, 0, 6)),
        B(-41.3, -37.3, -15.5, -8, 6, 18), capX(-41.3, -37.3, -8, 12, 6),
    )
    vents = [poly([(0, -4.5), (4.5, 0), (0, 4.5), (-4.5, 0)], 19).translate(V(x, y, 28))
             for x in (-12, 0, 12) for y in (-104, -92, -80, -68)]
    return cut(
        g,
        capY(-113, -16, 0, GZ, 29.5),                             # forearm space
        B(-24, 24, -113, -16, -30, -8),                           # open underside
        capX(37, 42, -8, 12, CLR), capX(39.3, 42, -8, 12, HEAD),  # wrist screws
        capX(-42, -37, -8, 12, CLR), capX(-42, -39.3, -8, 12, HEAD),
        *[capZ(42.5, 51, x, -43.5, PIL) for x in TX],             # tension screws
        *[B(x - 1, x + 1, -43.5, -31, 48.5, 51) for x in TX],     # line grooves to each screw
        B(-31, -23, -50, -23, -6, -2), B(23, 31, -50, -23, -6, -2),   # strap slots (25 mm)
        B(-31, -23, -100, -73, -6, -2), B(23, 31, -100, -73, -6, -2),
        *vents,
    )


LEN = {"index-and-ring": (22, 15.5, 13), "middle": (24, 16.5, 14), "little": (18, 15.5, 12)}


def seat(shape):
    bb = shape.BoundingBox()
    return shape.translate(V(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def finger_set(lengths):
    p, m, d = lengths
    parts = [phalanx(p, False), phalanx(m, False).translate(V(20, 0, 0)), phalanx(d, True).translate(V(40, 0, 0))]
    return seat(cq.Compound.makeCompound(parts))


def print_parts():
    """Every printable part, already turned to its print orientation and seated on z = 0."""
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
        cq.exporters.export(shape, str(out_dir / f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)
