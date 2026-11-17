"""
Procedural Edestus heinrichi (Late Carboniferous, about 310 million years ago, a giant
eugeneodont fish of the United States and Russia, perhaps over 6 m long) for map colonies
(Swim style).

A long, streamlined shark-like body with a pointed snout and a tall, crescent tail, and
the animal's famous "scissor jaws": a curved, saw-edged whorl of big triangular teeth sticks
forward out of the tip of each jaw, the upper one arching down and the lower one up so they
meet like shears. Dark slate back, pale belly. Built with nh_car_fish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/edestus_heinrichi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Edestus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

WHORL = (0.36, 0.30, 0.24)
TOOTH = (0.90, 0.86, 0.74)


def arc(c, r, a0, a1, n=8):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def whorls(sp, tree):
    """Two curved, saw-edged tooth whorls crossing in front of the snout like shears."""
    out = []
    for x, centre, a0, a1 in ((0.009, (-0.53, -0.07), 80, 235),     # upper: forward then down
                              (-0.009, (-0.53, 0.05), 275, 125)):   # lower: forward then up
        outer = arc(centre, 0.10, a0, a1, 10)
        inner = arc(centre, 0.078, a1, a0, 10)
        pts = [(x, y, z) for y, z in outer + inner]
        out.append((cf.panel(pts, (1, 0, 0), 0.014), WHORL))
        for (y, z) in outer[1:]:
            d = Vector((0, y - centre[0], z - centre[1])).normalized()
            b = Vector((x, y, z))
            out.append((nh.tube([b - d * 0.006, b + d * 0.026], [0.012, 0.0], sides=4), TOOTH))
    return out


SPEC = cf.Spec(
    name="Edestus",
    mid=[(-0.6, 0.0), (0.25, 0.0), (0.6, 0.06)],
    height=[(-0.6, 0.0), (-0.57, 0.03), (-0.45, 0.07), (-0.2, 0.095), (0.1, 0.08), (0.33, 0.035),
            (0.45, 0.022), (0.6, 0.005)],
    width=[(-0.6, 0.0), (-0.57, 0.025), (-0.45, 0.06), (-0.2, 0.08), (0.1, 0.06), (0.33, 0.028),
           (0.45, 0.018), (0.6, 0.004)],
    fins=[
        ("mid", [(0.40, 0.03), (0.55, 0.25), (0.62, 0.25), (0.57, 0.05), (0.62, -0.2), (0.56, -0.21), (0.40, -0.01)]),
        ("mid", [(-0.15, 0.08), (-0.06, 0.2), (-0.02, 0.2), (0.02, 0.07)]),
        ("pair", (0.06, -0.30, -0.06), [(0, 0, 0), (0.0, 0.08, 0.0), (0.17, 0.15, -0.06), (0.17, 0.11, -0.07)]),
        ("pair", (0.04, 0.16, -0.05), [(0, 0, 0), (0.0, 0.06, 0.0), (0.06, 0.08, -0.04), (0.05, 0.03, -0.04)]),
    ],
    back=(0.20, 0.23, 0.27), flank=(0.34, 0.38, 0.42), belly=(0.85, 0.84, 0.80),
    fin_col=(0.19, 0.22, 0.26), pattern="none",
    eye=(-0.49, 0.025, 0.018), iris=(0.40, 0.45, 0.40), gills=5, gill_y=-0.38,
    extra=[whorls],
)

if __name__ == "__main__":
    cf.run(SPEC)
