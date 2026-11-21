"""
Procedural Palaeolagus haydeni (North American plains, late Eocene - Oligocene, ~35-30 Ma) for map colonies. Built with nh_pal_quad.py.

An early rabbit about 25 cm long, one of the commonest fossils of the Badlands. Compared
with living rabbits its hind legs were shorter, so it probably scurried more than it leapt,
and its ears were somewhat shorter; it already had the typical rabbit teeth for grinding
grass and leaves. Coat: grey-brown agouti with a pale belly and white scut (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/palaeolagus_haydeni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeolagusHaydeni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

SPEC = q.Spec(
    name="PalaeolagusHaydeni",
    length=0.36, shoulder=0.27, hip=0.33, width=0.09, depth=0.1, belly=1.1, arch=0.03,
    fore_r=0.022, hind_r=0.045, shin=0.55, foot="paw", foot_r=0.025, toes=4, hock=0.7, stride=0.05,
    neck_len=0.07, neck_angle=40, neck_r=0.06,
    head_len=0.15, head_w=0.38, head_h=0.38, snout=0.5, snout_r=(0.3, 0.2), snout_tilt=25, jaw=0.6, jaw_r=0.18,
    ear=0.75, ear_angle=12, eye=0.1, eye_pos=(0.32, -0.15, 0.15), nose_col=(0.35, 0.22, 0.22),
    tail_len=0.06, tail_r=0.035, tail_angle=30, tail_tuft=0.035,
    coat=(0.50, 0.42, 0.32), back=(0.38, 0.32, 0.25), pale=(0.88, 0.84, 0.76), pale_amt=0.85,
    voxel=0.005, max_tris=8000, ground=(0.45, 0.45, 0.32),
)

if __name__ == "__main__":
    q.main(SPEC)
