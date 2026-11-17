"""
Procedural Scutosaurus karpinskii (Late Permian pareiasaur, ~2.5 m) for map colonies.

A massive, armoured plant-eater from the Russian Permian: a broad, deep, barrel body
covered with rows of bony knobs (osteoderms) along the back, short stout limbs held
semi-erect, a stub of a tail and a wide, flat-topped head ringed with bony bosses and
blunt spikes on the cheeks and lower jaw. Earthy grey-brown with paler bony knobs.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/scutosaurus_karpinskii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Scutosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

BONE = (0.66, 0.58, 0.46)
TORSO = [
    (-0.40, 0.40, 0.10, 0.11),
    (-0.32, 0.40, 0.20, 0.18),
    (-0.15, 0.42, 0.30, 0.25),
    (0.05, 0.43, 0.32, 0.26),
    (0.25, 0.41, 0.27, 0.22),
    (0.40, 0.37, 0.15, 0.14),
    (0.52, 0.32, 0.07, 0.07),
    (0.64, 0.27, 0.03, 0.03),
    (0.70, 0.25, 0.0, 0.0),
]
HEAD = [
    (-0.36, 0.43, 0.14, 0.10),
    (-0.47, 0.43, 0.16, 0.10),
    (-0.57, 0.41, 0.13, 0.085),
    (-0.65, 0.385, 0.08, 0.06),
    (-0.69, 0.37, 0.05, 0.04),
    (-0.705, 0.365, 0.0, 0.0),
]


def fused(b, spec):
    # cheek bosses and jaw flanges with blunt spikes
    for sx in (1, -1):
        b.add(pt.oriented((sx * 0.15, -0.46, 0.35), (0.055, 0.075, 0.06)), BONE)
        b.add(pt.oriented((sx * 0.12, -0.56, 0.31), (0.04, 0.05, 0.045)), BONE)
        for base, d in (((0.18, -0.45, 0.33), (0.07, 0.01, -0.04)), ((0.14, -0.56, 0.29), (0.05, -0.02, -0.05)),
                        ((0.19, -0.38, 0.38), (0.06, 0.03, -0.01)), ((0.15, -0.50, 0.45), (0.04, 0.0, 0.03))):
            p = V((sx * base[0], base[1], base[2]))
            b.add(pt.cone(p, p + V((sx * d[0], d[1], d[2])), 0.022, sides=8), BONE)
    # rows of osteoderm knobs over the back
    for y in [i * 0.07 - 0.30 for i in range(11)]:
        z, hw, hh, _x = pt.rows_at(TORSO, y)
        for t in (-0.55, -0.25, 0.0, 0.25, 0.55):
            x = t * hw
            zz = z + hh * math.sqrt(max(0.0, 1 - t * t)) - 0.005
            b.add(pt.oriented((x, y + (0.02 if abs(t) == 0.25 else 0), zz), (0.028, 0.028, 0.022)), BONE)


def paint(co, n, c):
    return c


SPEC = pt.Spec(
    name="Scutosaurus",
    torso=TORSO, head=HEAD, head_power=2.6,
    fore=pt.Limb(y=-0.20, z=0.30, x=0.22, upper=0.16, lower=0.22, sprawl=0.5, r=0.085, muscle=1.2,
                 foot=(0.065, 0.070, 0.026), toe_len=0.035, toe_r=0.016, claw=0.8),
    hind=pt.Limb(y=0.25, z=0.30, x=0.20, upper=0.16, lower=0.22, sprawl=0.45, r=0.09, muscle=1.2,
                 foot=(0.070, 0.080, 0.026), toe_len=0.035, toe_r=0.017, claw=0.8),
    eye=(0.12, -0.50, 0.46, 0.017), nostril=(0.03, -0.69, 0.40),
    back=(0.30, 0.26, 0.21), flank=(0.40, 0.35, 0.28), belly=(0.62, 0.56, 0.46), mark=(0.20, 0.17, 0.14),
    pattern="mottle", pattern_freq=6.0, pattern_amount=0.3,
    fused=fused, voxel=0.009, max_tris=12000, scale_bumps=1.5,
)

if __name__ == "__main__":
    pt.main(SPEC)
