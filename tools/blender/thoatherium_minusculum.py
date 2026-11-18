"""
Procedural Thoatherium minusculum (Early-Middle Miocene of Patagonia) for map
colonies: a small proterotheriid litoptern, a South American hoofed mammal that
evolved a single-toed, horse-like foot even more reduced than a modern horse's.

A small, lightly built, gazelle-sized runner (about 70 cm long): very long,
slender legs ending in single small hooves, a short, compact body, a moderately
long neck and a short, horse-like head with large eyes and pointed ears, and a
short tail. Warm sandy-brown with a pale belly and throat. Built with
nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thoatherium_minusculum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThoatheriumMinusculum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ThoatheriumMinusculum",
    leg_f=0.66, leg_h=0.70, length=0.66, girth=(0.15, 0.19),
    leg_r=(0.046, 0.054), leg_taper=0.6, foot="hoof", foot_r=0.9, stride=0.16,
    neck_len=0.40, neck_angle=48, neck_r=(0.10, 0.065),
    head_len=0.36, head_r=(0.07, 0.085), snout_r=(0.04, 0.045), head_pitch=55, eye_t=0.33,
    ears="point", ear_size=0.085,
    tail_len=0.18, tail_r=0.025, tail_droop=0.8,
    coat=(0.62, 0.46, 0.28), dark=(0.38, 0.27, 0.16), pale=(0.88, 0.80, 0.66),
    shag=0.003, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
