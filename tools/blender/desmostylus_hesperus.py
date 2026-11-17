"""
Procedural Desmostylus hesperus (Middle Miocene of the North Pacific coasts)
for map colonies: a desmostylian, an extinct order of amphibious marine
mammals.

A hippo-sized, heavily built quadruped with sprawling, stout limbs and broad
feet for paddling and walking on the sea floor, a long, low head whose upper
and lower tusks jut forward like a shovel, and a short tail. Its columnar
"bundle-of-pillars" molars give the genus its name. Dark grey-brown skin.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/desmostylus_hesperus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DesmostylusHesperus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DesmostylusHesperus",
    leg_f=0.36, leg_h=0.38, length=0.95, girth=(0.30, 0.30), belly=1.08,
    leg_r=(0.08, 0.085), leg_taper=0.75, foot="plantigrade", foot_r=1.25, stride=0.10,
    neck_len=0.16, neck_angle=10, neck_r=(0.22, 0.17),
    head_len=0.56, head_r=(0.13, 0.12), snout_r=(0.08, 0.07), head_pitch=18,
    ears="none",
    tail_len=0.18, tail_r=0.04, tail_droop=0.7,
    tusks=[dict(t=0.92, s=sx * 0.08, u=-0.04, dir=(sx * 0.15, -1, -0.5), len=0.17, r=0.03, tip=0.012) for sx in (-1, 1)]
         + [dict(t=0.92, s=sx * 0.06, u=-0.14, dir=(sx * 0.1, -1, -0.2), len=0.15, r=0.026, tip=0.01) for sx in (-1, 1)],
    coat=(0.36, 0.32, 0.28), dark=(0.24, 0.21, 0.19), pale=(0.52, 0.47, 0.42),
    voxel=0.019,
)

if __name__ == "__main__":
    q.main(SPEC)
