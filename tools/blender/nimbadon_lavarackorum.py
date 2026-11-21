"""
Procedural Nimbadon lavarackorum (Middle Miocene of Riversleigh, Australia) for
map colonies: a sheep-sized, tree-climbing diprotodontid, a distant relative of
wombats and koalas.

A heavy, round-bodied marsupial with a big, short-snouted head, small round
ears, strong curved claws for climbing, almost no tail and thick brown fur.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/nimbadon_lavarackorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NimbadonLavarackorum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="NimbadonLavarackorum",
    leg_f=0.30, leg_h=0.30, length=0.66, girth=(0.24, 0.25), belly=1.08,
    hump=0.06, hump_y=0.1,
    leg_r=(0.075, 0.075), leg_taper=0.7, foot="plantigrade", foot_r=1.2, stride=0.09,
    neck_len=0.12, neck_angle=15, neck_r=(0.20, 0.17),
    head_len=0.36, head_r=(0.15, 0.15), snout_r=(0.09, 0.09), head_pitch=25, cranium=1.1,
    eye_t=0.40, eye_u=0.35,
    ears="round", ear_size=0.08,
    tail_len=0.08, tail_r=0.04, tail_droop=0.9,
    coat=(0.42, 0.32, 0.22), dark=(0.26, 0.19, 0.13), pale=(0.64, 0.54, 0.42),
    pattern=q.face((0.24, 0.20, 0.17), t0=0.75, amount=0.8),
    shag=0.010, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
