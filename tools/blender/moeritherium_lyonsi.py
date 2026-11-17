"""
Procedural Moeritherium lyonsi (North Africa, late Eocene, ~37-35 Ma) for map colonies. Built with nh_pal_quad.py.

An early proboscidean, a relative of elephants that looked more like a
pygmy hippo or tapir: about 70 cm at the shoulder, long-bodied on short legs,
with a mobile, slightly elongated upper lip and short tusk-like incisors in both
jaws. It probably lived much like a hippo, in swamps and rivers. Skin: dark
grey-brown (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/moeritherium_lyonsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MoeritheriumLyonsi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="MoeritheriumLyonsi",
    length=0.95, shoulder=0.52, hip=0.54, width=0.2, depth=0.2, belly=1.1,
    fore_r=0.065, hind_r=0.075, shin=0.8, foot="pad", foot_r=0.065, hock=0.0, stride=0.07,
    neck_len=0.15, neck_angle=15, neck_r=0.14,
    head_len=0.33, head_w=0.38, head_h=0.36, snout=0.5, snout_r=(0.3, 0.25), snout_tilt=28, jaw=0.6, jaw_r=0.19,
    ear=0.12, ear_shape="round", eye=0.055, eye_pos=(0.32, -0.25, 0.14), nose_col=(0.25, 0.2, 0.18),
    tail_len=0.25, tail_r=0.04, tail_angle=-55,
    horns=[Horn(base=(0.07, -0.68, -0.3), direction=(0.05, -0.5, -1), length=0.12, radius=0.035,
                color=(0.88, 0.84, 0.72)),
           Horn(base=(0.05, -0.55, -0.4), direction=(0.05, -1, 0.3), length=0.1, radius=0.03,
                color=(0.88, 0.84, 0.72))],
    coat=(0.36, 0.33, 0.30), back=(0.28, 0.26, 0.24), pale=(0.50, 0.46, 0.42), pale_amt=0.6, skin=0.5, fur=0.3,
    voxel=0.013, max_tris=12000, ground=(0.36, 0.42, 0.28),
)


if __name__ == "__main__":
    q.main(SPEC)
