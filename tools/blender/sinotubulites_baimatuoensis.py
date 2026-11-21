"""
Procedural Sinotubulites baimatuoensis (Ediacaran tubular animal) for the map, Fixed style.

A tangle of straight to gently curved, almost parallel-sided calcified tubes built from many
thin, irregular, wrinkled layers stacked one inside the next (not the flaring funnels of
Cloudina), some standing up from the mat and several lying toppled across it. Grey-white
mineral walls. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Sinotubulites.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cloudina as cl  # noqa: E402

cl.CALCITE = (0.80, 0.80, 0.76)
cl.RIM = (0.92, 0.92, 0.88)
cl.SHADOW = (0.52, 0.52, 0.50)
cl.INSIDE = (0.18, 0.17, 0.16)

STYLE = cl.TubeStyle(
    radius=0.045, growth=1.008, collars=(13, 19), height=0.9, flare=0.10, sink=0.12,
    ecc=0.06, curve=0.05, sides=9, mid_ring=False, bud_chance=0.1, bore_chance=0.0,
)


def build():
    return cl.cluster(STYLE, 31, count=7, radius=0.34, tilt=(5, 40), lying=4, fragments=2,
                      name="Sinotubulites")


if __name__ == "__main__":
    nh.run(build, "Sinotubulites", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
