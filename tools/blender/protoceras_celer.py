"""
Procedural Protoceras celer (South Dakota and Nebraska, early Oligocene, ~33-30 Ma) for map colonies. Built with nh_pal_quad.py.

A protoceratid, a deer-sized (about 1 m long) even-toed hoofed mammal related to camels.
Males carried three pairs of skin-covered bony knobs: a pair of tall plates on the tip of the
snout, a pair above the eyes and a pair at the back of the skull, plus short tusk-like
upper canines; females were hornless. Slender legs with two-toed hooves. Coat: fawn with a
pale belly (unknown). This model is a male.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/protoceras_celer.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtocerasCeler.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

BONE = (0.46, 0.36, 0.26)

SPEC = q.Spec(
    name="ProtocerasCeler",
    length=0.6, shoulder=0.62, hip=0.66, width=0.11, depth=0.14,
    fore_r=0.035, hind_r=0.05, shin=0.5, foot="hoof", foot_r=0.025, hock=0.75, stride=0.08,
    neck_len=0.28, neck_angle=45, neck_r=0.07,
    head_len=0.25, head_w=0.34, head_h=0.36, snout=0.85, snout_r=(0.26, 0.15), snout_tilt=25, jaw=0.85, jaw_r=0.15,
    ear=0.26, ear_angle=35, eye=0.075, eye_pos=(0.3, -0.18, 0.14), nose_col=(0.12, 0.09, 0.08),
    tail_len=0.18, tail_r=0.03, tail_angle=-50,
    horns=[
        # snout-tip plates
        Horn(base=(0.07, -0.9, -0.2), direction=(0.25, -0.2, 1), length=0.38, radius=0.055, flat=0.6, tip=0.6,
             fuse=True, color=BONE),
        # brow knobs
        Horn(base=(0.24, -0.22, 0.3), direction=(0.6, 0.1, 1), length=0.2, radius=0.06, tip=0.75, fuse=True, color=BONE),
        # rear-skull horns
        Horn(base=(0.18, 0.2, 0.32), direction=(0.5, 0.5, 1), length=0.3, radius=0.06, tip=0.6, fuse=True, color=BONE),
        # tusk-like canines
        Horn(base=(0.11, -0.72, -0.4), direction=(0.05, -0.15, -1), length=0.15, radius=0.03, color=(0.9, 0.86, 0.75)),
    ],
    coat=(0.62, 0.48, 0.32), back=(0.48, 0.36, 0.24), pale=(0.88, 0.82, 0.70), pale_amt=0.85, dark_legs=0.3,
    voxel=0.009, max_tris=12000, ground=(0.45, 0.45, 0.32),
)

if __name__ == "__main__":
    q.main(SPEC)
