"""
Procedural Conotubus hemiannulatus (Ediacaran tubular animal) for the map, Fixed style.

Small, curved tubes of soft, barely mineralised organic wall built as a stack of broad,
nested funnels, each flaring out at its rim, so the tube looks like a pile of ice-cream cones.
A clump rooted in the mat, leaning every way. Translucent amber-brown. Pivot at the base
(z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Conotubus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cloudina as cl  # noqa: E402

cl.CALCITE = (0.76, 0.56, 0.34)
cl.RIM = (0.92, 0.74, 0.50)
cl.SHADOW = (0.46, 0.32, 0.20)
cl.INSIDE = (0.20, 0.12, 0.08)

STYLE = cl.TubeStyle(
    radius=0.035, growth=1.04, collars=(7, 10), height=0.95, flare=0.5, sink=0.3,
    ecc=0.08, curve=0.12, sides=10, mid_ring=True, bud_chance=0.0, bore_chance=0.0,
)


def build():
    return cl.cluster(STYLE, 17, count=9, radius=0.3, tilt=(10, 55), lying=1, fragments=1,
                      name="Conotubus")


if __name__ == "__main__":
    nh.run(build, "Conotubus", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
