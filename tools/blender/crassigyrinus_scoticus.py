"""
Procedural Crassigyrinus scoticus (Early Carboniferous of Scotland, an aquatic stem tetrapod about 2 m long) for map colonies (Swim style).

A big-headed, eel-like ambush predator: a huge, deep skull with gaping jaws full of large fangs
and big eyes, a long body, absurdly tiny forelimbs, small hind limbs and a long, deep,
finned swimming tail; dark olive with mottling and a paler belly.
Built with nh_car_tetrapod. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/crassigyrinus_scoticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Crassigyrinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Crassigyrinus",
    head_len=0.27, head_w=0.085, head_h=0.065, snout=0.5,
    neck_len=0.04, neck_r=0.058,
    trunk_len=0.5, trunk_r=0.056, trunk_h=1.05,
    tail_len=0.5, tail_r=0.03, tail_fin=2.3, tail_curve=0.05,
    leg_r=0.011, front=(0.025, 0.02), hind=(0.05, 0.04), foot=0.025, swim=True,
    back=(0.22, 0.24, 0.16), flank=(0.36, 0.37, 0.24), belly=(0.74, 0.70, 0.52),
    pattern="blotches", pattern_col=(0.12, 0.13, 0.08),
    head_col=(0.26, 0.26, 0.18), eye_r=0.017, eye_at=0.5, eye_up=0.55, teeth=10, tooth_len=0.014,
    lateral_line=True, voxel=0.007, max_tris=6000,
)

if __name__ == "__main__":
    tp.run(SPEC)
