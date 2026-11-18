"""
Procedural Mischoptera nigra (Late Carboniferous of Commentry, France, a large megasecopteran
insect with a wingspan of about 20 cm) in level flight, for map colonies.

Megasecopterans were beaked plant-sucking insects related to the palaeodictyopterans: a small
head with a piercing-sucking beak and long antennae, two pairs of slender, narrow-based wings
held straight out (they could not fold them), a slim ringed abdomen and very long cerci. As
the name says, Mischoptera's wings were dark, almost black, with paler patches near the tips.
Built with nh_car_palaeodicty (the prothoracic winglets of palaeodictyopterans are shrunk to
nothing here). Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/mischoptera_nigra.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mischoptera.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_palaeodicty as pd  # noqa: E402

SPEC = pd.Spec(
    name="Mischoptera",
    span=1.0, chord=0.12, hind_chord=0.13, body_len=0.55, body_r=0.03, winglet=0.004, cerci=0.6,
    body=(0.10, 0.08, 0.07), body_mark=(0.40, 0.18, 0.10),
    wing=(0.10, 0.09, 0.09), wing_root=(0.16, 0.12, 0.10), mark=(0.78, 0.74, 0.64),
    pattern="spots", bands=(0.78, 0.9), vein=(0.04, 0.03, 0.03), eye=(0.40, 0.14, 0.08),
)

if __name__ == "__main__":
    pd.run(SPEC)
