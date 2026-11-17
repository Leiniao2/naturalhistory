"""
Procedural Metoposaurus krasiejowensis (Late Triassic metoposaurid temnospondyl, ~2 m)
for map colonies (Swim style).

A large, flat-bodied amphibian known from hundreds of bones in the Carnian (about 228
million years ago) river and lake deposits of Krasiejów, Poland. Its broad, flat,
U-shaped skull had its eyes set unusually far forward and was lined with small sharp
teeth; the body was flattened like a giant salamander's, with short limbs and a short,
deep tail. It lurked on the bottoms of lakes and rivers, snapping up fish. Mass deaths
in drying pools are known for its relatives. Built with the shared Triassic tetrapod
recipe (nh_tri_tetrapod.py). Painted grey-brown with yellowish spots and a pale belly
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/metoposaurus_krasiejowensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Metoposaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.6)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.000, 0.110, 0.014),
    (-0.97, 0.000, 0.165, 0.022),
    (-0.90, 0.000, 0.200, 0.030),
    (-0.80, 0.002, 0.222, 0.038),
    (-0.68, 0.004, 0.230, 0.044),
    (-0.60, 0.004, 0.232, 0.048),
    (-0.54, 0.004, 0.190, 0.056),
    (-0.40, 0.004, 0.215, 0.072),
    (-0.15, 0.004, 0.225, 0.076),
    (0.08, 0.004, 0.200, 0.070),
    (0.22, 0.004, 0.130, 0.062),
    (0.36, 0.004, 0.070, 0.066, sway(0.36)),
    (0.55, 0.004, 0.040, 0.060, sway(0.55)),
    (0.72, 0.004, 0.016, 0.030, sway(0.72)),
    (0.80, 0.004, 0.002, 0.004, sway(0.80)),
]

FORE = tt.Limb(pts=[(0.18, -0.42, -0.02), (0.29, -0.39, -0.04), (0.31, -0.44, -0.05), (0.32, -0.46, -0.05)],
               radii=[0.040, 0.032, 0.025, 0.021], toes=4, toe_len=0.045, toe_r=0.010, toe_spread=60,
               toe_yaw=35, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.17, 0.14, -0.02), (0.28, 0.18, -0.04), (0.30, 0.24, -0.05), (0.31, 0.26, -0.05)],
               radii=[0.045, 0.035, 0.027, 0.022], toes=5, toe_len=0.05, toe_r=0.010, toe_spread=60,
               toe_yaw=70, toe_drop=0.0, claws=False)

SPEC = tt.TetrapodSpec(
    name="Metoposaurus",
    axis=AXIS, power=2.5,
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=10000,
    pivot="centre",
    mouth=(-1.0, -0.60, -0.006, -0.004, 0.005), mouth_min_x=0.15,
    teeth=(18, 0.012, 0.0038, -0.99, -0.62),
    eyes=(-0.86, 0.030, 0.015, (0.85, 0.70, 0.25), 0.085),
    back=(0.30, 0.28, 0.24), flank=(0.46, 0.43, 0.36), belly=(0.82, 0.78, 0.66),
    pattern=("spots", (0.80, 0.70, 0.36), 30.0, 0.35),
)

if __name__ == "__main__":
    tt.run(SPEC)
