"""
Procedural giant short-faced bear (Arctodus simus, Pleistocene of North
America) for map colonies.

One of the largest carnivorous land mammals, standing about 1.6 m at the
shoulder on all fours: long legs that give it a lanky, high-shouldered look,
a short back, a short, broad face with a deep muzzle, small round ears and a
stub tail. Brown shaggy coat with a paler face. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/arctodus_simus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArctodusSimus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ArctodusSimus",
    leg_f=0.75, leg_h=0.66, length=0.70, girth=(0.24, 0.28),
    hump=0.25, hump_y=-0.42,
    leg_r=(0.08, 0.085), leg_taper=0.7, foot="plantigrade", stride=0.12,
    neck_len=0.24, neck_angle=25, neck_r=(0.20, 0.15),
    head_len=0.30, head_r=(0.14, 0.13), snout_r=(0.085, 0.08), head_pitch=12, eye_t=0.42, eye_u=0.35,
    ears="round", ear_size=0.08,
    tail_len=0.08, tail_r=0.04, tail_droop=0.8,
    coat=(0.40, 0.28, 0.17), dark=(0.24, 0.16, 0.09), pale=(0.62, 0.50, 0.36),
    shag=0.014, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
