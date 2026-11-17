"""
Procedural Archaeothyris florensis (Late Carboniferous of Nova Scotia, one of the earliest known synapsids, about 50 cm long) for map colonies (Ground style).

A lizard-shaped early synapsid with a deep, fairly long skull, enlarged canine-like teeth near the
front of the upper jaw, a robust trunk on sprawling legs and a long tail; grey-brown with darker
blotches.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/archaeothyris_florensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archaeothyris.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Archaeothyris",
    head_len=0.15, head_w=0.034, head_h=0.03, snout=0.35,
    neck_len=0.05, neck_r=0.026,
    trunk_len=0.36, trunk_r=0.05, trunk_h=0.85,
    tail_len=0.6, tail_r=0.026, tail_curve=0.14,
    leg_r=0.012, front=(0.065, 0.062), hind=(0.075, 0.07), foot=0.04,
    back=(0.30, 0.27, 0.22), flank=(0.46, 0.41, 0.33), belly=(0.80, 0.74, 0.60),
    pattern="blotches", pattern_col=(0.16, 0.13, 0.10),
    head_col=(0.34, 0.30, 0.24), eye_r=0.009, eye_at=0.62, eye_up=0.45, teeth=8, tooth_len=0.006,
    voxel=0.005, max_tris=5500,
)

if __name__ == "__main__":
    tp.run(SPEC)
