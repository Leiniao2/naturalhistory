"""
Procedural Merycoidodon culbertsoni (North American plains, early Oligocene, ~33-30 Ma) for map colonies. Built with nh_pal_quad.py.

An oreodont, one of the commonest large mammals of the Oligocene Badlands: a sheep- to
pig-sized (about 1.4 m long) even-toed hoofed plant-eater with no living descendants. Stocky
barrel body on short legs with four-toed hooved feet, a long tail, and a short-faced,
deep head with small tusk-like canines. Herds grazed and browsed the open woodlands. Coat:
brown with a darker back (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/merycoidodon_culbertsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MerycoidodonCulbertsoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

SPEC = q.Spec(
    name="MerycoidodonCulbertsoni",
    length=0.78, shoulder=0.5, hip=0.53, width=0.15, depth=0.17, belly=1.12,
    fore_r=0.045, hind_r=0.055, shin=0.65, foot="hoof", foot_r=0.035, hock=0.45, stride=0.07,
    neck_len=0.17, neck_angle=30, neck_r=0.09,
    head_len=0.27, head_w=0.4, head_h=0.42, snout=0.5, snout_r=(0.3, 0.2), snout_tilt=25, jaw=0.8, jaw_r=0.2,
    ear=0.22, ear_angle=35, eye=0.065, eye_pos=(0.34, -0.22, 0.14), nose_col=(0.12, 0.09, 0.08),
    tail_len=0.42, tail_r=0.04, tail_angle=-55, tail_curl=-10,
    horns=[Horn(base=(0.12, -0.55, -0.32), direction=(0.05, -0.1, -1), length=0.12, radius=0.03, color=(0.9, 0.86, 0.75))],
    coat=(0.50, 0.38, 0.26), back=(0.34, 0.25, 0.17), pale=(0.78, 0.70, 0.56), pale_amt=0.75, dark_legs=0.4,
    voxel=0.011, max_tris=12000, ground=(0.45, 0.45, 0.32),
)

if __name__ == "__main__":
    q.main(SPEC)
