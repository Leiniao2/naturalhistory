"""
Procedural Mazothairos enormis (Late Carboniferous of Mazon Creek, Illinois, one of the largest palaeodictyopteran insects, wingspan perhaps 50-55 cm) for map colonies (Soar style).

A giant beaked insect gliding on four long, broad wings held straight out, with small winglets on
the first thoracic segment, a stout body with a downturned sucking beak, a long ringed abdomen and
long tail cerci. The wing pattern is a guess: smoky brown with pale crossbands.
Built with nh_car_palaeodicty. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/mazothairos_enormis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mazothairos.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_palaeodicty as pd  # noqa: E402

SPEC = pd.Spec(
    name="Mazothairos",
    span=1.0, chord=0.2, hind_chord=0.25, body_len=0.6, body_r=0.04, winglet=0.09, cerci=0.4,
    body=(0.16, 0.12, 0.08), body_mark=(0.40, 0.28, 0.14),
    wing=(0.38, 0.30, 0.20), wing_root=(0.28, 0.20, 0.12), mark=(0.80, 0.74, 0.58),
    pattern="bands", bands=(0.42, 0.75), vein=(0.14, 0.10, 0.07),
)

if __name__ == "__main__":
    pd.run(SPEC)
