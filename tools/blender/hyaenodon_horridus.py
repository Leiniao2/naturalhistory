"""
Procedural Hyaenodon horridus (North America, late Eocene to Oligocene, ~37-30 Ma) for map colonies. Built with nh_pal_quad.py.

A wolf-sized hyaenodont, one of the creodont-grade carnivores unrelated to
modern dogs and cats. It had a big, long and narrow head with shearing teeth,
slim legs, five-toed feet and a long tail. Coat: dull grey-brown with a darker
back (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hyaenodon_horridus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HyaenodonHorridus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="HyaenodonHorridus",
    length=0.78, shoulder=0.66, hip=0.64, width=0.13, depth=0.17,
    fore_r=0.048, hind_r=0.058, shin=0.55, foot="paw", foot_r=0.042, toes=4, hock=0.45, stride=0.09,
    neck_len=0.24, neck_angle=25, neck_r=0.09,
    head_len=0.33, head_w=0.33, head_h=0.34, snout=0.95, snout_r=(0.28, 0.17), snout_tilt=10, jaw=0.95, jaw_r=0.18,
    ear=0.2, ear_shape="round", eye=0.06, eye_pos=(0.3, -0.25, 0.12), nose_col=(0.06, 0.05, 0.05),
    tail_len=0.62, tail_r=0.045, tail_angle=-40, tail_curl=15,
    horns=[Horn(base=(0.1, -1.05, -0.17), direction=(0.05, -0.1, -1), length=0.11, radius=0.025,
                color=(0.9, 0.86, 0.75))],
    coat=(0.42, 0.37, 0.31), back=(0.25, 0.22, 0.19), pale=(0.64, 0.59, 0.50), pale_amt=0.7, dark_legs=0.4,
    voxel=0.011, max_tris=12000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
