"""
Procedural Namacalathus hermanastes (terminal-Ediacaran calcified goblet, Nama Group) for the
map: a small cluster of goblets of different heights on a patch of microbial-mat seafloor.
Each is a hollow, slightly squat, roughly spherical calcite cup with a large round opening on
top (its rim curling a little inward) and a ring of round lateral windows around its sides -
usually six, here one cup has five and one seven - set on a thin, gently curving stalk that
flares into a small foot on the mat. The cup wall is a real two-sided shell, so the windows and
the top opening look through into the shadowed interior. Pale cream calcite on a dark mat.
Fixed style: pivot at the base (z = 0), stalks nearly upright so the map can sway them.

Usage:
  blender --background --python tools/blender/namacalathus_hermanastes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Namacalathus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402
import nh_cloudina as cl  # noqa: E402

SEED = 4
SEGMENTS, RINGS = 16, 10      # cup sphere resolution (outer shell; inner is coarser)
WALL = 0.10                   # cup wall thickness, in cup radii
TOP_HOLE = 0.52               # top opening radius, in cup radii
WINDOW = 0.27                 # lateral window radius, in cup radii
WINDOW_Z = 0.05               # window centre height above the cup's equator, in cup radii

CUP = (0.88, 0.85, 0.76)      # pale cream outer wall
CUP_DARK = (0.70, 0.67, 0.58)  # lower cup, toward the stalk
INNER = (0.36, 0.32, 0.27)    # shadowed interior wall
EDGE = (0.97, 0.95, 0.89)     # cut edges of the windows and the top opening
STALK = (0.76, 0.73, 0.64)

# (x, y, total height, cup radius, windows, lean degrees, yaw degrees)
GOBLETS = [(0.00, 0.00, 1.00, 0.16, 6, 4, 10), (0.34, -0.20, 0.70, 0.14, 6, 9, -35),
           (-0.34, -0.14, 0.58, 0.12, 7, 8, 70), (0.12, 0.34, 0.80, 0.15, 6, 7, 140),
           (-0.24, 0.30, 0.42, 0.10, 5, 12, -110)]


def _obj(bm, name):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def cup(radius, windows, rng):
    """Hollow cup centred on the origin: outer + inner sphere shells, with the top opening and
    the lateral windows cut out by a boolean. Returns (bm, {vert: rgb})."""
    squash = 0.88
    wob = Vector((rng.random() * 9, rng.random() * 9, rng.random() * 9))

    def shell(r, flip):
        seg, rings = (SEGMENTS, RINGS) if not flip else (SEGMENTS - 4, RINGS - 2)
        bm = nh.uv_ellipsoid((0, 0, 0), (r, r, r * squash), seg, rings,
                             deform=lambda n: 1.0 + 0.03 * noise.noise(n * 2.0 + wob)
                             # the top shoulders curl inward around the opening
                             - 0.08 * nh.smoothstep(0.55, 0.9, n.z))
        if flip:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        return bm

    bm = shell(radius, False)
    inner = shell(radius * (1 - WALL), True)
    tmp = bpy.data.meshes.new("_inner")
    inner.to_mesh(tmp)
    inner.free()
    bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
    body = _obj(bm, "_cup")

    # cutters: one vertical cylinder for the top opening, one radial cylinder per window
    cut = bmesh.new()
    bmesh.ops.create_cone(cut, cap_ends=True, segments=16, radius1=radius * TOP_HOLE,
                          radius2=radius * TOP_HOLE, depth=radius * 1.2,
                          matrix=Matrix.Translation((0, 0, radius)))
    a0 = rng.uniform(0, math.tau)
    for k in range(windows):
        a = a0 + k / windows * math.tau
        m = (Matrix.Translation((0, 0, radius * WINDOW_Z)) @ Matrix.Rotation(a, 4, "Z")
             @ Matrix.Translation((radius, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        bmesh.ops.create_cone(cut, cap_ends=True, segments=12, radius1=radius * WINDOW,
                              radius2=radius * WINDOW, depth=radius * 0.8, matrix=m)
    cutter = _obj(cut, "_cut")
    mod = body.modifiers.new("holes", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    out = bmesh.new()
    out.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    for o in (body, cutter):
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    bmesh.ops.triangulate(out, faces=out.faces)
    out.normal_update()

    vcol = {}
    for v in out.verts:
        radial = Vector((v.co.x, v.co.y, v.co.z / squash)).normalized()
        facing = v.normal.dot(radial)       # +1 outer wall, -1 inner wall, ~0 on the cut edges
        c = nh.lerp(CUP_DARK, CUP, nh.smoothstep(-0.9, 0.1, v.co.z / radius))
        if facing < -0.3:
            c = nh.lerp(INNER, CUP_DARK, nh.smoothstep(-0.5, 0.6, v.co.z / radius) * 0.35)
        elif facing < 0.5:
            c = EDGE                         # bright cut rims of the windows and the opening
        k = 0.95 + 0.08 * noise.noise(v.co * (14.0 / radius) + wob)
        vcol[v] = tuple(min(1.0, x * k) for x in c)
    return out, vcol


def stalk(height, cup_bottom, rng):
    """Thin, slightly curved stalk from a small foot on the mat up into the cup base."""
    bend = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * height * 0.04
    pts, rad = [], []
    for k in range(6):
        t = k / 5
        p = Vector((0, 0, -0.01 + (cup_bottom + 0.02 - -0.01) * t)) + bend * math.sin(t * math.pi)
        pts.append(p)
        rad.append(0.028 * (1 - t) ** 3 + 0.014 + (0.012 if k == 0 else 0.0))
    return nh.tube(pts, rad, sides=7)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    cl.seafloor(mb, 0.58)
    for x, y, h, r, windows, lean, yaw in GOBLETS:
        m = (Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
             @ Matrix.Rotation(math.radians(lean), 4, "X"))
        cz = h - r * 0.88
        bm, vcol = cup(r, windows, rng)
        nh.transform(bm, m @ Matrix.Translation((0, 0, cz)))
        nf.add_colored(mb, bm, vcol)
        mb.add(nh.transform(stalk(h, cz - r * 0.8, rng), m), STALK)
    obj = mb.to_object("Namacalathus", roughness=0.7)
    for v in obj.data.vertices:  # flatten the buried underside of the mat
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Namacalathus", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
