"""
Procedural Nesodon imbricatus (Early Miocene of Patagonia) for map colonies:
a toxodontid notoungulate, a South American hoofed mammal with no living kin.

A tapir- to cow-sized grazer with a barrel body, short stout legs on three-toed
feet, a big, broad head with a blunt muzzle and chisel-like front teeth, small
ears and a short tail. Grey-brown hide.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/nesodon_imbricatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NesodonImbricatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="NesodonImbricatus",
    leg_f=0.36, leg_h=0.40, length=0.92, girth=(0.27, 0.29), belly=1.08,
    hump=0.05, hump_y=0.2,
    leg_r=(0.075, 0.085), leg_taper=0.7, foot="pillar", stride=0.09,
    neck_len=0.14, neck_angle=12, neck_r=(0.21, 0.17),
    head_len=0.44, head_r=(0.13, 0.15), snout_r=(0.10, 0.09), head_pitch=28,
    ears="point", ear_size=0.07,
    tail_len=0.18, tail_r=0.035, tail_droop=0.95,
    tusks=[dict(t=0.98, s=sx * 0.04, u=-0.06, dir=(0, -1, -0.4), len=0.05, r=0.016, tip=0.010, flat=0.6,
                color=(0.86, 0.80, 0.64)) for sx in (-1, 1)],
    coat=(0.48, 0.43, 0.36), dark=(0.33, 0.29, 0.24), pale=(0.66, 0.61, 0.53), countershade=0.5,
    shag=0.004, voxel=0.019,
)

if __name__ == "__main__":
    q.main(SPEC)
