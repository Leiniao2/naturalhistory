"""
Procedural staghorn coral (Acropora cervicornis) for the map: a thicket of antler-like
cylindrical branches forking upward and outward, fused into one seamless surface, studded
with small corallite bumps and pale growing tips, planted on a little rubble patch.
Ground style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/staghorn_coral.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402
from mathutils.kdtree import KDTree  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 21
TRUNKS = 7
DEPTH = 3
VOXEL = 0.0105
MAX_TRIS = 10000

GOLD = (0.70, 0.49, 0.21)     # golden-brown branches
BROWN = (0.52, 0.36, 0.18)    # shaded inner thicket / base
TIP = (0.95, 0.90, 0.78)      # pale growing tips
UP = Vector((0, 0, 1))


def grow(mb, rng, start, direction, length, radius, depth, tips):
    """One branch as a slightly wandering tapered tube; forks at its end, sometimes sprouts a
    side branch, and ends in a rounded pale tip when it stops."""
    pts, rads = [start.copy()], [radius]
    p, d = start.copy(), direction.normalized()
    steps = 4
    for i in range(1, steps + 1):
        jitter = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.18
        d = (d + jitter + UP * 0.06).normalized()
        p = p + d * (length / steps)
        pts.append(p.copy())
        rads.append(radius * (1.0 - 0.22 * i / steps))
    mb.add(nh.tube(pts, rads, sides=10), GOLD)

    end_r = rads[-1]
    if depth == 0:
        mb.add(nh.uv_ellipsoid(p, (end_r, end_r, end_r), 10, 6), GOLD)  # rounded tip
        tips.append(p)
        return
    # fork into two (sometimes three) children spreading out and up
    n_children = 3 if rng.random() < 0.25 else 2
    side = d.cross(UP)
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    base_rot = rng.uniform(0, math.tau)
    for c in range(n_children):
        ang = base_rot + c * math.tau / n_children
        spread = rng.uniform(0.4, 0.7)
        perp = (side * math.cos(ang) + d.cross(side) * math.sin(ang)).normalized()
        cd = (d + perp * spread + UP * 0.25).normalized()
        grow(mb, rng, p, cd, length * rng.uniform(0.72, 0.88), end_r * 0.95, depth - 1, tips)
    # occasional short side spur from mid-branch
    if rng.random() < 0.45:
        mid = pts[2]
        perp = (side * rng.uniform(-1, 1) + UP * 0.4).normalized()
        grow(mb, rng, mid, (d + perp).normalized(), length * 0.45, rads[2] * 0.7, 0, tips)


def build():
    rng = random.Random(SEED)
    body = nh.MeshBuilder()
    tips = []
    for i in range(TRUNKS):
        a = i / TRUNKS * math.tau + rng.uniform(-0.3, 0.3)
        r0 = rng.uniform(0.04, 0.14)
        start = Vector((math.cos(a) * r0, math.sin(a) * r0, -0.02))
        elev = math.radians(rng.uniform(34, 66))
        d = Vector((math.cos(a) * math.cos(elev), math.sin(a) * math.cos(elev), math.sin(elev)))
        grow(body, rng, start, d, rng.uniform(0.24, 0.30), rng.uniform(0.032, 0.038), DEPTH, tips)
    # a dead, algae-covered stump at the heart of the thicket
    body.add(nh.uv_ellipsoid((0, 0, 0.02), (0.13, 0.13, 0.07), 14, 8), BROWN)

    fused = body.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    # corallite bumps (applied at full resolution, before decimating)
    for v in fused.verts:
        c = noise.cell(v.co * 55.0)
        v.co += v.normal * 0.003 * max(0.0, 1.0 - c * 1.6)
    fused.normal_update()
    fused = nc.decimate(fused, MAX_TRIS)

    kd = KDTree(len(tips))
    for i, t in enumerate(tips):
        kd.insert(t, i)
    kd.balance()
    top = max((t.z for t in tips), default=0.6)

    def color(co, n):
        _, _, dist = kd.find(co)
        tip = 1.0 - nh.smoothstep(0.01, 0.045, dist)
        depth = nh.smoothstep(0.0, top * 0.8, co.z)  # darker deep in the thicket
        c = nh.lerp(BROWN, GOLD, 0.35 + 0.65 * depth)
        c = nh.lerp(c, nh.lerp(GOLD, (0.82, 0.62, 0.30), 0.5), 0.3 + 0.3 * noise.noise(co * 8.0))
        # corallite specks: tiny pale dots along the branches
        if noise.cell(co * 70.0) < 0.1:
            c = nh.lerp(c, TIP, 0.22)
        c = nh.lerp(c, TIP, tip)
        return c

    mb = nh.MeshBuilder()
    mb.add(fused, color)
    nc.rubble(mb, rng, 0.15, 0.6, count=12, size=(0.03, 0.075))
    obj = mb.to_object("StaghornCoral", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "StaghornCoral", ground=(0.75, 0.70, 0.55), views=((35, 28), (10, 70), (-90, 8)))
