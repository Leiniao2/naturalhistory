"""
Procedural Dromornis stirtoni (Late Miocene of central Australia) for map
colonies: Stirton's thunderbird, one of the largest birds that ever lived.

A flightless bird about 3 m tall and up to 600 kg, related to ducks and geese,
with a massive, deep, blunt-tipped beak, tiny wings, a heavy body and stout
legs ending in hoof-like toes. Brown plumage, a pale grey head and a horn-
coloured beak. Built with nh_neo_bigbird.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dromornis_stirtoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DromornisStirtoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="DromornisStirtoni",
    hip=0.95, body=(0.32, 0.52, 0.36), body_tilt=8, leg_r=0.11,
    neck=((0, -0.38, 0.25), (0, -0.46, 0.55), (0, -0.52, 0.80)), neck_r=(0.19, 0.15, 0.13),
    head_r=0.15, beak_len=0.40, beak_h=0.30, hook=0.3, wing=0.12, tail=0.10,
    feather=(0.42, 0.32, 0.22), dark=(0.24, 0.17, 0.11), pale=(0.66, 0.57, 0.44),
    head_col=(0.55, 0.53, 0.50), beak_col=(0.50, 0.44, 0.33), leg_col=(0.40, 0.36, 0.30), stride=0.30,
    shag=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
