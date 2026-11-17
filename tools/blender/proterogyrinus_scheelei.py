"""
Procedural Proterogyrinus scheelei (Early Carboniferous of West Virginia, an embolomere about 1.5 m long) for map colonies (Ground style).

A long, crocodile-like semi-aquatic hunter: a long, deep, wedge-shaped skull with sharp teeth,
a long trunk on moderately sturdy legs and a long, tall, flattened swimming tail; olive-brown
with dark blotches and a pale belly.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/proterogyrinus_scheelei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Proterogyrinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Proterogyrinus",
    head_len=0.2, head_w=0.05, head_h=0.04, snout=0.38,
    neck_len=0.03, neck_r=0.045,
    trunk_len=0.48, trunk_r=0.058, trunk_h=0.9,
    tail_len=0.6, tail_r=0.036, tail_fin=1.9, tail_curve=0.12,
    leg_r=0.014, front=(0.06, 0.06), hind=(0.07, 0.065), foot=0.04,
    back=(0.25, 0.25, 0.15), flank=(0.40, 0.38, 0.24), belly=(0.76, 0.70, 0.52),
    pattern="blotches", pattern_col=(0.13, 0.12, 0.07),
    head_col=(0.28, 0.27, 0.17), eye_r=0.011, eye_at=0.6, eye_up=0.6, teeth=10, tooth_len=0.008,
    lateral_line=True, voxel=0.0055, max_tris=6000,
)

if __name__ == "__main__":
    tp.run(SPEC)
