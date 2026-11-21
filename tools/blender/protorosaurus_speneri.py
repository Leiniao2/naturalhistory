"""
Procedural Protorosaurus speneri (Late Permian archosauromorph, ~1.8 m) for map colonies.

One of the first fossil reptiles ever described (1710) and an early relative of the line
leading to crocodiles and dinosaurs: a lizard-like body with a long, slender neck, a small,
pointed head with sharp teeth, long legs (longer hind legs) and a very long tail.
Grey-olive with dark cross-bands. Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/protorosaurus_speneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protorosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Protorosaurus",
    torso=[
        (-0.66, 0.37, 0.028, 0.030),
        (-0.55, 0.33, 0.033, 0.036),
        (-0.40, 0.26, 0.05, 0.055),
        (-0.28, 0.22, 0.085, 0.08),
        (-0.12, 0.215, 0.10, 0.09),
        (0.06, 0.215, 0.095, 0.085),
        (0.16, 0.21, 0.07, 0.07),
        (0.40, 0.15, 0.035, 0.035),
        (0.75, 0.07, 0.016, 0.016),
        (1.00, 0.04, 0.006, 0.006),
        (1.05, 0.035, 0.0, 0.0),
    ],
    head=[
        (-0.64, 0.380, 0.034, 0.034),
        (-0.71, 0.385, 0.034, 0.034),
        (-0.78, 0.375, 0.024, 0.026),
        (-0.83, 0.365, 0.014, 0.016),
        (-0.845, 0.363, 0.0, 0.0),
    ],
    jaw=[
        (-0.66, 0.352, 0.028, 0.013),
        (-0.79, 0.350, 0.016, 0.009),
        (-0.84, 0.352, 0.0, 0.0),
    ],
    teeth=[(-0.835, -0.70, 9, 0.008, 0.0025, True)],
    fore=pt.Limb(y=-0.22, z=0.19, x=0.08, upper=0.12, lower=0.12, sprawl=0.75, r=0.028,
                 foot=(0.025, 0.035, 0.010), toe_len=0.035, toe_r=0.006),
    hind=pt.Limb(y=0.11, z=0.19, x=0.08, upper=0.15, lower=0.15, sprawl=0.7, r=0.036,
                 foot=(0.030, 0.045, 0.010), toe_len=0.045, toe_r=0.007),
    eye=(0.028, -0.725, 0.40, 0.012), nostril=(0.010, -0.835, 0.37),
    back=(0.34, 0.35, 0.28), flank=(0.50, 0.50, 0.40), belly=(0.80, 0.78, 0.66), mark=(0.15, 0.15, 0.12),
    pattern="bands", pattern_freq=30.0, pattern_amount=0.65,
    voxel=0.0055, max_tris=8000, drop=0.03,
)

if __name__ == "__main__":
    pt.main(SPEC)
