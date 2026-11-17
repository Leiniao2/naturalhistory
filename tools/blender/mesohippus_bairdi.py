"""
Procedural Mesohippus bairdi (North America, late Eocene to Oligocene, ~37-32 Ma) for map colonies. Built with nh_pal_quad.py.

A three-toed early horse about 60 cm at the shoulder: longer, straighter legs
and a straighter back than the dawn horses, a longer neck and a longer face with
the eyes set further back, small hooves on three toes, a short dark mane and a
hanging tail. Coat: sandy grey-brown with a pale belly (colour unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mesohippus_bairdi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MesohippusBairdi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="MesohippusBairdi",
    length=0.76, shoulder=0.78, hip=0.80, width=0.13, depth=0.17,
    fore_r=0.05, hind_r=0.066, shin=0.52, foot="hoof", foot_r=0.03, hock=0.75, stride=0.08,
    neck_len=0.34, neck_angle=50, neck_r=0.09,
    head_len=0.27, head_w=0.34, head_h=0.38, snout=0.95, snout_r=(0.3, 0.2), snout_tilt=40, jaw=0.8, jaw_r=0.2,
    ear=0.3, ear_angle=12, eye=0.065, eye_pos=(0.3, -0.12, 0.15), nose_col=(0.15, 0.12, 0.1),
    mane=0.035, mane_col=(0.22, 0.17, 0.12),
    tail_len=0.42, tail_r=0.035, tail_angle=-60, tail_curl=-10, tail_tuft=0.04,
    coat=(0.58, 0.48, 0.36), back=(0.44, 0.35, 0.25), pale=(0.85, 0.79, 0.68), dark_legs=0.4,
    voxel=0.011, max_tris=12000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
