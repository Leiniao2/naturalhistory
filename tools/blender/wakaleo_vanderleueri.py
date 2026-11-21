"""
Procedural Wakaleo vanderleueri (Middle Miocene of Australia) for map colonies:
a dog-sized marsupial lion, an early relative of Thylacoleo.

A stocky, short-legged climber and ambush hunter with a short, deep, cat-like
head, powerful forelimbs, a long thick tail and grey-brown fur with faint dark
bands over the rump.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/wakaleo_vanderleueri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WakaleoVanderleueri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="WakaleoVanderleueri",
    leg_f=0.34, leg_h=0.36, length=0.70, girth=(0.17, 0.19),
    leg_r=(0.066, 0.058), leg_taper=0.65, foot="paw", foot_r=1.15, stride=0.11,
    neck_len=0.18, neck_angle=20, neck_r=(0.14, 0.11),
    head_len=0.30, head_r=(0.11, 0.11), snout_r=(0.07, 0.07), head_pitch=10,
    ears="round", ear_size=0.07,
    tail_len=0.62, tail_r=0.05, tail_droop=0.5,
    coat=(0.50, 0.44, 0.36), dark=(0.30, 0.26, 0.21), pale=(0.78, 0.72, 0.62),
    pattern=q.back_stripes((0.20, 0.16, 0.12), freq=8.0, amount=0.7, y0=0.2, y1=1.0),
    shag=0.005, voxel=0.015,
)

if __name__ == "__main__":
    q.main(SPEC)
