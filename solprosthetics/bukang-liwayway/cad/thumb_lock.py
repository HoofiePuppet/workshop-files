"""v3.3 thumb rosette lock: the thumb is set to any of 18 positions (20 deg apart) and locked by its screw.

Runs after palm2.py and changes build/thumb.stl and build/palm_back.stl (hand frame):
- thumb tongue: a ring of 18 radial teeth on the face toward the screw head, and a 4.0 mm hole for an
  M3 x 4 brass heat-set insert (pushed in from that face);
- palm barrel: the head-side cheek face moves 0.4 mm in (0.1 mm from the tongue) and gets the matching
  grooves, phased so the pinch pose is one of the positions; the far cheek keeps its 0.5 mm, which is
  the travel the teeth need to come free when the screw is loosened;
- screw: M3 x 12 button head from the head side, through the near cheek, into the insert in the tongue,
  tip into a 3.4 mm hole in the far cheek (keeps the thumb aligned). Tightening pulls the tongue's teeth
  into the grooves; a quarter turn loose lets the thumb swing to the next position.
"""
import json, numpy as np, trimesh, manifold3d as mf
from scipy.spatial.transform import Rotation as Rot

N_TEETH, H_TOOTH = 12, 1.0          # v3.4: 12 teeth, 30 deg steps, 1.0 mm tall (18 x 0.45 printed too small to work)
R_IN, R_OUT = 2.5, 4.4              # tooth ring (tongue disc radius 4.5, insert hole radius 2.0); v3.4 wider
TONGUE_HALF = 3.0                   # tongue face on the head (teeth) side
TONGUE_FAR = 2.4                    # v3.4: far face (was 3.0): 1.2 mm free travel to the far cheek, so 1.0 mm teeth come free
FACE_NEW = 3.1                      # head-side cheek face (was 3.5): 0.1 mm from the tongue when locked
GROOVE_EXTRA = 0.05                 # tip clearance in the grooves
SLAB_R = 6.3                        # inside the 6.5 mm barrel
TAPER_R = 8.5                       # the trim fades out here
TRIM_R = 6.7                        # thumb eye trimmed to an even 6 mm wide inside the barrel radius only (a trim out to 8.5 cut into the thumb body)
SLOT_FACE = 3.6                     # measured: both cheek faces of the v3.2 slot
SCREW = 20                          # v3.3b knob: M3 x 20 hex head (DIN 933), its head held in the knob's hex pocket
SEAT = 7.0                          # (v3.3a button-head seat; now solid up to the knob seat)
BORE_R = 3.6                        # v3.2 head-side bore, filled solid up to the seat
INSERT_D, INSERT_L = 4.0, 4.0
# v3.3b tool-free knob, captive: the barrel end is squared off at FACE_K and carries a round post with a small rim.
# The knob clips over the rim with 4 short PETG fingers; the bolt head sits in the knob's hex pocket (pushed in from
# below) and bears on the post top. Loosening lifts the head, which lifts the knob, until the fingers' lip meets the
# rim after KNOB_TRAVEL: enough to free the teeth (0.45 mm), not enough for the bolt to leave the insert.
FACE_K = 9.0                        # flat seat on the barrel end (the end face was slanted, 8.7 .. 11.3 mm)
CB_R = 7.6                          # palm cut back to the seat inside this radius (room for the knob)
CB_FLARE = 2.0                      # ...then opening out at 45 deg so its edge meets the skin at a gentle angle
KU = 0.4                            # v3.4: rim, post and the knob above its lip move up by this, so the lip catches after KNOB_TRAVEL
POST_R, POST_TOP = 3.55, 12.6 + KU       # post; the bolt head bears on its top
FL_R, FL0, FL1 = 4.0, 11.3 + KU, 11.9 + KU    # rim on the post: radius, underside, top (then a 45 deg lead-in)
HEX_AF, HEAD_K = 5.55, 2.0          # M3 hex head: 5.5 across flats, 2 mm tall (snug pocket)
KNOB_TRAVEL = 1.4                   # v3.4: frees the 1.0 mm teeth (was 1.0 for 0.45 mm teeth)
SK_IN, SK_OUT, LIP_IN = FL_R + 0.2, FL_R + 1.2, POST_R + 0.2   # skirt (fingers) and lip radii
GRIP_R, KNOB_TOP = 7.0, POST_TOP + HEAD_K + 2.4

