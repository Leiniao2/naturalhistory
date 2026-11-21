"""
Procedural Trilophosaurus buettneri (Late Triassic archosauromorph, ~2.5 m).

A lizard-like plant eater from Texas: a short, deep skull with a toothless beak at the
front and broad, three-crested cheek teeth for slicing tough plants, a long body, a long
tail and sprawling, strong-clawed legs that may have helped it dig or climb. Built with
nh_tri_tetrapod; painted grey-olive with pale cross bands. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Trilophosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


BEAK = (0.24, 0.22, 0.18)


def sway(y):
    s = max(0.0, (y - 0.0) / 1.0)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.170, 0.010, 0.020),
    (-0.975, 0.180, 0.024, 0.040),
    (-0.93, 0.192, 0.044, 0.052),
    (-0.87, 0.200, 0.058, 0.056),
    (-0.82, 0.200, 0.058, 0.052),
    (-0.77, 0.195, 0.048, 0.046),
    (-0.66, 0.195, 0.060, 0.056),
    (-0.50, 0.198, 0.094, 0.078),
    (-0.30, 0.200, 0.108, 0.086),
    (-0.10, 0.198, 0.100, 0.080),
    (0.04, 0.190, 0.072, 0.062),
    (0.20, 0.170, 0.046, 0.044, sway(0.20)),
    (0.44, 0.130, 0.030, 0.030, sway(0.44)),
    (0.72, 0.090, 0.016, 0.016, sway(0.72)),
    (1.00, 0.060, 0.003, 0.003, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.08, -0.56, 0.17), (0.19, -0.55, 0.14), (0.20, -0.58, 0.035), (0.20, -0.60, 0.010)],
               radii=[0.032, 0.026, 0.020, 0.017], toes=5, toe_len=0.040, toe_r=0.008, toe_spread=70,
               toe_yaw=20, stride=12, claw_len=0.022)
HIND = tt.Limb(pts=[(0.07, -0.02, 0.17), (0.19, -0.04, 0.14), (0.21, 0.01, 0.035), (0.21, -0.01, 0.010)],
               radii=[0.040, 0.030, 0.021, 0.018], toes=5, toe_len=0.050, toe_r=0.009, toe_spread=65,
               toe_yaw=25, stride=-12, claw_len=0.024)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.95, -0.985, co.y))


SPEC = tt.TetrapodSpec(
    name="Trilophosaurus",
    axis=AXIS,
    blobs=[((0.045, -0.86, 0.18), (0.035, 0.05, 0.035))],
    limbs=[FORE, HIND],
    voxel=0.0075, max_tris=10000,
    mouth=(-0.99, -0.82, 0.162, 0.180, 0.004),
    eyes=(-0.86, 0.222, 0.012, (0.80, 0.55, 0.15)),
    nostrils=(-0.97, 0.19),
    back=(0.28, 0.29, 0.22), flank=(0.48, 0.48, 0.38), belly=(0.82, 0.80, 0.66),
    pattern=("bands", (0.74, 0.70, 0.54), 22.0, 0.7, -0.7, 1.0),
    paint_extra=paint_extra,
)

if __name__ == "__main__":
    tt.run(SPEC)
