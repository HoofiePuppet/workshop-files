"""v3.4 thumb-mount brace: fill the space round the palm's thumb barrel back to the hand.

palm2.py carves the thumb's path out of the palm with a generous swept shape, then adds the barrel back on
top. That left the barrel's far end hanging off a thin strip, with an open window underneath that printed
loose or distorted, and supports damaged it (test prints). This step fills every bit of that space the thumb
does not actually need, so the barrel sits on solid plastic grown from the palm wall.

Filled: inside the natural skin outline (outer skin field), within BR_R of the barrel axis, touching the palm.
Kept clear: the real thumb (with its teeth) swept over its whole swing and slid 1.2 mm to the far cheek
(loosened), plus MARGIN; the index finger's swing -4..64 deg per joint plus MARGIN; the child's hand cavity plus CAV_GAP;
the TPU cover plus FLAP_GAP. The knob seat cut in thumb_lock.py runs after this, so the knob and the room to
turn it stay as before.
"""
import json, os, numpy as np, trimesh, manifold3d as mf
from scipy import ndimage
from scipy.spatial.transform import Rotation as Rot
from scipy.interpolate import RegularGridInterpolator
from skimage import measure

H = 0.3                 # voxel size (mm)
BOX = 21.0              # half size of the work box round the pivot
MARGIN = 0.8            # clearance to the moving thumb and the index finger
CAV_GAP = 0.8           # plastic kept this far off the child's hand cavity
FLAP_GAP = 0.4          # ... and off the TPU cover
SKIN_OUT = 0.3          # may sit this far outside the natural skin outline (smooth blend)
BR_R, BR_U = 12.5, 11.0 # radius round the barrel axis / half length along it (smooth bounds)
SLEEVE_R = 8.5          # outside the skin the fill may stand out to this radius round the barrel axis (round, organic)
HEAD_U = 1.5            # no fill past this toward the knob end (it is solid there already; the knob needs its room)
SMOOTH = 0.6            # gaussian sigma (mm) on the final field: rounded edges, no voxel steps