B = 'build/'
# palm2's output is kept as *_prelock.stl, so this step can be re-run on its own (TL_RERUN=1) without stacking twice
import shutil, os
if os.environ.get('TL_RERUN'):
    SRC = {n: n + '_prelock.stl' for n in ('palm_back', 'thumb')}
else:
    for _n in ('palm_back', 'thumb'): shutil.copy(B + _n + '.stl', B + _n + '_prelock.stl')
    SRC = {n: n + '.stl' for n in ('palm_back', 'thumb')}
PJ = json.load(open(B + 'palm.json')); TS = json.load(open(B + 'thumb_solution.json'))
tf = PJ['thumb_frame']; piv = np.array(tf['pivot']); xj, yj, zj = (np.array(tf[k]) for k in 'xyz')
hs = PJ['thumb_head']                                   # +1 / -1: which end of the axis has the screw head
ax_w = np.array(TS['hinge_axis']); R_open = Rot.from_quat(TS['open_quat'])
Rinv = R_open.inv(); xr, yr, zr = Rinv.apply(xj), Rinv.apply(yj), Rinv.apply(zj)
SWING = TS['swing_deg']

to_mf = lambda t: mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
def to_tm(m):
    o = m.to_mesh(); return trimesh.Trimesh(o.vert_properties[:, :3], o.tri_verts, process=False)


def frame(O, x, d, z):
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, d, z, O; return M


def cyl_u(r, u0, u1, M, seg=48):
    """cylinder along the local x (u) axis from u0 to u1, placed by frame M."""
    lo, hi = sorted((u0, u1))
    c = mf.Manifold.cylinder(hi - lo, r, r, seg).rotate([0, 90, 0]).translate([lo, 0, 0])
    return c.transform(M[:3, :])


def rev_u(prof, M, sgn, seg=96):
    """solid of revolution about the local u axis from a [(r, u), ...] profile (u >= 0 side), placed by M on side sgn."""
    rev = mf.Manifold.revolve(mf.CrossSection([[list(map(float, q)) for q in prof]]), seg).rotate([0, 90, 0])
    if sgn < 0: rev = rev.mirror([1, 0, 0])
    return rev.transform(M[:3, :])


def tooth_ring(M, base, height, sgn, phase_deg=0.0, r_in=R_IN, r_out=R_OUT, back=0.35):
    """18 radial wedge teeth on a plane u = sgn*base, pointing to +sgn, plus a thin base ring under them."""
    p = 2 * np.pi / N_TEETH; parts = []
    for k in range(N_TEETH):
        tc = np.radians(phase_deg) + k * p; ta, tb = tc - p / 2, tc + p / 2
        pts = []
        for r in (r_in, r_out):
            for t in (ta, tb):
                pts += [[sgn * (base - back), r * np.cos(t), r * np.sin(t)], [sgn * base, r * np.cos(t), r * np.sin(t)]]
            pts += [[sgn * (base + height), r * np.cos(tc), r * np.sin(tc)]]
        parts.append(mf.Manifold.hull_points(np.array(pts, np.float64)))
    ring = mf.Manifold.batch_boolean(parts, mf.OpType.Add)
    return ring.transform(M[:3, :])


Mr = frame(piv, xr, yr, zr)                              # thumb, rest (open) pose
Mw = frame(piv, xj, yj, zj)                              # palm

# ---------------- thumb
thumb = to_mf(trimesh.load(B + SRC['thumb']))
v0 = thumb.volume()
# even 6 mm eye and neck between the cheeks: free travel of 0.6 mm to the far cheek when loosened
# tapered, so the 7 mm neck blends into the 6 mm eye without a ledge: full 0.5 mm trim inside the barrel
# radius, fading to nothing at TAPER_R
def trim_side(sgn, half=TONGUE_HALF):
    prof = mf.CrossSection([[[0.0, half], [TRIM_R, half], [TAPER_R, TONGUE_HALF + 0.5], [TAPER_R + 0.01, 12.0], [0.0, 12.0]]])
    rev = mf.Manifold.revolve(prof, 96)                    # around the 2D y axis -> 3D z axis is the height
    rev = rev.rotate([0, 90, 0])                           # height (z) -> local +x (u)
    if sgn < 0: rev = rev.mirror([1, 0, 0])
    return rev.transform(Mr[:3, :])
