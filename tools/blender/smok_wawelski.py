"""
Procedural Smok wawelski (Late Triassic loricatan archosaur, ~5.5 m) for map colonies.

The top predator of the Lisowice site in southern Poland, about 205 million years ago,
named after the Wawel dragon of Kraków legend. A heavy, deep-bodied crocodile-line
predator with its legs held straight under the body and long hind legs (it may have
walked on two legs at times), a short thick neck and a huge, tall, broad-snouted skull
with big serrated teeth; its droppings are packed with crushed bone, so it bit through
the skeletons of its prey like a tyrannosaur. Two rows of low scutes down the back.
Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted rust-brown
with dark cross-bands, a paler head and a cream belly (speculative). Faces -Y, pivot on
the ground.

Usage:
  blender --background --python tools/blender/smok_wawelski.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Smok.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.500, 0.020, 0.030),
    (-0.965, 0.505, 0.048, 0.062),
    (-0.89, 0.520, 0.064, 0.088),
    (-0.80, 0.540, 0.080, 0.122),
    (-0.70, 0.560, 0.098, 0.134),
    (-0.62, 0.552, 0.100, 0.122),
    (-0.55, 0.530, 0.090, 0.098),
    (-0.46, 0.520, 0.110, 0.118),
    (-0.34, 0.520, 0.140, 0.150),
    (-0.18, 0.525, 0.150, 0.155),
    (-0.02, 0.535, 0.140, 0.140),
    (0.12, 0.540, 0.112, 0.110),
    (0.26, 0.520, 0.074, 0.074),
    (0.45, 0.480, 0.050, 0.050, sway(0.45)),
    (0.65, 0.430, 0.032, 0.032, sway(0.65)),
    (0.85, 0.385, 0.016, 0.016, sway(0.85)),
    (1.00, 0.355, 0.003, 0.003, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.10, -0.36, 0.45), (0.13, -0.34, 0.30), (0.125, -0.38, 0.13), (0.125, -0.40, 0.016)],
               radii=[0.066, 0.050, 0.038, 0.032], toes=5, toe_len=0.04, toe_r=0.011, toe_spread=60,
               stride=10, claw_len=0.018)
HIND = tt.Limb(pts=[(0.11, 0.10, 0.50), (0.145, 0.00, 0.31), (0.135, 0.12, 0.07), (0.135, 0.07, 0.016)],
               radii=[0.092, 0.066, 0.046, 0.036], toes=4, toe_len=0.07, toe_r=0.015, toe_spread=50,
               stride=-12, claw_len=0.022)

SPEC = tt.TetrapodSpec(
    name="Smok",
    axis=AXIS,
    blobs=[((0.10, 0.12, 0.48), (0.08, 0.15, 0.13), 25),          # thigh
           ((0.06, -0.66, 0.53), (0.05, 0.08, 0.08)),              # jaw muscles
           ((0.0, -0.80, 0.465), (0.06, 0.17, 0.04), 4)],          # deep lower jaw
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=12500,
    mouth=(-1.0, -0.62, 0.488, 0.505, 0.007),
    teeth=(10, 0.040, 0.0095, -0.985, -0.66), lower_teeth=True,
    eyes=(-0.665, 0.605, 0.0145, (0.90, 0.62, 0.12)),
    nostrils=(-0.975, 0.52),
    plates=[dict(xs=(0.026, -0.026), y0=-0.55, y1=0.95, step=0.055, size=0.024, taper=0.6, shrink=0.4,
                 follow=sway, col=(0.22, 0.12, 0.08), keel_col=(0.38, 0.24, 0.16), wide=1.1)],
    back=(0.32, 0.17, 0.10), flank=(0.58, 0.36, 0.22), belly=(0.86, 0.78, 0.62),
    pattern=("bands", (0.14, 0.08, 0.05), 18.0, 0.85, -0.55, 1.0),
    head=((0.66, 0.50, 0.36), -0.60, 0.35),
)

if __name__ == "__main__":
    tt.run(SPEC)
