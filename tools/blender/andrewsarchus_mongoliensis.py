"""
Procedural Andrewsarchus mongoliensis (Inner Mongolia, middle Eocene, ~45-42 Ma) for map colonies. Built with nh_pal_quad.py.

Known only from an 83 cm skull, the largest of any land mammal predator or
scavenger of its time. It was probably a relative of the entelodonts and
hippos, so it is shown as a bulky, long-legged, hoofed-toed animal with a huge,
long and low head full of big blunt teeth and stout canines. Coat: dark grey-brown
(unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/andrewsarchus_mongoliensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AndrewsarchusMongoliensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="AndrewsarchusMongoliensis",
    length=0.95, shoulder=0.82, hip=0.74, width=0.2, depth=0.24, hump=0.04,
    fore_r=0.075, hind_r=0.085, shin=0.6, foot="hoof", foot_r=0.05, hock=0.45, stride=0.09,
    neck_len=0.26, neck_angle=18, neck_r=0.15,
    head_len=0.46, head_w=0.36, head_h=0.38, snout=1.05, snout_r=(0.32, 0.25), snout_tilt=8, jaw=0.95, jaw_r=0.2,
    ear=0.14, ear_shape="round", eye=0.045, eye_pos=(0.3, -0.2, 0.12), nose_col=(0.1, 0.08, 0.07),
    tail_len=0.35, tail_r=0.05, tail_angle=-55,
    horns=[Horn(base=(0.14, -1.15, -0.25), direction=(0.05, -0.1, -1), length=0.16, radius=0.04,
                color=(0.88, 0.84, 0.72)),
           Horn(base=(0.12, -1.1, -0.42), direction=(0.05, -0.2, 1), length=0.13, radius=0.035,
                color=(0.88, 0.84, 0.72))],
    coat=(0.33, 0.29, 0.25), back=(0.22, 0.19, 0.16), pale=(0.55, 0.50, 0.43), pale_amt=0.6, dark_legs=0.5,
    voxel=0.014, max_tris=13000, ground=(0.52, 0.48, 0.34),
)


if __name__ == "__main__":
    q.main(SPEC)
