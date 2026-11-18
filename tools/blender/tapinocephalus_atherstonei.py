"""
Procedural Tapinocephalus atherstonei (Middle Permian tapinocephalid dinocephalian, ~3 m) for
map colonies.

The "humble-head" of the Karoo, one of the largest plant-eaters of its time (perhaps 1.5-2
tonnes): a short-snouted, massive head whose skull roof was hugely thickened into a broad,
bony dome up to 10 cm thick, used in head-butting contests; a deep, heavy body sloping down
from tall shoulders to the hips, stout limbs with the forelimbs more sprawling, and a short
tail. Dun brown with a pale, bony brow.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/tapinocephalus_atherstonei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tapinocephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

DOME = (0.72, 0.64, 0.52)


def fused(b, spec):
    b.add(pt.oriented((0, -0.60, 0.69), (0.13, 0.11, 0.08)), DOME)            # massive skull dome
    for sx in (1, -1):
        b.add(pt.oriented((sx * 0.11, -0.58, 0.63), (0.05, 0.06, 0.05)), DOME)  # brow bosses
    b.add(pt.oriented((0, -0.42, 0.74), (0.16, 0.16, 0.09)), spec.back)        # shoulder hump


def paint(co, n, c):
    if co.y < -0.52:
        c = nh.lerp(c, (0.64, 0.54, 0.44), 0.4 * nh.smoothstep(-0.52, -0.72, co.y))
    return c


SPEC = pt.Spec(
    name="Tapinocephalus",
    torso=[
        (-0.48, 0.58, 0.11, 0.13),
        (-0.38, 0.60, 0.22, 0.24),
        (-0.20, 0.58, 0.29, 0.29),
        (0.02, 0.54, 0.29, 0.27),
        (0.22, 0.50, 0.25, 0.23),
        (0.36, 0.45, 0.16, 0.16),
        (0.47, 0.40, 0.07, 0.07),
        (0.56, 0.35, 0.025, 0.025),
        (0.60, 0.33, 0.0, 0.0),
    ],
    head=[
        (-0.50, 0.62, 0.13, 0.12),
        (-0.58, 0.62, 0.14, 0.13),
        (-0.66, 0.58, 0.11, 0.11),
        (-0.72, 0.54, 0.075, 0.08),
        (-0.755, 0.51, 0.045, 0.05),
        (-0.77, 0.50, 0.0, 0.0),
    ],
    teeth=[(-0.77, -0.70, 4, 0.02, 0.007, True)],
    fore=pt.Limb(y=-0.28, z=0.46, x=0.21, upper=0.20, lower=0.28, sprawl=0.5, r=0.095, muscle=1.25,
                 foot=(0.07, 0.08, 0.028), toe_len=0.04, toe_r=0.017),
    hind=pt.Limb(y=0.22, z=0.43, x=0.19, upper=0.20, lower=0.27, sprawl=0.3, r=0.10, muscle=1.2,
                 foot=(0.068, 0.085, 0.028), toe_len=0.04, toe_r=0.018),
    eye=(0.11, -0.64, 0.62, 0.018), nostril=(0.03, -0.765, 0.535),
    back=(0.40, 0.31, 0.21), flank=(0.56, 0.45, 0.32), belly=(0.76, 0.68, 0.56), mark=(0.30, 0.22, 0.15),
    pattern="mottle", pattern_freq=5.0, pattern_amount=0.25,
    fused=fused, paint=paint, voxel=0.0095, max_tris=12000,
)

if __name__ == "__main__":
    pt.main(SPEC)
