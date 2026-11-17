"""
Procedural woolly rhinoceros (Coelodonta antiquitatis, Pleistocene of northern
Eurasia) for map colonies.

A stocky, short-legged rhino with a shoulder hump, the head carried low (it
grazed the mammoth steppe), a very long, flattened front horn sweeping forward
and up from the nose and a smaller second horn between the eyes; small ears
and a short tail. A long shaggy coat, reddish-brown with a darker hump and
legs. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/coelodonta_antiquitatis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CoelodontaAntiquitatis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="CoelodontaAntiquitatis",
    leg_f=0.42, leg_h=0.42, length=1.00, girth=(0.30, 0.33), belly=1.08,
    hump=0.40, hump_y=-0.40,
    leg_r=(0.08, 0.085), leg_taper=0.7, foot="pillar", stride=0.10,
    neck_len=0.16, neck_angle=-12, neck_r=(0.25, 0.19),
    head_len=0.56, head_r=(0.14, 0.15), snout_r=(0.08, 0.09), head_pitch=38,
    ears="point", ear_size=0.08,
    tail_len=0.25, tail_r=0.03, tail_tuft=0.05, tail_droop=0.95,
    horns=[dict(t=0.92, u=0.16, len=0.68, r=0.08, dir=(0, -0.9, 0.6), bend=(0, 0.6, 1.3), tip=0.006, flat=0.45,
                color=(0.26, 0.20, 0.15)),
           dict(t=0.55, u=0.20, len=0.20, r=0.05, dir=(0, -0.1, 1), bend=(0, 0.3, 0), tip=0.006, color=(0.26, 0.20, 0.15))],
    mane=0.08, beard=0.12,
    coat=(0.50, 0.36, 0.22), dark=(0.30, 0.21, 0.13), pale=(0.66, 0.54, 0.40),
    mane_col=(0.34, 0.24, 0.15), shag=0.022, voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
