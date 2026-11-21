"""
Procedural Hoplitomeryx matthei (Late Miocene island of Gargano, Italy) for map
colonies: the "prongdeer", a small island ruminant.

A roe-deer-sized ruminant with five horns - one long horn up the middle of the
nose and a pair of horns above each eye - and long sabre-like upper canines
like a musk deer. Russet brown coat, pale belly.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hoplitomeryx_matthei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HoplitomeryxMatthei.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="HoplitomeryxMatthei",
    leg_f=0.56, leg_h=0.60, length=0.62, girth=(0.14, 0.18),
    leg_r=(0.040, 0.050), leg_taper=0.5, foot="hoof", stride=0.12,
    neck_len=0.32, neck_angle=45, neck_r=(0.10, 0.07),
    head_len=0.34, head_r=(0.075, 0.08), snout_r=(0.04, 0.045), head_pitch=45,
    ears="point", ear_size=0.08,
    tail_len=0.10, tail_r=0.025, tail_droop=0.8,
    horns=[dict(t=0.42, s=0, u=0.2, len=0.22, r=0.020, dir=(0, 0.2, 1), bend=(0, 0.2, 0), tip=0.006,
                color=(0.28, 0.22, 0.17))]
          + [dict(t=0.25, s=sx * 0.10, u=0.22, len=0.13, r=0.016, dir=(sx * 0.5, 0.4, 1), tip=0.005,
                  color=(0.28, 0.22, 0.17)) for sx in (-1, 1)]
          + [dict(t=0.16, s=sx * 0.12, u=0.15, len=0.10, r=0.014, dir=(sx * 0.9, 0.5, 0.6), tip=0.005,
                  color=(0.28, 0.22, 0.17)) for sx in (-1, 1)],
    tusks=[dict(t=0.80, s=sx * 0.05, u=-0.14, dir=(0, 0.25, -1), len=0.10, r=0.010, tip=0.003, bend=(0, 0.3, 0))
           for sx in (-1, 1)],
    coat=(0.55, 0.34, 0.20), dark=(0.36, 0.22, 0.13), pale=(0.88, 0.80, 0.68),
    shag=0.002, voxel=0.013,
)

if __name__ == "__main__":
    q.main(SPEC)
