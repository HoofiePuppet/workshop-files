"""Make every print STL one clean closed solid.
1. Drop zero-volume slivers left by the booleans (keep the solid and any real inner void).
2. Where two surfaces of a part touch along an edge or a point, the solid is still valid (manifold3d keeps
   the two surfaces as separate topology) but they share vertex positions, so an STL reader that merges
   vertices by position sees non-manifold edges. Each such vertex is nudged 0.002 mm inward along its own
   normal, which keeps the topology manifold3d computed and makes the STL clean. Nothing else moves."""
import sys, glob, numpy as np, trimesh, manifold3d as mf


def load_mf(f):
    m = trimesh.load(f)
    me = mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)); me.merge()
    return mf.Manifold(me)


def clean(M, tol=0.03):
    # simplify first: the remeshed parts carry ~1M triangles; 0.03 mm tolerance keeps every feature
    # (max deviation about 0.06 mm, far below a 0.2 mm layer) and cuts file sizes about 6x
    M = M.simplify(tol)
    allp = M.decompose()
    solids = [p for p in allp if p.volume() > 1.0]
    voids = [p for p in allp if p.volume() < 0]            # sealed internal hollows: keep
    if voids and len(solids) == 1:
        pass                                               # one body plus its internal voids: leave as it is
    else:
        M = mf.Manifold.batch_boolean(solids, mf.OpType.Add) if len(solids) > 1 else solids[0]
    me = M.to_mesh(); V = np.asarray(me.vert_properties, np.float64)[:, :3].copy(); F = np.asarray(me.tri_verts, np.int64)
    key = np.round(V, 4)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    shared = cnt[inv.ravel()] > 1
    t = trimesh.Trimesh(V, F, process=False)
    N = t.vertex_normals
    V[shared] -= 0.002 * N[shared]
    t = trimesh.Trimesh(V, F, process=False)
    # drop zero-volume face fragments (a couple of degenerate triangles left on a fold)
    lab = trimesh.graph.connected_component_labels(t.face_adjacency, node_count=len(F))
    keep = np.ones(len(F), bool)
    for L in np.unique(lab):
        idx = lab == L
        if idx.sum() < 20 and abs(trimesh.Trimesh(V, F[idx], process=False).volume) < 1e-3: keep[idx] = False
    t = trimesh.Trimesh(V, F[keep], process=False); t.remove_unreferenced_vertices()
    return t, int(shared.sum())


if __name__ == '__main__':
    for f in sys.argv[1:] or sorted(glob.glob('stl/*.stl')):
        M = load_mf(f); v0 = M.volume()
        t, k = clean(M)
        t.export(f)
        t2 = trimesh.load(f)          # read back the way a slicer does: merge by position
        _, c = np.unique(t2.edges_sorted, axis=0, return_counts=True)
        print(f, 'nudged', k, 'non-manifold edges', int((c != 2).sum()), 'watertight', t2.is_watertight,
              'bodies', len(t2.split(only_watertight=False)), 'vol', round(t2.volume, 1), 'change', round(t2.volume - v0, 2))
