"""
Procedural Plateosaurus engelhardti (Late Triassic sauropodomorph, ~8 m) for map colonies.

A large, early long-necked plant-eater of the Norian of Germany, Switzerland and France,
standing on its hind legs as its skeleton shows it must have: a small, low skull with
leaf-shaped teeth, a long flexible neck, a heavy, deep body balanced over strong
columnar hind legs on four toes, a long, deep tail, and shorter arms whose hands carry a
big, curved thumb claw. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted olive brown with darker bands across the back and a pale
belly (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/plateosaurus_engelhardti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Plateosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.860, 0.006, 0.008),
    (-0.97, 0.866, 0.016, 0.020),
    (-0.925, 0.876, 0.023, 0.029),
    (-0.875, 0.882, 0.028, 0.035),
    (-0.835, 0.868, 0.024, 0.030),
    (-0.76, 0.820, 0.031, 0.037),
    (-0.67, 0.750, 0.042, 0.048),
    (-0.57, 0.670, 0.058, 0.066),
    (-0.46, 0.605, 0.088, 0.105),
    (-0.32, 0.575, 0.120, 0.150),
    (-0.15, 0.570, 0.130, 0.160),
    (0.02, 0.590, 0.115, 0.130),
    (0.18, 0.585, 0.082, 0.096),
    (0.38, 0.550, 0.056, 0.070, sway(0.38)),
    (0.58, 0.495, 0.036, 0.046, sway(0.58)),
    (0.78, 0.435, 0.020, 0.025, sway(0.78)),
    (0.98, 0.375, 0.004, 0.004, sway(0.98)),
]

LEGS = tt.Limb(pts=[(0.10, 0.02, 0.56), (0.122, -0.07, 0.36), (0.116, 0.04, 0.13), (0.116, -0.02, 0.022)],
               radii=[0.085, 0.056, 0.036, 0.027], toes=4, toe_len=0.07, toe_r=0.018, toe_spread=50,
               stride=10, claw_len=0.024, sole=(0.04, 0.05, 0.02))
ARMS = tt.Limb(pts=[(0.09, -0.38, 0.52), (0.115, -0.35, 0.40), (0.105, -0.43, 0.335), (0.10, -0.455, 0.315)],
               radii=[0.042, 0.031, 0.022, 0.018], toes=4, toe_len=0.04, toe_r=0.010, toe_spread=50,
               toe_drop=0.02, claw_len=0.018, stride=-8)


def thumb_claws(mb, surf, spec):
    for sx in (1, -1):
        pts = tt.limb_chain(ARMS, sx)
        hand = pts[-1]
        base = hand + Vector((sx * -0.012, -0.012, 0.004))
        mb.add(tt.curved_spike(base, (sx * -0.4, -1.0, -0.2), 0.045, 0.009, bend=(0, 0, -0.6)), tt.CLAW)


SPEC = tt.TetrapodSpec(
    name="Plateosaurus",
    axis=AXIS,
    blobs=[((0.095, 0.03, 0.50), (0.085, 0.15, 0.14), 25)],
    limbs=[LEGS, ARMS],
    voxel=0.0095, max_tris=12000,
    mouth=(-1.0, -0.905, 0.856, 0.862, 0.004),
    teeth=(7, 0.008, 0.0035, -0.99, -0.91),
    eyes=(-0.885, 0.890, 0.011, (0.80, 0.60, 0.20)),
    back=(0.30, 0.30, 0.18), flank=(0.55, 0.52, 0.34), belly=(0.85, 0.80, 0.64),
    pattern=("bands", (0.16, 0.15, 0.09), 18.0, 0.9, -0.5, 1.0),
    post=thumb_claws,
)

if __name__ == "__main__":
    tt.run(SPEC)
