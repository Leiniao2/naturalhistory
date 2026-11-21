"""
Procedural Ailuravus macrurus (Messel, Germany, middle Eocene, ~47 Ma) for map colonies. Built with nh_pal_quad.py.

One of the largest early rodents, about 70 cm long of which more than half was a very long,
bushy tail. Squirrel-like build with clawed feet for climbing, a short rodent face with
small round ears and orange-faced, ever-growing gnawing incisors. It lived in the trees of
the Messel forest and ate leaves (leaf remains survive in its gut). Coat: warm red-brown
with a pale belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ailuravus_macrurus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AiluravusMacrurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

SPEC = q.Spec(
    name="AiluravusMacrurus",
    length=0.42, shoulder=0.24, hip=0.27, width=0.08, depth=0.085, arch=0.02,
    fore_r=0.025, hind_r=0.035, shin=0.6, foot="paw", foot_r=0.025, toes=5, hock=0.4, stride=0.05,
    neck_len=0.08, neck_angle=30, neck_r=0.055,
    head_len=0.15, head_w=0.4, head_h=0.38, snout=0.45, snout_r=(0.28, 0.18), snout_tilt=20, jaw=0.6, jaw_r=0.16,
    ear=0.2, ear_shape="round", ear_angle=25, eye=0.1, eye_pos=(0.32, -0.2, 0.14), nose_col=(0.15, 0.1, 0.09),
    tail_len=0.75, tail_r=0.045, tail_bush=0.7, tail_angle=8, tail_curl=30,
    horns=[Horn(base=(0.035, -0.62, -0.25), direction=(0, -0.2, -1), length=0.14, radius=0.035, flat=0.7,
                color=(0.85, 0.55, 0.20))],
    coat=(0.55, 0.36, 0.22), back=(0.40, 0.26, 0.16), pale=(0.85, 0.78, 0.62), pale_amt=0.85,
    voxel=0.006, max_tris=9000, ground=(0.32, 0.40, 0.24),
)

if __name__ == "__main__":
    q.main(SPEC)
