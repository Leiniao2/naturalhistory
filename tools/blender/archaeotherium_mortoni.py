"""
Procedural Archaeotherium mortoni (North America, late Eocene to Oligocene, ~35-28 Ma) for map colonies. Built with nh_pal_quad.py.

An entelodont, one of the pig-like "hell pigs": about 1.2 m at the shoulder,
with a hump over the shoulders, slim legs on two-toed hooves, and a huge head
carrying bony flanges under the eyes and knobs under the chin. An omnivore that
dug roots and scavenged or killed other mammals. Coat: dark brown, bristly
(unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/archaeotherium_mortoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArchaeotheriumMortoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="ArchaeotheriumMortoni",
    length=0.8, shoulder=0.86, hip=0.74, width=0.16, depth=0.22, hump=0.07,
    fore_r=0.055, hind_r=0.068, shin=0.55, foot="hoof", foot_r=0.038, hock=0.7, stride=0.09,
    neck_len=0.25, neck_angle=15, neck_r=0.13,
    head_len=0.42, head_w=0.33, head_h=0.38, snout=0.85, snout_r=(0.28, 0.22), snout_tilt=22, jaw=0.95, jaw_r=0.22,
    ear=0.17, ear_angle=25, eye=0.05, eye_pos=(0.3, -0.2, 0.15), nose_col=(0.25, 0.18, 0.16),
    mane=0.04, mane_col=(0.15, 0.11, 0.09),
    tail_len=0.3, tail_r=0.025, tail_angle=-72, tail_tuft=0.03,
    horns=[
        Horn(base=(0.3, -0.25, -0.18), direction=(1, 0.2, -0.6), length=0.2, radius=0.13, tip=0.6, fuse=True,
             color=(0.30, 0.23, 0.19)),
        Horn(base=(0.1, -0.6, -0.48), direction=(0.3, 0, -1), length=0.1, radius=0.065, tip=0.6, fuse=True,
             color=(0.30, 0.23, 0.19)),
        Horn(base=(0.13, -1.0, -0.3), direction=(0.05, -0.1, -1), length=0.14, radius=0.035,
             color=(0.9, 0.86, 0.75)),
    ],
    coat=(0.30, 0.23, 0.19), back=(0.18, 0.14, 0.12), pale=(0.45, 0.37, 0.31), pale_amt=0.6, dark_legs=0.5,
    voxel=0.012, max_tris=12000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
