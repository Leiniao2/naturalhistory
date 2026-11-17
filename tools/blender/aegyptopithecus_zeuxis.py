"""
Procedural Aegyptopithecus zeuxis (Egypt (Fayum), early Oligocene, ~33-30 Ma) for map colonies. Built with nh_pal_quad.py.

An early catarrhine primate close to the common ancestor of Old World monkeys
and apes, about the size of a howler monkey (~6 kg). It was a slow-climbing,
fruit-eating tree dweller with a longer snout and smaller brain than later monkeys
and a long tail. Coat: reddish-brown with a darker face (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/aegyptopithecus_zeuxis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AegyptopithecusZeuxis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="AegyptopithecusZeuxis",
    length=0.55, shoulder=0.48, hip=0.48, width=0.12, depth=0.13,
    fore_r=0.042, hind_r=0.052, shin=0.65, foot="hand", foot_r=0.04, toes=4, hock=0.25, stride=0.06,
    neck_len=0.13, neck_angle=35, neck_r=0.075,
    head_len=0.2, head_w=0.48, head_h=0.46, snout=0.6, snout_r=(0.33, 0.24), snout_tilt=22, jaw=0.85, jaw_r=0.24,
    ear=0.14, ear_shape="round", eye=0.11, eye_pos=(0.26, -0.38, 0.16), nose_col=(0.12, 0.08, 0.07),
    tail_len=0.75, tail_r=0.035, tail_angle=-50, tail_curl=60,
    coat=(0.52, 0.33, 0.19), back=(0.40, 0.24, 0.13), pale=(0.72, 0.56, 0.40), pale_amt=0.6,
    muzzle_col=(0.28, 0.20, 0.17),
    voxel=0.0095, max_tris=10000, ground=(0.32, 0.40, 0.24),
)


if __name__ == "__main__":
    q.main(SPEC)
