"""
Procedural Arsinoitherium zitteli (North and East Africa, late Eocene to early Oligocene, ~36-30 Ma) for map colonies. Built with nh_pal_quad.py.

A rhino-like embrithopod about 3 m long and 1.8 m at the shoulder, related
to elephants and hyraxes. Two enormous, hollow conical horns rose side by side
from the top of its nose, with a small pair of knobs behind them. Columnar legs
on short, splayed feet suited soft ground in coastal swamp forests. Skin: dark
grey-brown (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/arsinoitherium_zitteli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArsinoitheriumZitteli.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="ArsinoitheriumZitteli",
    length=0.95, shoulder=0.86, hip=0.80, width=0.24, depth=0.26, belly=1.1,
    fore_r=0.08, hind_r=0.1, shin=0.8, foot="pad", foot_r=0.08, hock=0.0, stride=0.08,
    neck_len=0.2, neck_angle=15, neck_r=0.16,
    head_len=0.42, head_w=0.38, head_h=0.36, snout=0.75, snout_r=(0.27, 0.22), snout_tilt=18, jaw=0.85, jaw_r=0.2,
    ear=0.16, ear_angle=30, eye=0.05, eye_pos=(0.32, -0.22, 0.08),
    tail_len=0.25, tail_r=0.04, tail_angle=-65,
    horns=[
        Horn(base=(0.11, -0.55, 0.1), direction=(0.12, -0.6, 1), length=0.95, radius=0.16, bend=0.35,
             bend_dir=(0.1, 0.5, 0.2), fuse=True, tip=0.12, color=(0.32, 0.28, 0.25)),
        Horn(base=(0.16, -0.1, 0.28), direction=(0.35, -0.3, 1), length=0.18, radius=0.07, tip=0.5, fuse=True,
             color=(0.32, 0.28, 0.25)),
    ],
    coat=(0.40, 0.36, 0.32), back=(0.32, 0.29, 0.26), pale=(0.54, 0.49, 0.44), pale_amt=0.6, skin=0.6, fur=0.3,
    voxel=0.015, max_tris=14000, ground=(0.36, 0.42, 0.28),
)


if __name__ == "__main__":
    q.main(SPEC)
