"""Make palm_flap_print.stl: the TPU palm cover plus snip-off stabilizer fins.

Print orientation is the one palm_flap.stl is exported in (standing on its
bottom edge). Two thin TPU fins stand beside the side edges on wide feet and
hold the cover by small tabs that touch only the outer edge face of the lip.
The tabs stay clear of the hinge-screw holes on the +x edge.

usage: python3 flap_print.py stl/palm_flap.stl stl/palm_flap_print.stl
"""
import sys
import numpy as np
import trimesh
import manifold3d as mf

src, dst = sys.argv[1], sys.argv[2]
part = trimesh.load(src)

GAP = 1.0        # air gap between cover edge and fin
FIN_T = 1.6      # fin thickness (4 lines of 0.4)
FIN_TOP = 40.5   # fin height (cover is 49 mm tall)
FOOT_T = 0.6     # foot pad thickness (3 layers)
FOOT_OUT = 13.0  # foot pad reach outward
TAB_W, TAB_H, TAB_IN = 1.0, 0.8, 0.3   # tab width (y), height (z), bite into the edge

XE = np.abs(part.bounds[:, 0]).max()   # outermost edge, ~19.6



def hole_zones(side):
    """z ranges of holes (cover screws) within 4 mm of this side edge, found by slicing."""
    zs = []
    for z in np.arange(0.5, part.bounds[1, 2] - 0.5, 0.25):
        sec = part.section([0, 0, 1], [0, 0, z])
        if sec is None or len(sec.discrete) < 2: continue
        for e in sec.discrete:
            ext = np.ptp(e, 0); c = e.mean(0)
            if ext[0] < 6 and ext[1] < 6 and side * c[0] > XE - 4.0:
                zs.append(z)
    zs = np.array(zs); out = []
    if len(zs):
        start = prev = zs[0]
        for z in zs[1:]:
            if z - prev > 0.6: out.append((start, prev)); start = z
            prev = z
        out.append((start, prev))
    return out


def edge_point(z, side):
    s = part.section([0, 0, 1], [0, 0, z])
    v = s.vertices
    i = v[:, 0].argmax() if side > 0 else v[:, 0].argmin()
    return v[i]


def pick_tabs(side):
    zones = hole_zones(side)
    cands = list(np.arange(9.0, FIN_TOP - 0.4, 4.0))
    for (a0, b0), (a1, b1) in zip(zones[:-1], zones[1:]):       # a tab in every gap between holes that fits one
        if a1 - b0 >= 2.6: cands.append((b0 + a1) / 2)
    tabs = []
    for z0 in sorted(cands):
        for z in (z0, z0 - 1.0, z0 + 1.0, z0 - 2.0, z0 + 2.0):
            if z > FIN_TOP - 0.5 or z < 8.5: continue
            if any(a_ - 1.2 <= z <= b_ + 1.2 for a_, b_ in zones): continue
            if abs(edge_point(z, side)[0]) < XE - 2.6: continue          # edge too far in: long tab
            if tabs and min(abs(z - t_) for t_ in tabs) < 2.5: continue
            tabs.append(float(z)); break
    return sorted(tabs), zones


TABS, PLATE_Y = {}, {}
for _sd in (-1, 1):
    TABS[_sd], _zn = pick_tabs(_sd)
    _ys = [edge_point(z, _sd)[1] for z in TABS[_sd]]
    PLATE_Y[_sd] = (min(_ys) - 4.5, max(_ys) + 4.5)
    print('side %+d holes at z %s -> tabs %s' % (_sd, [(round(a, 1), round(b, 1)) for a, b in _zn], TABS[_sd]))


def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def to_mf(tm):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                               tri_verts=np.asarray(tm.faces, np.uint32)))


jig = []
report = []
for side in (-1, 1):
    xi = side * (XE + GAP)              # fin inner face
    xo = side * (XE + GAP + FIN_T)      # fin outer face
    y0, y1 = PLATE_Y[side]
    lo, hi = sorted([xi, xo])
    jig.append(box(lo, hi, y0, y1, 0, FIN_TOP))
    # foot pad
    f0, f1 = sorted([xi, xi + side * FOOT_OUT])
    jig.append(box(f0, f1, y0 - 2, y1 + 2, 0, FOOT_T))
    # buttress: triangle in x-z, outward, at plate mid-y
    yc = (y0 + y1) / 2
    tri = mf.CrossSection([[[0, 0], [11, 0], [0, 30]]])
    b = mf.Manifold.extrude(tri, FIN_T)          # in x-y, height along z
    b = b.rotate([90, 0, 0])                       # profile now in x-z, thickness along -y
    b = b.translate([0, yc + FIN_T / 2, 0])
    if side < 0:
        b = b.mirror([1, 0, 0])
    b = b.translate([xo, 0, 0])
    jig.append(b)
    # tabs
    for z in TABS[side]:
        p = edge_point(z, side)
        assert y0 + 1 < p[1] < y1 - 1, (side, z, p)
        a, c = sorted([p[0] - side * TAB_IN, xi + side * 0.1])
        jig.append(box(a, c, p[1] - TAB_W / 2, p[1] + TAB_W / 2, z - TAB_H / 2, z + TAB_H / 2))
        report.append((side, z, round(float(p[0]), 2), round(float(p[1]), 2), round(abs(xi - p[0]), 2)))

# sole: a 0.6 mm (3-layer) bar under the cover's bottom edge, joined to both foot pads, so the first layers of
# the cover (which only touch the bed along a thin edge) are held; snip it off the lip edge afterwards
s0 = part.section([0, 0, 1], [0, 0, 0.3])
if s0 is not None:
    yb = float(np.median(s0.vertices[:, 1]))
    jig.append(box(-(XE + GAP + FOOT_OUT), XE + GAP + FOOT_OUT, yb - 1.5, yb + 1.5, 0, FOOT_T))
    print('sole bar at y %.1f' % yb)
J = mf.Manifold.batch_boolean(jig, mf.OpType.Add)
out = J + to_mf(part)
mesh = out.to_mesh()
res = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)
# drop zero-area slivers left where a tab edge meets the cover surface
res.update_faces(res.area_faces > 1e-9)
res.remove_unreferenced_vertices()
bodies = res.split(only_watertight=False)
res = max(bodies, key=lambda b: abs(b.volume) if b.is_watertight else 0)
res.export(dst)
for r in report:
    print("tab side %+d z %5.1f  edge x %6.2f y %5.2f  span %.2f mm" % r)
print("watertight", res.is_watertight, "bodies", len(res.split(only_watertight=False)),
      "volume cm3 part %.2f total %.2f" % (part.volume / 1000, res.volume / 1000))
print("bounds", res.bounds.round(1).tolist())
