"""Pick print orientations: least support area (faces pointing more than 45 deg down, not on the bed),
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
        x = J[n]['joints'][0]['x']
        for f in sorted(glob.glob(f'build/fingers/{n}-*.stl')):
            m = trimesh.load(f)
            _, s, b, R = best(m, axis_up(x))
            save(f'finger-{n}-{os.path.basename(f)[-5]}', m, R, info)
    m = trimesh.load('build/thumb.stl')
    TS = json.load(open('build/thumb_solution.json'))
    R_open = Rot.from_quat(TS['open_quat'])
    _, s, b, R = best(m, axis_up(R_open.inv().apply(PJ['thumb_frame']['x'])))
    save('thumb', m, R, info)
    for part in ('palm_back', 'palm_flap', 'cuff'):
        m = trimesh.load(f'build/{part}.stl')
        _, s, b, R = best(m, sphere_cands())
        if part == 'palm_back':
            # stand it on the wrist end: a real footprint (with a brim) and the logo on a near-vertical
            # face, so no support ever touches the pressed-in logo
            R = Rot.from_euler('x', 90, degrees=True).as_matrix()
        save(part, m, R, info)
    json.dump(info, open('build/orient.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
