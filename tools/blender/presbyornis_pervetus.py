"""
Procedural Presbyornis pervetus (North America, late Paleocene to early Eocene,
~60-50 Ma) for map colonies. Built with nh_pal_bird.py.

An early relative of ducks and screamers, about the size of a goose, with a
duck-like, broad flat bill on a long neck and long, wader-like legs, so it looked
like a cross between a duck and a flamingo. It lived in large colonies around
shallow, salty lakes such as Wyoming's Green River lakes, filtering plankton
and plants with its bill. Plumage: pale grey-brown with darker wings (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/presbyornis_pervetus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PresbyornisPervetus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Spec(
    name="PresbyornisPervetus",
    body=(0.16, 0.3, 0.16), body_z=0.95, body_pitch=-5,
    neck_len=0.5, neck_r=0.045, neck_lean=20, head_r=0.065,
    beak_len=0.15, beak_h=0.05, beak_w=0.06, beak_flat=1.5,
    leg_len=0.82, leg_r=0.022, thigh_r=0.06, toe_len=0.1, web=True,
    wing=0.32, tail=0.08,
    plumage=(0.70, 0.67, 0.60), back=(0.45, 0.42, 0.38), wing_col=(0.38, 0.35, 0.31), head_col=(0.62, 0.60, 0.55),
    beak_col=(0.25, 0.24, 0.22), leg_col=(0.55, 0.45, 0.30), eye_r=0.012, shaggy=0.2,
    voxel=0.009, max_tris=10000, ground=(0.50, 0.55, 0.45),
)

if __name__ == "__main__":
    nb.main(SPEC)
