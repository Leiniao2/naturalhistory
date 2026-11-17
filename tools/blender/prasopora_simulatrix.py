"""
Procedural Prasopora simulatrix (Late Ordovician trepostome bryozoan, eastern North
America) for the map (Fixed style).

A colonial "moss animal": a hemispherical to gumdrop-shaped calcareous colony a few
centimetres across, flat underneath where it rested on the sea floor, its surface
pitted with thousands of tiny tubes (zooecia), each home to a filter-feeding zooid,
and dotted with low, regularly spaced bumps (monticules). Several colonies on a mud
patch. Tan-orange (colour conjectural). Built with nh_ord_shells.py.

Usage:
  blender --background --python tools/blender/prasopora_simulatrix.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PrasoporaSimulatrix.fbx (pivot on the sea floor, z = 0)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402
import nh_ord_shells as sh  # noqa: E402

COLONIES = (((0.05, -0.25), 0.36, 0.34), ((-0.52, 0.38), 0.25, 0.22), ((0.50, 0.42), 0.20, 0.18))


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.0, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    for c, r, h in COLONIES:
        sh.bryozoan_dome(mb, c, r, h, (0.76, 0.56, 0.34), (0.48, 0.32, 0.18))
    obj = mb.to_object("PrasoporaSimulatrix", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PrasoporaSimulatrix", **ec.VIEWS)
