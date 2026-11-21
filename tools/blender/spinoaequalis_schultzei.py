"""
Procedural Spinoaequalis schultzei (Late Carboniferous of Hamilton, Kansas, a small, mostly aquatic araeoscelid diapsid about 25 cm long) for map colonies (Swim style).

A slender lizard-like reptile, a Petrolacosaurus relative that took to the water: a small
pointed head, a slim body, thin limbs folded back, and a long, tall, laterally flattened tail
(tall neural and haemal spines make it a deep paddle); brown with dark bands across the tail.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for the tail bands).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/spinoaequalis_schultzei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Spinoaequalis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402

SPEC = tp.Spec(
    name="Spinoaequalis",
    head_len=0.1, head_w=0.03, head_h=0.024, snout=0.3,
    neck_len=0.05, neck_r=0.024,
    trunk_len=0.3, trunk_r=0.038, trunk_h=0.95,
    tail_len=0.7, tail_r=0.026, tail_fin=1.3, tail_curve=0.1,
    leg_r=0.008, front=(0.05, 0.045), hind=(0.06, 0.055), foot=0.035, toes=5, swim=True,
    back=(0.32, 0.22, 0.12), flank=(0.48, 0.35, 0.20), belly=(0.80, 0.70, 0.52),
    pattern="none", pattern_col=(0.20, 0.13, 0.07),
    head_col=(0.34, 0.24, 0.13), eye_r=0.009, eye_at=0.55, eye_up=0.45, teeth=0,
    voxel=0.004, max_tris=3800,
)

FUSED = [ct.tail_fin(0.09, below=0.85, start=0.0, end=0.97, peak=0.35)]
PAINT = [ct.tail_bands((0.15, 0.10, 0.06), period=0.07, duty=0.4, start=0.05)]

if __name__ == "__main__":
    ct.run(SPEC, fused=FUSED, paint=PAINT)
