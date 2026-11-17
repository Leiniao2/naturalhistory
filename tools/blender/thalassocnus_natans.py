"""
Procedural Thalassocnus natans (Late Miocene of the Pisco coast, Peru) for map
colonies: an aquatic ground sloth that waded and swam in shallow seas to
graze on seagrass and seaweed.

A long-bodied sloth with a long, downturned snout (its jaws ended in a broad,
spatula-like tip for cropping), strong forelimbs with long curved claws used
to hold on to the sea floor, short hind legs, and a long, thick tail.
Shaggy dark brown coat. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thalassocnus_natans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThalassocnusNatans.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ThalassocnusNatans",
    leg_f=0.42, leg_h=0.38, length=0.88, girth=(0.20, 0.23),
    leg_r=(0.065, 0.07), leg_taper=0.65, foot="knuckle", stride=0.10,
    neck_len=0.26, neck_angle=10, neck_r=(0.16, 0.11),
    head_len=0.42, head_r=(0.09, 0.09), snout_r=(0.055, 0.04), head_pitch=30,
    ears="none",
    tail_len=0.70, tail_r=0.08, tail_droop=0.4,
    coat=(0.34, 0.27, 0.19), dark=(0.22, 0.17, 0.11), pale=(0.50, 0.42, 0.32),
    shag=0.014, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
