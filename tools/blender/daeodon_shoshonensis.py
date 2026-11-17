"""
Procedural Daeodon shoshonensis (latest Oligocene - Early Miocene of North
America) for map colonies: the largest entelodont, or "hell pig".

A cow-sized, pig-like omnivore with a huge, long head nearly a metre long, its
cheekbones flaring into big bony flanges below the eyes and knobs under the
chin; a tall shoulder hump over a short back, long slender legs on two-toed
hooves and a thin tail. Dark, bristly coat. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/daeodon_shoshonensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DaeodonShoshonensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DaeodonShoshonensis",
    leg_f=0.72, leg_h=0.62, length=0.70, girth=(0.22, 0.28),
    hump=0.45, hump_y=-0.42,
    leg_r=(0.065, 0.075), leg_taper=0.55, foot="hoof", stride=0.12,
    neck_len=0.20, neck_angle=10, neck_r=(0.22, 0.17),
    head_len=0.72, head_r=(0.15, 0.17), snout_r=(0.075, 0.09), head_pitch=38, jaw=1.25,
    ears="point", ear_size=0.08,
    tail_len=0.30, tail_r=0.025, tail_tuft=0.03, tail_droop=0.9,
    mane=0.06, extra=lambda b, L: q.jowl_flanges(b, L, 0.42, 0.11, 0.08),
    coat=(0.30, 0.24, 0.19), dark=(0.16, 0.12, 0.10), pale=(0.48, 0.40, 0.32),
    mane_col=(0.14, 0.11, 0.09), shag=0.008, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
