"""Mesh helpers for the realistic Sol Prosthetics hand (trimesh + manifold3d)."""
import numpy as np
import trimesh
import manifold3d as mf


def to_mf(tm):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                               tri_verts=np.asarray(tm.faces, np.uint32)))


def to_tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts), process=True)


def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def rot_about(m, axis, deg, pivot):
    """Rotate manifold m about an arbitrary axis through pivot."""
    R = trimesh.transformations.rotation_matrix(np.radians(deg), axis, pivot)
    return m.transform(R[:3, :])


def frame_matrix(origin, x, y, z):
    """3x4 matrix taking local (x right, y along, z up) into world."""
    M = np.zeros((3, 4))
    M[:, 0], M[:, 1], M[:, 2], M[:, 3] = x, y, z, origin
    return M


def smooth(tm, subdiv=1, taubin=10):
    v, f = tm.vertices, tm.faces
    for _ in range(subdiv):
        v, f = trimesh.remesh.subdivide_loop(v, f, iterations=1)
    out = trimesh.Trimesh(v, f, process=True)
    if taubin:
        trimesh.smoothing.filter_taubin(out, lamb=0.5, nu=-0.53, iterations=taubin)
    return out
