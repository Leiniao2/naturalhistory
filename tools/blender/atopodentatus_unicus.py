"""
Procedural Atopodentatus unicus (Middle Triassic marine reptile, ~3 m) for map colonies
(Swim style).

A bizarre plant-eating marine reptile from the Anisian (about 245 million years ago) of
Luoping, Yunnan, China, distantly related to the sauropterygians. Its jaws were widened
at the front into a hammerhead shape, lined with rows of chisel-like teeth at the front
edge and many tiny needle-like teeth behind, which it probably used to scrape algae off
the sea floor and filter them from the mud. A small head on a long neck, a long body, a
long tail and slender, partly paddle-like limbs. Built with the shared Triassic
tetrapod recipe (nh_tri_tetrapod.py). Painted grey-green above with a pale belly
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/atopodentatus_unicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Atopodentatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.10 * s * s


AXIS = [
    (-0.985, 0.000, 0.022, 0.016),
    (-0.95, 0.000, 0.026, 0.020),
    (-0.90, 0.004, 0.030, 0.024),
    (-0.84, 0.008, 0.035, 0.028),
    (-0.80, 0.006, 0.028, 0.026),
    (-0.62, 0.000, 0.034, 0.032),
    (-0.45, 0.000, 0.060, 0.050),
    (-0.30, 0.000, 0.090, 0.070),
    (-0.05, 0.000, 0.100, 0.075),
    (0.12, 0.000, 0.080, 0.062),
    (0.28, 0.000, 0.045, 0.045, sway(0.28)),
    (0.55, 0.000, 0.028, 0.030, sway(0.55)),
    (0.80, 0.000, 0.014, 0.016, sway(0.80)),
    (1.00, 0.000, 0.003, 0.003, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.07, -0.30, -0.03), (0.15, -0.27, -0.05), (0.20, -0.23, -0.06), (0.22, -0.21, -0.06)],
               radii=[0.024, 0.019, 0.015, 0.012], toes=5, toe_len=0.04, toe_r=0.005, toe_spread=50,
               toe_yaw=125, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.06, 0.10, -0.03), (0.14, 0.15, -0.05), (0.19, 0.21, -0.06), (0.21, 0.23, -0.06)],
               radii=[0.028, 0.021, 0.016, 0.013], toes=5, toe_len=0.05, toe_r=0.0055, toe_spread=50,
               toe_yaw=150, toe_drop=0.0, claws=False)


def hammer_teeth(mb, surf, spec):
    # a comb of small white teeth along the front edge of the hammer-shaped jaws
    for k in range(17):
        x = -0.064 + 0.128 * k / 16
        loc, n = surf.hit((x, -2.0, -0.004), (0, 1, 0))
        if loc is None:
            continue
        mb.add(tt.cone(loc + Vector((0, 0.003, 0)), loc + Vector((0, -0.012, -0.006)), 0.0032, sides=5),
               tt.TOOTH, smooth=False)


SPEC = tt.TetrapodSpec(
    name="Atopodentatus",
    axis=AXIS,
    blobs=[((0.0, -0.975, 0.000), (0.072, 0.022, 0.018))],
    limbs=[FORE, HIND],
    voxel=0.0065, max_tris=9000,
    pivot="centre",
    eyes=(-0.875, 0.020, 0.0095, (0.75, 0.60, 0.20)),
    back=(0.24, 0.28, 0.22), flank=(0.46, 0.50, 0.42), belly=(0.86, 0.85, 0.76),
    pattern=("stripe", (0.16, 0.19, 0.15), 0.55, 0.2, 0.6),
    post=hammer_teeth,
)

if __name__ == "__main__":
    tt.run(SPEC)
