"""
Procedural Dorudon atrox (late Eocene, ~40-34 Ma, Tethys Sea, best
known from Egypt's Wadi Al-Hitan) for map colonies.

A dolphin-shaped archaeocete whale about 5 m long, with a long-snouted skull and
large shearing cheek teeth, short paddle flippers, a horizontal tail fluke and
tiny vestigial hind legs. Juveniles bitten by Basilosaurus are known from the
same rocks. Colour: dark grey above, pale below (unknown). Built with nh_pal_whale.py.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/dorudon_atrox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DorudonAtrox.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="DorudonAtrox",
    length=2.0, flat=0.9, head_end=0.2, teeth=8, tooth_len=0.024,
    profile=((0.0, 0.015), (0.08, 0.05), (0.18, 0.11), (0.3, 0.19), (0.45, 0.21), (0.7, 0.14), (0.9, 0.06),
             (1.0, 0.03)),
    flipper=(0.3, 0.26, 0.07), hind=(0.68, 0.05, 0.012), fluke=0.24, dorsal=0.0,
    back=(0.22, 0.25, 0.30), belly=(0.78, 0.77, 0.74), eye_r=0.018,
    voxel=0.012, max_tris=12000,
)

if __name__ == "__main__":
    w.main(SPEC)
