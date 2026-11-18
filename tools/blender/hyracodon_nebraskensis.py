"""
Procedural Hyracodon nebraskensis (North America, late Eocene to Oligocene, ~35-30 Ma) for map colonies. Built with nh_pal_quad.py.

A "running rhinoceros", hornless and pony-sized (about 1.5 m long): slim,
long legs with three-toed hooved feet built for speed on open plains, a fairly
long neck, a big, deep head, small ears and a short tail. Coat: tawny brown with
a darker back and pale belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hyracodon_nebraskensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HyracodonNebraskensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="HyracodonNebraskensis",
    length=0.8, shoulder=0.8, hip=0.82, width=0.14, depth=0.18,
    fore_r=0.052, hind_r=0.068, shin=0.5, foot="hoof", foot_r=0.032, hock=0.75, stride=0.12,
    neck_len=0.3, neck_angle=42, neck_r=0.1,
    head_len=0.32, head_w=0.36, head_h=0.40, snout=0.8, snout_r=(0.31, 0.22), snout_tilt=32, jaw=0.85, jaw_r=0.22,
    ear=0.22, ear_angle=18, eye=0.06, eye_pos=(0.3, -0.15, 0.15), nose_col=(0.14, 0.11, 0.09),
    tail_len=0.3, tail_r=0.035, tail_angle=-62, tail_tuft=0.035,
    coat=(0.60, 0.47, 0.32), back=(0.42, 0.32, 0.22), pale=(0.86, 0.79, 0.66), dark_legs=0.45,
    mask=(0.30, 0.23, 0.17), voxel=0.011, max_tris=12000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
