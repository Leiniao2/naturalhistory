"""
Procedural Kannemeyeria simocephalus (Middle Triassic dicynodont, ~3 m) for map colonies.

A big, barrel-bodied plant eater of the Karoo of South Africa: a long, narrow, high
snout ending in a horny beak, a pair of short tusks, a broad bony ridge over the
nostrils, a short tail and stout, semi-erect legs. Built with the shared Triassic
tetrapod recipe (nh_tri_tetrapod.py); painted dull olive-grey with a paler belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kannemeyeria_simocephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kannemeyeria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.22, 0.19, 0.15)
TUSK = (0.90, 0.86, 0.72)

AXIS = [
    (-1.00, 0.330, 0.020, 0.040),
    (-0.96, 0.360, 0.040, 0.075),
    (-0.88, 0.410, 0.058, 0.100),
    (-0.80, 0.450, 0.075, 0.110),
    (-0.72, 0.470, 0.098, 0.112),
    (-0.64, 0.470, 0.108, 0.110),
    (-0.56, 0.470, 0.105, 0.110),
    (-0.46, 0.480, 0.175, 0.170),
    (-0.28, 0.495, 0.240, 0.220),
    (-0.04, 0.505, 0.250, 0.225),
    (0.18, 0.495, 0.205, 0.190),
    (0.34, 0.465, 0.130, 0.120),
    (0.48, 0.420, 0.065, 0.060),
    (0.58, 0.380, 0.028, 0.026),
    (0.64, 0.360, 0.004, 0.004),
]

FORE = tt.Limb(pts=[(0.17, -0.36, 0.36), (0.24, -0.34, 0.22), (0.23, -0.38, 0.07), (0.23, -0.40, 0.018)],
               radii=[0.090, 0.068, 0.054, 0.050], toes=5, toe_len=0.035, toe_r=0.016, toe_spread=70,
               stride=8, claw_len=0.016)
HIND = tt.Limb(pts=[(0.16, 0.22, 0.38), (0.20, 0.15, 0.22), (0.20, 0.24, 0.065), (0.20, 0.21, 0.018)],
               radii=[0.100, 0.075, 0.056, 0.050], toes=5, toe_len=0.035, toe_r=0.016, toe_spread=70,
               stride=-8, claw_len=0.016)


def tusks(mb, surf, spec):
    for sx in (1, -1):
        base = tt.Vector((sx * 0.055, -0.90, 0.36))
        mb.add(tt.curved_spike(base, (sx * 0.1, -0.2, -1.0), 0.10, 0.016, bend=(0, -0.3, 0)), TUSK)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.94, -0.975, co.y))


SPEC = tt.TetrapodSpec(
    name="Kannemeyeria",
    axis=AXIS,
    blobs=[((0.05, -0.90, 0.37), (0.03, 0.045, 0.05)),        # tusk bosses
           ((0.0, -0.80, 0.555), (0.05, 0.10, 0.03), -10),      # nasal ridge
           ((0.0, -0.84, 0.32), (0.06, 0.12, 0.04), 8)],        # lower jaw
    limbs=[FORE, HIND],
    voxel=0.011, max_tris=11000,
    mouth=(-1.0, -0.78, 0.325, 0.36, 0.005),
    eyes=(-0.70, 0.535, 0.017, (0.60, 0.42, 0.18)),
    nostrils=(-0.93, 0.42),
    back=(0.28, 0.27, 0.20), flank=(0.48, 0.46, 0.36), belly=(0.80, 0.76, 0.62),
    pattern=("mottle", (0.34, 0.33, 0.25), 6.0, 0.4),
    paint_extra=paint_extra,
    post=tusks,
)

if __name__ == "__main__":
    tt.run(SPEC)
