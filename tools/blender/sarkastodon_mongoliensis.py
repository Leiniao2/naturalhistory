"""
Procedural Sarkastodon mongoliensis (Inner Mongolia, late Eocene, ~40-35 Ma) for map colonies. Built with nh_pal_quad.py.

A giant oxyaenid ("creodont"), bear-sized and bear-shaped: a heavy, deep body on
short, stout, plantigrade legs with broad five-toed paws, a short neck and a huge,
broad head with a short muzzle, deep jaws, big canines and blunt, bone-crushing
cheek teeth. Short tail. Coat: dark brown with a paler muzzle (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sarkastodon_mongoliensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SarkastodonMongoliensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402

FANG = (0.90, 0.86, 0.74)

SPEC = q.Spec(
    name="SarkastodonMongoliensis",
    length=0.86, shoulder=0.74, hip=0.70, width=0.21, depth=0.25, belly=1.05, hump=0.04,
    fore_r=0.08, hind_r=0.085, shin=0.72, foot="paw", foot_r=0.07, toes=5, hock=0.12, stride=0.08,
    neck_len=0.2, neck_angle=18, neck_r=0.14,
    head_len=0.44, head_w=0.44, head_h=0.38, snout=0.55, snout_r=(0.33, 0.24), snout_tilt=10, head_tilt=4,
    jaw=0.9, jaw_r=0.24, ear=0.14, ear_shape="round", eye=0.05, eye_pos=(0.32, -0.2, 0.14),
    nose_col=(0.05, 0.04, 0.04), muzzle_col=(0.45, 0.36, 0.27),
    tail_len=0.34, tail_r=0.05, tail_angle=-45, tail_curl=10,
    horns=[Horn(base=(0.13, -0.85, -0.2), direction=(0.05, -0.15, -1), length=0.16, radius=0.035, color=FANG),
           Horn(base=(0.1, -0.8, -0.38), direction=(0.05, -0.2, 1), length=0.1, radius=0.03, color=FANG)],
    coat=(0.30, 0.23, 0.17), back=(0.18, 0.14, 0.10), pale=(0.46, 0.38, 0.29), pale_amt=0.6, dark_legs=0.5,
    voxel=0.013, max_tris=14000, ground=(0.50, 0.46, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