thumb = thumb - trim_side(hs) - trim_side(-hs, TONGUE_FAR)
teeth = tooth_ring(Mr, TONGUE_HALF, H_TOOTH, hs, back=1.0)
# solid ring under the teeth: the tongue's edge is rounded, and without it small air pockets were left
# sealed between the tooth bases and the curved face
base = cyl_u(R_OUT, hs * (TONGUE_HALF - 1.0), hs * TONGUE_HALF, Mr, seg=96) - cyl_u(R_IN, -20, 20, Mr, seg=48)
thumb = thumb + teeth + base
thumb = thumb - cyl_u(INSERT_D / 2, hs * (TONGUE_HALF + 2.0), hs * (TONGUE_HALF - INSERT_L), Mr)   # insert from the head-side face
print('thumb: teeth + insert hole, volume %.0f -> %.0f mm3' % (v0, thumb.volume()))

# ---------------- palm: tongue teeth at the PINCH pose define the grooves (the pattern repeats every 20 deg,
# so every position 20 deg apart from the pinch meshes too)
pinch = Rot.from_rotvec(ax_w * np.radians(SWING)) * R_open          # world <- thumb model, at pinch
Mp = np.eye(4); Mp[:3, :3] = pinch.as_matrix(); Mp[:3, 3] = piv - Mp[:3, :3] @ piv     # model -> world (as check_thumb.py)
grooves = tooth_ring(Mr, TONGUE_HALF, H_TOOTH + GROOVE_EXTRA + (FACE_NEW - TONGUE_HALF), hs, back=0.0,
                     r_in=R_IN - 0.15, r_out=R_OUT + 0.15).transform(Mp[:3, :])
palm = to_mf(trimesh.load(B + SRC['palm_back'])); v1 = palm.volume()
# v3.4: brace the barrel: fill the space round it back to the palm wall, outside the thumb's real path
if not os.environ.get('NO_BRACE'):
    from brace import brace
    _bm, _tsw, _isw = brace(palm, thumb, B)
    palm = palm + _bm
    print('palm: barrel brace added, volume %.0f -> %.0f mm3' % (v1, palm.volume()), flush=True)
    # support keep-out for the slicer: the hinge (the air the thumb's tongue and eye use, out to r 8.5, and the
    # bolt bore) must never get support: it scars the cheek faces, the teeth grooves and the bore. With the brace
    # nothing there needs support any more. back_print.py adds this to the support blocker.
    # a plain solid (the swept thumb cut to this zone came out as touching fragments): the slot between the cheeks
    # with the groove faces (u -4.4 .. +3.7) out to r 8.5, plus the bolt bore; overlapping the part does no harm
    _keep = cyl_u(8.5, hs * (FACE_NEW + H_TOOTH + 0.3), -hs * (SLOT_FACE + 0.1), Mw, seg=72) + cyl_u(1.8, -14.0, 9.0, Mw, seg=32)
    to_tm(_keep).export(B + 'thumb_hinge_keepout.stl')
    print('hinge support keep-out: %.0f mm3' % _keep.volume(), flush=True)
slab = cyl_u(SLAB_R, hs * FACE_NEW, hs * (SLOT_FACE + 0.4), Mw, seg=72)   # head-side cheek moves in to 0.1 mm from the tongue
palm = palm + slab
# fill v3.2's head-side bore up to the new seat: 3.9 mm of solid cheek under the screw head (was 0.9 mm)
palm = palm + cyl_u(BORE_R, hs * FACE_NEW, hs * SEAT, Mw, seg=72)
palm = palm - grooves
# screw path: the near-cheek clearance (3.4) and the head recess are already there; the far cheek gets a
# 3.4 mm hole where the M3 x 12 tip lands (it was a 2.6 mm pilot for the old M3 x 20)
# v3.3b knob seat: square the barrel end off at FACE_K (small chamfer), cut the palm back to it inside CB_R, post + rim
palm = palm + rev_u([(0, SEAT - 0.5), (SLAB_R, SEAT - 0.5), (SLAB_R, FACE_K - 0.6), (SLAB_R - 0.6, FACE_K), (0, FACE_K)], Mw, hs)
# cut-back flares out at 45 deg (a straight wall met the outer skin at a grazing angle and left a 0.5 mm knife edge
# with a pinhole, seen in the slicer)
palm = palm - rev_u([(0, FACE_K), (CB_R - 0.6, FACE_K), (CB_R, FACE_K + 0.6), (CB_R + CB_FLARE, FACE_K + 0.6 + CB_FLARE), (CB_R + CB_FLARE, 40.0), (0, 40.0)], Mw, hs)
palm = palm + rev_u([(0, FACE_K - 0.5), (POST_R, FACE_K - 0.5), (POST_R, FL0), (FL_R, FL0), (FL_R, FL1),
                     (POST_R, FL1 + (FL_R - POST_R)), (POST_R, POST_TOP), (0, POST_TOP)], Mw, hs)
