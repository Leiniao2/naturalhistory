"""
Procedural thylacine or Tasmanian tiger (Thylacinus cynocephalus, Pleistocene
to 1936; Australia, New Guinea and Tasmania) for map colonies.

The largest recent marsupial predator, about 1-1.3 m long plus a 50 cm tail: a
dog-like head that could gape very wide, rounded upright ears, a long body on
fairly short legs and a stiff, thick-based tail tapering like a kangaroo's.
Short sandy-brown fur with 13-21 dark stripes across the back and rump.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thylacinus_cynocephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThylacinusCynocephalus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_neo_quad as q  # noqa: E402


def nose(mb, L, surf, size=0.022, col=(0.05, 0.04, 0.04)):
    """Dark nose pad at the tip of the muzzle."""
    p, _n = surf.hit(L.h(0.8, 0, 0.02), L.F)
    mb.add(nh.ellipsoid(tuple(p), (size, size * 0.72, size * 0.72), subdivisions=2), col)


SPEC = q.Spec(
    name="ThylacinusCynocephalus",
    leg_f=0.38, leg_h=0.40, length=0.78, girth=(0.13, 0.17), belly=0.85,
    leg_r=(0.045, 0.055), leg_taper=0.6, foot="paw", stride=0.13,
    neck_len=0.20, neck_angle=22, neck_r=(0.12, 0.11),
    head_len=0.28, head_r=(0.10, 0.09), snout_r=(0.032, 0.036), head_pitch=10, cranium=1.1,
    eye_t=0.40, eye_u=0.40,
    ears="round", ear_size=0.10,
    tail_len=0.55, tail_r=0.08, tail_droop=0.35,
    coat=(0.70, 0.56, 0.38), dark=(0.48, 0.37, 0.24), pale=(0.86, 0.80, 0.66),
    pattern=q.back_stripes((0.16, 0.11, 0.07), freq=11.0, amount=0.9, y0=0.25, y1=1.4),
    extra_details=nose,
    shag=0.004, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
