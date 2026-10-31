"""v3.3 art holder (simple): ONE TPU 95A part, no hardware. A short sleeve shaped from the index finger's middle
segment (it cannot turn on it), slid on over the fingertip, with a tube along its thumb side. Push a pencil, pen,
crayon, marker or paintbrush into the tube, point forward. Thin TPU fins inside the tube, all leaning the same way,
fold over as the tool goes in and hold anything from a thin brush handle (about 4.5 mm) to a fat marker
(about 11.5 mm), round, hex or triangular.
Prints standing on its back end, no supports.
Writes build/art_holder.stl (hand frame, on the straight finger) and stl/art-holder.stl (print-ready)."""
import json, os, numpy as np, trimesh, manifold3d as mf, shapely
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
from rlib import to_mf, to_tm
from pose import load, pose_finger
from scipy.spatial.transform import Rotation as Rot

B = 'build/'
J = json.load(open(B + 'joints.json'))
info = J['index']['joints']
O1, O2 = np.array(info[1]['O']), np.array(info[2]['O'])
ed = (O2 - O1) / np.linalg.norm(O2 - O1)
ex = np.array(info[1]['x'], float); ex -= ed * (ex @ ed); ex /= np.linalg.norm(ex)
ez = np.cross(ex, ed)
if ez @ np.array(info[1]['z']) < 0: ez = -ez
s = -1.0 if (ex @ np.array([1.0, 0, 0])) > 0 else 1.0        # thumb side of the index, in local x

# ---------------- sizes
SLEEVE_FIT = -0.15        # inner outline vs the finger's (TPU: slight squeeze)
SLEEVE_WALL = 1.5
SLEEVE_L = 8.0
BORE = 11.8               # tube bore: the fattest marker (11.5) folds the fins flat against the wall
TUBE_WALL = 1.4
FIN_N, FIN_T, FIN_GAP = 6, 0.8, 4.4   # fins: count, thickness, the opening they leave (thinnest brush)
FIN_LEAN = 35.0           # deg off radial, all the same way: they fold over instead of buckling
TUBE_L = 18.0             # tube length along the finger (the sleeve part is 9 of it)
WEB_T = 3.0               # web joining sleeve and tube
GAP_TO_SLEEVE = 0.0


def lc(p):
    q = np.atleast_2d(p) - C0; return np.c_[q @ ex, q @ ed, q @ ez]


def M_local():            # local (x, z, along) -> hand frame
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = ex, ez, ed, C0; return M


seg2 = trimesh.load(B + 'fingers/index-2.stl'); seg3 = trimesh.load(B + 'fingers/index-3.stl')
L12 = (O2 - O1) @ ed
s_mid = 4.5 + (L12 - 4.5 - 3.5) / 2 + 0.5     # clear of the knuckle segment's barrel
C0 = O1 + ed * s_mid


def outline(mesh, s_from, s_to, step=0.5):
    polys = []
    for t in np.arange(s_from, s_to + 1e-6, step):
        sec = mesh.section(ed, O1 + ed * t)
        if sec is None: continue
        for e in sec.discrete:
            q = lc(e); p = Polygon(np.c_[q[:, 0], q[:, 2]]).buffer(0)
            if p.area > 1.0: polys.append(p)
    return unary_union(polys).convex_hull


def to_cs(poly):
    polys = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
    loops = []
    for p in polys:
        loops.append(np.asarray(p.exterior.coords)[:-1].tolist()); loops += [np.asarray(i.coords)[:-1].tolist() for i in p.interiors]
    return mf.CrossSection(loops, mf.FillRule.EvenOdd)


P0 = outline(seg2, s_mid - SLEEVE_L / 2, s_mid + SLEEVE_L / 2)
P_over = outline(seg2, s_mid + SLEEVE_L / 2, L12 + 1.0).union(outline(seg3, L12, L12 + 18.0, 1.0))
inner = P0.buffer(SLEEVE_FIT, join_style=1)
print('sleeve: finger outline %.1f x %.1f mm; sliding over the joint and fingertip needs %.0f%% stretch'
      % (P0.bounds[2] - P0.bounds[0], P0.bounds[3] - P0.bounds[1], 100 * max(0.0, P_over.length / inner.length - 1)), flush=True)