seat = POST_TOP                                                           # bolt head bears here
tip = hs * (seat - SCREW)
palm = palm - cyl_u(1.7, hs * FACE_NEW, tip - hs * 0.8, Mw)
palm = palm - cyl_u(1.7, hs * (seat + 0.5), hs * (FACE_NEW - 0.01), Mw)   # near cheek and post

# the knob, in the hand frame, sitting on the bolt head (bolt tight)
def knob_shape():
    C = POST_TOP + HEAD_K                                                  # knob roof underside = head top
    body = rev_u([(0, 13.0 + KU), (GRIP_R - 0.5, 13.0 + KU), (GRIP_R, 13.5 + KU), (GRIP_R, KNOB_TOP - 0.8), (GRIP_R - 0.8, KNOB_TOP), (0, KNOB_TOP)], Mw, hs)
    skirt = rev_u([(LIP_IN, 9.4 + 0.4), (SK_IN - 0.05, 9.4), (SK_OUT - 0.3, 9.4), (SK_OUT, 9.7), (SK_OUT, 13.2 + KU), (LIP_IN, 13.2 + KU)], Mw, hs)
    k = body + skirt
    for i in range(12):                                                    # grip flutes
        a = 2 * np.pi * i / 12; off = (np.cos(a) * yj + np.sin(a) * zj) * (GRIP_R + 0.35)
        M2 = Mw.copy(); M2[:3, 3] = piv + off
        k = k - cyl_u(0.9, hs * (12.5 + KU), hs * (KNOB_TOP + 1), M2, seg=20)
    k = k - rev_u([(0, 9.0), (SK_IN, 9.0), (SK_IN, 13.0 + KU), (0, 13.0 + KU)], Mw, hs)        # cavity round the post and rim
    k = k - rev_u([(0, 9.0), (LIP_IN, 9.0), (LIP_IN, 13.0 + KU), (0, 13.0 + KU)], Mw, hs)
    # lip: the skirt's inner edge below the rim (LIP_IN .. SK_IN) stays solid from 9.4 to 10.3, lead-in below
    k = k + rev_u([(LIP_IN, 9.75), (SK_IN, 9.4), (SK_IN + 0.4, 9.4), (SK_IN + 0.4, 10.3), (LIP_IN, 10.3)], Mw, hs)
    hexp = mf.Manifold.cylinder(C - 13.0 - KU, HEX_AF / np.sqrt(3), HEX_AF / np.sqrt(3), 6).rotate([0, 90, 0])
    hexp = hexp.translate([13.0 + KU, 0, 0])
    if hs < 0: hexp = hexp.mirror([1, 0, 0])
    k = k - hexp.transform(Mw[:3, :])
    k = k - cyl_u(1.75, hs * (12.0 + KU), hs * C, Mw)                             # bolt shank
    for i in range(4):                                                     # 4 slits -> 4 fingers
        a = np.pi / 4 + i * np.pi / 2; d_ = np.cos(a) * yj + np.sin(a) * zj
        Ms = np.eye(4); Ms[:3, 0], Ms[:3, 1], Ms[:3, 2], Ms[:3, 3] = xj * hs, d_, np.cross(xj * hs, d_), piv
        k = k - mf.Manifold.cube([12.9 + KU - 9.0, SK_OUT + 1, 0.9]).translate([9.0, 0, -0.45]).transform(Ms[:3, :])
    return max(k.decompose(), key=lambda q: q.volume())          # drop flute slivers
knob = knob_shape()
print('knob: volume %.0f mm3, pieces %d' % (knob.volume(), len(knob.decompose())))
print('palm: cheek slab + grooves + screw path, volume %.0f -> %.0f mm3' % (v1, palm.volume()))
print('screw M3 x %d: head seat u=%+.2f, insert u=%+.2f..%+.2f, tip u=%+.2f' % (SCREW, hs * seat, hs * TONGUE_HALF, hs * (TONGUE_HALF - INSERT_L), tip))

