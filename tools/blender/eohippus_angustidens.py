"""
Procedural Eohippus angustidens (the North American "dawn horse", early Eocene,
~55-50 Ma) for map colonies. Built with nh_pal_quad.py.

A fox-sized early equid about 60 cm long and 30 cm at the shoulder: an arched
back with the rump higher than the shoulders, slender legs ending in small
hoofed toes (four in front, three behind), a short neck, a small head with a
moderately long face and a long, thin hanging tail. Coat: brown with a darker
back and faint pale dapples (forest camouflage; the real colour is unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eohippus_angustidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EohippusAngustidens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="EohippusAngustidens",
    length=0.72, shoulder=0.60, hip=0.68, width=0.12, depth=0.15, belly=1.0,
    fore_r=0.042, hind_r=0.058, shin=0.55, foot="hoof", foot_r=0.03, hock=0.7, stride=0.07,
    neck_len=0.24, neck_angle=42, neck_r=0.075,
    head_len=0.24, head_w=0.38, head_h=0.42, snout=0.85, snout_r=(0.27, 0.17), snout_tilt=30, jaw=0.75, jaw_r=0.2,
    ear=0.28, ear_shape="point", ear_angle=15, eye=0.075, eye_pos=(0.3, -0.25, 0.15),
    nose_col=(0.15, 0.11, 0.09),
    tail_len=0.36, tail_r=0.03, tail_angle=-55, tail_curl=-10,
    coat=(0.46, 0.33, 0.21), back=(0.30, 0.21, 0.13), pale=(0.78, 0.68, 0.52),
    dapple=0.35, dapple_col=(0.70, 0.58, 0.40),
    voxel=0.011, max_tris=12000, ground=(0.32, 0.40, 0.24),
)

if __name__ == "__main__":
    q.main(SPEC)
