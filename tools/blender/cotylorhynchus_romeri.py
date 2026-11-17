"""
Procedural Cotylorhynchus romeri (Early Permian caseid synapsid, ~4 m) for map colonies.

A giant plant-eating caseid: an enormous, broad barrel of a body (room for a huge gut to
ferment tough plants) on short, massive sprawling limbs with big claws on the hands, a
thick tapering tail and an absurdly small head with a short, blunt, overhanging snout and
large nostrils. Dull grey-brown with darker mottling over the back.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cotylorhynchus_romeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cotylorhynchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Cotylorhynchus",
    torso=[
        (-0.50, 0.33, 0.075, 0.085),
        (-0.42, 0.34, 0.16, 0.15),
        (-0.28, 0.35, 0.28, 0.23),
        (-0.05, 0.36, 0.34, 0.26),
        (0.18, 0.35, 0.31, 0.24),
        (0.34, 0.32, 0.19, 0.17),
        (0.48, 0.27, 0.095, 0.09),
        (0.70, 0.18, 0.055, 0.05),
        (0.90, 0.11, 0.025, 0.025),
        (1.00, 0.09, 0.0, 0.0),
    ],
    head=[
        (-0.47, 0.37, 0.065, 0.062),
        (-0.55, 0.375, 0.062, 0.058),
        (-0.62, 0.36, 0.048, 0.045),
        (-0.665, 0.345, 0.030, 0.030),
        (-0.68, 0.34, 0.0, 0.0),
    ],
    fore=pt.Limb(y=-0.28, z=0.24, x=0.22, upper=0.15, lower=0.16, sprawl=0.85, r=0.075, muscle=1.2,
                 foot=(0.060, 0.070, 0.024), toe_len=0.05, toe_r=0.015, claw=1.6),
    hind=pt.Limb(y=0.20, z=0.25, x=0.20, upper=0.16, lower=0.17, sprawl=0.8, r=0.085, muscle=1.2,
                 foot=(0.065, 0.080, 0.024), toe_len=0.05, toe_r=0.016, claw=1.2),
    eye=(0.045, -0.565, 0.395, 0.013), nostril=(0.022, -0.655, 0.37),
    back=(0.34, 0.31, 0.27), flank=(0.48, 0.44, 0.37), belly=(0.70, 0.65, 0.55), mark=(0.22, 0.20, 0.17),
    pattern="mottle", pattern_freq=7.0, pattern_amount=0.45,
    voxel=0.009, max_tris=11000,
)

if __name__ == "__main__":
    pt.main(SPEC)
