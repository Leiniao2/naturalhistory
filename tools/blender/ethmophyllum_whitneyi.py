"""
Procedural Ethmophyllum whitneyi (early Cambrian regular archaeocyath, Nevada and California) for
the map: one tall, slender, horn-shaped cup and a small juvenile beside it, their pointed tips
set in a patch of lime mud and microbial crust.

Ethmophyllum has a long, narrow, cylindrical-conical cup with porous outer and inner walls and an
intervallum crossed by many closely spaced radial septa. The cups are built with
nh_archaeocyath.py's ring-stack cup (pores in straight vertical rows; the lip shows the crowded
ring of septa around the dark cavity), then bent so the narrow tip curves like a horn and the
upper cup rises nearly straight. Compared with Metaldetes and Antarcticocyathus it is much taller
and narrower, almost pointed at the base, and has about twice as many septa.
Living colours are unknown; a pale cream-ivory calcite tone is used.
Fixed style: pivot at the base (z = 0). Seabed patch: nh_archaeo_reef.py.

Usage:
  blender --background --python tools/blender/ethmophyllum_whitneyi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ethmophyllum.fbx
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_archaeocyath as na  # noqa: E402
import nh_archaeo_reef as nr  # noqa: E402

SEED = 5
# (cup, horn bend (dx, dy) of the rim relative to the tip; the bend is strongest near the tip)
CUPS = [
    (na.Cup(base=(0.0, 0.0), height=1.55, radii=(0.012, 0.045, 0.08, 0.108, 0.128, 0.142, 0.15, 0.153),
            wall=0.3, sides=40, septa=20, rings=26, depth=0.5), (-0.36, 0.1)),
    (na.Cup(base=(0.2, -0.12), height=0.5, radii=(0.008, 0.025, 0.042, 0.056, 0.066, 0.072, 0.076, 0.077),
            wall=0.3, sides=24, septa=12, rings=12, depth=0.5), (0.1, -0.05)),
]

STYLE = na.Style(
    pores="rows",
    pore_depth=0.07,
    rib_depth=0.04,
    body=(0.62, 0.56, 0.44),       # pale cream-ivory
    body_dark=(0.42, 0.36, 0.27),
    pore=(0.15, 0.12, 0.08),
    rim=(0.76, 0.70, 0.58),
    chamber=(0.17, 0.13, 0.09),
    cavity=(0.08, 0.06, 0.04),
)

CLOTS = [(0.0, 0.0, 0.04, 0.11, 0.1, 0.06), (0.2, -0.12, 0.03, 0.08, 0.08, 0.05),
         (-0.12, 0.1, 0.02, 0.12, 0.08, 0.04), (0.12, 0.1, 0.02, 0.08, 0.07, 0.035)]


def horn(cup, bend, rng):
    bm = na.cup_mesh(cup, STYLE, rng)
    for v in bm.verts:
        t = max(0.0, min(1.0, (v.co.z - cup.z0) / cup.height))
        k = 1 - (1 - t) ** 2.2          # steep near the tip, flat near the rim
        v.co.x += bend[0] * k
        v.co.y += bend[1] * k
    return bm


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    nr.seabed(mb, rng, 0.42, CLOTS, pebbles=3)
    for cup, bend in CUPS:
        mb.add(horn(cup, bend, rng))
    return nr.finish(mb, "Ethmophyllum")


if __name__ == "__main__":
    nh.run(build, "Ethmophyllum", ground=(0.62, 0.58, 0.48), views=((20, 20), (95, 30), (10, 75)))
