"""
Procedural Barylambda faberi (North America, late Paleocene, ~59-56 Ma) for map colonies. Built with nh_pal_quad.py.

A heavy pantodont about 2.5 m long and some 600 kg, with a small head for
its size, massive hindquarters and a very thick, muscular tail that may have
propped it up when it reared to browse. Short, sturdy legs end in broad five-toed
feet. Coat: dull olive-brown (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/barylambda_faberi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BarylambdaFaberi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="BarylambdaFaberi",
    length=0.95, shoulder=0.62, hip=0.74, width=0.24, depth=0.25, belly=1.1, arch=0.02,
    fore_r=0.075, hind_r=0.11, shin=0.78, foot="pad", foot_r=0.07, hock=0.0, stride=0.07,
    neck_len=0.2, neck_angle=20, neck_r=0.13,
    head_len=0.27, head_w=0.4, head_h=0.38, snout=0.6, snout_r=(0.3, 0.24), snout_tilt=18, jaw=0.85, jaw_r=0.22,
    ear=0.16, ear_shape="round", eye=0.06, eye_pos=(0.32, -0.25, 0.12), nose_col=(0.18, 0.15, 0.12),
    tail_len=0.78, tail_r=0.11, tail_angle=-28, tail_curl=-8,
    coat=(0.42, 0.38, 0.28), back=(0.32, 0.29, 0.21), pale=(0.62, 0.57, 0.46), pale_amt=0.7, fur=0.8,
    voxel=0.014, max_tris=13000, ground=(0.40, 0.44, 0.28),
)


if __name__ == "__main__":
    q.main(SPEC)
