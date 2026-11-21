"""
Procedural Metaxytherium floridanum (Middle Miocene of the Caribbean and
Florida) for map colonies: an extinct dugong relative.

A sea cow about 3 m long: a fat, spindle-shaped body with paddle-like
flippers, no hind limbs, a whale-like tail fluke (as in the living dugong),
a small head with a down-turned snout for grazing seagrass and wrinkled grey
skin. Built with nh_pal_whale.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/metaxytherium_floridanum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MetaxytheriumFloridanum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="MetaxytheriumFloridanum",
    length=2.0, flat=1.05, head_end=0.14, jaw_open=0.0, teeth=0, tooth_len=0.0,
    profile=((0.0, 0.07), (0.05, 0.10), (0.12, 0.13), (0.2, 0.17), (0.4, 0.27), (0.6, 0.25), (0.8, 0.12),
             (0.93, 0.05), (1.0, 0.03)),
    flipper=(0.24, 0.30, 0.11), hind=(0.6, 0.0, 0.0), fluke=0.34, dorsal=0.0, sag=0.05,
    back=(0.40, 0.40, 0.40), belly=(0.62, 0.60, 0.57), mid=(0.50, 0.49, 0.48), pattern=0.3, eye_r=0.012,
    voxel=0.014, max_tris=11000,
)

if __name__ == "__main__":
    w.main(SPEC)
