"""
Procedural Ambulocetus natans (Pakistan, early Eocene, ~49 Ma) for map colonies. Built with nh_pal_quad.py.

The "walking whale", a 3 m amphibious early whale that lived like a crocodile
in estuaries and coastal rivers. It had a long-snouted head, short limbs with huge
paddle-like hind feet for swimming, and a long powerful tail; it probably ambushed
prey from the water. Skin: dark grey-brown above, paler below (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ambulocetus_natans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmbulocetusNatans.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="AmbulocetusNatans",
    length=0.85, shoulder=0.36, hip=0.40, width=0.17, depth=0.15,
    fore_r=0.05, hind_r=0.068, shin=0.7, foot="web", foot_r=0.075, hock=0.15, stride=0.08,
    neck_len=0.22, neck_angle=8, neck_r=0.11,
    head_len=0.34, head_w=0.32, head_h=0.27, snout=1.3, snout_r=(0.23, 0.14), snout_flat=1.05, snout_tilt=0,
    jaw=0.95, jaw_r=0.16, ear=0.06, ear_shape="round", eye=0.06, eye_pos=(0.22, -0.2, 0.26), eye_up=True,
    nose_col=(0.12, 0.1, 0.09),
    tail_len=0.9, tail_r=0.09, tail_angle=-6, tail_curl=-6,
    horns=[Horn(base=(0.13, -1.1, -0.18), direction=(0.1, -0.1, -1), length=0.08, radius=0.022,
                color=(0.9, 0.86, 0.75)),
           Horn(base=(0.13, -1.45, -0.15), direction=(0.1, -0.1, -1), length=0.07, radius=0.02,
                color=(0.9, 0.86, 0.75))],
    coat=(0.33, 0.30, 0.25), back=(0.22, 0.21, 0.18), pale=(0.58, 0.53, 0.44), pale_amt=0.8, skin=0.3, fur=0.5,
    voxel=0.012, max_tris=12000, ground=(0.36, 0.42, 0.28),
)


if __name__ == "__main__":
    q.main(SPEC)
