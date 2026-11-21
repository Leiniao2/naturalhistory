"""
Procedural Taeniolabis taoensis (New Mexico and Colorado, early Paleocene, ~65-63 Ma) for map colonies. Built with nh_pal_quad.py.

The largest multituberculate, a member of an extinct, rodent-like branch of mammals that
lived alongside the dinosaurs: about 1 m long and 20-30 kg, the size of a beaver. Very deep,
broad skull with huge cheek muscles, a pair of large, self-sharpening gnawing incisors in
front and broad grinding teeth for tough plants; a stocky, low body with short clawed legs
and a thick tail. Coat: dark brown (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/taeniolabis_taoensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TaeniolabisTaoensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

SPEC = q.Spec(
    name="TaeniolabisTaoensis",
    length=0.62, shoulder=0.38, hip=0.42, width=0.16, depth=0.16, belly=1.2, arch=0.04,
    fore_r=0.045, hind_r=0.055, shin=0.7, foot="paw", foot_r=0.045, toes=5, hock=0.2, stride=0.06,
    neck_len=0.1, neck_angle=20, neck_r=0.1,
    head_len=0.26, head_w=0.48, head_h=0.48, snout=0.42, snout_r=(0.32, 0.24), snout_tilt=25, jaw=0.7, jaw_r=0.24,
    ear=0.14, ear_shape="round", ear_angle=30, eye=0.065, eye_pos=(0.36, -0.25, 0.2), nose_col=(0.12, 0.09, 0.08),
    tail_len=0.4, tail_r=0.06, tail_angle=-25, tail_curl=10,
    horns=[Horn(base=(0.05, -0.8, -0.3), direction=(0, -0.25, -1), length=0.3, radius=0.045, flat=0.75,
                bend=0.3, bend_dir=(0, 1, 0), color=(0.86, 0.62, 0.30))],
    coat=(0.36, 0.27, 0.19), back=(0.25, 0.19, 0.14), pale=(0.58, 0.48, 0.36), pale_amt=0.7,
    voxel=0.01, max_tris=11000, ground=(0.36, 0.42, 0.28),
)

if __name__ == "__main__":
    q.main(SPEC)
