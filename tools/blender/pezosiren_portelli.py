"""
Procedural Pezosiren portelli (middle Eocene, ~50 Ma, Jamaica) for map colonies.
Built with nh_pal_quad.py.

The 'walking sea cow': an early sirenian about 2.1 m long that still had four short,
sturdy legs able to carry it on land, with a heavy barrel body of dense bone like a
small hippo, a thick tail and the down-turned, fleshy snout of a manatee for grazing
sea grass in shallow coastal water. Skin: grey-brown, wrinkled (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pezosiren_portelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PezosirenPortelli.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="PezosirenPortelli",
    length=1.1, shoulder=0.64, hip=0.64, width=0.23, depth=0.21, belly=1.1,
    fore_r=0.07, hind_r=0.075, shin=0.8, foot="pad", foot_r=0.06, hock=0.0, stride=0.08,
    neck_len=0.14, neck_angle=5, neck_r=0.15,
    head_len=0.32, head_w=0.40, head_h=0.38, snout=0.5, snout_r=(0.36, 0.34), snout_tilt=50,
    head_tilt=5, jaw=0.5, jaw_r=0.18,
    ear=0.0, eye=0.045, eye_pos=(0.30, -0.22, 0.18), nose_col=(0.22, 0.20, 0.18),
    tail_len=0.6, tail_r=0.12, tail_angle=-18, tail_bush=0.3,
    coat=(0.42, 0.40, 0.37), back=(0.32, 0.31, 0.29), pale=(0.58, 0.55, 0.50), pale_amt=0.6,
    skin=0.8, fur=0.2, voxel=0.014, max_tris=12000, ground=(0.55, 0.52, 0.40),
)

if __name__ == "__main__":
    q.main(SPEC)
