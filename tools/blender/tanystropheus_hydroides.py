"""
Procedural Tanystropheus hydroides (Middle Triassic archosauromorph, ~5-6 m) for map
colonies (Swim style).

The large species of the giraffe-necked reptile of Monte San Giorgio on the Swiss-Italian
border, about 242 million years ago (split in 2020 from the smaller T. longobardicus). Its stiff neck, built from only 13 enormously long vertebrae, was
longer than its body and tail together; the small head held long, interlocking fangs
for snapping up fish and squid. Studies of its skull (nostrils on top of the snout) and
body suggest it lived in shallow coastal water as an ambush predator. Shown swimming,
limbs trailing. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py).
Painted brown above with darker cross-bands on the neck and tail and a pale belly
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/tanystropheus_hydroides.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tanystropheus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.3) / 0.7)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.000, 0.004, 0.004),
    (-0.975, 0.000, 0.012, 0.010),
    (-0.94, 0.003, 0.018, 0.016),
    (-0.90, 0.006, 0.022, 0.020),
    (-0.875, 0.005, 0.016, 0.016),
    (-0.70, 0.000, 0.018, 0.018),
    (-0.45, 0.000, 0.026, 0.026),
    (-0.20, 0.000, 0.040, 0.038),
    (-0.08, 0.000, 0.062, 0.056),
    (0.06, 0.000, 0.074, 0.064),
    (0.20, 0.000, 0.068, 0.058),
    (0.32, 0.000, 0.044, 0.044, sway(0.32)),
    (0.52, 0.000, 0.028, 0.034, sway(0.52)),
    (0.76, 0.000, 0.016, 0.020, sway(0.76)),
    (1.00, 0.000, 0.003, 0.004, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.045, -0.07, -0.02), (0.12, -0.04, -0.04), (0.18, 0.01, -0.05), (0.20, 0.03, -0.05)],
               radii=[0.020, 0.015, 0.012, 0.010], toes=5, toe_len=0.03, toe_r=0.0045, toe_spread=50,
               toe_yaw=140, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.05, 0.20, -0.02), (0.15, 0.25, -0.05), (0.22, 0.33, -0.06), (0.24, 0.36, -0.06)],
               radii=[0.028, 0.021, 0.015, 0.012], toes=5, toe_len=0.055, toe_r=0.005, toe_spread=50,
               toe_yaw=160, toe_drop=0.0, claws=False)

SPEC = tt.TetrapodSpec(
    name="Tanystropheus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0065, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.89, -0.002, 0.000, 0.003),
    teeth=(7, 0.013, 0.0032, -0.99, -0.91), lower_teeth=True,
    eyes=(-0.905, 0.012, 0.0085, (0.85, 0.60, 0.15)),
    back=(0.32, 0.24, 0.16), flank=(0.58, 0.46, 0.32), belly=(0.88, 0.82, 0.68),
    pattern=("bands", (0.16, 0.11, 0.07), 34.0, 0.7, -0.88, 1.0),
)

if __name__ == "__main__":
    tt.run(SPEC)
