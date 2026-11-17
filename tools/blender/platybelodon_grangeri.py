"""
Procedural Platybelodon grangeri (Middle Miocene of China and Mongolia) for map
colonies: the "shovel-tusker".

A medium-sized gomphothere with a very long lower jaw ending in a broad, flat
scoop tipped by two wide, flattened lower incisors, a broad trunk resting on
the scoop, two short down-curved upper tusks, a long body on pillar legs and a
short tail. Grey-brown skin. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/platybelodon_grangeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlatybelodonGrangeri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="PlatybelodonGrangeri",
    leg_f=0.72, leg_h=0.66, length=0.90, girth=(0.33, 0.37), belly=1.08,
    leg_r=(0.10, 0.105), foot="pillar", stride=0.10,
    neck_len=0.10, neck_angle=5, neck_r=(0.30, 0.24),
    head_len=0.52, head_r=(0.21, 0.21), snout_r=(0.11, 0.09), head_pitch=28, jaw=0.9,
    ears="flap", ear_size=0.22,
    tail_len=0.40, tail_r=0.035, tail_tuft=0.035, tail_droop=0.95,
    shovel=0.55, shovel_teeth="plate",
    trunk_len=0.34, trunk_r=0.08, trunk_curl=0.7,
    tusks=[dict(t=0.82, s=sx * 0.14, u=-0.18, dir=(sx * 0.2, -0.5, -1.0), len=0.20, r=0.035, bend=(0, -0.6, 0.0))
           for sx in (-1, 1)],
    coat=(0.44, 0.40, 0.36), dark=(0.31, 0.28, 0.25), pale=(0.56, 0.52, 0.47), countershade=0.5,
    voxel=0.022, max_tris=12000,
)

if __name__ == "__main__":
    q.main(SPEC)
