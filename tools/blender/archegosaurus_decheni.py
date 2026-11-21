"""
Procedural Archegosaurus decheni (Early Permian archegosaurid temnospondyl, ~1.5 m) for map colonies.

A gharial-like amphibian of the great lakes of the Saar-Nahe basin in Germany: a long,
narrow, flat snout lined with sharp teeth, a low, eel-like body, small limbs held back
while swimming and a long, deep, finned tail. Muddy olive-brown with darker spots and the
faint lines of the lateral-line canals on the head. Built with nh_per_tetra.
Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/archegosaurus_decheni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archegosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Archegosaurus",
    torso=[
        (-0.38, 0.0, 0.08, 0.048),
        (-0.30, 0.0, 0.11, 0.058),
        (-0.12, 0.0, 0.12, 0.064),
        (0.06, 0.0, 0.11, 0.062),
        (0.20, 0.0, 0.08, 0.06),
        (0.38, 0.0, 0.04, 0.065),
        (0.62, 0.0, 0.022, 0.060),
        (0.82, 0.0, 0.010, 0.038),
        (0.92, 0.0, 0.0, 0.0),
    ],
    head=[
        (-0.36, 0.012, 0.10, 0.040),
        (-0.46, 0.012, 0.09, 0.036),
        (-0.54, 0.006, 0.055, 0.026),
        (-0.68, 0.0, 0.034, 0.019),
        (-0.78, -0.004, 0.030, 0.017),
        (-0.81, -0.004, 0.0, 0.0),
    ],
    head_power=2.6,
    teeth=[(-0.80, -0.44, 24, 0.013, 0.0032, True)],
    fore=pt.Limb(y=-0.25, z=-0.02, x=0.10, upper=0.06, lower=0.06, sprawl=1.0, r=0.02, grounded=False,
                 foot=(0.02, 0.025, 0.007), toe_len=0.02, toe_r=0.005, claw=0.0, toes=4),
    hind=pt.Limb(y=0.16, z=-0.02, x=0.07, upper=0.07, lower=0.07, sprawl=1.0, r=0.024, grounded=False,
                 foot=(0.022, 0.03, 0.007), toe_len=0.025, toe_r=0.005, claw=0.0),
    eye=(0.034, -0.43, 0.045, 0.013), nostril=(0.014, -0.78, 0.008),
    back=(0.30, 0.25, 0.16), flank=(0.46, 0.40, 0.26), belly=(0.78, 0.70, 0.48), mark=(0.14, 0.11, 0.07),
    pattern="spots", pattern_freq=16.0, pattern_amount=0.7,
    pivot="centre", voxel=0.0055, max_tris=9000,
)

if __name__ == "__main__":
    pt.main(SPEC)