outer = P0.buffer(SLEEVE_WALL, join_style=1)
bx0 = outer.bounds[0] if s < 0 else outer.bounds[2]
zc = (P0.bounds[1] + P0.bounds[3]) / 2
R_out = BORE / 2 + TUBE_WALL
tc = np.array([bx0 + s * (R_out + 2.6), zc + 1.0])            # tube centre: beside the sleeve, a 4 mm web between
tube_ring = Point(tc).buffer(R_out, 96).difference(Point(tc).buffer(BORE / 2, 96))
fins = []
for i in range(FIN_N):
    a = np.radians(i * 360 / FIN_N + 15)
    L = BORE / 2 - FIN_GAP / 2 + 1.2                            # from 0.9 mm inside the wall to the opening
    f = shapely.geometry.box(0, -FIN_T / 2, L, FIN_T / 2)       # a fin pointing in from the wall (x = in)
    f = affinity.rotate(f, FIN_LEAN, origin=(0, 0))             # leaning
    f = affinity.translate(f, -BORE / 2 - 0.9, 0)               # root sunk 0.9 mm into the 1.4 mm wall
    f = affinity.rotate(f, np.degrees(a), origin=(0, 0), use_radians=False)
    fins.append(affinity.translate(f, tc[0], tc[1]))
fins = unary_union(fins).intersection(Point(tc).buffer(BORE / 2 + 0.5, 96)).difference(Point(tc).buffer(FIN_GAP / 2, 96))
tube2d = unary_union([tube_ring, fins])
# web: the strip that joins the sleeve and the tube, as tall as it can be inside both
web = shapely.geometry.box(min(bx0 - s * 1.0, tc[0]), tc[1] - 4.5, max(bx0 - s * 1.0, tc[0]), tc[1] + 4.5).difference(Point(tc).buffer(BORE / 2, 96)).difference(inner)
sleeve2d = outer.difference(inner)
sec_sleeve = unary_union([sleeve2d, web, tube2d]).difference(inner)
sec_free = unary_union([tube2d, web.difference(outer.buffer(0.6))])   # beyond the sleeve: tube and web only
s_back = -SLEEVE_L / 2
part = to_cs(sec_sleeve).extrude(SLEEVE_L).translate([0, 0, s_back])
part = part + to_cs(sec_free.buffer(0)).extrude(TUBE_L - SLEEVE_L).translate([0, 0, s_back + SLEEVE_L])
part = part.transform(M_local()[:3, :])
print('tube: bore %.1f mm, fins leave %.1f mm, %.1f mm long; outside %.1f mm' % (BORE, FIN_GAP, TUBE_L, 2 * R_out), flush=True)

try:                                    # optional local finishing step, not part of the published source
    from finish_private import finish_art_holder
    part = finish_art_holder(part, C0, ex, ed, ez, (bx0 + (tc[0] - s * BORE / 2)) / 2, s_back + TUBE_L / 2, tc[1])
except ImportError:
    pass

# ---------------- checks
seg2m = to_mf(seg2)
print('sleeve squeeze on the finger: %.1f mm3 (TPU; small is right)' % (part ^ seg2m).volume())
Jd, segs = load()
TS = json.load(open(B + 'thumb_solution.json')); piv = np.array(TS['pivot'])
thumb = to_mf(trimesh.load(B + 'thumb.stl'))
def ride(m, curl):
    P = [np.array(i['O']) for i in info]; X = [np.array(i['x']) for i in info]; out = m
    for j in range(2):
        R = trimesh.transformations.rotation_matrix(np.radians(-curl), X[j], P[j])
        out = out.transform(R[:3, :])
        for k in range(j + 1, len(info)): P[k] = (R @ np.r_[P[k], 1])[:3]; X[k] = R[:3, :3] @ X[k]
    return out
for curl in (0, 30, 49, 70):
    sg = pose_finger(Jd, segs, 'index', curl); hd = ride(part, curl)
    th_ = []
    _step = json.load(open('build/palm.json')).get('thumb_lock', {}).get('step_deg', 20)   # v3.4: 30 deg clicks
    for k in range(int(TS['swing_deg'] // _step) + 1):
        a = TS['swing_deg'] - _step * k
        R = Rot.from_rotvec(np.array(TS['hinge_axis']) * np.radians(a)) * Rot.from_quat(TS['open_quat'])
        M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = piv - R.as_matrix() @ piv
        th_.append(round((thumb.transform(M[:3, :]) ^ hd).volume(), 1))
    mid = sum((hd ^ q).volume() for q in pose_finger(Jd, segs, 'middle', curl))
    print('finger curl %2d: holder vs index tip %.1f, knuckle segment %.1f, middle finger %.1f mm3; vs thumb at its clicks (pinch first) %s mm3'
          % (curl, (hd ^ sg[2]).volume(), (hd ^ sg[0]).volume(), mid, th_), flush=True)

to_tm(part).export(B + 'art_holder.stl')
os.makedirs('stl', exist_ok=True)
t = to_tm(part); Rr = trimesh.geometry.align_vectors(ed, [0, 0, 1]); t.apply_transform(Rr)
t.apply_translation([-t.centroid[0], -t.centroid[1], -t.bounds[0, 2]]); t.export('stl/art-holder.stl')
json.dump({'bore': BORE, 'fin_gap': FIN_GAP}, open(B + 'art_holder.json', 'w'))
print('wrote stl/art-holder.stl (TPU 95A, one part)')
