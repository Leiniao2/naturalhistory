"""
Procedural Karaurus sharovi (Late Jurassic stem salamander, Kazakhstan) for map colonies.

One of the oldest known salamanders, about 19 cm long, preserved complete in lake-bed shales:
a broad, flat head with a rounded snout and small eyes, its skull roof roughened with
bony sculpture, a long body, four short legs and a fairly short, slightly flattened tail.
It probably lived along the shores and hunted insects and worms. Painted dark olive-brown
with blotches and a yellowish belly (colour unknown). Built with nh_car_tetrapod. Faces -Y,
pivot on the ground.

Usage:
  blender --background --python tools/blender/karaurus_sharovi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Karaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Karaurus",
    head_len=0.16, head_w=0.085, head_h=0.03, snout=0.6,
    neck_len=0.03, neck_r=0.06,
    trunk_len=0.48, trunk_r=0.065, trunk_h=0.75,
    tail_len=0.42, tail_r=0.045, tail_fin=1.5, tail_curve=0.12,
    leg_r=0.016, front=(0.05, 0.055), hind=(0.055, 0.06), foot=0.035, toes=4,
    back=(0.22, 0.22, 0.14), flank=(0.32, 0.31, 0.18), belly=(0.82, 0.72, 0.36),
    pattern="blotches", pattern_col=(0.10, 0.10, 0.06), pattern_scale=0.9,
    head_col=(0.25, 0.24, 0.15), iris=(0.80, 0.66, 0.25), eye_r=0.012, eye_at=0.55, eye_up=0.8, teeth=0,
    voxel=0.005, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
