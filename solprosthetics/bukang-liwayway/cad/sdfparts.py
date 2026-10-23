"""Smooth signed-distance building blocks for the v3.1 parts.

Every printed part is built as a distance field on its own fine grid: the skin, the joint regions, tongues,
slots and clearance carves are combined with smooth min / max, so every edge comes out rounded and every
root filleted. Only exact functional features (screw holes, line channels, logo, rubber pockets) are cut
as mesh booleans afterwards. Negative = inside."""
import json, numpy as np
from scipy import ndimage
from sdf import Grid, to_manifold, smin, smax
from lib_grid import load_skin

GAP = 0.4


class Skin:
    """Outer skin field sampled with a cubic spline (smooth between grid nodes, no facets)."""

    def __init__(self, key='outer', path=None):
        d, g = load_skin(path) if path else load_skin()
        self.g = g
        self.c = ndimage.spline_filter(d[key].astype(np.float64), order=3).astype(np.float32)

    def __call__(self, P):
        idx = ((np.asarray(P, np.float64) - self.g.o) / self.g.p).T
        return ndimage.map_coordinates(self.c, idx, order=3, mode='nearest', prefilter=False).astype(np.float32)


def local(P, O, x, d, z):
    Q = P - np.asarray(O)
    return Q @ np.asarray(x), Q @ np.asarray(d), Q @ np.asarray(z)


def rot_points(P, O, axis, deg):
    """Rotate points P about the axis through O by deg (right-hand rule)."""
    a = np.asarray(axis, float); a /= np.linalg.norm(a); t = np.radians(deg)
    Q = P - O
    c, s = np.cos(t), np.sin(t)
    return O + Q * c + np.cross(a, Q) * s + np.outer(Q @ a, a) * (1 - c)


def box2(a, b, ha, hb):
    """2D box distance (centred), a/b coordinates, half sizes ha/hb."""
    qa = np.abs(a) - ha; qb = np.abs(b) - hb
    return np.sqrt(np.maximum(qa, 0) ** 2 + np.maximum(qb, 0) ** 2) + np.minimum(np.maximum(qa, qb), 0)


def opening(f, g, r):
    """Remove material thinner than 2r and round convex edges to r (field in, field out)."""
    eroded = f < -r
    h = ndimage.distance_transform_edt(~eroded).astype(np.float32) * g.p - g.p / 2 - r
    # the voxel distance is stair-stepped (about +-p/2): blur it and give it a small bias, so it only
    # takes over where it really removes material and never prints its steps onto ordinary surfaces
    h = ndimage.gaussian_filter(h, 1.0) - 0.6 * g.p
    return np.maximum(f, h)


def closing(f, g, r):
    """Fill slits, gaps and crevices narrower than 2r and round concave corners to r (field in, field out).
    Anything functional that is narrower (cups, slots, carves) must be cut again afterwards."""
    dil = f < r
    e = ndimage.distance_transform_edt(dil).astype(np.float32) * g.p - g.p / 2
    c = ndimage.gaussian_filter(r - e, 1.0) + 0.6 * g.p
    return np.minimum(f, c)


def grid_points(g):
    X, Y, Z = g.points()
    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1), X.shape


class JointSDF:
    """Hinge in the joint frame (x screw axis, y along the finger, z back of hand), axis through O.
    barrel='P': proximal owns the barrel, distal the cup + tongue. barrel='D': the reverse (MCP)."""

    def __init__(self, info, barrel, wt, ws, hn, flex):
        self.O = np.array(info['O']); self.x = np.array(info['x']); self.d = np.array(info['d']); self.z = np.array(info['z'])
        self.R, self.Rt = info['R'], info['Rt']
        self.barrel, self.wt, self.ws, self.hn, self.flex = barrel, wt, ws, hn, flex

    def loc(self, P):
        return local(P, self.O, self.x, self.d, self.z)

    def cyl(self, P, r):
        u, v, w = self.loc(P); return np.sqrt(v * v + w * w) - r

    def side(self, P, which):
        """Region of the proximal ('P') or distal ('D') part at this joint, smooth edges."""
        u, v, w = self.loc(P)
        cyl = np.sqrt(v * v + w * w)
        if which == 'P':
            h = v + GAP / 2
        else:
            h = GAP / 2 - v
        if which == self.barrel:       # half space plus the barrel, filleted where they meet
            return smin(h, cyl - self.R, 1.0)
        return smax(h, -(cyl - (self.R + GAP)), 0.6)     # half space minus the cup, rounded rim

    def tongue(self, P):
        """Tongue on the cup side: rounded disk on the axis + neck back to the cup-side body."""
        u, v, w = self.loc(P)
        sgn = 1 if self.barrel == 'P' else -1            # cup side is distal (+v) for a P barrel
        reach = self.R + GAP + 2.0
        disk = np.sqrt(v * v + w * w) - self.Rt
        vc = sgn * reach / 2
        neck = box2(v - vc, w, reach / 2, self.hn)
        t2 = smin(disk, neck, 1.0)
        return smax(t2, np.abs(u) - self.wt / 2, 0.6)

    def slot_from(self, P, tongue_field, step=3.0):
        """What the tongue (+0.35 clearance) sweeps through, inside the barrel. tongue_field(points) is
        the cup-side part restricted to the joint zone; it turns relative to the barrel."""
        sgn = -1 if self.barrel == 'P' else 1
        out = np.full(len(P), 1e3, np.float32)
        for a in np.arange(self.flex[0], self.flex[1] + 0.01, step):
            out = np.minimum(out, tongue_field(rot_points(P, self.O, self.x, -sgn * a)) - 0.35)
        return smax(out, self.cyl(P, self.R + 0.01), 0.3)


def sweep_carve(P, O, axis, part_field, angles, grow=0.35):
    """Union of the distal part_field over flexion angles (deg, + = toward the palm; flexion turns the
    distal part by -angle about the joint x axis, so its field at angle a is f(rot(P, +a)))."""
    out = np.full(len(P), 1e3, np.float32)
    for a in angles:
        out = np.minimum(out, part_field(rot_points(P, O, axis, a)) - grow)
    return out


def chain_field(P, pts, r, pad=2.0):
    """Distance to a polyline tube of radius r (negative inside), evaluated only near the path."""
    from sdf import seg_dist
    pts = np.asarray(pts, float)
    out = np.full(len(P), 1e3, np.float32)
    lo = pts.min(0) - r - pad; hi = pts.max(0) + r + pad
    m = np.all((P >= lo) & (P <= hi), axis=1)
    if not m.any():
        return out
    Q = P[m]; best = np.full(len(Q), 1e3, np.float32)
    for a, b in zip(pts[:-1], pts[1:]):
        lo2 = np.minimum(a, b) - r - pad; hi2 = np.maximum(a, b) + r + pad
        mm = np.all((Q >= lo2) & (Q <= hi2), axis=1)
        if mm.any():
            best[mm] = np.minimum(best[mm], seg_dist(Q[mm], a, b) - r)
    out[m] = best
    return out


def opening_true(f, g, r):
    """Opening that measures real thickness (re-distanced from the field's sign), so a field whose values
    were flattened by smoothing is not eroded away."""
    inside = f < 0
    d_in = ndimage.distance_transform_edt(inside).astype(np.float32) * g.p - g.p / 2
    eroded = d_in > r
    h = ndimage.distance_transform_edt(~eroded).astype(np.float32) * g.p - g.p / 2 - r
    h = ndimage.gaussian_filter(h, 1.0) - 0.6 * g.p
    return np.maximum(f, h)
