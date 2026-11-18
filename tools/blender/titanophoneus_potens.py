"""
Procedural Titanophoneus potens (Middle Permian anteosaurid dinocephalian, ~2.5 m) for map
colonies.

The "titanic murderer" from the Ural foreland of Russia: a big, heavy predator with a long,
deep skull, a slightly raised, thickened skull roof, large interlocking front incisors for
gripping and big canines, on a long, heavy body with sprawling, powerful limbs and a long,
thick tail. Dark olive-brown above with faint darker mottling, paler underneath.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/titanophoneus_potens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Titanophoneus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

ROOF = (0.46, 0.40, 0.30)


def fused(b, spec):
    b.add(pt.oriented((0, -0.56, 0.53), (0.065, 0.10, 0.04)), ROOF)        # thickened skull roof
    b.add(pt.oriented((0, -0.38, 0.52), (0.12, 0.12, 0.06)), spec.back)     # shoulder


SPEC = pt.Spec(
    name="Titanophoneus",
    torso=[
        (-0.42, 0.44, 0.09, 0.10),
        (-0.32, 0.44, 0.16, 0.15),
        (-0.15, 0.43, 0.19, 0.16),
        (0.05, 0.42, 0.18, 0.15),
        (0.22, 0.40, 0.14, 0.12),
        (0.34, 0.37, 0.10, 0.09),
        (0.60, 0.28, 0.06, 0.055),
        (0.90, 0.18, 0.03, 0.028),
        (1.10, 0.12, 0.01, 0.01),
        (1.15, 0.11, 0.0, 0.0),
    ],
    head=[
        (-0.42, 0.50, 0.09, 0.09),
        (-0.52, 0.50, 0.09, 0.095),
        (-0.64, 0.48, 0.07, 0.08),
        (-0.76, 0.45, 0.05, 0.065),
        (-0.84, 0.43, 0.035, 0.05),
        (-0.865, 0.42, 0.0, 0.0),
    ],
    head_power=2.5,
    jaw=[
        (-0.45, 0.385, 0.07, 0.032),
        (-0.66, 0.37, 0.05, 0.028),
        (-0.83, 0.37, 0.03, 0.022),
        (-0.86, 0.37, 0.0, 0.0),
    ],
    teeth=[(-0.86, -0.80, 3, 0.04, 0.010, True), (-0.72, -0.58, 6, 0.016, 0.005, True)],
    fangs=[(0.04, -0.76, 0.40, 0.08, 0.013, 0.008)],
    fore=pt.Limb(y=-0.26, z=0.36, x=0.15, upper=0.17, lower=0.21, sprawl=0.55, r=0.065, muscle=1.2,
                 foot=(0.05, 0.06, 0.018), toe_len=0.045, toe_r=0.012),
    hind=pt.Limb(y=0.22, z=0.35, x=0.14, upper=0.17, lower=0.21, sprawl=0.45, r=0.07, muscle=1.2,
                 foot=(0.05, 0.065, 0.018), toe_len=0.05, toe_r=0.013),
    eye=(0.07, -0.62, 0.52, 0.018), nostril=(0.025, -0.85, 0.45),
    back=(0.26, 0.24, 0.15), flank=(0.42, 0.38, 0.25), belly=(0.74, 0.68, 0.52), mark=(0.15, 0.13, 0.08),
    pattern="mottle", pattern_freq=9.0, pattern_amount=0.45,
    fused=fused, voxel=0.008, max_tris=12000,
)

if __name__ == "__main__":
    pt.main(SPEC)
