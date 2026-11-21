"""
Procedural Casea broilii (Early Permian caseid synapsid, ~1.2 m) for map colonies.

A small relative of Cotylorhynchus: a ridiculously small, short-snouted head with a big
nasal opening and an overhanging snout, on a huge, wide barrel of a body (a big gut to
ferment tough plants), short sprawling legs with broad clawed feet and a long tail.
Grey-brown with pale belly. Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/casea_broilii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Casea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Casea",
    torso=[
        (-0.40, 0.22, 0.05, 0.05),
        (-0.33, 0.23, 0.11, 0.10),
        (-0.18, 0.25, 0.22, 0.17),
        (0.02, 0.25, 0.25, 0.18),
        (0.20, 0.24, 0.20, 0.15),
        (0.32, 0.21, 0.09, 0.08),
        (0.55, 0.14, 0.045, 0.04),
        (0.85, 0.07, 0.018, 0.018),
        (0.98, 0.05, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.25, 0.050, 0.050),
        (-0.44, 0.255, 0.050, 0.050),
        (-0.50, 0.245, 0.040, 0.042),
        (-0.535, 0.235, 0.024, 0.028),
        (-0.545, 0.232, 0.0, 0.0),
    ],
    fore=pt.Limb(y=-0.22, z=0.17, x=0.17, upper=0.12, lower=0.13, sprawl=0.9, r=0.05,
                 foot=(0.045, 0.05, 0.015), toe_len=0.035, toe_r=0.011, claw=1.2),
    hind=pt.Limb(y=0.20, z=0.17, x=0.15, upper=0.13, lower=0.13, sprawl=0.85, r=0.055,
                 foot=(0.048, 0.058, 0.015), toe_len=0.04, toe_r=0.012, claw=1.0),
    eye=(0.038, -0.46, 0.27, 0.014), nostril=(0.02, -0.535, 0.25),
    back=(0.34, 0.31, 0.26), flank=(0.50, 0.46, 0.38), belly=(0.80, 0.74, 0.62), mark=(0.25, 0.22, 0.18),
    pattern="mottle", pattern_freq=9.0, pattern_amount=0.35,
    voxel=0.007, max_tris=9000, drop=0.02,
)

if __name__ == "__main__":
    pt.main(SPEC)
