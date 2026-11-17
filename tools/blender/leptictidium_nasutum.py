"""
Procedural Leptictidium nasutum (Europe (Messel, Germany), middle Eocene, ~47 Ma) for map colonies. Built with nh_pal_quad.py.

A small leptictid insectivore 60-90 cm long including a tail longer than its
body. Its hind legs were much longer than its forelegs, so it probably ran or hopped
on two legs through the forest floor, balancing with the stiff tail, and it probed
for insects and small animals with a long, mobile snout. Coat: brown with a pale
belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/leptictidium_nasutum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LeptictidiumNasutum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="LeptictidiumNasutum",
    length=0.42, shoulder=0.44, hip=0.52, width=0.09, depth=0.11, biped=True,
    fore_r=0.028, hind_r=0.06, shin=0.45, foot="hand", foot_r=0.038, toes=4, hock=0.95, stride=0.05,
    neck_len=0.14, neck_angle=35, neck_r=0.06,
    head_len=0.17, head_w=0.4, head_h=0.4, snout=1.5, snout_r=(0.2, 0.08), snout_tilt=12, jaw=0.7, jaw_r=0.14,
    ear=0.35, ear_shape="round", eye=0.1, eye_pos=(0.3, -0.25, 0.12), nose_col=(0.25, 0.15, 0.14),
    tail_len=0.95, tail_r=0.035, tail_angle=-5, tail_curl=8,
    coat=(0.52, 0.40, 0.28), back=(0.36, 0.27, 0.18), pale=(0.85, 0.78, 0.64), pale_amt=0.9,
    voxel=0.0085, max_tris=10000, ground=(0.32, 0.40, 0.24),
)


if __name__ == "__main__":
    q.main(SPEC)
