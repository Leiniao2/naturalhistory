"""
Procedural grooved brain coral (Diploria labyrinthiformis) for the map: a squat boulder dome
covered in meandering labyrinth ridges and valleys, planted on a little rubble patch.
Ground style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/brain_coral.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 11
RADIUS = 0.55      # dome footprint radius
HEIGHT = 0.40      # dome height
RD_STEPS = 14000   # reaction-diffusion iterations (more = more settled labyrinth)
AMP = 0.038        # ridge height

RIDGE_TOP = (0.86, 0.72, 0.36)    # yellow-tan ridge crests
RIDGE_SIDE = (0.70, 0.60, 0.30)
VALLEY = (0.36, 0.45, 0.22)       # olive-green grooves
BASE_DARK = (0.40, 0.36, 0.22)

WARP = Vector((3.7, 1.3, 8.1))


def labyrinth(bm, rng, iterations=RD_STEPS):
    """Gray-Scott reaction-diffusion ("coral" regime) on the mesh's vertex graph: it settles into
    meandering stripes of even width, the labyrinth of a brain coral. Returns {vert: 0..1}."""
    import numpy as np
    bm.verts.index_update()
    verts = list(bm.verts)
    n = len(verts)
    deg = max(len(v.link_edges) for v in verts)
    nb = np.empty((n, deg), dtype=np.int64)
    w = np.zeros((n, deg))
    for v in verts:
        others = [e.other_vert(v).index for e in v.link_edges]
        nb[v.index, :] = v.index
        nb[v.index, :len(others)] = others
        w[v.index, :len(others)] = 1.0 / len(others)
    a = np.ones(n)
    b = np.zeros(n)
    seeds = np.array([rng.random() < 0.04 for _ in range(n)])
    b[seeds] = 1.0
    f, k, da, db = 0.0545, 0.062, 0.22, 0.11  # small diffusion -> narrow meanders
    for _ in range(iterations):
        la = (a[nb] * w).sum(1) - a
        lb = (b[nb] * w).sum(1) - b
        abb = a * b * b
        a += da * la - abb + f * (1.0 - a)
        b += db * lb + abb - (k + f) * b
    lo, hi = np.percentile(b, 5), np.percentile(b, 95)
    t = np.clip((b - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    return {v: float(t[v.index]) for v in verts}


def dome_point(d):
    """Shape of the boulder (before ridges) for a unit direction d with d.z >= 0."""
    bulge = 1.0 + 0.06 * noise.noise(d * 1.3 + WARP)
    z = max(d.z, 0.0)
    # flatten the very top a little, tuck the rim in toward the base
    zz = HEIGHT * (z ** 0.9)
    rr = RADIUS * bulge * math.sqrt(max(0.0, 1.0 - z * z)) * (0.92 + 0.08 * z)
    h = math.hypot(d.x, d.y) or 1.0
    return Vector((d.x / h * rr, d.y / h * rr, zz))


def build():
    rng = random.Random(SEED)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=6, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.02], context="VERTS")

    maze = labyrinth(bm, rng)
    by_pos = {}
    for v in bm.verts:
        d = v.co.normalized()
        base = dome_point(d)
        rim = nh.smoothstep(0.0, 0.25, d.z)  # ridges fade out where the dome meets the rubble
        m = maze[v]
        polyp = 0.004 * noise.noise(d * 60.0)
        base.z -= 0.02  # sink the rim slightly into the rubble
        v.co = base + d * (AMP * rim * (m - 0.5) + polyp * rim)
        by_pos[v.co.to_tuple(5)] = m
    bm.normal_update()

    def color(co, n):
        m = by_pos.get(co.to_tuple(5), 0.5)
        c = nh.lerp(VALLEY, RIDGE_SIDE, nh.smoothstep(0.1, 0.6, m))
        c = nh.lerp(c, RIDGE_TOP, nh.smoothstep(0.6, 0.95, m))
        # polyp speckle in the valleys, slight greenish tint toward the top
        speck = noise.noise(co * 90.0)
        if m < 0.35 and speck > 0.35:
            c = nh.lerp(c, (0.55, 0.62, 0.34), 0.5)
        c = nh.lerp(BASE_DARK, c, nh.smoothstep(0.0, 0.18, co.z + 0.02))
        return c

    mb = nh.MeshBuilder()
    mb.add(bm, color)
    nc.rubble(mb, rng, RADIUS * 0.95, RADIUS * 1.35, count=11, size=(0.05, 0.11))
    obj = mb.to_object("BrainCoral", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "BrainCoral", ground=(0.75, 0.70, 0.55), views=((35, 30), (10, 70), (-90, 10)))
