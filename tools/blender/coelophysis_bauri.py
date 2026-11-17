"""
Procedural Coelophysis bauri (Late Triassic coelophysoid theropod, ~3 m) for map colonies.

A slender, lightly built early theropod from the Ghost Ranch quarry of New Mexico, caught
mid-stride: a long, low, narrow skull with a kink-free tapering snout and many small
recurved teeth, a long S-curved neck, a short slim trunk, a very long thin tail held out
behind, short grasping arms and long, bird-like hind legs with three main toes. Built
with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted grey-tan with dark
bands across the back and tail and a pale belly (speculative).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/coelophysis_bauri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Coelophysis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.15) / 0.85)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.700, 0.004, 0.004),
    (-0.97, 0.705, 0.012, 0.013),
    (-0.90, 0.714, 0.017, 0.021),
    (-0.82, 0.724, 0.023, 0.029),
    (-0.765, 0.733, 0.030, 0.036),
    (-0.725, 0.722, 0.022, 0.028),
    (-0.67, 0.680, 0.021, 0.026),
    (-0.59, 0.610, 0.026, 0.030),
    (-0.49, 0.560, 0.036, 0.040),
    (-0.38, 0.540, 0.058, 0.064),
    (-0.25, 0.530, 0.078, 0.088),
    (-0.10, 0.530, 0.082, 0.088),
    (0.05, 0.540, 0.072, 0.074),
    (0.20, 0.535, 0.048, 0.050),
    (0.40, 0.515, 0.031, 0.032, sway(0.40)),
    (0.60, 0.485, 0.020, 0.020, sway(0.60)),
    (0.80, 0.455, 0.011, 0.011, sway(0.80)),
    (1.00, 0.425, 0.003, 0.003, sway(1.00)),
]

LEGS = tt.Limb(pts=[(0.06, 0.02, 0.53), (0.078, -0.075, 0.36), (0.076, 0.055, 0.15), (0.076, -0.005, 0.016)],
               radii=[0.048, 0.030, 0.018, 0.013], toes=3, toe_len=0.065, toe_r=0.011, toe_spread=44,
               stride=13, claw_len=0.02)
ARMS = tt.Limb(pts=[(0.05, -0.37, 0.50), (0.064, -0.34, 0.435), (0.056, -0.40, 0.41), (0.05, -0.425, 0.40)],
               radii=[0.022, 0.016, 0.012, 0.010], toes=3, toe_len=0.03, toe_r=0.0055, toe_spread=30,
               toe_drop=0.02, claw_len=0.012, stride=-6)

SPEC = tt.TetrapodSpec(
    name="Coelophysis",
    axis=AXIS,
    blobs=[((0.055, 0.03, 0.47), (0.048, 0.10, 0.085), 25),
           ((0.0, -0.80, 0.700), (0.020, 0.06, 0.018))],
    limbs=[LEGS, ARMS],
    voxel=0.0085, max_tris=11000,
    mouth=(-1.0, -0.79, 0.699, 0.706, 0.004),
    teeth=(13, 0.013, 0.0035, -0.985, -0.80),
    eyes=(-0.772, 0.742, 0.012, (0.85, 0.62, 0.15)),
    back=(0.30, 0.27, 0.22), flank=(0.58, 0.52, 0.42), belly=(0.86, 0.82, 0.72),
    pattern=("bands", (0.16, 0.13, 0.10), 26.0, 0.75, -0.55, 1.1),
    head=((0.62, 0.30, 0.18), -0.72, 0.35),
)

if __name__ == "__main__":
    tt.run(SPEC)
