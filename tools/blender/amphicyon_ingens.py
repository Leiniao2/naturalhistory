"""
Procedural Amphicyon ingens (Middle Miocene of North America) for map colonies:
a giant "bear-dog".

A heavy, bear-like predator the size of a large brown bear, with powerful
plantigrade limbs, a long wolf-like head and muzzle with prominent canines,
small rounded ears and a long, thick tail. Brown coat with a paler muzzle.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/amphicyon_ingens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmphicyonIngens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="AmphicyonIngens",
    leg_f=0.48, leg_h=0.46, length=0.88, girth=(0.22, 0.25),
    leg_r=(0.075, 0.08), leg_taper=0.65, foot="plantigrade", stride=0.12,
    neck_len=0.28, neck_angle=22, neck_r=(0.18, 0.13),
    head_len=0.44, head_r=(0.12, 0.11), snout_r=(0.055, 0.06), head_pitch=12,
    ears="round", ear_size=0.08,
    tail_len=0.60, tail_r=0.05, tail_droop=0.55,
    tusks=[dict(t=0.90, s=sx * 0.06, u=-0.12, dir=(0, -0.2, -1), len=0.07, r=0.014, tip=0.003) for sx in (-1, 1)],
    coat=(0.42, 0.31, 0.21), dark=(0.24, 0.17, 0.11), pale=(0.66, 0.56, 0.44),
    shag=0.008, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
