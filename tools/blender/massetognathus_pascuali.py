"""
Procedural Massetognathus pascuali (Middle-Late Triassic traversodontid cynodont, ~50 cm).

A cat-sized plant-eating relative of mammals from the Chañares beds of Argentina: a short,
deep head with broad cheeks (wide grinding cheek teeth), a stocky body, a medium tail and
semi-erect legs. Fur and whiskers are speculative; painted tawny with dark back stripes
and a pale belly. Built with nh_tri_tetrapod. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Massetognathus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.15) / 0.6)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.300, 0.012, 0.014),
    (-0.96, 0.312, 0.035, 0.040),
    (-0.89, 0.330, 0.060, 0.060),
    (-0.80, 0.345, 0.085, 0.074),
    (-0.72, 0.350, 0.092, 0.078),
    (-0.64, 0.345, 0.078, 0.074),
    (-0.54, 0.345, 0.100, 0.100),
    (-0.38, 0.350, 0.130, 0.124),
    (-0.18, 0.352, 0.138, 0.128),
    (0.02, 0.350, 0.124, 0.116),
    (0.16, 0.338, 0.098, 0.092),
    (0.28, 0.315, 0.058, 0.054),
    (0.46, 0.272, 0.034, 0.032, sway(0.46)),
    (0.66, 0.228, 0.019, 0.018, sway(0.66)),
    (0.82, 0.198, 0.004, 0.004, sway(0.82)),
]

FORE = tt.Limb(pts=[(0.10, -0.42, 0.28), (0.16, -0.40, 0.17), (0.155, -0.44, 0.045), (0.155, -0.46, 0.012)],
               radii=[0.045, 0.036, 0.027, 0.022], toes=5, toe_len=0.035, toe_r=0.010, toe_spread=65,
               toe_yaw=10, stride=12, claw_len=0.015)
HIND = tt.Limb(pts=[(0.09, 0.12, 0.30), (0.145, 0.06, 0.18), (0.145, 0.15, 0.05), (0.145, 0.12, 0.012)],
               radii=[0.056, 0.040, 0.029, 0.022], toes=5, toe_len=0.040, toe_r=0.011, toe_spread=60,
               toe_yaw=10, stride=-12, claw_len=0.016)


def whiskers(mb, surf, spec):
    for sx in (1, -1):
        for k in range(3):
            b = tt.Vector((sx * 0.035, -0.95, 0.315 + 0.008 * k))
            mb.add(nh.tube([b, b + tt.Vector((sx * 0.09, 0.01, 0.01 * (k - 1)))], [0.0025, 0.0005], sides=4),
                   (0.85, 0.82, 0.72))


SPEC = tt.TetrapodSpec(
    name="Massetognathus",
    axis=AXIS,
    blobs=[((0.07, -0.78, 0.33), (0.045, 0.07, 0.05)),            # deep cheeks
           ((0.08, 0.13, 0.29), (0.06, 0.10, 0.09), 25)],
    limbs=[FORE, HIND],
    voxel=0.009, max_tris=9000,
    scale_bump=0.0010, scale_freq=90.0,
    mouth=(-0.995, -0.80, 0.296, 0.318, 0.004),
    teeth=(4, 0.014, 0.005, -0.99, -0.95),
    eyes=(-0.80, 0.385, 0.015, (0.30, 0.20, 0.10)),
    nostrils=(-0.99, 0.31),
    back=(0.40, 0.28, 0.16), flank=(0.66, 0.50, 0.32), belly=(0.90, 0.84, 0.70),
    pattern=("bands", (0.22, 0.15, 0.09), 30.0, 0.6, -0.6, 0.3),
    post=whiskers,
)

if __name__ == "__main__":
    tt.run(SPEC)
