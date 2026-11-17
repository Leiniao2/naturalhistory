"""
Procedural Protungulatum donnae (Montana, earliest Paleocene, ~66 Ma) for map colonies. Built with nh_pal_quad.py.

One of the earliest undoubted placental mammals, found within a few hundred thousand years of
the asteroid impact: a generalised, rat-sized animal (25-30 cm) with low-crowned, blunt-cusped
teeth for insects, fruit and seeds, long thought to be near the ancestry of the hoofed
mammals. Drawn low-slung on short legs with small clawed feet, a long body, a medium snout,
small round ears and a long, thinly haired tail. Coat: warm brown, paler below (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/protungulatum_donnae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protungulatum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="Protungulatum",
    length=0.55, shoulder=0.28, hip=0.31, width=0.11, depth=0.11, arch=0.03, belly=1.08,
    fore_r=0.035, hind_r=0.05, shin=0.62, foot="paw", foot_r=0.032, toes=5, hock=0.25, stride=0.06,
    neck_len=0.08, neck_angle=22, neck_r=0.075,
    head_len=0.21, head_w=0.4, head_h=0.38, snout=0.72, snout_r=(0.26, 0.12), snout_tilt=16, jaw=0.85, jaw_r=0.15,
    ear=0.15, ear_shape="round", eye=0.075, eye_pos=(0.32, -0.28, 0.14), nose_col=(0.25, 0.17, 0.15),
    tail_len=0.75, tail_r=0.04, tail_angle=-10, tail_curl=25,
    coat=(0.48, 0.36, 0.24), back=(0.34, 0.25, 0.17), pale=(0.80, 0.72, 0.58), pale_amt=0.8,
    voxel=0.0095, max_tris=10000, ground=(0.36, 0.38, 0.24),
)


if __name__ == "__main__":
    q.main(SPEC)
