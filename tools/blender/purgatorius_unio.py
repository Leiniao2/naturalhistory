"""
Procedural Purgatorius unio (Montana, earliest Paleocene, ~65.9 Ma) for map colonies. Built with nh_pal_quad.py.

The earliest known plesiadapiform, the stem of the primates: a squirrel-sized climber about
15 cm long plus a longer tail, whose ankle bones show it could rotate its feet to climb down
tree trunks. Drawn like a small tree shrew or squirrel: a short pointed snout, eyes on the
sides of the head (not yet forward-facing), small round ears, grasping hands and feet and a
long, bushy tail. Coat: reddish brown with a pale belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/purgatorius_unio.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Purgatorius.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="Purgatorius",
    length=0.4, shoulder=0.3, hip=0.36, width=0.085, depth=0.095, arch=0.03,
    fore_r=0.028, hind_r=0.044, shin=0.6, foot="paw", foot_r=0.03, toes=5, hock=0.3, stride=0.06,
    neck_len=0.08, neck_angle=32, neck_r=0.06,
    head_len=0.17, head_w=0.42, head_h=0.42, snout=0.58, snout_r=(0.25, 0.12), snout_tilt=12, jaw=0.8, jaw_r=0.14,
    ear=0.18, ear_shape="round", eye=0.1, eye_pos=(0.36, -0.22, 0.13), nose_col=(0.22, 0.14, 0.12),
    tail_len=0.8, tail_r=0.045, tail_bush=0.9, tail_angle=45, tail_curl=-55,
    coat=(0.56, 0.36, 0.22), back=(0.40, 0.25, 0.15), pale=(0.88, 0.80, 0.66), pale_amt=0.9,
    voxel=0.008, max_tris=10000, ground=(0.30, 0.38, 0.22),
)


if __name__ == "__main__":
    q.main(SPEC)
