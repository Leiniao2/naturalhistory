"""
Procedural Petrolacosaurus kansensis (Late Carboniferous of Kansas, the earliest known
diapsid reptile, about 40 cm long) for map colonies (Ground style).

A slender, long-legged lizard-like reptile: small pointed head with big eyes, a long
neck, a slim trunk and a very long whip-like tail; brown back with paler dorsolateral
stripes. Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/petrolacosaurus_kansensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Petrolacosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Petrolacosaurus",
    head_len=0.085, head_w=0.022, head_h=0.016, snout=0.3,
    neck_len=0.09, neck_r=0.014,
    trunk_len=0.27, trunk_r=0.03, trunk_h=0.85,
    tail_len=0.72, tail_r=0.016, tail_curve=0.18,
    leg_r=0.0085, front=(0.06, 0.06), hind=(0.075, 0.075), foot=0.032,
    back=(0.36, 0.26, 0.15), flank=(0.52, 0.42, 0.28), belly=(0.84, 0.77, 0.6),
    pattern="stripes", pattern_col=(0.72, 0.62, 0.40),
    head_col=(0.40, 0.30, 0.18), eye_r=0.0075, eye_at=0.6, teeth=6, tooth_len=0.004,
    voxel=0.0042, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
