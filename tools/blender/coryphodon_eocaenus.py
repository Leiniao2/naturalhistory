"""
Procedural Coryphodon eocaenus (Europe and North America, latest Paleocene to early Eocene, ~56-50 Ma) for map colonies. Built with nh_pal_quad.py.

A pantodont about 2.25 m long and 1 m at the shoulder, built like a small
hippo: a heavy barrel body on short, stout legs with broad five-toed feet, a short
neck, a broad head with small tusk-like canines, and a short tail. It probably
wallowed in the swamps it browsed. Skin: dark brown-grey (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/coryphodon_eocaenus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CoryphodonEocaenus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="CoryphodonEocaenus",
    length=0.95, shoulder=0.62, hip=0.62, width=0.24, depth=0.24, belly=1.15,
    fore_r=0.075, hind_r=0.09, shin=0.8, foot="pad", foot_r=0.075, hock=0.0, stride=0.07,
    neck_len=0.16, neck_angle=12, neck_r=0.16,
    head_len=0.38, head_w=0.42, head_h=0.34, snout=0.65, snout_r=(0.3, 0.27), snout_flat=1.2, snout_tilt=12,
    jaw=0.9, jaw_r=0.24, ear=0.12, ear_shape="round", eye=0.05, eye_pos=(0.34, -0.25, 0.12),
    nose_col=(0.2, 0.16, 0.14),
    tail_len=0.3, tail_r=0.05, tail_angle=-45,
    horns=[Horn(base=(0.17, -0.82, -0.22), direction=(0.2, -0.15, -1), length=0.16, radius=0.04, bend=0.6,
                bend_dir=(0.3, -0.5, 0.6), color=(0.88, 0.84, 0.72))],
    coat=(0.36, 0.31, 0.27), back=(0.28, 0.24, 0.21), pale=(0.50, 0.44, 0.38), pale_amt=0.6, skin=0.5, fur=0.4,
    voxel=0.014, max_tris=13000, ground=(0.36, 0.42, 0.28),
)


if __name__ == "__main__":
    q.main(SPEC)
