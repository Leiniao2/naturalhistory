"""
Procedural polar bear (Ursus maritimus, Pleistocene to today, Arctic) for map
colonies.

The largest living land carnivore, males about 2.4-2.6 m long and up to 700 kg:
a long body and neck, a relatively small, narrow head with a Roman nose, small
round ears, huge furry paws and a stub tail. Thick creamy-white fur over black
skin, with a black nose and dark eyes.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ursus_maritimus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/UrsusMaritimus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_neo_quad as q  # noqa: E402


def nose(mb, L, surf, size=0.022, col=(0.05, 0.04, 0.04)):
    """Dark nose pad at the tip of the muzzle."""
    p, _n = surf.hit(L.h(0.8, 0, 0.02), L.F)
    mb.add(nh.ellipsoid(tuple(p), (size, size * 0.72, size * 0.72), subdivisions=2), col)


SPEC = q.Spec(
    name="UrsusMaritimus",
    leg_f=0.42, leg_h=0.45, length=0.88, girth=(0.25, 0.28), belly=1.0,
    hump=0.05, hump_y=0.25,
    leg_r=(0.085, 0.09), leg_taper=0.75, foot="plantigrade", foot_r=1.25, stride=0.12,
    neck_len=0.34, neck_angle=14, neck_r=(0.20, 0.13),
    head_len=0.30, head_r=(0.11, 0.105), snout_r=(0.055, 0.055), head_pitch=12, cranium=1.0,
    eye_t=0.45, eye_u=0.35,
    ears="round", ear_size=0.06,
    tail_len=0.07, tail_r=0.04, tail_droop=0.8,
    coat=(0.93, 0.91, 0.84), dark=(0.84, 0.80, 0.68), pale=(0.97, 0.96, 0.92), countershade=0.4,
    extra_details=lambda mb, L, surf: nose(mb, L, surf, 0.032),
    shag=0.012, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
