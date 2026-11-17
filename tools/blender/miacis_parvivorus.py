"""
Procedural Miacis parvivorus (a miacid, North America, middle Eocene, ~48-40 Ma) for map
colonies. Built with nh_pal_quad.py.

Miacids were small, tree-climbing meat-eaters near the root of the carnivorans: a long,
low, genet-like body about 30 cm long, short legs with five clawed toes and flexible
ankles for climbing, a long bushy tail about as long as the body, a pointed face and
small rounded ears. Coat: warm grey-brown with darker rings on the tail and a pale throat
(the real colour is unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/miacis_parvivorus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MiacisParvivorus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="MiacisParvivorus",
    length=0.62, shoulder=0.34, hip=0.36, width=0.095, depth=0.1,
    fore_r=0.032, hind_r=0.042, shin=0.6, foot="paw", foot_r=0.032, toes=5, hock=0.3, stride=0.07,
    neck_len=0.15, neck_angle=25, neck_r=0.06,
    head_len=0.2, head_w=0.36, head_h=0.34, snout=0.85, snout_r=(0.24, 0.12), snout_tilt=10, jaw=0.85, jaw_r=0.14,
    ear=0.2, ear_shape="round", ear_angle=20, eye=0.08, eye_pos=(0.3, -0.28, 0.14), nose_col=(0.1, 0.08, 0.07),
    tail_len=0.72, tail_r=0.045, tail_bush=0.8, tail_angle=-12, tail_curl=-20,
    coat=(0.50, 0.42, 0.33), back=(0.34, 0.28, 0.22), pale=(0.82, 0.76, 0.66), pale_amt=0.85,
    stripes=0, dark_legs=0.3,
    voxel=0.008, max_tris=11000, ground=(0.32, 0.40, 0.24),
)

if __name__ == "__main__":
    q.main(SPEC)
