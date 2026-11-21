"""
Procedural Mesopithecus pentelicus (Late Miocene of Europe and western Asia)
for map colonies: an early leaf-eating colobine monkey.

A macaque-sized monkey that lived both in trees and on open ground, with a
short-faced round head, slender limbs and a long tail. Grey fur, paler below,
with a dark face and darker hands and feet.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mesopithecus_pentelicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MesopithecusPentelicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="MesopithecusPentelicus",
    leg_f=0.34, leg_h=0.38, length=0.42, girth=(0.11, 0.13),
    leg_r=(0.035, 0.042), leg_taper=0.7, foot="plantigrade", stride=0.13,
    neck_len=0.08, neck_angle=30, neck_r=(0.08, 0.07),
    head_len=0.17, head_r=(0.08, 0.08), snout_r=(0.045, 0.04), head_pitch=8, cranium=1.2,
    eye_t=0.50, eye_u=0.30,
    ears="round", ear_size=0.03,
    tail_len=0.60, tail_r=0.022, tail_droop=0.35,
    coat=(0.52, 0.52, 0.50), dark=(0.32, 0.32, 0.31), pale=(0.82, 0.80, 0.76),
    leg_col=(0.20, 0.19, 0.18),
    pattern=q.combine(q.face((0.18, 0.16, 0.15), t0=0.55, amount=0.9), q.lower_legs((0.22, 0.21, 0.20), z1=0.35)),
    shag=0.006, voxel=0.010, max_tris=8000,
)

if __name__ == "__main__":
    q.main(SPEC)
