"""
Procedural horned gopher (Ceratogaulus hatcheri, Late Miocene - Early Pliocene of
the North American Great Plains) for map colonies.

A burrowing mylagaulid rodent about 30 cm long, the smallest mammal known to
have carried horns: a pair of stout bony horns rising side by side from the
top of its nose. A stocky, short-legged body, big digging claws on the front
feet, tiny eyes and ears and a short tail. Sandy-brown fur.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ceratogaulus_hatcheri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CeratogaulusHatcheri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="CeratogaulusHatcheri",
    leg_f=0.18, leg_h=0.18, length=0.55, girth=(0.17, 0.18), belly=1.05,
    leg_r=(0.05, 0.055), leg_taper=0.75, foot="paw", foot_r=1.3, stride=0.06,
    neck_len=0.10, neck_angle=10, neck_r=(0.15, 0.13),
    head_len=0.30, head_r=(0.10, 0.09), snout_r=(0.055, 0.05), head_pitch=12,
    ears="round", ear_size=0.035,
    tail_len=0.14, tail_r=0.025, tail_droop=0.5,
    horns=[dict(t=0.70, s=sx * 0.07, u=0.18, len=0.13, r=0.028, dir=(sx * 0.35, -0.3, 1), bend=(0, 0.2, 0), tip=0.006,
                color=(0.55, 0.46, 0.36)) for sx in (-1, 1)],
    coat=(0.60, 0.47, 0.32), dark=(0.40, 0.30, 0.20), pale=(0.80, 0.72, 0.58),
    shag=0.003, voxel=0.011, max_tris=8000,
)

if __name__ == "__main__":
    q.main(SPEC)
