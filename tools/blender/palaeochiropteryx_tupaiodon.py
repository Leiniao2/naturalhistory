"""
Procedural Palaeochiropteryx tupaiodon (middle Eocene, ~47 Ma, Messel pit,
Germany) in flight, wings spread, for map colonies. Built with nh_pal_bat.py.

A small bat with a wingspan of about 30 cm, among the commonest fossils at
Messel, where whole skeletons with wing membranes and stomach contents of moths
and caddisflies are preserved. Its short, broad wings suit slow, agile flight
low over the lake shore and under the forest canopy, and its ear bones show it
echolocated. Fossil melanosomes indicate a reddish-brown fur.
Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/palaeochiropteryx_tupaiodon.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeochiropteryxTupaiodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bat as bat  # noqa: E402

SPEC = bat.Spec(
    name="PalaeochiropteryxTupaiodon",
    span=0.8, chord=0.46, body=(0.075, 0.16, 0.07), head_r=0.065, snout=0.04, ear=0.09,
    tail=0.22, tail_membrane=1.0,
    fur=(0.55, 0.30, 0.17), belly=(0.70, 0.47, 0.32), membrane=(0.30, 0.18, 0.13), bone=(0.20, 0.12, 0.09),
)

if __name__ == "__main__":
    bat.main(SPEC)
