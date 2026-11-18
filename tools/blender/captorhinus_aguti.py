"""
Procedural Captorhinus aguti (Early Permian captorhinid reptile, ~25 cm) for map colonies.

A small, lizard-like early reptile from the Texas and Oklahoma red beds: a broad, triangular
head with a slightly hooked snout and several rows of teeth for crushing insects and tough
plants, a stout body on sprawling legs and a long tail - one of the earliest animals known
to shed its tail to escape predators, along breakage planes in the tail bones, and regrow it.
The regrown tail tip is shown plainer and paler than the banded original part.
Grey-brown with dark cross-bands and a cream belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/captorhinus_aguti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Captorhinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402


def paint(co, n, c):
    return nh.lerp(c, (0.66, 0.60, 0.48), nh.smoothstep(0.62, 0.70, co.y))   # regrown tail tip


SPEC = pt.Spec(
    name="Captorhinus",
    torso=[
        (-0.36, 0.14, 0.06, 0.05),
        (-0.28, 0.145, 0.10, 0.075),
        (-0.12, 0.15, 0.12, 0.085),
        (0.06, 0.15, 0.115, 0.08),
        (0.18, 0.14, 0.085, 0.065),
        (0.28, 0.12, 0.05, 0.045),
        (0.55, 0.08, 0.028, 0.025),
        (0.85, 0.05, 0.012, 0.011),
        (1.00, 0.04, 0.0, 0.0),
    ],
    head=[
        (-0.34, 0.165, 0.085, 0.055),
        (-0.42, 0.165, 0.085, 0.052),
        (-0.50, 0.155, 0.06, 0.042),
        (-0.57, 0.14, 0.032, 0.03),
        (-0.60, 0.132, 0.0, 0.0),
    ],
    head_power=2.5,
    teeth=[(-0.58, -0.40, 10, 0.008, 0.0028, True)],
    fore=pt.Limb(y=-0.22, z=0.11, x=0.09, upper=0.08, lower=0.08, sprawl=0.9, r=0.025,
                 foot=(0.022, 0.026, 0.008), toe_len=0.03, toe_r=0.005),
    hind=pt.Limb(y=0.17, z=0.11, x=0.08, upper=0.09, lower=0.09, sprawl=0.85, r=0.03,
                 foot=(0.025, 0.03, 0.008), toe_len=0.035, toe_r=0.0055),
    eye=(0.06, -0.44, 0.19, 0.014), nostril=(0.015, -0.595, 0.15),
    back=(0.36, 0.32, 0.26), flank=(0.50, 0.45, 0.36), belly=(0.86, 0.80, 0.66), mark=(0.16, 0.13, 0.10),
    pattern="bands", pattern_freq=30.0, pattern_amount=0.75, paint=paint,
    voxel=0.0045, max_tris=7000,
)

if __name__ == "__main__":
    pt.main(SPEC)
