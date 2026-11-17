"""
Procedural Placerias hesternus (Late Triassic kannemeyeriiform dicynodont, ~3.5 m) for
map colonies.

One of the last and largest dicynodonts, a hippo-sized, barrel-bodied plant-eater known
from a bonebed of more than 40 individuals at the Placerias Quarry in Arizona, about
220 million years ago. A big head with a toothless, turtle-like horny beak and a pair of
short tusks growing down from bony bosses on the upper jaw, a short thick neck, a huge
round body on stout, semi-erect legs and a short tail. Built with the shared Triassic
tetrapod recipe (nh_tri_tetrapod.py). Painted grey-brown with a darker back and a pale
belly, the beak dark horn (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/placerias_hesternus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Placerias.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.20, 0.17, 0.14)
TUSK = (0.90, 0.86, 0.72)

AXIS = [
    (-1.00, 0.300, 0.022, 0.032),
    (-0.96, 0.330, 0.052, 0.070),
    (-0.88, 0.370, 0.086, 0.100),
    (-0.78, 0.400, 0.110, 0.110),
    (-0.70, 0.410, 0.116, 0.110),
    (-0.62, 0.412, 0.122, 0.122),
    (-0.50, 0.425, 0.190, 0.180),
    (-0.30, 0.435, 0.250, 0.230),
    (-0.05, 0.445, 0.252, 0.232),
    (0.18, 0.435, 0.206, 0.190),
    (0.36, 0.405, 0.130, 0.120),
    (0.50, 0.365, 0.070, 0.060),
    (0.62, 0.325, 0.030, 0.026),
    (0.70, 0.305, 0.004, 0.004),
]

FORE = tt.Limb(pts=[(0.18, -0.40, 0.30), (0.25, -0.38, 0.18), (0.24, -0.42, 0.055), (0.24, -0.44, 0.016)],
               radii=[0.090, 0.070, 0.055, 0.050], toes=5, toe_len=0.035, toe_r=0.016, toe_spread=70,
               stride=8, claw_len=0.016)
HIND = tt.Limb(pts=[(0.17, 0.22, 0.33), (0.21, 0.15, 0.19), (0.21, 0.24, 0.055), (0.21, 0.21, 0.016)],
               radii=[0.100, 0.075, 0.058, 0.050], toes=5, toe_len=0.035, toe_r=0.016, toe_spread=70,
               stride=-8, claw_len=0.016)


def tusks(mb, surf, spec):
    for sx in (1, -1):
        base = tt.Vector((sx * 0.072, -0.895, 0.335))
        mb.add(tt.curved_spike(base, (sx * 0.15, -0.25, -1.0), 0.13, 0.019, bend=(0, -0.3, 0)), TUSK)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.94, -0.975, co.y))


SPEC = tt.TetrapodSpec(
    name="Placerias",
    axis=AXIS,
    blobs=[((0.07, -0.89, 0.33), (0.035, 0.045, 0.05)),       # tusk bosses
           ((0.0, -0.86, 0.30), (0.07, 0.11, 0.04), 8)],        # lower jaw
    limbs=[FORE, HIND],
    voxel=0.011, max_tris=11000,
    mouth=(-1.0, -0.80, 0.298, 0.335, 0.005),
    eyes=(-0.80, 0.465, 0.017, (0.55, 0.40, 0.20)),
    nostrils=(-0.95, 0.39),
    back=(0.30, 0.27, 0.24), flank=(0.50, 0.45, 0.38), belly=(0.78, 0.72, 0.60),
    pattern=("mottle", (0.36, 0.30, 0.25), 6.0, 0.4),
    paint_extra=paint_extra,
    post=tusks,
)

if __name__ == "__main__":
    tt.run(SPEC)
