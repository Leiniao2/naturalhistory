"""
Procedural Hudsonaster incomptus (Late Ordovician sea star of the Cincinnati region, a few
centimetres across) for the map. One of the earliest true starfish: a small disc and five
short, broad arms built of regular rows of block-like plates (large marginals along the
edges), with a small madreporite on top. Tan (colour conjectural).
Built with nh_ord_echino.py.

Usage:
  blender --background --python tools/blender/hudsonaster_incomptus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HudsonasterIncomptus.fbx (Fixed style: pivot on the sea floor, z = 0)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

if __name__ == "__main__":
    nh.run(lambda: ec.seastar("HudsonasterIncomptus"), "HudsonasterIncomptus", **ec.VIEWS)
