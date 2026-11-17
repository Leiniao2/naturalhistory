"""
Shared helpers for the Carboniferous chelicerates of the "car" batch
(megarachne_servinei.py, euproops_danae.py, weygoldtina_anglica.py, ...).

Bodies are assembled from overlapping, individually coloured shells (flattened
ellipsoids for tergites and shields, thick outlines for flat plates, tapering tubes for
jointed legs), fused into one seamless surface that keeps the part colours, then crisp
details (eyes, spines, claws) are added. Faces -Y.
"""

import math

import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh


def plate(outline, z, th, dome=0.0, rings=4):
    """Domed plate from a closed XY outline (list of (x, y)): a stack of shrinking outlines
    so the top bulges by `dome` at the centre. Bottom is flat at z - th/2."""
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    bm = bmesh.new()
    layers = []
    bot = [bm.verts.new((x, y, z - th * 0.5)) for x, y in outline]
    layers.append(bot)
    for r in range(rings + 1):
        t = r / rings
        k = 1.0 - 0.85 * t ** 1.5
        h = z + th * 0.5 + dome * math.sin(t * math.pi * 0.5)
        layers.append([bm.verts.new((cx + (x - cx) * k, cy + (y - cy) * k, h)) for x, y in outline])
    n = len(outline)
    for a, b in zip(layers, layers[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([a[i], a[j], b[j], b[i]])
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(layers[-1])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def leg(points, r0, r1, sides=6):
    """Jointed leg through points, tapering r0 -> r1, with slightly swollen joints."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    radii = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
    # densify with joint bulges
    dense, dr = [], []
    for i in range(n - 1):
        for k in range(3):
            t = k / 3
            dense.append(pts[i].lerp(pts[i + 1], t))
            dr.append((radii[i] + (radii[i + 1] - radii[i]) * t) * (1.15 if k == 0 else 1.0))
    dense.append(pts[-1])
    dr.append(radii[-1])
    return nh.tube(dense, dr, sides=sides)


def jointed(root, segs, start_dir, bends):
    """Polyline from root: segs lengths, start_dir (vector), bends: list of (yaw°, pitch°) applied
    progressively to the direction before each segment."""
    from mathutils import Matrix
    pts = [Vector(root)]
    d = Vector(start_dir).normalized()
    for L, (yaw, pitch) in zip(segs, bends):
        d = Matrix.Rotation(math.radians(yaw), 3, "Z") @ d
        side = d.cross(Vector((0, 0, 1)))
        if side.length > 1e-6:
            d = Matrix.Rotation(math.radians(pitch), 3, side.normalized()) @ d
        pts.append(pts[-1] + d * L)
    return pts


def fuse_parts(parts, voxel, max_tris, smooth=3):
    """parts: [(bm, rgb)] -> fused bmesh with the part colours."""
    mb = nh.MeshBuilder()
    for bm, c in parts:
        mb.add(bm, c)
    fused = mb.fuse(voxel=voxel, smooth=smooth, smooth_factor=0.5, max_tris=max_tris)
    fused.normal_update()
    return fused


def finish(fused, details, name, ground=True, roughness=0.5, grain=0.1, grain_scale=50.0):
    """Adds the fused body (keeping its colours, with a little brightness grain) and the
    crisp details, then centres (ground=False) or grounds the object."""
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            k = 1.0 + grain * noise.noise(l.vert.co * grain_scale)
            c = l[col]
            l[col] = (c[0] * k, c[1] * k, c[2] * k, 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for bm, c in details:
        mb.add(bm, c, smooth=False)
    obj = mb.to_object(name, roughness=roughness)
    if ground:
        nh.ground_to_zero(obj)
    else:
        vs = obj.data.vertices
        mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
        mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
        c = (mn + mx) / 2
        for v in vs:
            v.co -= c
    return obj


def eye(centre, r, look, iris=(0.15, 0.13, 0.10), pupil=(0.02, 0.02, 0.02)):
    look = Vector(look).normalized()
    c = Vector(centre)

    def col(co, n):
        k = (co - c).normalized().dot(look)
        return pupil if k > 0.6 else iris
    return nh.ellipsoid(c, (r, r, r), subdivisions=2), col


def ray_down(tree, x, y, z0=5.0):
    loc, nrm, _i, _d = tree.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
    return loc, nrm
