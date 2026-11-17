"""
Procedural Saurosuchus galilei (Late Triassic loricatan pseudosuchian, ~6.5 m) for map
colonies.

The top predator of the Ischigualasto Formation of Argentina, about 231 million years
ago: a long, heavy, four-legged crocodile-line archosaur with its legs held erect under
the body, a huge, deep, narrow skull (about a sixth of its length) armed with big
serrated teeth, a short thick neck, a long body and long heavy tail, and two rows of
bony scutes down the back. Lower and longer than its relative Postosuchus. Built with
the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted dark slate-olive with
pale yellowish cross-bands and a cream belly (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/saurosuchus_galilei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Saurosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.360, 0.008, 0.014),
    (-0.965, 0.370, 0.028, 0.040),
    (-0.89, 0.385, 0.040, 0.060),
    (-0.81, 0.400, 0.050, 0.075),
    (-0.73, 0.412, 0.064, 0.086),
    (-0.665, 0.405, 0.070, 0.086),
    (-0.60, 0.392, 0.072, 0.082),
    (-0.50, 0.388, 0.096, 0.106),
    (-0.38, 0.385, 0.124, 0.130),
    (-0.22, 0.385, 0.138, 0.138),
    (-0.05, 0.390, 0.134, 0.130),
    (0.10, 0.395, 0.114, 0.110),
    (0.25, 0.380, 0.080, 0.080),
    (0.45, 0.345, 0.055, 0.055, sway(0.45)),
    (0.65, 0.305, 0.035, 0.035, sway(0.65)),
    (0.85, 0.265, 0.018, 0.018, sway(0.85)),
    (1.02, 0.235, 0.003, 0.003, sway(1.02)),
]

FORE = tt.Limb(pts=[(0.09, -0.37, 0.33), (0.122, -0.35, 0.20), (0.116, -0.39, 0.055), (0.116, -0.41, 0.016)],
               radii=[0.055, 0.042, 0.031, 0.026], toes=5, toe_len=0.04, toe_r=0.011, toe_spread=60,
               stride=12, claw_len=0.018)
HIND = tt.Limb(pts=[(0.10, 0.10, 0.36), (0.132, 0.03, 0.22), (0.126, 0.13, 0.06), (0.126, 0.085, 0.016)],
               radii=[0.070, 0.050, 0.035, 0.028], toes=4, toe_len=0.06, toe_r=0.013, toe_spread=50,
               stride=-12, claw_len=0.02)

SPEC = tt.TetrapodSpec(
    name="Saurosuchus",
    axis=AXIS,
    blobs=[((0.095, 0.12, 0.32), (0.07, 0.13, 0.11), 25),
           ((0.0, -0.82, 0.335), (0.045, 0.16, 0.032), 4),
           ((0.05, -0.68, 0.40), (0.04, 0.06, 0.06))],
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=12500,
    mouth=(-1.0, -0.665, 0.348, 0.372, 0.006),
    teeth=(11, 0.030, 0.0075, -0.985, -0.70), lower_teeth=True,
    eyes=(-0.705, 0.455, 0.0135, (0.85, 0.65, 0.15)),
    nostrils=(-0.975, 0.38),
    plates=[dict(xs=(0.028, -0.028), y0=-0.60, y1=0.95, step=0.055, size=0.025, taper=0.6, shrink=0.4,
                 follow=sway, col=(0.17, 0.18, 0.13), keel_col=(0.30, 0.30, 0.22), wide=1.1)],
    back=(0.22, 0.24, 0.18), flank=(0.42, 0.42, 0.32), belly=(0.82, 0.78, 0.60),
    pattern=("bands", (0.72, 0.66, 0.42), 20.0, 0.55, -0.55, 1.0),
)

if __name__ == "__main__":
    tt.run(SPEC)
