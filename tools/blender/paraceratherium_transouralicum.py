"""
Procedural Paraceratherium transouralicum (Central Asia, Oligocene, ~34-23 Ma) for map colonies. Built with nh_pal_quad.py.

A hornless rhinoceros and one of the largest land mammals ever, about 4.8 m
at the shoulder and 15-20 tonnes. Long, pillar-like three-toed legs and a long
neck let it browse treetops like a giraffe; the small head had a mobile upper lip
and downward-pointing tusk-like incisors. Skin: grey, nearly hairless.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/paraceratherium_transouralicum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ParaceratheriumTransouralicum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="ParaceratheriumTransouralicum",
    length=1.05, shoulder=1.45, hip=1.32, width=0.29, depth=0.36, hump=0.04, belly=1.05,
    fore_r=0.1, hind_r=0.12, shin=0.72, foot="pad", foot_r=0.095, hock=0.15, stride=0.1,
    neck_len=0.6, neck_angle=36, neck_r=0.17,
    head_len=0.46, head_w=0.34, head_h=0.38, snout=0.8, snout_r=(0.3, 0.24), snout_tilt=30, jaw=0.75, jaw_r=0.2,
    ear=0.24, ear_angle=25, eye=0.05, eye_pos=(0.3, -0.25, 0.1),
    tail_len=0.38, tail_r=0.04, tail_angle=-72, tail_tuft=0.035,
    coat=(0.52, 0.49, 0.45), back=(0.42, 0.40, 0.37), pale=(0.62, 0.59, 0.55), pale_amt=0.5, skin=0.6, fur=0.3,
    voxel=0.016, max_tris=14000, ground=(0.52, 0.48, 0.34),
)


if __name__ == "__main__":
    q.main(SPEC)
