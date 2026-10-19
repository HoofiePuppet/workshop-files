"""Round every line-channel mouth.
Where a channel leaves a joint slot or a clearance cut at a slant, the boolean leaves knife-edge lips
(0.05-0.3 mm) round the hole: too thin to print cleanly and sharp enough to fray braided line. Each mouth
is found by casting rays round the channel centre line (open = rays escape, bore = all rays hit within
1 mm), and a 2.4 mm long trumpet (1.6 mm radius at the face, channel radius inside) is cut there.
Rewrites build/palm_back.stl and build/fingers/*.stl in place and logs the mouths to build/mouths.json."""
import json, glob, numpy as np, trimesh, manifold3d as mf
from trimesh.ray.ray_pyembree import RayMeshIntersector
from rlib import to_mf, to_tm

A = np.linspace(0, 2 * np.pi, 24, endpoint=False)


def enclosed(ri, p, t):
    u = np.cross(t, [0, 0, 1.0]); u = u if np.linalg.norm(u) > 0.2 else np.cross(t, [1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(t, u)
    D = np.array([np.cos(a) * u + np.sin(a) * v for a in A])
    loc, ir, _ = ri.intersects_location(np.tile(p, (24, 1)), D, multiple_hits=False)
    if len(ir) < 24: return False
    return np.linalg.norm(loc - p, axis=1).max() < 1.0


def trumpet(p_face, t_in, r):
    """Frustum: radius 1.6 at the face (starting 0.4 outside it) narrowing to r at 2.0 inside."""
    L = 2.4; c = mf.Manifold.cylinder(L, 1.6, r, 32)
    z = t_in / np.linalg.norm(t_in); x = np.cross(z, [0, 0, 1.0]); x = x if np.linalg.norm(x) > 0.2 else np.cross(z, [1.0, 0, 0])
    x /= np.linalg.norm(x); y = np.cross(z, x); o = p_face - z * 0.4
    M = np.zeros((3, 4)); M[:, 0], M[:, 1], M[:, 2], M[:, 3] = x, y, z, o
    return c.transform(M)


def flare_part(path, channels):
    tm = trimesh.load(path); ri = RayMeshIntersector(tm); cuts = []
    for c in channels:
        P = np.array(c['pts'])
        S = []
        for a, b in zip(P[:-1], P[1:]):
            for s in np.linspace(0, 1, 5, endpoint=False): S.append(a + s * (b - a))
        S.append(P[-1]); S = np.array(S)
        T = np.gradient(S, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
        st = np.array([enclosed(ri, p, t) for p, t in zip(S, T)])
        for k in range(len(S) - 1):
            if st[k] == st[k + 1]: continue
            # bisect the open/bore boundary between samples k and k+1
            lo, hi = (S[k], S[k + 1]) if not st[k] else (S[k + 1], S[k])
            t_in = hi - lo
            for _ in range(12):
                mid = (lo + hi) / 2
                if enclosed(ri, mid, t_in / np.linalg.norm(t_in)): hi = mid
                else: lo = mid
            # skip transitions that are just the end of the part (bore runs out into open air through a flat face is fine
            # but a trumpet there is harmless too, so every mouth gets one)
            cuts.append({'p': hi.tolist(), 't_in': (t_in / np.linalg.norm(t_in)).tolist(), 'r': c['r']})
    if not cuts: return 0, []
    M = to_mf(tm)
    tools = mf.Manifold.batch_boolean([trumpet(np.array(q['p']), np.array(q['t_in']), q['r']) for q in cuts], mf.OpType.Add)
    M2 = M - tools
    to_tm(M2).export(path)
    return len(cuts), cuts


if __name__ == '__main__':
    log = {}
    pc = json.load(open('build/palm_channels.json'))
    fc = json.load(open('build/finger_channels.json'))
    n, cuts = flare_part('build/palm_back.stl', pc); log['palm_back'] = cuts; print('palm_back mouths', n)
    for f in sorted(glob.glob('build/fingers/*.stl')):
        n, cuts = flare_part(f, fc); log[f] = cuts; print(f, 'mouths', n)
    json.dump(log, open('build/mouths.json', 'w'), indent=1)
