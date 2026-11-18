"""
Procedural Acinonyx pardinensis (giant cheetah, Pliocene to Middle Pleistocene of
Eurasia and Africa) for map colonies.

A cheetah built about twice as heavy as the living one (60-120 kg), nearly lion
height but still a sprinter: very long, slender legs, a deep chest and narrow
waist, a small, short-faced round head with small ears, short canines (no
sabres) and a long tail used as a rudder. Tawny coat covered in solid black
spots, pale belly, dark tail tip. Built with nh_sabretooth.py (the shared cat
rig) with the sabres cut down to ordinary canines.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/acinonyx_pardinensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AcinonyxPardinensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_sabretooth as st  # noqa: E402

SPEC = st.Spec(
    name="AcinonyxPardinensis",
    withers=0.98, croup=0.96, length=1.10, girth=0.76,
    fore=0.86, hind=0.88, paw=0.80, neck=0.80, head=0.86, head_z=0.04, muzzle=-0.02,
    sabre=0.045, sabre_depth=0.014, sabre_flat=0.6,
    tail=((0, 0.0, 0.0), (0, 0.18, -0.10), (0, 0.32, -0.30), (0, 0.40, -0.50), (0, 0.50, -0.66),
          (0, 0.62, -0.74)),
    tail_r=(0.04, 0.035, 0.032, 0.03, 0.028, 0.027),
    coat=(0.80, 0.62, 0.36), coat_dark=(0.66, 0.48, 0.25), pale=(0.94, 0.89, 0.78),
    spot=(0.07, 0.05, 0.03), spots=1.0, tail_tip=0.9,
)


if __name__ == "__main__":
    st.main(SPEC, ground=(0.52, 0.48, 0.32))
