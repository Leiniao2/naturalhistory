"""
Procedural Phenacodus primaevus (a condylarth, North America, late Paleocene to early
Eocene, ~57-50 Ma) for map colonies. Built with nh_pal_quad.py.

Phenacodus is one of the best-known early hoofed mammals and stands near the ancestry of
the later ungulates: sheep-sized, about 1.5 m long, with a long low body, a long heavy
tail, fairly short legs ending in five toes tipped with small hooves (the middle one the
biggest), a short neck and a smallish head with a short face. Coat: olive brown with a
darker back and a pale belly (the real colour is unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/phenacodus_primaevus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhenacodusPrimaevus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="PhenacodusPrimaevus",
    length=0.86, shoulder=0.56, hip=0.6, width=0.14, depth=0.16, belly=1.05, arch=0.02,
    fore_r=0.05, hind_r=0.066, shin=0.6, foot="hoof", foot_r=0.038, toes=5, hock=0.55, stride=0.08,
    neck_len=0.2, neck_angle=30, neck_r=0.085,
    head_len=0.26, head_w=0.38, head_h=0.4, snout=0.7, snout_r=(0.28, 0.18), snout_tilt=22, jaw=0.8, jaw_r=0.2,
    ear=0.2, ear_shape="point", ear_angle=18, eye=0.07, eye_pos=(0.3, -0.25, 0.15), nose_col=(0.14, 0.1, 0.08),
    tail_len=0.85, tail_r=0.075, tail_bush=0.45, tail_angle=-20, tail_curl=-10,
    coat=(0.45, 0.39, 0.27), back=(0.30, 0.25, 0.17), pale=(0.76, 0.70, 0.55), pale_amt=0.8,
    voxel=0.011, max_tris=12000, ground=(0.40, 0.44, 0.28),
)

if __name__ == "__main__":
    q.main(SPEC)
