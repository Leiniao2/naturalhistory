"""
Procedural Merychippus insignis (Middle Miocene of North America) for map
colonies: an early grazing horse about a metre at the shoulder.

Pony-sized and light, with long slender three-toed legs (the side toes small
and held off the ground), a long head with the deep jaw of a grass-eater, a
short dark mane and a slim tail. Sandy coat with a dark dorsal stripe and
faint bars on the legs (a reconstruction choice). Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/merychippus_insignis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MerychippusInsignis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="MerychippusInsignis",
    leg_f=0.72, leg_h=0.76, length=0.68, girth=(0.15, 0.19),
    leg_r=(0.045, 0.054), leg_taper=0.5, foot="hoof", stride=0.13,
    neck_len=0.42, neck_angle=45, neck_r=(0.11, 0.07),
    head_len=0.40, head_r=(0.07, 0.09), snout_r=(0.04, 0.05), head_pitch=55,
    ears="point", ear_size=0.08, mane=0.045,
    tail_len=0.40, tail_r=0.028, tail_tuft=0.05, tail_droop=0.9,
    coat=(0.70, 0.56, 0.38), dark=(0.38, 0.28, 0.18), pale=(0.90, 0.84, 0.72),
    mane_col=(0.20, 0.14, 0.09),
    pattern=q.combine(q.leg_bands((0.40, 0.30, 0.20), freq=20, amount=0.45),
                      q.lower_legs((0.30, 0.22, 0.15), z1=0.25, amount=0.8)),
    shag=0.003, voxel=0.015,
)

if __name__ == "__main__":
    q.main(SPEC)
