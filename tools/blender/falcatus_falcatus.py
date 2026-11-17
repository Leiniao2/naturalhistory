"""
Procedural Falcatus falcatus (Early Carboniferous Bear Gulch Limestone of Montana, a small
symmoriiform shark about 25-30 cm long) for map colonies (Swim style).

A small, big-eyed shark with a short rounded snout and a crescent-shaped tail; the male's
famous sword-shaped spine grows from the top of the shoulders and curves forward over the
head, its underside lined with denticles. The pectoral fins trail long whip-like streamers.
Grey-brown back with darker spots, pale belly. Built with nh_car_fish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/falcatus_falcatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Falcatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.30, 0.27, 0.22)
WHIP = (0.24, 0.23, 0.22)
DENT = (0.85, 0.82, 0.72)

SPINE_PTS = [(0, -0.20, 0.08), (0, -0.21, 0.20), (0, -0.28, 0.27), (0, -0.40, 0.28), (0, -0.52, 0.24)]


def sword(sp):
    return [nh.tube(SPINE_PTS, [0.03, 0.026, 0.022, 0.016, 0.004], sides=10)]


def whips(sp, tree):
    out = []
    for sx in (-1, 1):
        root = Vector((sx * 0.21, -0.22, -0.1))
        pts = [root, root + Vector((sx * 0.03, 0.12, -0.02)), root + Vector((sx * 0.02, 0.26, -0.03)),
               root + Vector((sx * -0.02, 0.38, -0.02))]
        out.append((nh.tube(pts, [0.007, 0.005, 0.004, 0.0015], sides=5), WHIP))
    for i in range(6):
        p = Vector(SPINE_PTS[2]).lerp(Vector(SPINE_PTS[4]), i / 6.0)
        out.append((nh.tube([p, p + Vector((0, 0.004, -0.028))], [0.006, 0.0], sides=4), DENT))
    return out


SPEC = cf.Spec(
    name="Falcatus",
    mid=[(-0.6, 0.0), (0.25, 0.0), (0.6, 0.05)],
    height=[(-0.6, 0.0), (-0.585, 0.05), (-0.5, 0.1), (-0.3, 0.12), (0.0, 0.09), (0.28, 0.04),
            (0.45, 0.025), (0.6, 0.005)],
    width=[(-0.6, 0.0), (-0.585, 0.045), (-0.5, 0.085), (-0.3, 0.095), (0.0, 0.07), (0.28, 0.03),
           (0.45, 0.02), (0.6, 0.004)],
    fins=[
        ("mid", [(0.38, 0.03), (0.54, 0.24), (0.61, 0.24), (0.56, 0.05), (0.62, -0.17), (0.56, -0.18), (0.38, -0.01)]),
        ("mid", [(0.15, 0.06), (0.22, 0.12), (0.26, 0.12), (0.28, 0.04)]),
        ("pair", (0.07, -0.33, -0.07), [(0, 0, 0), (0.0, 0.08, 0.0), (0.15, 0.12, -0.03), (0.15, 0.08, -0.03)]),
        ("pair", (0.04, 0.10, -0.06), [(0, 0, 0), (0.0, 0.07, 0.0), (0.07, 0.09, -0.04), (0.06, 0.03, -0.04)]),
    ],
    fused_extra=[sword],
    back=(0.30, 0.28, 0.25), flank=(0.46, 0.43, 0.38), belly=(0.86, 0.83, 0.75),
    fin_col=(0.28, 0.26, 0.23), pattern="spots", pattern_col=(0.16, 0.14, 0.12), pattern_scale=0.7,
    eye=(-0.47, 0.03, 0.045), iris=(0.70, 0.62, 0.35), gills=5, gill_y=-0.36,
    extra=[whips],
)

if __name__ == "__main__":
    cf.run(SPEC)
