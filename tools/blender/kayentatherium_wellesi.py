"""
Procedural Kayentatherium wellesi (Early Jurassic tritylodontid cynodont, Arizona) for map colonies.

A heavily built, badger-sized plant-eater about 1 m long, one of the last of the non-mammal
cynodonts and a close cousin of mammals: a deep, short-snouted head with a pair of big,
rodent-like gnawing incisors in front and broad grinding cheek teeth, small ears, a stout,
furry barrel of a body on short, strong, semi-sprawling legs with digging claws, and a short
tail. A fossil adult was found with 38 tiny babies. Painted grizzled brown fur with a paler
face stripe and belly (colour unknown). Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kayentatherium_wellesi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kayentatherium.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_jurassic_small as sm  # noqa: E402

SPEC = tp.Spec(
    name="Kayentatherium",
    head_len=0.2, head_w=0.08, head_h=0.07, snout=0.55,
    neck_len=0.05, neck_r=0.085,
    trunk_len=0.5, trunk_r=0.15, trunk_h=0.85,
    tail_len=0.18, tail_r=0.05, tail_fin=1.0, tail_curve=0.02,
    leg_r=0.036, front=(0.09, 0.09), hind=(0.1, 0.1), foot=0.05, toes=5,
    back=(0.30, 0.22, 0.14), flank=(0.44, 0.34, 0.22), belly=(0.72, 0.62, 0.46),
    pattern="blotches", pattern_col=(0.22, 0.16, 0.10), pattern_scale=1.2,
    head_col=(0.56, 0.48, 0.36), iris=(0.10, 0.07, 0.05), eye_r=0.014, eye_at=0.45, eye_up=0.45, teeth=0,
    voxel=0.008, max_tris=8000,
    extra=[sm.ears(0.025, (0.30, 0.22, 0.14), inner=(0.55, 0.38, 0.30)), sm.incisors(0.03, 0.007), sm.whiskers(0.05)],
)

if __name__ == "__main__":
    tp.run(SPEC)
