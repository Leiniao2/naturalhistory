"""
Procedural Irish elk (Megaloceros giganteus, Pleistocene - early Holocene of
Eurasia) for map colonies.

A giant deer about 2 m at the shoulder whose stags carried the largest antlers
of any deer, up to 3.6 m across: broad, flat palms held out to the sides with a
fringe of tines and a forward brow tine. A strong shoulder hump, long legs, a
short tail. Coat reconstructed from cave paintings: pale fawn with a dark
collar band across the shoulders and a dark stripe down the hump.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/megaloceros_giganteus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegalocerosGiganteus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="MegalocerosGiganteus",
    leg_f=0.92, leg_h=0.90, length=0.80, girth=(0.20, 0.26),
    hump=0.40, hump_y=-0.40,
    leg_r=(0.058, 0.068), leg_taper=0.5, foot="hoof", stride=0.14,
    neck_len=0.46, neck_angle=40, neck_r=(0.17, 0.10),
    head_len=0.42, head_r=(0.085, 0.10), snout_r=(0.045, 0.055), head_pitch=55,
    ears="point", ear_size=0.10, beard=0.08,
    tail_len=0.14, tail_r=0.035, tail_droop=0.8,
    antler=1.05,
    coat=(0.72, 0.58, 0.40), dark=(0.34, 0.25, 0.16), pale=(0.90, 0.85, 0.74),
    mane_col=(0.30, 0.22, 0.15),
    pattern=q.collar((0.28, 0.20, 0.13), -0.75, -0.42, amount=0.8), shag=0.006, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
