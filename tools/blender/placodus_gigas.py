"""
Procedural Placodus gigas (Middle Triassic placodont, ~2 m) for map colonies (Swim style).

A stocky, slow marine reptile of the Muschelkalk sea of Germany (about 243 million years
ago). A short, deep skull with forward-jutting, peg-like front teeth for prising shellfish
off the sea floor and great flat crushing tooth-plates in the jaws and palate; a short
neck, a heavy, barrel-shaped body with a row of bony knobs down the spine, short paddle
limbs with webbed toes and a long, deep, flattened tail. Its dense, heavy bones worked as
ballast for feeding on the bottom. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted brown-grey with a darker back and a pale belly
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/placodus_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Placodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.09 * s * s


AXIS = [
    (-1.00, 0.000, 0.026, 0.030),
    (-0.96, 0.005, 0.046, 0.050),
    (-0.88, 0.012, 0.070, 0.070),
    (-0.80, 0.015, 0.085, 0.080),
    (-0.74, 0.012, 0.080, 0.080),
    (-0.62, 0.015, 0.120, 0.110),
    (-0.45, 0.020, 0.170, 0.140),
    (-0.20, 0.020, 0.180, 0.145),
    (0.02, 0.015, 0.150, 0.120),
    (0.18, 0.010, 0.090, 0.085),
    (0.38, 0.000, 0.050, 0.065, sway(0.38)),
    (0.62, -0.005, 0.030, 0.045, sway(0.62)),
    (0.85, -0.010, 0.015, 0.025, sway(0.85)),
    (1.00, -0.010, 0.003, 0.004, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.12, -0.48, -0.06), (0.22, -0.46, -0.10), (0.28, -0.42, -0.12)],
               radii=[0.042, 0.034, 0.027], paddle=(0.07, 0.045, 130, -10))
HIND = tt.Limb(pts=[(0.10, 0.05, -0.05), (0.19, 0.10, -0.09), (0.24, 0.15, -0.10)],
               radii=[0.040, 0.032, 0.026], paddle=(0.07, 0.045, 150, -10))


def front_teeth(mb, surf, spec):
    for sx in (-0.018, -0.006, 0.006, 0.018):
        base = Vector((sx, -0.985, -0.012))
        mb.add(tt.cone(base, base + Vector((sx * 0.3, -0.04, -0.022)), 0.006), tt.TOOTH, smooth=False)


SPEC = tt.TetrapodSpec(
    name="Placodus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.01, max_tris=10000,
    pivot="centre",
    mouth=(-1.0, -0.82, -0.012, -0.004, 0.005),
    eyes=(-0.82, 0.045, 0.015, (0.70, 0.55, 0.20)),
    plates=[dict(xs=(0.0,), y0=-0.62, y1=0.55, step=0.06, size=0.020, kind="knob", height=0.8, taper=0.5,
                 follow=sway, col=(0.24, 0.20, 0.15))],
    back=(0.26, 0.23, 0.19), flank=(0.48, 0.44, 0.38), belly=(0.84, 0.80, 0.70),
    pattern=("spots", (0.20, 0.17, 0.13), 14.0, 0.4),
    post=front_teeth,
)

if __name__ == "__main__":
    tt.run(SPEC)
