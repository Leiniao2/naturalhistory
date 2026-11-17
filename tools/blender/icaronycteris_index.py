"""
Procedural Icaronycteris index (early Eocene, ~52 Ma, Green River Formation,
Wyoming) in flight, wings spread, for map colonies. Built with nh_pal_bat.py.

One of the oldest well-preserved bats, about 14 cm long with a 37 cm wingspan.
It already flew and probably echolocated much like living insect-eating bats, but
it kept a claw on its index finger as well as the thumb, had relatively short,
broad wings and a long tail only partly joined to the tail membrane. Moth scales
have been found in its gut. Fur: brown (unknown).
Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/icaronycteris_index.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IcaronycterisIndex.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bat as bat  # noqa: E402

SPEC = bat.Spec(
    name="IcaronycterisIndex",
    span=0.95, chord=0.4, body=(0.07, 0.17, 0.065), head_r=0.06, snout=0.05, ear=0.07,
    tail=0.34, tail_membrane=0.4,
    fur=(0.40, 0.31, 0.22), belly=(0.58, 0.49, 0.37), membrane=(0.24, 0.19, 0.15), bone=(0.16, 0.12, 0.10),
)

if __name__ == "__main__":
    bat.main(SPEC)
