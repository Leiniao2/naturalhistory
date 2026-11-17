"""
Procedural Diprotodon optatum (Pleistocene of Australia) for map colonies: the
largest marsupial that ever lived, about the size of a hippopotamus.

A heavy, wombat-like quadruped with a deep barrel body, stout legs on broad
plantigrade feet turned slightly inward, a large head with a broad, blunt
muzzle and small eyes, small rounded ears and a stub tail. Brown coat with a
paler muzzle. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/diprotodon_optatum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DiprotodonOptatum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DiprotodonOptatum",
    leg_f=0.42, leg_h=0.42, length=0.95, girth=(0.31, 0.33), belly=1.1,
    leg_r=(0.085, 0.09), leg_taper=0.75, foot="plantigrade", foot_r=1.1, stride=0.10,
    neck_len=0.14, neck_angle=5, neck_r=(0.25, 0.20),
    head_len=0.50, head_r=(0.16, 0.17), snout_r=(0.11, 0.10), head_pitch=25,
    ears="round", ear_size=0.10,
    tail_len=0.08, tail_r=0.04, tail_droop=0.8,
    coat=(0.44, 0.34, 0.24), dark=(0.28, 0.21, 0.15), pale=(0.66, 0.57, 0.46),
    shag=0.008, voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
