"""
Procedural Aepycamelus giraffinus (Middle-Late Miocene of North America) for
map colonies: the "giraffe camel".

A humpless camel with enormously long, slender legs and a long, almost upright
neck that put its small head about 3 m above the ground, where it browsed on
trees. Padded two-toed feet, a short tail, sandy fawn coat with a pale belly.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/aepycamelus_giraffinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AepycamelusGiraffinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="AepycamelusGiraffinus",
    leg_f=1.25, leg_h=1.20, length=0.72, girth=(0.17, 0.22),
    leg_r=(0.052, 0.062), leg_taper=0.55, foot="hoof", foot_r=1.25, stride=0.16,
    neck_len=1.05, neck_angle=68, neck_r=(0.12, 0.07),
    head_len=0.36, head_r=(0.07, 0.08), snout_r=(0.045, 0.05), head_pitch=35,
    ears="point", ear_size=0.06,
    tail_len=0.30, tail_r=0.025, tail_tuft=0.03, tail_droop=0.85,
    coat=(0.72, 0.58, 0.40), dark=(0.55, 0.42, 0.28), pale=(0.90, 0.83, 0.70),
    hoof_col=(0.30, 0.25, 0.20), shag=0.004, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
