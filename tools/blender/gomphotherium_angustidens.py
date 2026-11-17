"""
Procedural Gomphotherium angustidens (Middle Miocene of Europe) for map colonies.

An elephant-sized "four-tusker": two long upper tusks that curve down and then
forward and up, and two shorter, straight lower tusks projecting forward from a
long lower jaw. A long, low body on pillar legs, a domed head, a trunk resting
on the lower jaw and a short tail. Grey skin. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gomphotherium_angustidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GomphotheriumAngustidens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="GomphotheriumAngustidens",
    leg_f=0.78, leg_h=0.70, length=0.85, girth=(0.33, 0.38), belly=1.05,
    leg_r=(0.10, 0.105), foot="pillar", stride=0.10,
    neck_len=0.10, neck_angle=10, neck_r=(0.30, 0.25),
    head_len=0.50, head_r=(0.22, 0.24), snout_r=(0.11, 0.10), head_pitch=42, jaw=0.9, cranium=1.08,
    ears="flap", ear_size=0.24,
    tail_len=0.42, tail_r=0.035, tail_tuft=0.035, tail_droop=0.95,
    shovel=0.26, shovel_teeth="tusks",
    trunk_len=0.62, trunk_r=0.09, trunk_curl=0.35,
    tusks=[dict(t=0.80, s=sx * 0.12, u=-0.30, dir=(sx * 0.15, -0.35, -1.0), len=0.62, r=0.045, bend=(sx * 0.1, -1.0, 1.9), tip=0.012)
           for sx in (-1, 1)],
    coat=(0.46, 0.44, 0.41), dark=(0.32, 0.31, 0.29), pale=(0.58, 0.56, 0.52), countershade=0.5,
    voxel=0.022, max_tris=12000,
)

if __name__ == "__main__":
    q.main(SPEC)
