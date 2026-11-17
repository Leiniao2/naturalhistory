"""
Procedural Chalicotherium grande (Middle Miocene of Europe) for map colonies.

A browsing odd-toed ungulate related to horses and rhinos, but with a gorilla-
like stance: very long forelimbs that raise the shoulders high above the short
hind legs, so the back slopes steeply to the rump; it walked on the knuckles of
its forefeet to keep the long hooked claws off the ground. Horse-like head on
a moderate neck, no tail to speak of. Brown coat. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/chalicotherium_grande.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChalicotheriumGrande.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ChalicotheriumGrande",
    leg_f=1.02, leg_h=0.50, length=0.78, girth=(0.25, 0.30),
    leg_r=(0.075, 0.09), leg_taper=0.6, foot="knuckle", stride=0.10,
    neck_len=0.40, neck_angle=40, neck_r=(0.17, 0.10),
    head_len=0.46, head_r=(0.09, 0.11), snout_r=(0.055, 0.06), head_pitch=55,
    ears="point", ear_size=0.09,
    tail_len=0.12, tail_r=0.03, tail_droop=0.9,
    coat=(0.46, 0.35, 0.24), dark=(0.28, 0.20, 0.13), pale=(0.70, 0.62, 0.50),
    mane=0.04, mane_col=(0.25, 0.18, 0.12), shag=0.006, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
