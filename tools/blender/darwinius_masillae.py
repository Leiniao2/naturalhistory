"""
Procedural Darwinius masillae (Germany (Messel), middle Eocene, ~47 Ma) for map colonies. Built with nh_pal_quad.py.

A lemur-like adapiform primate known from "Ida", a superbly preserved
skeleton with fur outline and gut contents (fruit and leaves). About 58 cm long,
over half of it tail, it had grasping hands and feet with nails, forward-facing
eyes and a short snout, and climbed in the subtropical forest. Coat: grey-brown
with a pale belly and a dark face (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/darwinius_masillae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DarwiniusMasillae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="DarwiniusMasillae",
    length=0.5, shoulder=0.4, hip=0.45, width=0.1, depth=0.11,
    fore_r=0.034, hind_r=0.05, shin=0.6, foot="hand", foot_r=0.035, toes=4, hock=0.3, stride=0.06,
    neck_len=0.12, neck_angle=35, neck_r=0.065,
    head_len=0.17, head_w=0.5, head_h=0.45, snout=0.45, snout_r=(0.3, 0.17), snout_tilt=18, jaw=0.7, jaw_r=0.18,
    ear=0.24, ear_shape="round", eye=0.15, eye_pos=(0.28, -0.38, 0.12), nose_col=(0.08, 0.06, 0.06),
    tail_len=0.85, tail_r=0.04, tail_bush=0.4, tail_angle=25, tail_curl=-110,
    coat=(0.47, 0.41, 0.35), back=(0.36, 0.31, 0.26), pale=(0.82, 0.78, 0.70), pale_amt=0.9,
    muzzle_col=(0.15, 0.12, 0.10),
    voxel=0.0085, max_tris=10000, ground=(0.32, 0.40, 0.24),
)


if __name__ == "__main__":
    q.main(SPEC)
