"""
Procedural Dunbaria fasciipennis (Early Permian palaeodictyopteran, ~2 cm) for map colonies
(Swarm style).

A small, beaked palaeodictyopteran from Elmo, Kansas, famous for its boldly banded wings:
four broad, rounded wings held straight out (they could not be folded back), each crossed by
dark brown bands on a pale amber ground, tiny prothoracic winglets, a slender body with a
piercing-sucking beak for drinking plant sap and two short cerci.
Built with nh_car_palaeodicty. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/dunbaria_fasciipennis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dunbaria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_palaeodicty as pd  # noqa: E402

SPEC = pd.Spec(
    name="Dunbaria",
    span=0.85, chord=0.24, hind_chord=0.27, body_len=0.50, body_r=0.04, winglet=0.06, cerci=0.18,
    body=(0.16, 0.10, 0.06), body_mark=(0.70, 0.52, 0.22),
    wing=(0.92, 0.80, 0.52), wing_root=(0.62, 0.44, 0.22), mark=(0.20, 0.11, 0.06),
    pattern="bands", bands=(0.28, 0.52, 0.78), vein=(0.40, 0.28, 0.16),
)

if __name__ == "__main__":
    pd.run(SPEC)
