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

# z heights for the tabs; +x edge has hinge screws at z 15.8-18.8, 25.5-28.8, 35.2-38.2
TABS = {-1: [9, 13, 17, 21, 25, 29, 33, 37, 40],
        +1: [9, 12, 22, 31.8, 40]}
# plate y spans (cover the edge path z 8-41 with margin)
PLATE_Y = {-1: (-4.0, 11.5), +1: (-8.0, 7.0)}


def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def edge_point(z, side):
    s = part.section([0, 0, 1], [0, 0, z])
    v = s.vertices
    i = v[:, 0].argmax() if side > 0 else v[:, 0].argmin()
    return v[i]


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
