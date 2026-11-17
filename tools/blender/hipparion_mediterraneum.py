"""
Procedural Hipparion (Hipparion mediterraneum, Late Miocene of Greece and Turkey)
for map colonies: a slender, pony-sized three-toed horse.

Light build with long slim legs ending in a central hoof (the two small side
toes are hidden in the fetlock at map scale), a fairly long neck with a short
upright dark mane, a long horse head and a thin tail with a dark switch. Coat
dun-brown with darker back, pale belly and muzzle. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hipparion_mediterraneum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HipparionMediterraneum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="HipparionMediterraneum",
    leg_f=0.78, leg_h=0.80, length=0.78, girth=(0.17, 0.21),
    leg_r=(0.050, 0.060), leg_taper=0.5, foot="hoof", stride=0.14,
    neck_len=0.48, neck_angle=50, neck_r=(0.12, 0.075),
    head_len=0.46, head_r=(0.075, 0.095), snout_r=(0.045, 0.055), head_pitch=58,
    ears="point", ear_size=0.085, mane=0.05,
    tail_len=0.45, tail_r=0.03, tail_tuft=0.06, tail_droop=0.9,
    coat=(0.58, 0.45, 0.30), dark=(0.30, 0.22, 0.15), pale=(0.85, 0.78, 0.66),
    mane_col=(0.15, 0.11, 0.08), shag=0.004, voxel=0.016,
)

if __name__ == "__main__":
    q.main(SPEC)
