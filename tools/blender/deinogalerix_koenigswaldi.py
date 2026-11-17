"""
Procedural Deinogalerix koenigswaldi (Late Miocene of the Gargano island,
Italy) for map colonies: a giant island gymnure, or "moonrat", a hairy
relative of hedgehogs that grew to about the size of a cat.

A low, long-bodied insectivore with a long, conical snout, a big head, short
legs and a long, naked, rat-like tail; coarse fur (no spines). Dark brown fur
with a paler face, pinkish tail. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/deinogalerix_koenigswaldi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DeinogalerixKoenigswaldi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DeinogalerixKoenigswaldi",
    leg_f=0.20, leg_h=0.20, length=0.58, girth=(0.15, 0.16),
    leg_r=(0.04, 0.045), leg_taper=0.7, foot="paw", stride=0.08,
    neck_len=0.12, neck_angle=10, neck_r=(0.13, 0.11),
    head_len=0.42, head_r=(0.10, 0.09), snout_r=(0.025, 0.025), head_pitch=12,
    ears="round", ear_size=0.04,
    tail_len=0.55, tail_r=0.035, tail_droop=0.25,
    coat=(0.36, 0.28, 0.20), dark=(0.22, 0.16, 0.11), pale=(0.66, 0.56, 0.44),
    pattern=q.pink_tail((0.72, 0.56, 0.50)),
    shag=0.006, voxel=0.011, max_tris=8000,
)

if __name__ == "__main__":
    q.main(SPEC)
