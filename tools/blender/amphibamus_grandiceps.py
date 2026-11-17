"""
Procedural Amphibamus grandiceps (Late Carboniferous of Mazon Creek, Illinois, a small temnospondyl amphibian about 12 cm long) for map colonies (Ground style).

A salamander-like little amphibian, close to the ancestry of frogs and salamanders: a large,
broad, round-snouted head with huge eyes, a short trunk, slender legs with four fingers and a
short tail; dark brown with yellow spots and a pale belly.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/amphibamus_grandiceps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Amphibamus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Amphibamus",
    head_len=0.2, head_w=0.095, head_h=0.035, snout=0.72,
    neck_len=0.02, neck_r=0.07,
    trunk_len=0.33, trunk_r=0.07, trunk_h=0.75,
    tail_len=0.28, tail_r=0.04, tail_fin=1.2, tail_curve=0.08,
    leg_r=0.014, front=(0.07, 0.07), hind=(0.08, 0.075), foot=0.045, toes=4,
    back=(0.20, 0.15, 0.09), flank=(0.32, 0.25, 0.15), belly=(0.80, 0.70, 0.46),
    pattern="spots", pattern_col=(0.85, 0.68, 0.20), pattern_scale=1.6,
    head_col=(0.22, 0.17, 0.10), eye_r=0.024, eye_at=0.5, eye_up=0.7, teeth=0,
    voxel=0.006, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
