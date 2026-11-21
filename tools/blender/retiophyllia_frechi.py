"""
Procedural Retiophyllia frechi (Late Triassic reef-building stony coral) for map colonies.

One of the first modern-type (scleractinian) reef corals, common in the Late Triassic reefs
of the Northern Calcareous Alps, about 210 million years ago: a bushy, "phaceloid" colony of
separate, finger-thick tubes that branch again and again and grow upward side by side, each
tube ending in a cup with a star of radiating septa where one polyp sat. Fixed, pivot on the
ground (on a little rubble).

Output: Assets/Resources/Models/Species/Retiophyllia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

TUBE = (0.80, 0.70, 0.52)
TUBE_DARK = (0.52, 0.42, 0.28)
RIM = (0.92, 0.86, 0.70)
CUP = (0.36, 0.26, 0.18)
POLYP = (0.62, 0.78, 0.48)
SEED = 5


def tube_col(co, n):
    # growth rings and long ribs (costae)
    ring = 0.5 + 0.5 * math.sin(co.z * 140.0)
    c = nh.lerp(TUBE, TUBE_DARK, 0.35 * nh.smoothstep(0.7, 1.0, ring))
    c = nh.lerp(c, TUBE_DARK, 0.5 * nh.smoothstep(0.35, 0.0, co.z))
    return c


def calyx(mb, p, d, r):
    """Open cup at a branch tip: raised rim, dark well, radiating septa and a green polyp disc."""
    mb.add(nh.tube([p - d * 0.01, p + d * 0.012], [r * 1.05, r * 1.12], sides=12, cap_end=False), RIM)
    mb.add(nh.ellipsoid(tuple(p + d * 0.006), (r * 0.85, r * 0.85, r * 0.85), subdivisions=2), CUP)
    side = d.cross(Vector((1, 0, 0)))
    if side.length < 1e-3:
        side = d.cross(Vector((0, 1, 0)))
    side.normalize()
    other = d.cross(side).normalized()
    for k in range(12):
        a = k / 12 * math.tau
        v = side * math.cos(a) + other * math.sin(a)
        mb.add(nh.tube([p + d * 0.010 + v * r * 0.25, p + d * 0.012 + v * r * 0.98], [0.0028, 0.0018], sides=3),
               RIM, smooth=False)
    mb.add(nh.ellipsoid(tuple(p + d * 0.014), (r * 0.3, r * 0.3, r * 0.12), subdivisions=1), POLYP)


def grow(mb, rng, p, d, length, r, depth, tips):
    steps = 4
    pts, d = [p.copy()], d.normalized()
    for i in range(steps):
        d = (d + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.06 + Vector((0, 0, 0.18))).normalized()
        p = p + d * (length / steps)
        pts.append(p.copy())
    mb.add(nh.tube(pts, [r] * len(pts), sides=10, cap_end=False), tube_col)
    if depth == 0 or rng.random() < 0.12:
        tips.append((p, d, r))
        return
    a = rng.uniform(0, math.tau)
    perp = Vector((math.cos(a), math.sin(a), 0.0))
    for sg in (1, -1):
        grow(mb, rng, p, (d + perp * sg * 0.32).normalized(), length * rng.uniform(0.8, 1.0), r, depth - 1, tips)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    nc.rubble(mb, rng, 0.25, 0.45, count=8)
    mb.add(nh.ellipsoid((0, 0, 0.0), (0.24, 0.24, 0.06), subdivisions=2,
                        deform=lambda n: 1.0 + 0.2 * noise.noise(n * 3.0)), TUBE_DARK)
    tips = []
    for i in range(6):
        a = i / 6 * math.tau + rng.uniform(-0.3, 0.3)
        r0 = rng.uniform(0.03, 0.12)
        start = Vector((math.cos(a) * r0, math.sin(a) * r0, 0.02))
        d = Vector((math.cos(a) * 0.35, math.sin(a) * 0.35, 1.0))
        grow(mb, rng, start, d, rng.uniform(0.16, 0.22), 0.032, 3, tips)
    for p, d, r in tips:
        calyx(mb, p, d, r)
    obj = mb.to_object("Retiophyllia", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Retiophyllia", background=(0.05, 0.16, 0.20), ground=(0.70, 0.66, 0.54),
           views=((30, 25), (0, 75), (-90, 6)))