# ---------------- check: the tongue at every 20 deg position from the pinch back to the open pose sits in
# the palm without touching (teeth in the grooves)
fails = []
STEP = 360.0 / N_TEETH
for k in range(int(SWING // STEP) + 1):
    a = SWING - STEP * k
    Ra = Rot.from_rotvec(ax_w * np.radians(a)) * R_open
    Ma = np.eye(4); Ma[:3, :3] = Ra.as_matrix(); Ma[:3, 3] = piv - Ma[:3, :3] @ piv
    hinge_zone = cyl_u(7.5, -8, 8, Mr)
    tk = (thumb ^ hinge_zone).transform(Ma[:3, :])
    ov = (tk ^ palm).volume()
    print('  position %5.1f deg from open: thumb/palm overlap %.3f mm3' % (a, ov))
    if ov > 0.05: fails.append(a)
# loosened: the tongue slides 1.1 mm (of its 1.2) to the far side, the teeth must clear the cheek face
Ml = np.eye(4); Ml[:3, 3] = -hs * 1.1 * xj
Ra = Rot.from_rotvec(ax_w * np.radians(SWING - STEP / 2)) * R_open     # half-way between two positions
Ma = np.eye(4); Ma[:3, :3] = Ra.as_matrix(); Ma[:3, 3] = piv - Ma[:3, :3] @ piv
tk = (thumb ^ cyl_u(7.5, -8, 8, Mr)).transform(Ma[:3, :]).transform(Ml[:3, :])
print('  loosened, between positions: overlap %.3f mm3' % (tk ^ palm).volume())

# knob checks: tight (on the head) and lifted to the stop; against the palm and the thumb at every position
for lift in (0.0, KNOB_TRAVEL):
    kk = knob.translate((xj * hs * lift).tolist())
    print('  knob lifted %.1f: knob/palm overlap %.3f mm3' % (lift, (kk ^ palm).volume()))
    for k_ in range(int(SWING // STEP) + 1):
        a = SWING - STEP * k_
        Ra = Rot.from_rotvec(ax_w * np.radians(a)) * R_open
        Ma = np.eye(4); Ma[:3, :3] = Ra.as_matrix(); Ma[:3, 3] = piv - Ma[:3, :3] @ piv
        ov = (thumb.transform(Ma[:3, :]) ^ kk).volume()
        if ov > 0.001: print('    thumb at %.1f deg hits the knob: %.3f mm3' % (a, ov)); fails.append(('knob', a))
# the lip must catch the rim: lifting further than the travel must collide
kk = knob.translate((xj * hs * (KNOB_TRAVEL + 0.3)).tolist())
print('  knob lifted past the stop (+0.3): overlap with the rim %.3f mm3 (must be > 0)' % (kk ^ palm).volume())
import os
to_tm(knob).export(B + 'thumb_knob.stl')
# print version: knob top down on the bed, skirt fingers up
km = to_tm(knob); up = -xj * hs                                  # print 'up' = toward the slot
Rp = trimesh.geometry.align_vectors(up, [0, 0, 1]); km.apply_transform(Rp)
km.apply_translation(-np.array([km.centroid[0], km.centroid[1], km.bounds[0, 2]]))
os.makedirs('stl', exist_ok=True); km.export('stl/thumb-knob.stl')
print('thumb-knob.stl: %.1f x %.1f x %.1f mm' % tuple(km.extents))
# v3.4: the brace closes the old v3.2 pilot's open end past the far cheek, which would leave a sealed air pocket in
# the palm; the palm has no designed internal voids, so keep its outer shell only = solid
_pt = to_tm(palm); _pt.merge_vertices(); _sh = _pt.split(only_watertight=False)
if len(_sh) > 1:
    _out = max(_sh, key=lambda q: q.volume)
    print('palm: filled %d sealed air pocket(s), %.1f mm3' % (len(_sh) - 1, sum(-q.volume for q in _sh if q is not _out)), flush=True)
    palm = to_mf(_out)
to_tm(thumb).export(B + 'thumb.stl'); to_tm(palm).export(B + 'palm_back.stl')
PJ['thumb_screw'] = SCREW; PJ['thumb_insert'] = True; PJ['thumb_knob'] = {'travel': KNOB_TRAVEL, 'bolt': 'hex'}; PJ['thumb_lock'] = {'teeth': N_TEETH, 'step_deg': 360 / N_TEETH}
json.dump(PJ, open(B + 'palm.json', 'w'), indent=1)
print('FAILED positions' if fails else 'all positions clear', fails)
