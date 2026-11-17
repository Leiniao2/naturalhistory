"""
Procedural Moschops capensis (Middle Permian tapinocephalid dinocephalian, ~2.7 m) for map
colonies.

A massive, bull-like plant-eater from the Karoo of South Africa: a short, deep head with an
enormously thickened, domed skull roof (possibly used for head-butting) and a short snout
with interlocking chisel-like front teeth, held low in front of tall, heavy shoulders; the
back slopes steeply down to the hips and a short tail. The forelimbs are stout and
semi-sprawling with the elbows out, the hind limbs more upright beneath the body. Tawny
brown, darker on the back, with a paler pinkish-grey face and belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/moschops_capensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Moschops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402

DOME = (0.62, 0.52, 0.42)


def fused(b, spec):
    b.add(pt.oriented((0, -0.58, 0.705), (0.105, 0.095, 0.065)), DOME)          # thickened skull roof
    b.add(pt.oriented((0, -0.44, 0.74), (0.14, 0.14, 0.08)), spec.back)         # shoulder hump


def paint(co, n, c):
    if co.y < -0.50:
        c = nh.lerp(c, (0.60, 0.50, 0.44), 0.5 * nh.smoothstep(-0.50, -0.70, co.y))
    return c


SPEC = pt.Spec(
    name="Moschops",
    torso=[
        (-0.48, 0.56, 0.10, 0.12),
        (-0.38, 0.59, 0.20, 0.22),
        (-0.22, 0.58, 0.27, 0.28),
        (0.00, 0.54, 0.27, 0.26),
        (0.20, 0.50, 0.24, 0.22),
        (0.34, 0.46, 0.16, 0.16),
        (0.46, 0.40, 0.07, 0.07),
        (0.56, 0.34, 0.03, 0.03),
        (0.60, 0.32, 0.0, 0.0),
    ],
    head=[
        (-0.50, 0.60, 0.12, 0.12),
        (-0.58, 0.60, 0.12, 0.13),
        (-0.66, 0.57, 0.10, 0.11),
        (-0.73, 0.52, 0.075, 0.08),
        (-0.77, 0.49, 0.045, 0.05),
        (-0.785, 0.48, 0.0, 0.0),
    ],
    teeth=[(-0.785, -0.70, 5, 0.022, 0.007, True)],
    fore=pt.Limb(y=-0.28, z=0.45, x=0.20, upper=0.20, lower=0.27, sprawl=0.55, r=0.09, muscle=1.25,
                 foot=(0.065, 0.075, 0.026), toe_len=0.04, toe_r=0.016),
    hind=pt.Limb(y=0.22, z=0.42, x=0.18, upper=0.20, lower=0.26, sprawl=0.3, r=0.10, muscle=1.2,
                 foot=(0.065, 0.080, 0.026), toe_len=0.04, toe_r=0.017),
    eye=(0.10, -0.62, 0.62, 0.019), nostril=(0.03, -0.77, 0.53),
    back=(0.38, 0.27, 0.17), flank=(0.54, 0.40, 0.27), belly=(0.74, 0.64, 0.54), mark=(0.26, 0.18, 0.11),
    pattern="stripes", pattern_freq=9.0, pattern_amount=0.0,
    fused=fused, paint=paint, voxel=0.0095, max_tris=12000,
)

if __name__ == "__main__":
    pt.main(SPEC)
