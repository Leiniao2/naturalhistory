"""
Procedural Lisowicia bojani (Late Triassic dicynodont, ~4.5 m, ~9 t) for map colonies.

The largest known non-mammal synapsid, an elephant-sized dicynodont from Lisowice in
southern Poland, about 210 million years ago. Unlike earlier sprawling dicynodonts it
stood on straight, pillar-like legs held under the body like a rhino or elephant. A
massive barrel-shaped body, a big head with a toothless horny beak and two short tusks
growing down from bony bosses on the upper jaw, a short neck and a stubby tail. Built
with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted grey-brown with
a darker back, faint mottling and a dark beak (speculative). Faces -Y, pivot on the
ground.

Usage:
  blender --background --python tools/blender/lisowicia_bojani.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lisowicia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.12, 0.10, 0.08)
TUSK = (0.90, 0.86, 0.72)

AXIS = [
    (-1.00, 0.410, 0.028, 0.042),
    (-0.96, 0.440, 0.061, 0.083),
    (-0.88, 0.480, 0.098, 0.114),
    (-0.78, 0.510, 0.125, 0.127),
    (-0.70, 0.520, 0.131, 0.127),
    (-0.62, 0.522, 0.148, 0.146),
    (-0.50, 0.540, 0.228, 0.224),
    (-0.30, 0.550, 0.281, 0.265),
    (-0.05, 0.555, 0.281, 0.265),
    (0.18, 0.545, 0.233, 0.224),
    (0.36, 0.510, 0.148, 0.140),
    (0.48, 0.470, 0.074, 0.068),
    (0.58, 0.435, 0.030, 0.027),
    (0.64, 0.420, 0.004, 0.004),
]

FORE = tt.Limb(pts=[(0.18, -0.40, 0.42), (0.20, -0.39, 0.25), (0.20, -0.41, 0.08), (0.20, -0.42, 0.02)],
               radii=[0.105, 0.085, 0.072, 0.070], toes=5, toe_len=0.03, toe_r=0.018, toe_spread=80,
               stride=6, claw_len=0.014, sole=(0.075, 0.075, 0.025))
HIND = tt.Limb(pts=[(0.17, 0.20, 0.44), (0.19, 0.17, 0.26), (0.19, 0.22, 0.08), (0.19, 0.21, 0.02)],
               radii=[0.115, 0.090, 0.074, 0.072], toes=5, toe_len=0.03, toe_r=0.018, toe_spread=80,
               stride=-6, claw_len=0.014, sole=(0.078, 0.078, 0.025))


def tusks(mb, surf, spec):
    for sx in (1, -1):
        base = tt.Vector((sx * 0.078, -0.895, 0.440))
        mb.add(tt.curved_spike(base, (sx * 0.12, -0.25, -1.0), 0.14, 0.021, bend=(0, -0.3, 0)), TUSK)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.92, -0.95, co.y))


SPEC = tt.TetrapodSpec(
    name="Lisowicia",
    axis=AXIS,
    blobs=[((0.075, -0.89, 0.44), (0.038, 0.048, 0.055)),      # tusk bosses
           ((0.0, -0.86, 0.41), (0.075, 0.11, 0.045), 8),       # lower jaw
           ((0.15, -0.40, 0.43), (0.10, 0.12, 0.12)),           # shoulders
           ((0.15, 0.20, 0.45), (0.11, 0.13, 0.13))],           # hips
    limbs=[FORE, HIND],
    voxel=0.012, max_tris=11000,
    scale_bump=0.0022, scale_freq=30.0,
    mouth=(-1.0, -0.80, 0.405, 0.440, 0.006),
    eyes=(-0.80, 0.575, 0.017, (0.45, 0.32, 0.18)),
    nostrils=(-0.95, 0.50),
    back=(0.36, 0.31, 0.25), flank=(0.58, 0.52, 0.43), belly=(0.80, 0.74, 0.62),
    pattern=("mottle", (0.36, 0.33, 0.29), 5.0, 0.45),
    paint_extra=paint_extra,
    post=tusks,
)

if __name__ == "__main__":
    tt.run(SPEC)
