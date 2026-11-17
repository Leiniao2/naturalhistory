"""
Procedural Teleoceras major (Miocene of North America) for map colonies.

A hippo-like rhinoceros: a long, barrel-shaped body slung low on very short,
stout legs, a big head carried low with a single small conical horn on the tip
of the nose, and a short tail. Grey-brown, sparsely haired skin. Built with
nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/teleoceras_major.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TeleocerasMajor.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="TeleocerasMajor",
    leg_f=0.30, leg_h=0.30, length=1.15, girth=(0.34, 0.33), belly=1.12,
    leg_r=(0.085, 0.09), leg_taper=0.75, foot="pillar", foot_r=1.0, stride=0.08,
    neck_len=0.14, neck_angle=5, neck_r=(0.26, 0.20),
    head_len=0.48, head_r=(0.15, 0.18), snout_r=(0.10, 0.11), head_pitch=22,
    ears="point", ear_size=0.09,
    tail_len=0.25, tail_r=0.03, tail_tuft=0.03, tail_droop=0.95,
    horns=[dict(t=0.90, u=0.18, len=0.12, r=0.045, dir=(0, -0.3, 1), bend=(0, 0.4, 0))],
    coat=(0.45, 0.41, 0.37), dark=(0.33, 0.30, 0.27), pale=(0.58, 0.54, 0.49), countershade=0.5,
    voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
