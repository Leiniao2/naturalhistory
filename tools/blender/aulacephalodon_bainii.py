"""
Procedural Aulacephalodon bainii (Late Permian dicynodont, ~2 m) for map colonies.

One of the largest Late Permian dicynodonts of the Karoo: a very broad, heavy skull with a
toothless horny beak, a pair of big downward tusks and large, rough bosses on top of the
snout (possibly used in shoving contests), on a massive, low barrel body with sprawling,
powerful forelimbs, more upright hind limbs and a short tail. Grey-brown hide with a dark
beak and pale bosses and tusks.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/aulacephalodon_bainii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Aulacephalodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

BEAK = (0.12, 0.10, 0.08)
BOSS = (0.66, 0.60, 0.50)


def fused(b, spec):
    for sx in (1, -1):
        b.add(pt.oriented((sx * 0.06, -0.68, 0.49), (0.05, 0.06, 0.035)), BOSS)   # nasal bosses
        b.add(pt.oriented((sx * 0.15, -0.52, 0.47), (0.05, 0.07, 0.05)), spec.flank)  # wide cheeks


def paint(co, n, c):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.71, -0.75, co.y) * nh.smoothstep(0.50, 0.46, co.z))


SPEC = pt.Spec(
    name="Aulacephalodon",
    torso=[
        (-0.40, 0.40, 0.12, 0.12),
        (-0.30, 0.41, 0.22, 0.20),
        (-0.12, 0.43, 0.31, 0.26),
        (0.08, 0.43, 0.31, 0.26),
        (0.26, 0.41, 0.26, 0.22),
        (0.40, 0.37, 0.15, 0.13),
        (0.50, 0.33, 0.06, 0.06),
        (0.58, 0.30, 0.02, 0.02),
        (0.61, 0.29, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.47, 0.15, 0.11),
        (-0.48, 0.47, 0.17, 0.11),
        (-0.60, 0.45, 0.13, 0.10),
        (-0.70, 0.42, 0.09, 0.08),
        (-0.76, 0.39, 0.05, 0.055),
        (-0.78, 0.38, 0.0, 0.0),
    ],
    head_power=2.6,
    fangs=[(0.08, -0.68, 0.37, 0.10, 0.02, -0.02)],
    fore=pt.Limb(y=-0.20, z=0.30, x=0.24, upper=0.16, lower=0.20, sprawl=0.7, r=0.08, muscle=1.25,
                 foot=(0.07, 0.07, 0.024), toe_len=0.035, toe_r=0.016, claw=1.2),
    hind=pt.Limb(y=0.26, z=0.30, x=0.20, upper=0.15, lower=0.21, sprawl=0.4, r=0.085, muscle=1.2,
                 foot=(0.065, 0.08, 0.024), toe_len=0.035, toe_r=0.016),
    eye=(0.12, -0.56, 0.52, 0.018), nostril=(0.04, -0.75, 0.43),
    back=(0.36, 0.33, 0.28), flank=(0.50, 0.46, 0.39), belly=(0.74, 0.70, 0.60), mark=(0.24, 0.22, 0.18),
    pattern="mottle", pattern_freq=6.0, pattern_amount=0.35, paint=paint,
    fused=fused, voxel=0.009, max_tris=12000, scale_bumps=1.3,
)

if __name__ == "__main__":
    pt.main(SPEC)
