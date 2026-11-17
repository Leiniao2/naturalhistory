"""
Procedural Echinosphaerites aurantium (Middle Ordovician rhombiferan cystoid of the Baltic
region, a ball 2-4 cm across, so common it forms 'Echinosphaerites limestone') for the map.
A near-spherical theca of many thin polygonal plates crossed by pore rhombs (respiratory
pore slits across the sutures), a small mouth on top with a few short brachioles, the
anal pyramid on one side and a short stem stub; adults lay loose on the sea floor.
Orange-tan (colour conjectural). Built with nh_ord_echino.py.

Usage:
  blender --background --python tools/blender/echinosphaerites_aurantium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EchinosphaeritesAurantium.fbx (Fixed style: pivot on the sea floor, z = 0)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

if __name__ == "__main__":
    nh.run(lambda: ec.cystoid("EchinosphaeritesAurantium"), "EchinosphaeritesAurantium", **ec.VIEWS)
