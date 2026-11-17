"""
Procedural Basilosaurus cetoides (late Eocene, ~41-34 Ma, warm
seas over today's south-eastern USA) for map colonies.

A fully marine archaeocete whale 15-18 m long with a very long, slender, almost
eel-like body of elongated vertebrae, a comparatively small 1.5 m head with long
jaws full of large shearing teeth, small paddle flippers, tiny but complete hind
legs useless for walking, and probably a small tail fluke. Colour: dark grey
above, pale below (unknown). Built with nh_pal_whale.py.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/basilosaurus_cetoides.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BasilosaurusCetoides.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="BasilosaurusCetoides",
    length=2.6, flat=0.85, head_end=0.075, teeth=7, tooth_len=0.02,
    profile=((0.0, 0.012), (0.03, 0.035), (0.07, 0.06), (0.12, 0.085), (0.3, 0.1), (0.6, 0.09), (0.85, 0.06),
             (1.0, 0.02)),
    flipper=(0.13, 0.16, 0.05), hind=(0.55, 0.07, 0.015), fluke=0.11, sag=0.02,
    back=(0.20, 0.22, 0.24), belly=(0.70, 0.68, 0.64), pattern=0.15, eye_r=0.012,
    voxel=0.011, max_tris=14000,
)

if __name__ == "__main__":
    w.main(SPEC)
