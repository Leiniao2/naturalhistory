"""
Procedural Deinotherium giganteum (Middle-Late Miocene of Europe) for map colonies.

One of the largest land mammals ever: a tall, long-legged proboscidean about
4 m at the shoulder, with a level back, a relatively small, low flat skull,
a shortish trunk and no upper tusks - instead a pair of thick lower tusks
that curve straight down and back from the tip of the downturned lower jaw.
Grey, nearly hairless skin. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/deinotherium_giganteum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DeinotheriumGiganteum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DeinotheriumGiganteum",
    leg_f=0.98, leg_h=0.90, length=0.80, girth=(0.34, 0.40), belly=1.05,
    leg_r=(0.105, 0.11), foot="pillar", foot_r=1.1, stride=0.10,
    neck_len=0.10, neck_angle=10, neck_r=(0.30, 0.25),
    head_len=0.52, head_r=(0.22, 0.22), snout_r=(0.13, 0.12), head_pitch=55, jaw=0.9,
    ears="flap", ear_size=0.24,
    tail_len=0.45, tail_r=0.04, tail_tuft=0.04, tail_droop=0.95,
    trunk_len=0.62, trunk_r=0.10, trunk_curl=0.25,
    tusks=[dict(t=0.88, s=sx * 0.10, u=-0.36, dir=(sx * 0.15, -0.3, -1.0), len=0.50, r=0.055, bend=(0, 2.2, 0.0), tip=0.015)
           for sx in (-1, 1)],
    coat=(0.42, 0.40, 0.38), dark=(0.30, 0.29, 0.28), pale=(0.55, 0.53, 0.50), countershade=0.5,
    voxel=0.022, max_tris=12000,
)

if __name__ == "__main__":
    q.main(SPEC)
