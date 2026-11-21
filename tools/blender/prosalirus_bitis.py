"""
Procedural Prosalirus bitis (Early Jurassic frog, Kayenta Formation, Arizona) for map colonies.

The oldest known true frog that could jump, about 5 cm long: its hips, long hind legs and
fused ankle bones show the frog leaping build already in place 190 million years ago. Broad,
flat head with big eyes and a wide mouth, short body with no tail, short arms. Painted
olive-green with darker blotches and a pale belly (colour unknown). Built with
nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/prosalirus_bitis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Prosalirus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Prosalirus",
    head_len=0.2, head_w=0.13, head_h=0.05, snout=0.55,
    neck_len=0.01, neck_r=0.1,
    trunk_len=0.24, trunk_r=0.11, trunk_h=0.7,
    tail_len=0.03, tail_r=0.03, tail_fin=1.0, tail_curve=0.0,
    leg_r=0.024, front=(0.07, 0.08), hind=(0.2, 0.16), foot=0.09, toes=5,
    back=(0.30, 0.36, 0.16), flank=(0.44, 0.50, 0.26), belly=(0.88, 0.86, 0.66),
    pattern="blotches", pattern_col=(0.14, 0.18, 0.07), pattern_scale=1.4,
    head_col=(0.32, 0.38, 0.17), iris=(0.88, 0.70, 0.22), eye_r=0.026, eye_at=0.5, eye_up=0.9, teeth=0,
    voxel=0.006, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
