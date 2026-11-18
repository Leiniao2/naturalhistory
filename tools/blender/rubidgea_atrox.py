"""
Procedural Rubidgea atrox (Late Permian rubidgeine gorgonopsian, ~3 m) for map colonies.

One of the largest African gorgonopsians and the heaviest-skulled of them all: a very broad,
deep skull that flares out behind the eyes into massive cheek bones, rough bony bosses over
the eyes and cheeks, a short deep snout and enormous sabre-like upper canines reaching below
the chin. A powerful, deep-chested body on stout, fairly erect limbs and a medium tail.
Dark rust-brown with blackish spots over the back and a pale buff belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/rubidgea_atrox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rubidgea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

BOSS = (0.46, 0.34, 0.24)


def fused(b, spec):
    for sx in (1, -1):
        # flaring cheek (zygomatic) bones behind the eyes
        b.add(pt.oriented((sx * 0.10, -0.50, 0.47), (0.06, 0.08, 0.06)), spec.flank)
        # rough bosses over the eyes and on the cheeks
        b.add(pt.oriented((sx * 0.07, -0.60, 0.555), (0.032, 0.035, 0.022)), BOSS)
        b.add(pt.oriented((sx * 0.125, -0.49, 0.45), (0.03, 0.04, 0.03)), BOSS)
    b.add(pt.oriented((0, -0.40, 0.56), (0.10, 0.12, 0.07)), spec.back)      # neck/shoulder muscle


SPEC = pt.Spec(
    name="Rubidgea",
    torso=[
        (-0.42, 0.47, 0.09, 0.10),
        (-0.33, 0.47, 0.16, 0.16),
        (-0.18, 0.46, 0.19, 0.18),
        (0.00, 0.45, 0.18, 0.17),
        (0.18, 0.44, 0.15, 0.14),
        (0.30, 0.42, 0.11, 0.10),
        (0.50, 0.35, 0.06, 0.06),
        (0.72, 0.26, 0.035, 0.035),
        (0.88, 0.20, 0.012, 0.012),
        (0.93, 0.19, 0.0, 0.0),
    ],
    head=[
        (-0.42, 0.52, 0.11, 0.10),
        (-0.50, 0.52, 0.12, 0.105),
        (-0.60, 0.50, 0.095, 0.09),
        (-0.70, 0.47, 0.07, 0.075),
        (-0.77, 0.45, 0.05, 0.055),
        (-0.795, 0.44, 0.0, 0.0),
    ],
    head_power=2.6,
    jaw=[
        (-0.45, 0.405, 0.085, 0.035),
        (-0.62, 0.39, 0.06, 0.03),
        (-0.76, 0.385, 0.035, 0.024),
        (-0.79, 0.385, 0.0, 0.0),
    ],
    teeth=[(-0.785, -0.75, 3, 0.022, 0.007, True)],
    fangs=[(0.045, -0.725, 0.42, 0.13, 0.016, 0.015)],
    fore=pt.Limb(y=-0.28, z=0.38, x=0.13, upper=0.18, lower=0.21, sprawl=0.35, r=0.065, muscle=1.2,
                 foot=(0.045, 0.058, 0.018), toe_len=0.045, toe_r=0.012),
    hind=pt.Limb(y=0.20, z=0.38, x=0.12, upper=0.19, lower=0.21, sprawl=0.25, r=0.072, muscle=1.15,
                 foot=(0.045, 0.065, 0.018), toe_len=0.05, toe_r=0.012),
    eye=(0.075, -0.60, 0.53, 0.017), nostril=(0.025, -0.785, 0.465),
    back=(0.32, 0.18, 0.10), flank=(0.50, 0.30, 0.17), belly=(0.82, 0.70, 0.52), mark=(0.10, 0.07, 0.05),
    pattern="spots", pattern_freq=16.0, pattern_amount=0.7,
    fused=fused, voxel=0.0075, max_tris=12000,
)

if __name__ == "__main__":
    pt.main(SPEC)
