"""
Procedural Kubanochoerus gigas (Middle Miocene of Eurasia) for map colonies:
a giant, long-legged forest pig.

A pig the size of a small horse, with long legs, a long head and snout, big
outward-flaring tusks and, in males, a single horn on the forehead used in
head-butting fights. Bristly dark brown coat with a mane along the back.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kubanochoerus_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KubanochoerusGigas.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="KubanochoerusGigas",
    leg_f=0.60, leg_h=0.60, length=0.90, girth=(0.22, 0.28), belly=1.05,
    hump=0.10, hump_y=-0.35,
    leg_r=(0.055, 0.065), leg_taper=0.55, foot="hoof", stride=0.12,
    neck_len=0.16, neck_angle=15, neck_r=(0.20, 0.18),
    head_len=0.58, head_r=(0.13, 0.16), snout_r=(0.06, 0.07), head_pitch=30,
    ears="point", ear_size=0.09,
    tail_len=0.22, tail_r=0.02, tail_tuft=0.025, tail_droop=0.9,
    mane=0.05,
    horns=[dict(t=0.30, s=0, u=0.30, len=0.20, r=0.040, dir=(0, -0.7, 1), tip=0.014, color=(0.62, 0.56, 0.46))],
    tusks=[dict(t=0.85, s=sx * 0.08, u=-0.04, dir=(sx * 1.0, 0.1, 0.5), len=0.17, r=0.022, tip=0.005, bend=(0, 0.3, 0.4))
           for sx in (-1, 1)],
    coat=(0.46, 0.36, 0.27), dark=(0.28, 0.21, 0.16), pale=(0.66, 0.57, 0.46), mane_col=(0.18, 0.14, 0.11),
    skin=(0.40, 0.32, 0.28),
    shag=0.012, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
