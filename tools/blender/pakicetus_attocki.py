"""
Procedural Pakicetus attocki (Pakistan, early Eocene, ~50 Ma) for map colonies. Built with nh_pal_quad.py.

One of the earliest whales, a wolf-sized land mammal about 1-2 m long that
waded in shallow streams. It had long slender legs with small hooves, a long thick
tail and a long, narrow snout, with its eyes set high on top of the head like a
crocodile's; the ear bones already show the thick, whale-like shell. Coat: brown
with a darker back (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pakicetus_attocki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PakicetusAttocki.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="PakicetusAttocki",
    length=0.7, shoulder=0.52, hip=0.55, width=0.12, depth=0.14,
    fore_r=0.038, hind_r=0.052, shin=0.55, foot="hoof", foot_r=0.028, hock=0.6, stride=0.07,
    neck_len=0.22, neck_angle=28, neck_r=0.072,
    head_len=0.26, head_w=0.32, head_h=0.32, snout=1.1, snout_r=(0.25, 0.14), snout_tilt=8, jaw=0.95, jaw_r=0.16,
    ear=0.14, ear_shape="round", eye=0.07, eye_pos=(0.2, -0.2, 0.26), eye_up=True, nose_col=(0.1, 0.08, 0.07),
    tail_len=0.75, tail_r=0.055, tail_angle=-18, tail_curl=-12,
    coat=(0.50, 0.40, 0.29), back=(0.30, 0.23, 0.17), pale=(0.80, 0.72, 0.58), pale_amt=0.8,
    voxel=0.0105, max_tris=12000, ground=(0.50, 0.46, 0.30),
)


if __name__ == "__main__":
    q.main(SPEC)