def _to_mf(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def _to_tm(m):
    o = m.to_mesh(); return trimesh.Trimesh(o.vert_properties[:, :3], o.tri_verts, process=False)


def _contains(m, pts):
    return _to_tm(m).contains(pts) if isinstance(m, mf.Manifold) else m.contains(pts)


def brace(palm, thumb, B='build/'):
    import palm2 as P2
    from pose import load, pose_finger
    TS = json.load(open(B + 'thumb_solution.json')); PJ = json.load(open(B + 'palm.json'))
    piv = np.array(TS['pivot']); ax = np.array(TS['hinge_axis']); ax /= np.linalg.norm(ax)
    xj = np.array(PJ['thumb_frame']['x']); hs = PJ['thumb_head']; R_open = Rot.from_quat(TS['open_quat'])
    # thumb swept (rest-pose thumb -> world at each swing angle), also loosened toward the far cheek
    sw = []
    for a in np.linspace(-3, TS['swing_deg'] + 3, 48):
        R = Rot.from_rotvec(ax * np.radians(a)) * R_open
        M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = piv - R.as_matrix() @ piv
        for s in (0.0, -hs * 0.6, -hs * 1.2):
            M2 = M.copy(); M2[:3, 3] += s * xj; sw.append(thumb.transform(M2[:3, :]))
    thumb_sw = _to_tm(mf.Manifold.batch_boolean(sw, mf.OpType.Add))
    J, segs = load(B.rstrip('/'))
    idx = []
    for c in list(range(-4, 65, 4)):            # check_fingers range is -4..60 per joint (wrist -50 gives 54-60)
        idx += pose_finger(J, segs, 'index', c)
    idx_sw = _to_tm(mf.Manifold.batch_boolean(idx, mf.OpType.Add))
    flap = trimesh.load(B + 'palm_flap.stl')
    palm_t = _to_tm(palm)

    ax_ = np.arange(-BOX, BOX + H / 2, H)
    X, Y, Z = np.meshgrid(ax_ + piv[0], ax_ + piv[1], ax_ + piv[2], indexing='ij'); shape = X.shape
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1); del X, Y, Z
    inpalm = palm_t.contains(P).reshape(shape)
    inS = thumb_sw.contains(P).reshape(shape)
    inI = idx_sw.contains(P).reshape(shape)
    inF = flap.contains(P).reshape(shape)
    d, g0 = P2.load_skin()
    cv = P2.Sampler(P2.cavity_field(d, g0), g0)(P.astype(np.float32)).reshape(shape)
    outer = RegularGridInterpolator(g0.axes(), d['outer'], bounds_error=False, fill_value=20)(P).reshape(shape)
    del d
    edt = lambda m: ndimage.distance_transform_edt(~m) * H - ndimage.distance_transform_edt(m) * H   # + outside
    Q = P - piv; u = (Q @ xj).reshape(shape); rad = np.linalg.norm(Q - np.outer(Q @ xj, xj), axis=1).reshape(shape)
    # the barrel stands out past the natural skin, so the skin alone can't bound the fill: also allow a round
    # sleeve round the barrel axis (a convex hull here left flat, boxy faces)
    hull_f = rad - SLEEVE_R
    F = np.maximum.reduce([
        MARGIN - edt(inS),                      # clear of the moving thumb
        MARGIN - edt(inI),                      # clear of the index finger
        CAV_GAP - cv,                           # clear of the child's hand
        FLAP_GAP - edt(inF),                    # clear of the cover
        np.minimum(outer - SKIN_OUT, hull_f),   # inside the natural hand outline, or the hull round the barrel
        rad - BR_R, np.abs(u) - BR_U,           # near the barrel
        hs * u - HEAD_U,                        # far (cheek) side only
    ]).astype(np.float32)
    if os.environ.get('BRACE_DEBUG'):
        names = ['thumb', 'index', 'cavity', 'cover', 'outline', 'radius', 'length']
        Fs = np.stack([MARGIN - edt(inS), MARGIN - edt(inI), CAV_GAP - cv, FLAP_GAP - edt(inF),
                       np.minimum(outer - SKIN_OUT, hull_f), rad - BR_R, np.abs(u) - BR_U, hs * u - HEAD_U])
        np.savez_compressed('/home/claude/sol/brace_dbg.npz', arg=np.argmax(Fs, 0).astype(np.int8), F=F, inpalm=inpalm, inS=inS, u=u, P=P.reshape(shape + (3,)))
    fill = (F < 0) & ~inpalm
    lab, n = ndimage.label(fill)
    touch = ndimage.binary_dilation(inpalm, iterations=1)
    keep_ids = [i for i in range(1, n + 1) if ((lab == i) & touch).any() and (lab == i).sum() * H ** 3 > 2.0]
    keep = np.isin(lab, keep_ids)
    vol = keep.sum() * H ** 3
    # field for meshing: the fill region, slightly overlapping the palm so the union is seamless
    G = np.where(keep, np.minimum(F, -H), 1.0)
    G = np.where(inpalm & ndimage.binary_dilation(keep, iterations=3), -0.6, G)   # overlap into the palm
    G = ndimage.gaussian_filter(G.astype(np.float32), SMOOTH / H)
    G = np.maximum(G, np.maximum(MARGIN - 0.1 - edt(inS), MARGIN - 0.1 - edt(inI)))   # smoothing must not creep into the paths
    G = np.pad(G, 1, constant_values=1.0)
    vs, fs, _, _ = measure.marching_cubes(G, 0.0, spacing=(H, H, H))
    o = np.array([ax_[0], ax_[0], ax_[0]]) + piv - H
    bm = trimesh.Trimesh(vs + o, fs[:, ::-1] if False else fs)
    if bm.volume < 0: bm.invert()
    bmf = _to_mf(bm)
    if bmf.status() != mf.Error.NoError or bmf.volume() < 1:
        bm.fix_normals(); bmf = _to_mf(bm)
    print('brace: %d piece(s), fill %.0f mm3 (mesh %.0f mm3)' % (len(keep_ids), vol, bmf.volume()), flush=True)
    return bmf, thumb_sw, idx_sw
