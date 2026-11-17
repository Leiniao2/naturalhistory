"""
Procedural Indohyus indirae (a raoellid, Kashmir, middle Eocene, ~48 Ma) for map colonies.
Built with nh_pal_quad.py.

The closest known relative of the whales: a raccoon-sized even-toed ungulate about 40 cm
long, like a small chevrotain, with long slender legs on small hooves, a long tail, a
long, low snout and a small head. Its limb bones had a thick outer wall that weighed it
down in water, and it probably hid in streams from predators, as the African mousedeer
does. Coat: rich brown with pale streaks along the flanks (borrowed from the mousedeer;
the real colour is unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/indohyus_indirae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IndohyusIndirae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="IndohyusIndirae",
    length=0.56, shoulder=0.5, hip=0.58, width=0.09, depth=0.11, arch=0.03,
    fore_r=0.03, hind_r=0.045, shin=0.6, foot="hoof", foot_r=0.024, hock=0.65, stride=0.07,
    neck_len=0.18, neck_angle=30, neck_r=0.055,
    head_len=0.2, head_w=0.32, head_h=0.32, snout=1.05, snout_r=(0.24, 0.12), snout_tilt=14, jaw=0.9, jaw_r=0.14,
    ear=0.22, ear_shape="round", ear_angle=18, eye=0.08, eye_pos=(0.28, -0.25, 0.16), nose_col=(0.1, 0.08, 0.07),
    tail_len=0.5, tail_r=0.035, tail_angle=-40, tail_curl=-10,
    coat=(0.46, 0.32, 0.20), back=(0.30, 0.20, 0.12), pale=(0.84, 0.76, 0.62), pale_amt=0.85,
    stripes=0, dapple=0.4, dapple_col=(0.82, 0.74, 0.60),
    voxel=0.0085, max_tris=11000, ground=(0.40, 0.46, 0.30),
)

if __name__ == "__main__":
    q.main(SPEC)
