"""
Procedural Toxodon platensis (Pleistocene of South America) for map colonies:
a notoungulate, one of South America's native hoofed mammals, described by
Owen from fossils Darwin collected.

Rhino-sized and barrel-bodied with short, stout legs - the hind legs longer
than the front, so the back rises to the hips - three-toed feet, a short neck
and a big, broad head with a blunt, hippo-like muzzle. Short tail. Grey-brown,
sparsely haired skin. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/toxodon_platensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ToxodonPlatensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ToxodonPlatensis",
    leg_f=0.40, leg_h=0.52, length=0.95, girth=(0.30, 0.32), belly=1.08,
    leg_r=(0.08, 0.09), leg_taper=0.75, foot="pillar", stride=0.10,
    neck_len=0.14, neck_angle=-5, neck_r=(0.24, 0.19),
    head_len=0.52, head_r=(0.15, 0.16), snout_r=(0.11, 0.10), head_pitch=35,
    ears="point", ear_size=0.08,
    tail_len=0.22, tail_r=0.03, tail_tuft=0.03, tail_droop=0.95,
    coat=(0.45, 0.39, 0.33), dark=(0.32, 0.27, 0.22), pale=(0.58, 0.52, 0.45),
    voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
