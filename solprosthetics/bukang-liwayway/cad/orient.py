"""v3.2: finger segments and the thumb print at 45 deg: knuckle end down, tip up, the back (nail side) facing
up and the hinge axis level, so supports only touch the palm side (user's test print: lying them on their side
left rough support scars). Other parts: pick print orientations: least support area (faces pointing more than 45 deg down, not on the bed),
with a stable footprint. Fingers and thumb are laid with the screw axis vertical (round holes, layers
along the finger for bending strength) and only the up/down choice is searched.
Writes stl/ (print-ready, already turned) and build/orient.json"""
import json, os, glob, numpy as np, trimesh
from scipy.spatial.transform import Rotation as Rot

OUT = 'stl'; os.makedirs(OUT, exist_ok=True)
J = json.load(open('build/joints.json')); PJ = json.load(open('build/palm.json'))


def support_area(m, R):
    v = m.vertices @ R.T; n = m.face_normals @ R.T
    zmin = v[:, 2].min()
    fz = v[m.faces][:, :, 2].mean(1)
    over = (n[:, 2] < -0.707) & (fz > zmin + 0.4)
    bed = (n[:, 2] < -0.95) & (fz <= zmin + 0.4)
    return m.area_faces[over].sum(), m.area_faces[bed].sum()


def best(m, cands):
    res = []
    for R in cands:
        s, b = support_area(m, R)
        res.append((s - 3.0 * b, s, b, R))
    res.sort(key=lambda r: r[0])
    return res[0]


def axis_up(axis):
    """Rotations taking `axis` to +z and to -z, plus spins about z (spin does not change supports)."""
    a = np.asarray(axis, float); a /= np.linalg.norm(a)
    out = []
    for s in (1, -1):
        r, _ = Rot.align_vectors([[0, 0, s]], [a])
        out.append(r.as_matrix())
    return out


def sphere_cands(n=200):
    rng = np.random.default_rng(3)
    return [Rot.random(random_state=rng.integers(1e9)).as_matrix() for _ in range(n)] + [np.eye(3)] + \
           [Rot.from_euler('x', a, degrees=True).as_matrix() for a in (90, 180, 270)] + \
           [Rot.from_euler('y', a, degrees=True).as_matrix() for a in (90, 270)]


def tilt45(x, d, z):
    """Rotation taking the up direction (d + z)/sqrt2 to +z and the hinge axis x to +x."""
    x = np.asarray(x, float); x /= np.linalg.norm(x)
    u = np.asarray(d, float) + np.asarray(z, float); u -= x * (u @ x); u /= np.linalg.norm(u)
    return np.stack([x, np.cross(u, x), u])


def save(name, m, R, info):
    t = m.copy(); M = np.eye(4); M[:3, :3] = R; t.apply_transform(M)
    t.apply_translation([-t.bounds[0][0] - (t.bounds[1][0] - t.bounds[0][0]) / 2, -t.bounds[0][1] - (t.bounds[1][1] - t.bounds[0][1]) / 2, -t.bounds[0][2]])
    t.export(f'{OUT}/{name}.stl')
    T = M.copy(); T[:3, 3] = t.bounds[0] * 0 + (t.vertices[0] - (R @ m.vertices[0]))
    info[name] = {'support_mm2': round(float(support_area(m, R)[0])), 'bed_mm2': round(float(support_area(m, R)[1])),
                  'size_mm': (t.bounds[1] - t.bounds[0]).round(1).tolist(), 'watertight': bool(t.is_watertight),
                  'volume_cm3': round(float(t.volume) / 1000, 2), 'matrix': T.tolist()}
    print(name, info[name])


def main():
    info = {}
    for n in ('index', 'middle', 'ring', 'little'):
        for f in sorted(glob.glob(f'build/fingers/{n}-*.stl')):
            m = trimesh.load(f)
            k = int(os.path.basename(f)[-5]) - 1
            jk = J[n]['joints'][k]
            R = tilt45(jk['x'], jk['d'], jk['z'])
            save(f'finger-{n}-{k + 1}', m, R, info)
    m = trimesh.load('build/thumb.stl')
    tp = PJ['thumb_print']
    x = np.array(tp['x']); u = np.array(tp['up'])
    R = np.stack([x, np.cross(u, x), u])
    save('thumb', m, R, info)
    for part in ('palm_back', 'palm_flap', 'cuff'):
        m = trimesh.load(f'build/{part}.stl')
        _, s, b, R = best(m, sphere_cands())
        if part in ('palm_back', 'palm_flap'):
            # (v3.2b) the TPU cover is locked to the same turn: standing on its wrist-end edge, least support,
            # and the snip-off stabilizer fins (flap_print.py) are built for that orientation
            # stand it on the wrist end: a real footprint (with a brim) and the logo on a near-vertical
            # face, so no support ever touches the pressed-in logo
            R = Rot.from_euler('x', 90, degrees=True).as_matrix()
        save(part, m, R, info)
    json.dump(info, open('build/orient.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
