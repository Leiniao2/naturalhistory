"""
Procedural Cloudina carinata (terminal-Ediacaran tube animal) for the map: a clump of
cone-in-cone tubes like C. hartmannae, but ornamented - every flared collar carries
longitudinal ridges (keels, "carinata") that line up from collar to collar down the tube and
jut out past each rim as short spines, so the tubes look fluted and spiny instead of smooth-
walled. Fewer, stouter tubes leaning out of a dark microbial mat, one toppled on its side and
a broken collar stack beside it. Cream-white calcite on the olive-grey mat.
Fixed style: pivot at the base (z = 0). Shared tube/cluster code lives in nh_cloudina.py.

Usage:
  blender --background --python tools/blender/cloudina_carinata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CloudinaCarinata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_cloudina as cl  # noqa: E402

SEED = 31
STYLE = cl.TubeStyle(
    radius=0.036, growth=1.04, collars=(5, 9), height=1.1, flare=0.22, sink=0.22,
    ecc=0.10, curve=0.08, sides=12, mid_ring=False,
    keels=6, keel_amp=0.30, spine_amp=0.45,     # six keels per collar, spiny at the rims
    bud_chance=0.25, bore_chance=0.0,
)


def build():
    return cl.cluster(STYLE, SEED, count=10, radius=0.40, tilt=(10, 55), lying=1, fragments=1,
                      name="CloudinaCarinata")


if __name__ == "__main__":
    nh.run(build, "CloudinaCarinata", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
