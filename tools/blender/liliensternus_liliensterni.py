"""
Procedural Liliensternus liliensterni (Late Triassic coelophysoid theropod, ~5 m) for map
colonies.

One of the largest predatory dinosaurs of the Triassic, from the Trossingen beds of
Germany about 210 million years ago: a long, slender, fast two-legged hunter related to
Coelophysis but much bigger, with a long neck, a narrow skull with a pair of thin bony
crests along the top of the snout, long grasping three-fingered hands and a long
balancing tail. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py).
Painted grey-brown with dark back bands, a cream belly and orange-red crests (speculative).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/liliensternus_liliensterni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Liliensternus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

CREST = (0.80, 0.32, 0.14)


def sway(y):
    s = max(0.0, (y - 0.15) / 0.85)
    return 0.09 * s * s


AXIS = [
    (-1.00, 0.735, 0.006, 0.006),
    (-0.97, 0.740, 0.016, 0.018),
    (-0.90, 0.750, 0.023, 0.030),
    (-0.82, 0.762, 0.030, 0.040),
    (-0.76, 0.772, 0.036, 0.046),
    (-0.715, 0.760, 0.027, 0.034),
    (-0.66, 0.715, 0.025, 0.031),
    (-0.58, 0.645, 0.031, 0.036),
    (-0.48, 0.590, 0.044, 0.050),
    (-0.37, 0.565, 0.070, 0.078),
    (-0.24, 0.555, 0.090, 0.100),
    (-0.09, 0.555, 0.094, 0.100),
    (0.06, 0.565, 0.082, 0.084),
    (0.20, 0.560, 0.054, 0.056),
    (0.40, 0.540, 0.035, 0.036, sway(0.40)),
    (0.60, 0.510, 0.022, 0.022, sway(0.60)),
    (0.80, 0.478, 0.012, 0.012, sway(0.80)),
    (1.00, 0.448, 0.003, 0.003, sway(1.00)),
]

LEGS = tt.Limb(pts=[(0.065, 0.03, 0.55), (0.085, -0.07, 0.37), (0.083, 0.06, 0.15), (0.083, 0.0, 0.016)],
               radii=[0.056, 0.036, 0.022, 0.016], toes=3, toe_len=0.07, toe_r=0.013, toe_spread=44,
               stride=13, claw_len=0.022)
ARMS = tt.Limb(pts=[(0.055, -0.36, 0.52), (0.072, -0.33, 0.445), (0.064, -0.40, 0.41), (0.058, -0.43, 0.395)],
               radii=[0.026, 0.019, 0.014, 0.012], toes=3, toe_len=0.035, toe_r=0.0065, toe_spread=30,
               toe_drop=0.022, claw_len=0.016, stride=-6)


def crests(mb, surf, spec):
    for sx in (1, -1):
        pts = []
        for i in range(9):
            t = i / 8
            y = -0.96 + 0.20 * t
            loc, n = surf.hit((sx * 0.008, y, 2.0), (0, 0, -1))
            if loc is None:
                continue
            pts.append(loc - Vector((0, 0, 0.004)))
        if len(pts) < 2:
            continue
        top = [p + Vector((sx * 0.004, 0, 0.004 + 0.022 * (1.0 - abs(2 * i / (len(pts) - 1) - 1.0) ** 1.6)))
               for i, p in enumerate(pts)]
        mb.add(tt.panel(pts + list(reversed(top)), 0.004), CREST, smooth=False)


SPEC = tt.TetrapodSpec(
    name="Liliensternus",
    axis=AXIS,
    blobs=[((0.06, 0.03, 0.49), (0.054, 0.11, 0.095), 25),
           ((0.0, -0.81, 0.735), (0.022, 0.06, 0.02))],
    limbs=[LEGS, ARMS],
    voxel=0.0085, max_tris=11000,
    mouth=(-1.0, -0.775, 0.734, 0.744, 0.004),
    teeth=(13, 0.016, 0.0042, -0.985, -0.79),
    eyes=(-0.785, 0.785, 0.013, (0.88, 0.58, 0.12)),
    back=(0.26, 0.24, 0.22), flank=(0.52, 0.48, 0.42), belly=(0.86, 0.82, 0.72),
    pattern=("bands", (0.14, 0.12, 0.10), 24.0, 0.75, -0.55, 1.1),
    head=((0.40, 0.34, 0.30), -0.72, 0.30),
    post=crests,
)

if __name__ == "__main__":
    tt.run(SPEC)
