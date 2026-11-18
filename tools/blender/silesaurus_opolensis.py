"""
Procedural Silesaurus opolensis (Late Triassic silesaurid, ~2.3 m) for map colonies.

A slender, long-legged four-footed relative of the first dinosaurs from Krasiejów in
southern Poland, about 230 million years ago (often placed at the base of the
bird-hipped dinosaurs). A small head on a long, thin neck, jaws with leaf-shaped teeth
and a toothless, probably horn-covered tip to the lower jaw, a light body, long thin
legs (the front ones shorter) and a long tail; built to cover ground fast. It cropped
plants and probably picked up beetles too. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted fawn with a darker back, pale belly and faint bars
(speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/silesaurus_opolensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Silesaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.22, 0.18, 0.14)


def sway(y):
    s = max(0.0, (y - 0.1) / 0.9)
    return 0.09 * s * s


AXIS = [
    (-1.00, 0.550, 0.004, 0.007),
    (-0.97, 0.556, 0.012, 0.015),
    (-0.92, 0.566, 0.019, 0.024),
    (-0.87, 0.576, 0.024, 0.031),
    (-0.83, 0.580, 0.026, 0.031),
    (-0.79, 0.570, 0.019, 0.022),
    (-0.72, 0.530, 0.019, 0.022),
    (-0.63, 0.475, 0.024, 0.029),
    (-0.53, 0.435, 0.040, 0.046),
    (-0.40, 0.427, 0.062, 0.070),
    (-0.24, 0.451, 0.070, 0.077),
    (-0.08, 0.482, 0.066, 0.070),
    (0.05, 0.505, 0.053, 0.055),
    (0.22, 0.490, 0.033, 0.035, sway(0.22)),
    (0.45, 0.455, 0.020, 0.021, sway(0.45)),
    (0.72, 0.415, 0.010, 0.010, sway(0.72)),
    (1.00, 0.380, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.05, -0.43, 0.41), (0.066, -0.41, 0.26), (0.062, -0.45, 0.09), (0.062, -0.46, 0.012)],
               radii=[0.028, 0.020, 0.014, 0.012], toes=4, toe_len=0.022, toe_r=0.006, toe_spread=40,
               stride=12, claw_len=0.009)
HIND = tt.Limb(pts=[(0.05, 0.02, 0.49), (0.068, -0.07, 0.32), (0.066, 0.05, 0.12), (0.066, 0.00, 0.012)],
               radii=[0.046, 0.028, 0.017, 0.013], toes=4, toe_len=0.045, toe_r=0.008, toe_spread=40,
               stride=-14, claw_len=0.012)


def beak(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.95, -0.985, co.y) * nh.smoothstep(0.57, 0.55, co.z))


SPEC = tt.TetrapodSpec(
    name="Silesaurus",
    axis=AXIS,
    blobs=[((0.05, 0.03, 0.46), (0.040, 0.085, 0.07), 25)],
    limbs=[FORE, HIND],
    voxel=0.0075, max_tris=8000,
    mouth=(-1.0, -0.84, 0.548, 0.560, 0.003),
    eyes=(-0.845, 0.590, 0.0105, (0.80, 0.55, 0.15)),
    back=(0.42, 0.32, 0.22), flank=(0.66, 0.56, 0.42), belly=(0.90, 0.86, 0.76),
    pattern=("bands", (0.30, 0.22, 0.15), 26.0, 0.6, -0.5, 1.0),
    paint_extra=beak,
)

if __name__ == "__main__":
    tt.run(SPEC)
