"""
Procedural Platycrinites laevis (Early Carboniferous sea lily of the crinoid meadows
whose remains built the Carboniferous Limestone of England) for the map.

A stalked crinoid of the great Carboniferous crinoid meadows: a root-like holdfast, a long
column of elliptical columnals (Platycrinites stems are famous for their slight twist), a
smooth, bowl-shaped cup of a few large plates and five arms that fork into a feathery fan
for catching drifting food. Wine-red with paler arms (colour conjectural).
Built with nh_ord_echino.crinoid. Fixed style: pivot on the sea floor (z = 0).

Usage:
  blender --background --python tools/blender/platycrinites_laevis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Platycrinites.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

if __name__ == "__main__":
    nh.run(lambda: ec.crinoid("Platycrinites", forks=3, stem_h=1.1, stem_r=0.04, arm_len=0.75, spread=0.6,
                              cup_h=0.2, body=(0.56, 0.24, 0.24), dark=(0.34, 0.12, 0.14),
                              arm=(0.82, 0.52, 0.46), mud=((0.38, 0.36, 0.30), (0.56, 0.52, 0.44)), sway=0.12),
           "Platycrinites", **ec.VIEWS)
