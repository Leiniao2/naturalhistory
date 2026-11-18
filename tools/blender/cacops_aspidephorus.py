"""
Procedural Cacops aspidephorus (Early Permian dissorophid temnospondyl, ~40 cm) for map
colonies.

A stocky, armoured land amphibian from the Texas and Oklahoma red beds: a large, broad,
box-like head with big eyes and a large ear notch at the back of the skull, a short, sturdy
body with a double row of interlocking bony plates (osteoderms) running down the spine like
a dorsal shield, sturdy legs and a short tail. Reddish-brown with a darker plated back and
a paler, yellowish underside.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cacops_aspidephorus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cacops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

PLATE = (0.24, 0.15, 0.10)
TORSO = [
    (-0.38, 0.22, 0.10, 0.08),
    (-0.30, 0.23, 0.15, 0.115),
    (-0.12, 0.24, 0.17, 0.125),
    (0.06, 0.24, 0.16, 0.12),
    (0.20, 0.22, 0.12, 0.10),
    (0.30, 0.19, 0.07, 0.065),
    (0.44, 0.14, 0.03, 0.03),
    (0.52, 0.12, 0.0, 0.0),
]


def fused(b, spec):
    # double row of armour plates down the spine
    for i in range(10):
        y = -0.34 + i * 0.07
        z, hw, hh, _x = pt.rows_at(spec.torso, y)
        for sx in (1, -1):
            b.add(pt.oriented((sx * 0.032, y, z + hh + 0.006), (0.04, 0.042, 0.02), roll=sx * 14), PLATE)
    # ear-notch ridges at the back of the skull
    for sx in (1, -1):
        b.add(pt.oriented((sx * 0.13, -0.40, pt.rows_at(spec.head, -0.40)[0] + 0.02), (0.03, 0.04, 0.03)), PLATE)


SPEC = pt.Spec(
    name="Cacops",
    torso=TORSO,
    head=[
        (-0.36, 0.28, 0.16, 0.08),
        (-0.46, 0.28, 0.16, 0.08),
        (-0.56, 0.265, 0.14, 0.07),
        (-0.64, 0.245, 0.10, 0.055),
        (-0.69, 0.235, 0.055, 0.035),
        (-0.70, 0.232, 0.0, 0.0),
    ],
    head_power=2.9,
    jaw=[
        (-0.38, 0.21, 0.14, 0.03),
        (-0.56, 0.205, 0.11, 0.025),
        (-0.68, 0.21, 0.05, 0.018),
        (-0.70, 0.21, 0.0, 0.0),
    ],
    teeth=[(-0.69, -0.45, 12, 0.010, 0.004, True)],
    fore=pt.Limb(y=-0.24, z=0.19, x=0.14, upper=0.11, lower=0.12, sprawl=0.75, r=0.042, toes=4,
                 foot=(0.04, 0.045, 0.014), toe_len=0.035, toe_r=0.010, toe_fan=70, claw=0.4),
    hind=pt.Limb(y=0.20, z=0.19, x=0.12, upper=0.12, lower=0.12, sprawl=0.7, r=0.048,
                 foot=(0.042, 0.05, 0.014), toe_len=0.04, toe_r=0.010, claw=0.4),
    eye=(0.09, -0.52, 0.33, 0.022), nostril=(0.05, -0.685, 0.255),
    back=(0.40, 0.22, 0.14), flank=(0.56, 0.32, 0.20), belly=(0.82, 0.68, 0.40), mark=(0.22, 0.12, 0.08),
    pattern="spots", pattern_freq=14.0, pattern_amount=0.4,
    fused=fused, voxel=0.006, max_tris=9000, scale_bumps=1.3, drop=0.06,
)

if __name__ == "__main__":
    pt.main(SPEC)
