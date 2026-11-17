"""
Procedural Stenodictya lobata (Late Carboniferous of Commentry, France, a palaeodictyopteran insect) for map colonies (Swarm style).

A beaked insect with four long, slender, pale wings held flat out, marked with dark spots and
bands, a pair of prominent lobe-like prothoracic winglets (the lobata of its name), a slim body with
a sucking beak and two long cerci.
Built with nh_car_palaeodicty. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/stenodictya_lobata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Stenodictya.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_palaeodicty as pd  # noqa: E402

SPEC = pd.Spec(
    name="Stenodictya",
    span=1.0, chord=0.17, hind_chord=0.2, body_len=0.55, body_r=0.035, winglet=0.13, cerci=0.45,
    body=(0.20, 0.14, 0.09), body_mark=(0.62, 0.46, 0.22),
    wing=(0.82, 0.78, 0.66), wing_root=(0.55, 0.45, 0.30), mark=(0.16, 0.12, 0.09),
    pattern="spots", bands=(0.3, 0.55, 0.8), vein=(0.35, 0.28, 0.18),
)

if __name__ == "__main__":
    pd.run(SPEC)
