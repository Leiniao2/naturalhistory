"""
Procedural Bunostegos akokanensis (Late Permian pareiasaur, ~2 m) for map colonies.

The "knobby-roofed" pareiasaur from the desert interior of Pangaea (today's Niger): a
cow-sized, heavily built plant-eater whose skull is covered with big, rounded bony knobs -
pairs over the snout and eyes and larger ones at the back and on the cheeks - with a deep,
armoured barrel body covered in osteoderms and, unusually for a pareiasaur, fairly upright
limbs carried under the body. Warm sandy-ochre with darker rust patches and pale knobs.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/bunostegos_akokanensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Bunostegos.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

KNOB = (0.80, 0.70, 0.52)
TORSO = [
    (-0.40, 0.50, 0.10, 0.11),
    (-0.32, 0.51, 0.20, 0.19),
    (-0.15, 0.53, 0.28, 0.25),
    (0.05, 0.54, 0.29, 0.26),
    (0.25, 0.52, 0.25, 0.22),
    (0.40, 0.48, 0.14, 0.13),
    (0.52, 0.43, 0.06, 0.06),
    (0.62, 0.39, 0.02, 0.02),
    (0.66, 0.38, 0.0, 0.0),
]


def fused(b, spec):
    for y in [i * 0.08 - 0.30 for i in range(10)]:     # osteoderm armour
        z, hw, hh, _x = pt.rows_at(spec.torso, y)
        for t in (-0.7, -0.4, -0.12, 0.12, 0.4, 0.7):
            zz = z + hh * math.sqrt(max(0.0, 1 - t * t)) - 0.006
            b.add(pt.oriented((t * hw, y + (0.03 if t in (-0.4, 0.12, 0.7) else 0), zz), (0.03, 0.03, 0.022)),
                  KNOB)
    hz = lambda y: pt.rows_at(spec.head, y)  # noqa: E731
    for sx in (1, -1):
        for y, x, r in ((-0.69, 0.03, 0.028), (-0.62, 0.05, 0.033), (-0.54, 0.07, 0.04), (-0.46, 0.08, 0.05)):
            z, hw, hh, _x = hz(y)
            b.add(pt.oriented((sx * x, y, z + hh * 0.85), (r, r, r * 0.8)), KNOB)
        b.add(pt.oriented((sx * 0.15, -0.48, 0.46), (0.05, 0.06, 0.05)), KNOB)    # cheek knobs
        b.add(pt.oriented((sx * 0.13, -0.58, 0.42), (0.035, 0.04, 0.035)), KNOB)


def paint(co, n, c):
    from mathutils import noise
    v = noise.noise(co * 4.0 + pt.V((3, 1, 2)))
    return pt.nh.lerp(c, (0.48, 0.26, 0.14), 0.5 * pt.nh.smoothstep(0.2, 0.5, v))


SPEC = pt.Spec(
    name="Bunostegos",
    torso=TORSO,
    head=[
        (-0.38, 0.54, 0.13, 0.10),
        (-0.48, 0.54, 0.15, 0.10),
        (-0.58, 0.52, 0.12, 0.085),
        (-0.66, 0.50, 0.08, 0.06),
        (-0.71, 0.485, 0.05, 0.04),
        (-0.725, 0.48, 0.0, 0.0),
    ],
    head_power=2.6,
    fore=pt.Limb(y=-0.20, z=0.42, x=0.20, upper=0.18, lower=0.26, sprawl=0.25, r=0.085, muscle=1.2,
                 foot=(0.06, 0.07, 0.026), toe_len=0.035, toe_r=0.016, claw=0.7),
    hind=pt.Limb(y=0.25, z=0.42, x=0.19, upper=0.18, lower=0.26, sprawl=0.2, r=0.09, muscle=1.2,
                 foot=(0.065, 0.08, 0.026), toe_len=0.035, toe_r=0.017, claw=0.7),
    eye=(0.12, -0.54, 0.57, 0.017), nostril=(0.03, -0.72, 0.50),
    back=(0.62, 0.46, 0.28), flank=(0.72, 0.56, 0.36), belly=(0.84, 0.74, 0.58), mark=(0.40, 0.26, 0.16),
    pattern="none", paint=paint,
    fused=fused, voxel=0.009, max_tris=12000, scale_bumps=1.5,
)

if __name__ == "__main__":
    pt.main(SPEC)
