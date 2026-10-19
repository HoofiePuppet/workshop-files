"""Stage 3a: re-solve the thumb for the shell build.
The thumb hinge must sit outside the child's cavity (with a wall), so its pivot moves out of the thenar.
For each candidate pivot: find the pinch pose (thumb pad meets the index+middle pads), derive the single
hinge axis from the open pose, and score palm overlap along the whole swing."""
import json, numpy as np, trimesh, manifold3d as mf
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as Rot
from scipy.interpolate import RegularGridInterpolator
from rlib import to_mf, to_tm
from sdf import Grid, sdf, to_manifold, smin, seg_dist
from lib_grid import load_skin

CFG = json.load(open('src/config.json')); P0 = json.load(open('src/thumb_poses.json'))
J = json.load(open('build/joints.json'))
SC = 1.1; OFF = 1.0
R_OPEN = Rot.from_quat(P0['open_quat'])


def pose_point(n, curl, p):
    info = J[n]['joints']; p = np.array(p, float)
    Ps = [np.array(i['O']) for i in info]; Xs = [np.array(i['x']) for i in info]
    for j in range(len(info)):
        R = trimesh.transformations.rotation_matrix(np.radians(-curl), Xs[j], Ps[j])
        p = (R @ np.r_[p, 1])[:3]
        for k in range(j + 1, len(info)):
            Ps[k] = (R @ np.r_[Ps[k], 1])[:3]; Xs[k] = R[:3, :3] @ Xs[k]
    return p


def pad_target(curl):
    # the rubber pads are the contact: aim 1 mm off each pad, midway between index and middle
    pts = []
    for n in ('index', 'middle'):
        info = J[n]['joints'][-1]; z = np.array(info['z'])
        pts.append(pose_point(n, curl, np.array(J[n]['tip_pad']) - z * 0.5))
    return (pts[0] + pts[1]) / 2


def thumb_rest_field(pivot):
    """Thumb (scaled 1.1 about the old pivot), grown 1 mm, with an organic base blended to the new pivot."""
    t = trimesh.load('src/thumb_rest.stl')
    piv0 = np.array(CFG['thumb_pivot'])
    t.apply_translation(-piv0); t.apply_scale(SC); t.apply_translation(piv0)
    lo = np.minimum(t.bounds[0], pivot) - 12; hi = np.maximum(t.bounds[1], pivot) + 12
    g = Grid(lo, hi, 0.3)
    f = sdf(t, g) - OFF
    X, Y, Z = g.points(); Pg = np.stack([X, Y, Z], -1)
    base = t.vertices[t.vertices[:, 1] < t.bounds[0][1] + 1.0].mean(0)       # centre of the cut base face
    cap = seg_dist(Pg, np.asarray(pivot, float), base) - 6.8
    return smin(f, cap, 4.0), g, t


def main():
    d, g = load_skin()
    Mo = to_manifold(d['outer'], g)
    from cavity import cavity_field
    CAV = RegularGridInterpolator(g.axes(), cavity_field(d, g), bounds_error=False, fill_value=50)
    OUTER = RegularGridInterpolator(g.axes(), d['outer'], bounds_error=False, fill_value=50)
    best = None
    t = trimesh.load('src/thumb_rest.stl'); piv0 = np.array(CFG['thumb_pivot'])
    t.apply_translation(-piv0); t.apply_scale(SC); t.apply_translation(piv0)
    V = t.vertices
    cands = []
    for x in np.arange(-40, -25, 1.5):
        for y in np.arange(32, 50, 2.0):
            for z in np.arange(-18, -4, 1.5):
                p = np.array([x, y, z])
                if CAV([p])[0] >= 9.0 and OUTER([p])[0] <= 7.0:
                    cands.append(p)
    print('candidate pivots', len(cands))
    th_for = [pad_target(c) for c in (35, 42, 49, 56)]
    scored = []
    for p in cands:
        far = V[np.argmax(np.linalg.norm(V - p, axis=1))] - p
        for curl, T in zip((35, 42, 49, 56), th_for):
            if np.linalg.norm(T - p) > np.linalg.norm(far) + 3: continue
            def cost(rv):
                return np.sum((Rot.from_rotvec(rv).apply(far) + p - T) ** 2) + 0.2 * np.dot(rv, rv)
            r = min((minimize(cost, np.array(s0), method='Nelder-Mead', options={'maxiter': 3000, 'xatol': 1e-4, 'fatol': 1e-4})
                     for s0 in [(0, 0, 0), (-0.5, -0.1, -0.5), (0.3, 0.6, -0.2), (-0.3, 0.4, -0.7)]), key=lambda r: r.fun)
            miss = np.linalg.norm(Rot.from_rotvec(r.x).apply(far) + p - T)
            if miss < 1.5:
                scored.append((curl, p, r.x, miss)); break
    print('pivots that reach a pinch', len(scored))
    # palm overlap along the swing for the reachable ones (coarse thumb mesh for speed)
    tc = t.simplify_quadric_decimation(face_count=4000) if hasattr(t, 'simplify_quadric_decimation') else t
    res = []
    for curl, p, rv, miss in scored:
        Rp = Rot.from_rotvec(rv); rel = Rp * R_OPEN.inv(); ax = rel.as_rotvec(); ang = np.linalg.norm(ax); ax /= ang
        tot = 0
        for f in (0, 0.33, 0.66, 1.0):
            R = Rot.from_rotvec(ax * ang * f) * R_OPEN
            tt = tc.copy(); M = np.eye(4); M[:3, :3] = R.as_matrix(); M[:3, 3] = p - R.as_matrix() @ p
            tt.apply_transform(M)
            o = to_mf(tt) ^ Mo
            o = o - mf.Manifold.sphere(13, 32).translate(list(p))
            tot += o.volume()
        res.append((curl + tot / 40.0, curl, tot, p, rv, ax, np.degrees(ang), miss))
    res.sort(key=lambda r: r[0])
    for r in res[:8]:
        print(f'curl {r[1]} overlap {r[2]:.0f} pivot {r[3]} swing {r[6]:.1f} miss {r[7]:.2f}')
    s, curl, tot, p, rv, ax, ang, miss = res[0]
    json.dump({'pivot': p.tolist(), 'scale': SC, 'offset': OFF, 'pinch_rotvec': rv.tolist(), 'open_quat': R_OPEN.as_quat().tolist(),
               'hinge_axis': ax.tolist(), 'swing_deg': float(ang), 'pinch_curl_deg': float(curl), 'pinch_miss': float(miss),
               'pivot0': CFG['thumb_pivot']}, open('build/thumb_solution.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
