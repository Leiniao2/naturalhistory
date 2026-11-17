"""
Procedural Gigantophis garstini (late Eocene, ~40-34 Ma, Fayum, Egypt) for map
colonies. Built with nh_pal_snake.py.

A madtsoiid, member of an ancient extinct family of constricting snakes unrelated
to boas and pythons, estimated at 7-10 m long and long thought the largest snake
until Titanoboa was found. Known from vertebrae found near Egypt's Fayum lakes
in rocks laid down by rivers and coastal swamps. Pattern: dark brown with
narrow pale bands (colour unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gigantophis_garstini.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GigantophisGarstini.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_snake as sn  # noqa: E402

SPEC = sn.Spec(
    name="GigantophisGarstini",
    length=2.4, girth=0.07, head_len=0.12, head_w=0.065, neck=0.6, tail=0.12,
    base=(0.62, 0.52, 0.36), saddle=(0.24, 0.17, 0.11), belly=(0.82, 0.76, 0.62),
    saddles=26, saddle_w=0.72, side_spots=0.0, head_col=(0.24, 0.17, 0.11),
)

if __name__ == "__main__":
    sn.main(SPEC, ground=(0.55, 0.50, 0.36))
