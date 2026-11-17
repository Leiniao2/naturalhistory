"""
Procedural Diictodon feliceps (Late Permian dicynodont, ~45 cm) for map colonies.

A small, burrowing, plant-eating dicynodont from the Karoo: a sausage-shaped body on short
sprawling forelimbs with broad clawed digging hands, a stub of a tail, and a rounded head
ending in a sharp-edged horny beak with a pair of small tusks (upper canines) growing down
beside it. Sandy buff-brown, paler beneath, with a dark beak.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/diictodon_feliceps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Diictodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

BEAK = (0.14, 0.11, 0.08)


def paint(co, n, c):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.585, -0.615, co.y) * nh.smoothstep(0.26, 0.22, co.z))


SPEC = pt.Spec(
    name="Diictodon",
    torso=[
        (-0.40, 0.20, 0.08, 0.08),
        (-0.30, 0.20, 0.13, 0.13),
        (-0.10, 0.21, 0.16, 0.15),
        (0.10, 0.21, 0.155, 0.145),
        (0.25, 0.20, 0.12, 0.11),
        (0.34, 0.18, 0.06, 0.06),
        (0.42, 0.15, 0.02, 0.02),
        (0.45, 0.14, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.25, 0.10, 0.09),
        (-0.48, 0.255, 0.095, 0.09),
        (-0.56, 0.235, 0.075, 0.075),
        (-0.62, 0.205, 0.05, 0.055),
        (-0.645, 0.19, 0.0, 0.0),
    ],
    fangs=[(0.045, -0.575, 0.20, 0.055, 0.012, -0.012)],
    fore=pt.Limb(y=-0.22, z=0.14, x=0.12, upper=0.10, lower=0.10, sprawl=0.85, r=0.040,
                 foot=(0.040, 0.042, 0.015), toe_len=0.03, toe_r=0.010, claw=1.6),
    hind=pt.Limb(y=0.20, z=0.15, x=0.10, upper=0.10, lower=0.11, sprawl=0.5, r=0.045,
                 foot=(0.038, 0.048, 0.015), toe_len=0.03, toe_r=0.010),
    eye=(0.075, -0.50, 0.29, 0.020), nostril=(0.03, -0.60, 0.27),
    back=(0.48, 0.38, 0.25), flank=(0.62, 0.50, 0.34), belly=(0.84, 0.77, 0.62), mark=(0.30, 0.22, 0.14),
    pattern="mottle", pattern_freq=10.0, pattern_amount=0.25, paint=paint,
    voxel=0.006, max_tris=7000,
)

if __name__ == "__main__":
    pt.main(SPEC)
