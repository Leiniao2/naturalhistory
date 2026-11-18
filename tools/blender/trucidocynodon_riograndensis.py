"""
Procedural Trucidocynodon riograndensis (Late Triassic ecteniniid cynodont, ~1.2 m) for
map colonies.

The "butcher cynodont" from the Santa Maria Formation of southern Brazil, about 230
million years ago: one of the largest meat-eating cynodonts of its time, a relative of
the ancestors of mammals. Long, slender, upright legs built for running, a long,
dog-like skull with big canine fangs and blade-like cheek teeth, and a fairly short tail;
probably covered in hair. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py) plus crisp fangs. Painted tawny with dark stripes across the back
and a pale muzzle and belly (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/trucidocynodon_riograndensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Trucidocynodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.35) / 0.65)
    return 0.06 * s * s


AXIS = [
    (-1.00, 0.400, 0.009, 0.011),
    (-0.96, 0.408, 0.029, 0.036),
    (-0.88, 0.425, 0.045, 0.054),
    (-0.79, 0.442, 0.060, 0.067),
    (-0.71, 0.452, 0.074, 0.074),
    (-0.64, 0.445, 0.065, 0.067),
    (-0.56, 0.430, 0.072, 0.083),
    (-0.44, 0.440, 0.101, 0.112),
    (-0.26, 0.450, 0.116, 0.123),
    (-0.06, 0.450, 0.110, 0.114),
    (0.10, 0.445, 0.092, 0.099),
    (0.24, 0.425, 0.056, 0.058),
    (0.40, 0.385, 0.034, 0.034, sway(0.40)),
    (0.58, 0.335, 0.018, 0.018, sway(0.58)),
    (0.72, 0.300, 0.004, 0.004, sway(0.72)),
]

FORE = tt.Limb(pts=[(0.08, -0.42, 0.38), (0.11, -0.40, 0.23), (0.105, -0.45, 0.08), (0.105, -0.47, 0.014)],
               radii=[0.044, 0.034, 0.025, 0.021], toes=5, toe_len=0.03, toe_r=0.008, toe_spread=55,
               stride=14, claw_len=0.013)
HIND = tt.Limb(pts=[(0.08, 0.10, 0.40), (0.115, 0.03, 0.25), (0.11, 0.13, 0.09), (0.11, 0.09, 0.014)],
               radii=[0.056, 0.040, 0.026, 0.021], toes=5, toe_len=0.038, toe_r=0.009, toe_spread=55,
               stride=-14, claw_len=0.014)


def fangs(mb, surf, spec):
    for sx in (1, -1):
        loc, n = surf.hit((sx * 2.0, -0.925, 0.41), (-sx, 0, 0))
        if loc is None:
            continue
        base = loc - n * 0.006
        mb.add(nh.tube([base, base + Vector((0, 0.004, -0.030)), base + Vector((0, 0.010, -0.050))],
                       [0.0075, 0.005, 0.0], sides=6), tt.TOOTH, smooth=False)


def muzzle(co, n, c, spec):
    return nh.lerp(c, (0.86, 0.78, 0.62), 0.45 * nh.smoothstep(-0.84, -0.93, co.y) * nh.smoothstep(0.3, -0.4, n.z))


SPEC = tt.TetrapodSpec(
    name="Trucidocynodon",
    axis=AXIS,
    blobs=[((0.08, 0.11, 0.39), (0.06, 0.10, 0.09), 25),
           ((0.05, -0.70, 0.435), (0.035, 0.05, 0.04))],
    limbs=[FORE, HIND],
    voxel=0.0085, max_tris=9000,
    scale_bump=0.0010, scale_freq=90.0,
    mouth=(-0.995, -0.72, 0.394, 0.410, 0.004),
    teeth=(9, 0.014, 0.0045, -0.90, -0.76),
    eyes=(-0.74, 0.478, 0.0135, (0.40, 0.25, 0.10)),
    nostrils=(-0.985, 0.405),
    back=(0.42, 0.30, 0.16), flank=(0.68, 0.52, 0.32), belly=(0.90, 0.84, 0.70),
    pattern=("bands", (0.18, 0.12, 0.07), 30.0, 0.8, -0.55, 0.45),
    paint_extra=muzzle,
    post=fangs,
)

if __name__ == "__main__":
    tt.run(SPEC)
