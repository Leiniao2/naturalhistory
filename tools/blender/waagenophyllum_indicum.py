"""
Procedural Waagenophyllum indicum (Permian colonial rugose coral) for map colonies.

A typical reef-building rugose coral of the warm Tethys Ocean: a bushy (phaceloid) colony
of many slender, cylindrical corallites a few millimetres thick that branch and grow
upward side by side, each ending in a cup with radiating septa around a small central
column, from which the polyp spread its tentacles. Cream-tan walls with fine growth
wrinkles, darker cups, a few polyps out (orange-pink). Mud patch base.
Faces -Y, pivot on the sea floor (Fixed style).

Usage:
  blender --background --python tools/blender/waagenophyllum_indicum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Waagenophyllum.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as oe  # noqa: E402

WALL = (0.80, 0.68, 0.50)
WALL_DARK = (0.56, 0.44, 0.30)
CUP = (0.30, 0.22, 0.16)
SEPTUM = (0.92, 0.88, 0.78)
POLYP = (0.92, 0.55, 0.42)
POLYP_TIP = (0.98, 0.85, 0.70)
MUD = ((0.58, 0.54, 0.46), (0.70, 0.66, 0.56))


def wall_col(co, n):
    rug = 0.5 + 0.5 * math.sin(co.z * 140.0)
    return nh.lerp(WALL, WALL_DARK, 0.35 * rug + 0.25 * (0.5 + 0.5 * noise.noise(co * 12)))


def corallite(mb, pts, r, rng, polyp):
    mb.add(nh.tube(pts, [r] * len(pts), sides=10, cap_end=False), wall_col)
    top, prev = Vector(pts[-1]), Vector(pts[-2])
    d = (top - prev).normalized()
    # cup: dark disc slightly sunk, septa as radial ribs, central column
    mb.add(nh.tube([top - d * r * 0.5, top - d * r * 0.15], [r * 0.92, r * 0.92], sides=10), CUP)
    side = d.cross(Vector((1, 0, 0)))
    if side.length < 1e-3:
        side = d.cross(Vector((0, 1, 0)))
    side.normalize()
    up2 = d.cross(side)
    for k in range(12):
        a = k / 12 * math.tau
        v = side * math.cos(a) + up2 * math.sin(a)
        mb.add(nh.tube([top - d * r * 0.12 + v * r * 0.2, top - d * r * 0.05 + v * r * 0.9],
                       [r * 0.07, r * 0.07], sides=3), SEPTUM, smooth=False)
    mb.add(nh.ellipsoid(tuple(top - d * r * 0.05), (r * 0.18,) * 3, subdivisions=1), SEPTUM)
    if polyp:
        for k in range(10):
            a = k / 10 * math.tau + rng.random() * 0.2
            v = side * math.cos(a) + up2 * math.sin(a)
            base = top + v * r * 0.6
            tip = base + v * r * 1.3 + d * r * 1.1
            mb.add(nh.tube([base, base.lerp(tip, 0.5) + d * r * 0.2, tip], [r * 0.12, r * 0.09, 0.0], sides=4),
                   lambda co, n, b=base: nh.lerp(POLYP, POLYP_TIP, min(1.0, (co - b).length / (r * 1.8))))


def grow(mb, rng, base, direction, length, r, depth):
    pts = [Vector(base)]
    d = Vector(direction).normalized()
    steps = 6
    for i in range(steps):
        d = (d + Vector((rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), 0.18))).normalized()
        pts.append(pts[-1] + d * length / steps)
    if depth > 0:
        # branch from about half-way: the stem ends there and two daughters carry on
        k = steps // 2 + rng.randint(-1, 1)
        mb.add(nh.tube(pts[:k + 1], [r] * (k + 1), sides=10, cap_end=False), wall_col)
        for sgn in (1, -1):
            a = rng.uniform(0, math.tau)
            nd = (d + Vector((math.cos(a), math.sin(a), 0)) * 0.30 * sgn).normalized()
            grow(mb, rng, pts[k], nd, length * rng.uniform(0.55, 0.75), r, depth - 1)
    else:
        corallite(mb, pts, r, rng, rng.random() < 0.45)


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()
    oe.mud_patch(mb, 0.70, MUD, seed=4)
    for i in range(22):
        a = rng.uniform(0, math.tau)
        rr = 0.40 * math.sqrt(rng.random())
        base = (math.cos(a) * rr, math.sin(a) * rr, 0.0)
        d = (math.cos(a) * rr * 0.6, math.sin(a) * rr * 0.6, 1.0)
        grow(mb, rng, base, d, rng.uniform(0.40, 0.60), 0.042, 1)
    return oe._finish(mb, "Waagenophyllum", roughness=0.7)


if __name__ == "__main__":
    nh.run(build, "Waagenophyllum", ground=(0.62, 0.58, 0.48), views=((30, 25), (10, 70), (-100, 12)))
