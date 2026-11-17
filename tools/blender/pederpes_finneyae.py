"""
Procedural Pederpes finneyae (Early Carboniferous of Scotland, about 348 million years old, an early tetrapod about 1 m long) for map colonies (Ground style).

A stout, low early tetrapod with a broad, flat, triangular head, a thick trunk on short,
sturdy sprawling legs whose feet point forward, and a moderately long, slightly deepened tail;
muddy brown with dark crossbands.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pederpes_finneyae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pederpes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Pederpes",
    head_len=0.19, head_w=0.075, head_h=0.03, snout=0.45,
    neck_len=0.03, neck_r=0.06,
    trunk_len=0.45, trunk_r=0.075, trunk_h=0.7,
    tail_len=0.42, tail_r=0.04, tail_fin=1.4, tail_curve=0.1,
    leg_r=0.018, front=(0.065, 0.06), hind=(0.075, 0.065), foot=0.045,
    back=(0.30, 0.25, 0.16), flank=(0.44, 0.37, 0.24), belly=(0.74, 0.66, 0.48),
    pattern="bands", pattern_col=(0.17, 0.14, 0.09), pattern_scale=1.3,
    head_col=(0.32, 0.27, 0.17), eye_r=0.012, eye_at=0.55, eye_up=0.6, teeth=8, tooth_len=0.007,
    voxel=0.006, max_tris=6000,
)

if __name__ == "__main__":
    tp.run(SPEC)
