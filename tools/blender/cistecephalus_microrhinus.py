"""
Procedural Cistecephalus microrhinus (Late Permian burrowing dicynodont, ~30 cm) for map
colonies.

A small, mole-like dicynodont of the Karoo: a flat, broad, wedge-shaped head (wider than long
at the back) with a short horny beak and tiny eyes, a compact, sausage-shaped body with no
neck to speak of, very short, massively built forelimbs with broad, clawed hands for
digging, smaller hind limbs and a stubby tail. Earthy grey-brown with a dark beak.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cistecephalus_microrhinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cistecephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

BEAK = (0.12, 0.10, 0.08)


def paint(co, n, c):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.60, -0.63, co.y) * nh.smoothstep(0.20, 0.17, co.z))


SPEC = pt.Spec(
    name="Cistecephalus",
    torso=[
        (-0.36, 0.17, 0.12, 0.09),
        (-0.26, 0.17, 0.15, 0.115),
        (-0.08, 0.17, 0.16, 0.12),
        (0.10, 0.165, 0.15, 0.115),
        (0.24, 0.16, 0.12, 0.10),
        (0.34, 0.14, 0.06, 0.06),
        (0.40, 0.12, 0.02, 0.02),
        (0.42, 0.115, 0.0, 0.0),
    ],
    head=[
        (-0.34, 0.19, 0.15, 0.07),
        (-0.42, 0.185, 0.15, 0.065),
        (-0.52, 0.175, 0.11, 0.055),
        (-0.60, 0.16, 0.065, 0.04),
        (-0.64, 0.15, 0.03, 0.025),
        (-0.65, 0.148, 0.0, 0.0),
    ],
    head_power=2.9,
    fore=pt.Limb(y=-0.22, z=0.12, x=0.13, upper=0.08, lower=0.07, sprawl=0.9, r=0.05, muscle=1.4,
                 foot=(0.05, 0.05, 0.014), toe_len=0.035, toe_r=0.011, toe_fan=80, claw=2.2),
    hind=pt.Limb(y=0.22, z=0.12, x=0.11, upper=0.07, lower=0.07, sprawl=0.7, r=0.038,
                 foot=(0.035, 0.04, 0.012), toe_len=0.025, toe_r=0.008, claw=1.0),
    eye=(0.10, -0.47, 0.215, 0.010), nostril=(0.025, -0.64, 0.165),
    back=(0.40, 0.34, 0.27), flank=(0.52, 0.45, 0.36), belly=(0.74, 0.66, 0.54), mark=(0.26, 0.21, 0.16),
    pattern="mottle", pattern_freq=10.0, pattern_amount=0.3, paint=paint,
    voxel=0.006, max_tris=7000,
)

if __name__ == "__main__":
    pt.main(SPEC)
