"""
Procedural Squalodon calvertensis (Miocene of the North Atlantic) for map
colonies: a "shark-toothed dolphin".

A dolphin about 3 m long with a long, slender beak lined with sharp front
teeth and triangular, serrated cheek teeth like a shark's, a low dorsal fin,
broad flippers and flukes. Dark grey back, pale belly. Built with
nh_pal_whale.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/squalodon_calvertensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SqualodonCalvertensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="SqualodonCalvertensis",
    length=2.0, flat=0.92, head_end=0.24, jaw_open=0.12, teeth=12, tooth_len=0.026,
    profile=((0.0, 0.012), (0.08, 0.03), (0.17, 0.07), (0.25, 0.14), (0.4, 0.19), (0.6, 0.16), (0.82, 0.07),
             (1.0, 0.03)),
    flipper=(0.31, 0.24, 0.08), hind=(0.6, 0.0, 0.0), fluke=0.26, dorsal=0.10, dorsal_t=0.55,
    back=(0.24, 0.27, 0.31), belly=(0.80, 0.80, 0.78), mid=(0.48, 0.50, 0.53), eye_r=0.016,
    voxel=0.012, max_tris=12000,
)

if __name__ == "__main__":
    w.main(SPEC)
