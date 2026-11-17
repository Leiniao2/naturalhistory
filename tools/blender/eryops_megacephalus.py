"""
Procedural Eryops megacephalus (Early Permian temnospondyl, ~2 m) for map colonies.

A big, heavy, crocodile-like amphibian: a huge, broad, flattened, triangular head (about a
quarter of its length) with eyes on top and a mouth lined with sharp teeth, a squat,
broad body low to the ground on short strong sprawling legs (four fingers, five toes) and
a short, thick tail. Dark grey-brown with blotchy darker spots and a dull yellowish belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eryops_megacephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eryops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Eryops",
    torso=[
        (-0.40, 0.20, 0.10, 0.07),
        (-0.30, 0.21, 0.17, 0.11),
        (-0.10, 0.22, 0.20, 0.12),
        (0.10, 0.22, 0.18, 0.115),
        (0.25, 0.21, 0.13, 0.09),
        (0.38, 0.18, 0.07, 0.06),
        (0.60, 0.12, 0.04, 0.035),
        (0.80, 0.08, 0.018, 0.016),
        (0.90, 0.07, 0.0, 0.0),
    ],
    head=[
        (-0.36, 0.225, 0.16, 0.065),
        (-0.48, 0.225, 0.155, 0.060),
        (-0.62, 0.210, 0.120, 0.047),
        (-0.74, 0.195, 0.075, 0.036),
        (-0.80, 0.187, 0.040, 0.027),
        (-0.82, 0.185, 0.0, 0.0),
    ],
    head_power=2.8,
    jaw=[
        (-0.38, 0.160, 0.15, 0.028),
        (-0.60, 0.157, 0.11, 0.021),
        (-0.78, 0.160, 0.045, 0.016),
        (-0.81, 0.162, 0.0, 0.0),
    ],
    teeth=[(-0.80, -0.44, 16, 0.014, 0.0045, True)],
    fore=pt.Limb(y=-0.25, z=0.17, x=0.15, upper=0.13, lower=0.13, sprawl=0.9, r=0.045, toes=4,
                 foot=(0.040, 0.045, 0.016), toe_len=0.04, toe_r=0.011, toe_fan=70, claw=0.5),
    hind=pt.Limb(y=0.25, z=0.17, x=0.13, upper=0.14, lower=0.14, sprawl=0.85, r=0.052,
                 foot=(0.045, 0.055, 0.016), toe_len=0.045, toe_r=0.012, claw=0.5),
    eye=(0.07, -0.50, 0.27, 0.020), nostril=(0.045, -0.775, 0.21),
    back=(0.22, 0.21, 0.17), flank=(0.33, 0.31, 0.24), belly=(0.66, 0.60, 0.38), mark=(0.10, 0.09, 0.07),
    pattern="spots", pattern_freq=14.0, pattern_amount=0.6,
    voxel=0.0075, max_tris=11000,
)

if __name__ == "__main__":
    pt.main(SPEC)
