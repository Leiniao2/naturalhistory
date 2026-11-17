"""
Procedural Phorusrhacos longissimus (Early-Middle Miocene of Patagonia) for map
colonies: the terror bird that gave its family, the Phorusrhacidae, its name.

A flightless predator about 2.5 m tall: long, powerful running legs, a
horizontal body with small vestigial wings, a long, strong neck and a huge,
deep, laterally flattened head ending in a sharply hooked beak used to strike
and tear prey. Grey-brown plumage with a paler belly (a reconstruction choice).
Built with nh_neo_bigbird.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/phorusrhacos_longissimus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhorusrhacosLongissimus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="PhorusrhacosLongissimus",
    hip=1.00, body=(0.22, 0.42, 0.26), body_tilt=12, leg_r=0.055,
    neck=((0, -0.32, 0.20), (0, -0.40, 0.52), (0, -0.48, 0.78)), neck_r=(0.11, 0.08, 0.07),
    head_r=0.13, beak_len=0.36, beak_h=0.28, hook=1.0, wing=0.28, tail=0.22,
    feather=(0.40, 0.35, 0.28), dark=(0.22, 0.19, 0.15), pale=(0.72, 0.66, 0.55),
    beak_col=(0.78, 0.64, 0.36), leg_col=(0.62, 0.52, 0.32), stride=0.32,
)

if __name__ == "__main__":
    q.main(SPEC)
