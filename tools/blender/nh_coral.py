"""
Shared helpers for the coral models (table_coral.py, brain_coral.py, staghorn_coral.py):
a rubble/rock patch to plant each colony on, and a decimate step for meshes that were
displaced at full resolution (displace first, then decimate, then repaint).
"""

import math

import bpy
import bmesh
from mathutils import Vector, noise

import nh_model as nh

ROCK_COLS = [(0.42, 0.38, 0.33), (0.50, 0.46, 0.40), (0.36, 0.33, 0.30), (0.55, 0.50, 0.42)]
CORALLINE = (0.78, 0.45, 0.55)  # pink crustose coralline algae
SAND = (0.80, 0.74, 0.58)


def rubble(mb, rng, inner, outer, count=9, size=(0.05, 0.11)):
    """Scatters faceted, flattened rocks (some with pink coralline algae) in a ring."""
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(inner, outer)
        s = rng.uniform(*size)
        seed = Vector((rng.random() * 50, rng.random() * 50, rng.random() * 50))
        bm = nh.ellipsoid(
            (math.cos(a) * r, math.sin(a) * r, s * 0.18),
            (s, s * rng.uniform(0.7, 1.1), s * 0.5),
            subdivisions=1,
            deform=lambda n, seed=seed: 1.0 + 0.32 * noise.noise(n * 1.7 + seed),
        )
        base = rng.choice(ROCK_COLS)

        def col(co, nrm, base=base, seed=seed):
            k = 0.85 + 0.3 * noise.noise(co * 30 + seed)
            c = tuple(min(1.0, x * k) for x in base)
            if noise.noise(co * 10 + seed * 2) > 0.3 and nrm.z > 0.3:
                c = nh.lerp(c, CORALLINE, 0.65)
            return c

        mb.add(bm, col, smooth=False)


def decimate(bm, max_tris):
    """Returns a decimated copy of bm (bm is freed). Colours are not kept: repaint afterwards."""
    bmesh.ops.triangulate(bm, faces=bm.faces)
    n = len(bm.faces)
    if n <= max_tris:
        return bm
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = max_tris / n
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    out = bmesh.new()
    out.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for f in out.faces:
        f.smooth = True
    out.normal_update()
    return out
