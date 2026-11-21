"""
Procedural Leperditia fabulites (Ordovician leperditicopid ostracod, North America) for map
colonies (Swim style).

A giant among ostracods, up to about 2 cm long: a smooth, bean-shaped, two-valved carapace
with a long straight hinge along the back, the right valve a little larger and overlapping
the left along the lower edge, and a small eye tubercle near the front of each valve.
Short antennae and legs peek out from the gape below, used to crawl and scull over the
sea floor. Glossy amber-brown with a darker muscle-scar spot. Faces -Y, pivot at the body
centre.

Usage:
  blender --background --python tools/blender/leperditia_fabulites.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LeperditiaFabulites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "LeperditiaFabulites"
SHELL = (0.66, 0.45, 0.22)
LIGHT = (0.86, 0.66, 0.40)
DARK = (0.30, 0.18, 0.08)
LIMB = (0.80, 0.62, 0.42)
EYE = (0.06, 0.05, 0.04)
H = 0.24   # hinge height above the centre


def outline_for(scale):
    def outline(a):
        r = 1.0 / math.sqrt((math.cos(a) / 0.55) ** 2 + (math.sin(a) / 0.34) ** 2)
        # front end a little narrower than the back
        r *= 1.0 - 0.08 * max(0.0, -math.cos(a))
        if math.sin(a) > 1e-3:
            r = min(r, H / math.sin(a))
        return r * scale
    return outline


def col(co, n):
    c = nh.lerp(SHELL, LIGHT, 0.5 * max(0.0, n.z) + 0.25 * max(0.0, -n.y))
    # muscle-scar spot in the middle of each valve
    d = math.hypot(co.y - 0.02, co.z - 0.02)
    c = nh.lerp(c, DARK, 0.55 * (1 - nh.smoothstep(0.03, 0.06, d)) * nh.smoothstep(0.1, 0.2, abs(co.x)))
    if abs(co.x) < 0.012 and co.z > H - 0.03:
        c = DARK
    return c


def build():
    mb = nh.MeshBuilder()
    for side, sc in ((1, 1.0), (-1, 0.96)):
        bm = kit.valve(outline_for(sc), 0.22, side=side, peak=(-0.05, 0.25), power=0.5)
        nh.transform(bm, Matrix.Translation((side * 0.004, 0, 0.02 if side < 0 else 0.0)))
        mb.add(bm, col)
        # eye tubercle near the front of the hinge
        mb.add(nh.ellipsoid((side * 0.135, -0.32, 0.13), (0.03, 0.035, 0.03), 2), EYE)
    # limbs from the ventral gape
    for k, (y, L) in enumerate(((-0.40, 0.22), (-0.30, 0.20), (-0.12, 0.16), (0.05, 0.15), (0.20, 0.12))):
        for sx in (-1, 1):
            b = Vector((sx * 0.03, y, -0.22))
            d = Vector((sx * 0.35, -0.5 if k < 2 else 0.1, -1.0)).normalized()
            mb.add(nh.tube([b, b + d * L * 0.6, b + d * L + Vector((0, -0.04, 0.02))], [0.016, 0.012, 0.0],
                           sides=5), LIMB)
    return kit.finish_swim(mb, NAME, roughness=0.3)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.SWIM_VIEWS)
