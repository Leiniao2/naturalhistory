"""
Procedural Urtinotherium incisivum (Inner Mongolia and northern China, late Eocene to early
Oligocene, ~37-30 Ma) for map colonies. Built with nh_pal_quad.py.

One of the earliest giant indricotheres, a hornless rhinoceros close to
Paraceratherium in size: very long, pillar-like legs, a long neck for browsing
high branches and a fairly small head that still kept a full set of front teeth
(incisors and canines). Skin: warm grey-brown with a paler belly, nearly hairless
(unknown). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/urtinotherium_incisivum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/UrtinotheriumIncisivum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="UrtinotheriumIncisivum",
    length=1.1, shoulder=1.38, hip=1.24, width=0.3, depth=0.37, hump=0.06, belly=1.1,
    fore_r=0.1, hind_r=0.12, shin=0.74, foot="pad", foot_r=0.095, hock=0.15, stride=0.11,
    neck_len=0.52, neck_angle=30, neck_r=0.18,
    head_len=0.46, head_w=0.34, head_h=0.36, snout=0.85, snout_r=(0.3, 0.23), snout_tilt=28, jaw=0.8, jaw_r=0.2,
    ear=0.26, ear_angle=30, eye=0.05, eye_pos=(0.3, -0.25, 0.1),
    tail_len=0.4, tail_r=0.04, tail_angle=-70, tail_tuft=0.04,
    coat=(0.55, 0.45, 0.36), back=(0.43, 0.35, 0.28), pale=(0.68, 0.60, 0.50), pale_amt=0.6, skin=0.6, fur=0.3,
    dark_legs=0.25, voxel=0.016, max_tris=15000, ground=(0.54, 0.50, 0.34),
)


if __name__ == "__main__":
    q.main(SPEC)
