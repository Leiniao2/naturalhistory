"""
Procedural Elasmotherium sibiricum (Pleistocene of the Eurasian steppe) for map
colonies: the "Siberian unicorn".

A giant rhinoceros, about 2 m at the shoulder and up to 4 t, with a tall
shoulder hump, comparatively long legs for a rhino, a long head carried low and
a huge dome on the forehead that is reconstructed bearing a single long horn.
Shaggy brown coat for the cold steppe. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/elasmotherium_sibiricum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ElasmotheriumSibiricum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ElasmotheriumSibiricum",
    leg_f=0.62, leg_h=0.58, length=0.95, girth=(0.30, 0.34), belly=1.05,
    hump=0.55, hump_y=-0.38,
    leg_r=(0.085, 0.09), leg_taper=0.65, foot="pillar", stride=0.12,
    neck_len=0.18, neck_angle=0, neck_r=(0.26, 0.20),
    head_len=0.62, head_r=(0.14, 0.16), snout_r=(0.08, 0.09), head_pitch=32, cranium=1.1,
    ears="point", ear_size=0.10,
    tail_len=0.30, tail_r=0.03, tail_tuft=0.05, tail_droop=0.95,
    horns=[dict(t=0.42, u=0.28, len=0.75, r=0.07, dir=(0, -0.35, 1), bend=(0, 0.7, 0), tip=0.004)],
    mane=0.07, beard=0.10,
    coat=(0.45, 0.33, 0.22), dark=(0.28, 0.20, 0.13), pale=(0.62, 0.52, 0.40),
    mane_col=(0.32, 0.23, 0.15), shag=0.018, voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
