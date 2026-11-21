"""
Procedural Vulcanops jennyworthyae (Early Miocene of New Zealand) for map
colonies: a giant burrowing bat.

About three times the size of an ordinary small bat, a relative of New
Zealand's living burrowing bats that foraged on the forest floor as well as in
the air, eating insects, spiders, fruit and nectar. Shown in flight: broad
wings, a big head with a stout muzzle and rounded ears, a short tail and thick
grey-brown fur. Built with nh_pal_bat.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/vulcanops_jennyworthyae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VulcanopsJennyworthyae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_bat as bat  # noqa: E402

SPEC = bat.Spec(
    name="VulcanopsJennyworthyae",
    span=0.90, chord=0.46, body=(0.09, 0.20, 0.08), head_r=0.075, snout=0.06, ear=0.06,
    tail=0.12, tail_membrane=0.8,
    fur=(0.38, 0.34, 0.30), belly=(0.58, 0.53, 0.47), membrane=(0.20, 0.17, 0.15), bone=(0.14, 0.12, 0.10),
)

if __name__ == "__main__":
    bat.main(SPEC)
