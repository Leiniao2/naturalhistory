"""
Procedural Uintatherium anceps (North America, middle Eocene, ~46-40 Ma) for map colonies. Built with nh_pal_quad.py.

A rhino-sized dinoceratan about 4 m long and 1.5 m at the shoulder with
heavy, columnar legs on broad padded feet. Its long, low skull carries three pairs
of blunt, skin-covered bony knobs (on the nose tip, above the eyes and at the back
of the skull), and the males have long, sabre-like upper canines. Skin: grey-brown,
nearly hairless (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/uintatherium_anceps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/UintatheriumAnceps.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="UintatheriumAnceps",
    length=1.1, shoulder=0.86, hip=0.80, width=0.25, depth=0.27, belly=1.1,
    fore_r=0.085, hind_r=0.1, shin=0.8, foot="pad", foot_r=0.085, hock=0.0, stride=0.08,
    neck_len=0.22, neck_angle=15, neck_r=0.17,
    head_len=0.42, head_w=0.36, head_h=0.34, snout=0.9, snout_r=(0.26, 0.2), snout_tilt=10, jaw=0.85, jaw_r=0.22,
    ear=0.15, ear_shape="round", eye=0.055, eye_pos=(0.3, -0.25, 0.1),
    tail_len=0.25, tail_r=0.04, tail_angle=-60, tail_tuft=0.03,
    horns=[
        Horn(base=(0.10, -0.98, 0.06), direction=(0.25, -0.3, 1), length=0.16, radius=0.07, tip=0.7, fuse=True,
             color=(0.40, 0.36, 0.32)),
        Horn(base=(0.20, -0.52, 0.12), direction=(0.45, -0.1, 1), length=0.24, radius=0.085, tip=0.7, fuse=True,
             color=(0.40, 0.36, 0.32)),
        Horn(base=(0.22, 0.12, 0.28), direction=(0.35, 0.25, 1), length=0.3, radius=0.1, tip=0.65, fuse=True,
             color=(0.40, 0.36, 0.32)),
        Horn(base=(0.15, -0.62, -0.2), direction=(0.05, 0.12, -1), length=0.42, radius=0.045, flat=0.55, bend=0.35,
             bend_dir=(0, 1, 0), color=(0.88, 0.84, 0.72)),
    ],
    coat=(0.46, 0.41, 0.36), back=(0.36, 0.32, 0.28), pale=(0.58, 0.53, 0.47), pale_amt=0.6, skin=0.6, fur=0.3,
    voxel=0.015, max_tris=14000, ground=(0.50, 0.47, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
