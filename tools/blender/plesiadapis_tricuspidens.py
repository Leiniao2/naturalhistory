"""
Procedural Plesiadapis tricuspidens (Europe, late Paleocene, ~58-56 Ma) for map colonies. Built with nh_pal_quad.py.

A plesiadapiform, a close relative of the primates that looked more like a
squirrel: about 60 cm long with a long bushy tail, claws rather than nails, eyes on
the sides of a long head and big, rodent-like front incisors separated from the
cheek teeth by a gap. It climbed trees and fed on leaves and fruit. Coat:
grey-brown with a pale belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/plesiadapis_tricuspidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlesiadapisTricuspidens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="PlesiadapisTricuspidens",
    length=0.48, shoulder=0.34, hip=0.4, width=0.1, depth=0.11, arch=0.02,
    fore_r=0.034, hind_r=0.05, shin=0.6, foot="paw", foot_r=0.032, toes=5, hock=0.3, stride=0.06,
    neck_len=0.1, neck_angle=30, neck_r=0.07,
    head_len=0.2, head_w=0.4, head_h=0.4, snout=0.7, snout_r=(0.26, 0.14), snout_tilt=15, jaw=0.8, jaw_r=0.16,
    ear=0.2, ear_shape="round", eye=0.09, eye_pos=(0.34, -0.25, 0.12), nose_col=(0.2, 0.13, 0.12),
    tail_len=0.7, tail_r=0.05, tail_bush=0.85, tail_angle=40, tail_curl=-60,
    horns=[Horn(base=(0.03, -1.0, -0.12), direction=(0, -0.6, -1), length=0.1, radius=0.025,
                color=(0.85, 0.72, 0.45))],
    coat=(0.47, 0.42, 0.36), back=(0.35, 0.31, 0.27), pale=(0.85, 0.82, 0.75), pale_amt=0.9,
    voxel=0.0085, max_tris=10000, ground=(0.32, 0.40, 0.24),
)


if __name__ == "__main__":
    q.main(SPEC)
