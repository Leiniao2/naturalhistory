"""
Procedural Rodhocetus kasranii (middle Eocene, ~47 Ma,
Pakistan) for map colonies.

A protocetid early whale about 3 m long that still had four working legs: short
forelimbs and big hind feet with long webbed toes that it paddled with, a long
narrow snout and a long muscular tail without a fluke. It could probably still
haul out on land, like a sea lion. Colour: dark brown-grey above, pale below
(unknown). Built with nh_pal_whale.py.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/rodhocetus_kasranii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RodhocetusKasranii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="RodhocetusKasranii",
    length=2.0, flat=0.95, head_end=0.18, teeth=7, tooth_len=0.02,
    profile=((0.0, 0.014), (0.07, 0.04), (0.16, 0.08), (0.24, 0.1), (0.4, 0.15), (0.6, 0.13), (0.8, 0.07),
             (1.0, 0.02)),
    flipper=(0.3, 0.22, 0.045), flipper_legs=True, hind=(0.6, 0.24, 0.07),
    back=(0.26, 0.24, 0.21), belly=(0.68, 0.63, 0.55), pattern=0.1, eye_r=0.016,
    voxel=0.011, max_tris=12000,
)

if __name__ == "__main__":
    w.main(SPEC)
