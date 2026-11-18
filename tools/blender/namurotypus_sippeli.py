"""
Procedural Namurotypus sippeli (Late Carboniferous of Hagen-Vorhalle, Germany, one of the
oldest known griffinflies, wingspan about 32 cm) in level flight, for map colonies.

Uses the griffinfly body of meganeura_monyi.py (huge compound eyes, boxy forward-tilted
thorax, long ringed abdomen with cerci, four long narrow veined wings held flat, spiny legs
folded into a catching basket) repainted for Namurotypus: a dark metallic green-bronze body
ringed with pale yellow, red-brown eyes and smoky-tinted wings with dark veins.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/namurotypus_sippeli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Namurotypus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import meganeura_monyi as mm  # noqa: E402

mm.BODY = (0.08, 0.16, 0.11)
mm.BODY_DARK = (0.03, 0.06, 0.04)
mm.STRIPE = (0.86, 0.80, 0.36)
mm.EYE = (0.30, 0.10, 0.06)
mm.EYE_SHEEN = (0.62, 0.30, 0.16)
mm.LEG = (0.05, 0.06, 0.04)
mm.MEMBRANE = (0.58, 0.56, 0.48)
mm.MEMBRANE_ROOT = (0.30, 0.24, 0.14)
mm.VEIN = (0.10, 0.08, 0.05)

if __name__ == "__main__":
    nh.run(mm.build, "Namurotypus", background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
