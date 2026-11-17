"""
Procedural Thrinaxodon liorhinus (Early Triassic cynodont, ~45 cm) for map colonies.

A small, low-slung, fox-sized relative of mammals from the Karoo of South Africa and
from Antarctica, about 250 million years ago, soon after the end-Permian extinction.
A pointed snout with small incisors, a pair of canines and three-cusped cheek teeth, a
long low body (its ribcage already had a distinct chest and lower back, hinting at a
diaphragm), a fairly short tail and semi-sprawling legs. Fossils curled up in burrows,
one shared with an injured amphibian, show it dug and rested underground. Built with
the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted warm brown with
dark speckles and a pale belly; it may have had whiskers and fur (speculative).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thrinaxodon_liorhinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Thrinaxodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.15) / 0.6)
    return 0.07 * s * s


AXIS = [
    (-1.00, 0.300, 0.007, 0.009),
    (-0.96, 0.310, 0.025, 0.030),
    (-0.88, 0.326, 0.045, 0.048),
    (-0.78, 0.342, 0.065, 0.063),
    (-0.70, 0.348, 0.076, 0.069),
    (-0.62, 0.338, 0.066, 0.066),
    (-0.52, 0.338, 0.090, 0.090),
    (-0.38, 0.343, 0.114, 0.114),
    (-0.20, 0.347, 0.120, 0.117),
    (-0.02, 0.347, 0.110, 0.108),
    (0.12, 0.337, 0.090, 0.088),
    (0.25, 0.312, 0.055, 0.050),
    (0.42, 0.272, 0.032, 0.030, sway(0.42)),
    (0.60, 0.232, 0.018, 0.017, sway(0.60)),
    (0.75, 0.205, 0.004, 0.004, sway(0.75)),
]

FORE = tt.Limb(pts=[(0.09, -0.42, 0.28), (0.15, -0.40, 0.17), (0.15, -0.44, 0.04), (0.15, -0.46, 0.012)],
               radii=[0.040, 0.032, 0.024, 0.020], toes=5, toe_len=0.035, toe_r=0.009, toe_spread=65,
               toe_yaw=10, stride=14, claw_len=0.016)
HIND = tt.Limb(pts=[(0.08, 0.10, 0.30), (0.13, 0.04, 0.18), (0.13, 0.13, 0.05), (0.13, 0.10, 0.012)],
               radii=[0.050, 0.036, 0.026, 0.020], toes=5, toe_len=0.040, toe_r=0.010, toe_spread=60,
               toe_yaw=10, stride=-14, claw_len=0.018)

SPEC = tt.TetrapodSpec(
    name="Thrinaxodon",
    axis=AXIS,
    blobs=[((0.075, 0.11, 0.29), (0.055, 0.09, 0.08), 25),
           ((0.055, -0.70, 0.33), (0.035, 0.05, 0.04))],
    limbs=[FORE, HIND],
    voxel=0.009, max_tris=9000,
    scale_bump=0.0010, scale_freq=90.0,
    mouth=(-0.995, -0.74, 0.296, 0.312, 0.004),
    teeth=(9, 0.016, 0.005, -0.985, -0.86),
    eyes=(-0.755, 0.372, 0.0135, (0.35, 0.22, 0.10)),
    nostrils=(-0.985, 0.305),
    back=(0.36, 0.24, 0.15), flank=(0.60, 0.44, 0.30), belly=(0.88, 0.80, 0.66),
    pattern=("spots", (0.20, 0.13, 0.08), 16.0, 0.5),
    pattern2=("stripe", (0.26, 0.17, 0.10), 0.95, 0.10, 0.8),
)

if __name__ == "__main__":
    tt.run(SPEC)
