"""Hinge joint geometry for the realistic hand, built in a local joint frame
(x = screw axis / lateral, y = along the finger toward the tip, z = back of the hand).

Joint = rounded barrel (radius R) on one side, matching cup (R + GAP) on the other,
a tongue on the cup side that sits in a slot through the barrel, and an M3 screw on the x axis.
Flexion turns the distal part about +x by a negative angle (fingertip toward the palm)."""
import numpy as np, manifold3d as mf

GAP = 0.4          # radial clearance barrel/cup, also the flat dorsal stop gap
SEG = 64


def cyl_x(r, h=80, c=0.0):
    return mf.Manifold.cylinder(h, r, r, SEG).translate([0, 0, -h / 2]).rotate([0, 90, 0]).translate([c, 0, 0])


def cyl_x_span(r, x0, x1):
    return mf.Manifold.cylinder(x1 - x0, r, r, SEG).rotate([0, 90, 0]).translate([x0, 0, 0])


def bx(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def rot_x(m, deg):
    return m.rotate([deg, 0, 0])


BIG = 200


class Joint:
    """barrel='P': proximal part owns the barrel (finger PIP/DIP, like a real knuckle head).
    barrel='D': distal part owns the barrel (MCP: so each finger carries its own screw)."""

    def __init__(self, R, Rt=3.4, wt=5.6, ws=6.2, hn=3.0, barrel='P', flex=(-8, 92), split=(45, 45)):
        self.R, self.Rt, self.wt, self.ws, self.hn, self.barrel, self.flex = R, Rt, wt, ws, hn, barrel, flex
        self.phiP, self.phiD = split   # palm-side clearance notch: degrees taken from the proximal / distal part

    # regions (local)
    def prox_region(self):
        half = bx(-BIG, BIG, -BIG, -GAP / 2, -BIG, BIG)
        if self.barrel == 'P':
            return half + cyl_x(self.R)
        return half - cyl_x(self.R + GAP)

    def dist_region(self):
        half = bx(-BIG, BIG, GAP / 2, BIG, -BIG, BIG)
        if self.barrel == 'D':
            return half + cyl_x(self.R)
        return half - cyl_x(self.R + GAP)

    def _neck(self, extra=0.0, reach=None):
        sgn = 1 if self.barrel == 'P' else -1          # tongue lives on the cup side
        reach = reach if reach is not None else self.R + GAP + 1.5
        y0, y1 = (0, reach) if sgn > 0 else (-reach, 0)
        w = (self.ws if extra else self.wt) / 2
        return bx(-w, w, y0, y1, -self.hn - extra, self.hn + extra)

    def tongue(self):
        w = self.wt / 2
        disk = cyl_x(self.Rt) ^ bx(-w, w, -BIG, BIG, -BIG, BIG)
        return (disk + self._neck()) - cyl_x(1.7)

    def slot(self):
        """Everything the tongue (plus clearance) sweeps through over the flex range, inside the barrel."""
        w = self.ws / 2
        slab = bx(-w, w, -BIG, BIG, -BIG, BIG)
        disk = cyl_x(self.Rt + 0.35) ^ slab
        neck = self._neck(extra=0.35, reach=self.R + GAP + 0.6)
        # tongue side moves relative to the barrel: for a P barrel the distal tongue turns by -phi,
        # for a D barrel the proximal tongue turns by +phi (seen from the barrel)
        sgn = -1 if self.barrel == 'P' else 1
        angs = np.arange(self.flex[0], self.flex[1] + 0.1, 6.0)
        parts = [disk]
        for a0, a1 in zip(angs[:-1], angs[1:]):
            parts.append(mf.Manifold.batch_hull([rot_x(neck, sgn * a0), rot_x(neck, sgn * a1)]))
        sweep = mf.Manifold.batch_boolean(parts, mf.OpType.Add)
        return sweep ^ cyl_x(self.R + 0.01)

    def _wedge(self, a0, a1):
        pts = [(0.0, 0.0)] + [(BIG * np.cos(np.radians(a)), BIG * np.sin(np.radians(a))) for a in np.linspace(a0, a1, 12)]
        # polygon in the (y, z) plane, extruded along x
        cs = mf.CrossSection([pts])
        w = cs.extrude(2 * BIG).translate([0, 0, -BIG])           # extrude along z: (X=y, Y=z, Z=x)
        w = w.transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float))
        return w - cyl_x(self.R)

    def wedge_prox(self):
        """Palm-side notch cut from the proximal part so the distal part can fold down."""
        return self._wedge(-90 - self.phiP, -89.5)

    def wedge_dist(self):
        return self._wedge(-90.5, -90 + self.phiD)

    def screw_holes(self, head_side, x_head, x_far, recess=2.2):
        """Material removed from the barrel part: head recess (6.2 x 2.2 deep, from the outer surface at x_head),
        3.4 clearance on the head side, 2.6 pilot in the far arm. head_side = -1 or +1 (local x)."""
        w = self.ws / 2
        if head_side < 0:
            rec = cyl_x_span(3.1, -BIG, x_head + recess)
            clear = cyl_x_span(1.7, -BIG, w)
            pilot = cyl_x_span(1.3, -BIG, BIG)
        else:
            rec = cyl_x_span(3.1, x_head - recess, BIG)
            clear = cyl_x_span(1.7, -w, BIG)
            pilot = cyl_x_span(1.3, -BIG, BIG)
        return rec + clear + pilot
