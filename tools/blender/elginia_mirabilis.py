"""
Procedural Elginia mirabilis (Late Permian pareiasaur, ~60 cm) for map colonies.

A small, spectacularly horned pareiasaur from the Elgin sandstones of Scotland: a compact,
barrel-shaped, armoured body studded with bony knobs, short stout limbs and a short tail,
and a broad head crowned with a ring of long, pointed bony horns and spikes - a pair of
large horns sweeping back from the skull roof and rows of shorter spikes on the cheeks and
over the eyes. Sandy grey-brown with pale bone-coloured horns and knobs.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/elginia_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Elginia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

BONE = (0.78, 0.72, 0.58)
TORSO = [
    (-0.36, 0.36, 0.10, 0.10),
    (-0.28, 0.37, 0.20, 0.17),
    (-0.12, 0.39, 0.28, 0.23),
    (0.06, 0.40, 0.29, 0.24),
    (0.24, 0.38, 0.24, 0.20),
    (0.36, 0.34, 0.13, 0.12),
    (0.46, 0.30, 0.05, 0.05),
    (0.52, 0.28, 0.0, 0.0),
]


def horn(b, base, d, r):
    p = V(base)
    b.add(pt.cone(p, p + V(d), r, sides=8), BONE)


def fused(b, spec):
    for y in [i * 0.075 - 0.26 for i in range(9)]:      # knobby back armour
        z, hw, hh, _x = pt.rows_at(spec.torso, y)
        for t in (-0.6, -0.3, 0.0, 0.3, 0.6):
            zz = z + hh * math.sqrt(max(0.0, 1 - t * t)) - 0.005
            b.add(pt.oriented((t * hw, y, zz), (0.026, 0.026, 0.02)), BONE)
    for sx in (1, -1):
        # large horns sweeping back and out from the back of the skull
        horn(b, (sx * 0.10, -0.40, 0.45), (sx * 0.09, 0.10, 0.09), 0.028)
        horn(b, (sx * 0.06, -0.42, 0.47), (sx * 0.02, 0.06, 0.12), 0.02)
        # spikes over the eyes and on the cheeks and jaw
        horn(b, (sx * 0.085, -0.50, 0.44), (sx * 0.05, -0.01, 0.06), 0.016)
        horn(b, (sx * 0.14, -0.44, 0.37), (sx * 0.10, 0.02, -0.01), 0.022)
        horn(b, (sx * 0.12, -0.52, 0.33), (sx * 0.07, -0.02, -0.04), 0.018)
        horn(b, (sx * 0.10, -0.42, 0.30), (sx * 0.06, 0.03, -0.06), 0.018)


SPEC = pt.Spec(
    name="Elginia",
    torso=TORSO,
    head=[
        (-0.34, 0.39, 0.12, 0.08),
        (-0.44, 0.39, 0.14, 0.08),
        (-0.53, 0.375, 0.11, 0.07),
        (-0.60, 0.355, 0.07, 0.05),
        (-0.635, 0.345, 0.04, 0.032),
        (-0.645, 0.34, 0.0, 0.0),
    ],
    head_power=2.6,
    fore=pt.Limb(y=-0.18, z=0.28, x=0.20, upper=0.14, lower=0.20, sprawl=0.55, r=0.07, muscle=1.2,
                 foot=(0.055, 0.06, 0.022), toe_len=0.03, toe_r=0.013, claw=0.8),
    hind=pt.Limb(y=0.24, z=0.28, x=0.18, upper=0.14, lower=0.20, sprawl=0.5, r=0.075, muscle=1.2,
                 foot=(0.06, 0.07, 0.022), toe_len=0.03, toe_r=0.014, claw=0.8),
    eye=(0.10, -0.48, 0.42, 0.016), nostril=(0.025, -0.64, 0.37),
    back=(0.42, 0.37, 0.28), flank=(0.54, 0.48, 0.37), belly=(0.74, 0.68, 0.56), mark=(0.28, 0.24, 0.18),
    pattern="mottle", pattern_freq=7.0, pattern_amount=0.3,
    fused=fused, voxel=0.0075, max_tris=11000, scale_bumps=1.5,
)

if __name__ == "__main__":
    pt.main(SPEC)
