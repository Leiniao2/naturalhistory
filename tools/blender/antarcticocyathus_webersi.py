"""
Procedural Antarcticocyathus webersi (late Cambrian cup sponge, Minaret Formation, Ellsworth
Mountains, West Antarctica) for the map: a tight cluster of slender, cylindrical-conical,
double-walled cups on a small holdfast.

Antarcticocyathus was described in 1984 as an archaeocyath (family Loculicyathidae): a
cylindrical-conical cup with two walls and an empty central cavity, an outer wall with simple
polygonal pores scattered at random, and an intervallum crossed only by sparse, perforated
pseudosepta (no tabulae). It lived solitary or modular, budding new cups inside the intervallum
of the parent, so daughter cups stand pressed against it. Here: one tall, gently curved cup with
two daughters fused to its side. The few, thin pseudosepta leave wide chambers in the lip (unlike
the crowded partitions of Metaldetes), and the pores are staggered and thinned out so they look
scattered. A 2022 restudy reinterpreted it as an anthaspidellid (lithistid) demosponge instead,
but the cup shape stays the same. Living colours are unknown; a pale peach-cream is used.
Fixed style: pivot at the base (z = 0). Shared cup builder: nh_archaeocyath.py.

Usage:
  blender --background --python tools/blender/antarcticocyathus_webersi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Antarcticocyathus.fbx
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_archaeocyath as na  # noqa: E402

SEED = 3
CUPS = [
    # parent: tall and slender, gently curved
    na.Cup(base=(0.0, 0.02), height=1.3, radii=(0.07, 0.10, 0.13, 0.155, 0.17, 0.18, 0.185, 0.186),
           lean=(-0.06, 0.1), wall=0.36, sides=27, septa=9, rings=28, depth=0.55),
    # daughters budded against the parent's side
    na.Cup(base=(0.15, -0.06), height=0.86, radii=(0.06, 0.085, 0.11, 0.13, 0.142, 0.15, 0.154, 0.155),
           lean=(0.07, -0.03), wall=0.36, sides=24, septa=8, rings=20, depth=0.55),
    na.Cup(base=(-0.11, -0.12), height=0.55, radii=(0.05, 0.07, 0.09, 0.105, 0.115, 0.12, 0.124, 0.125),
           lean=(-0.06, -0.06), wall=0.36, sides=24, septa=8, rings=14, depth=0.55),
]

STYLE = na.Style(
    pores="random",
    pore_keep=0.7,
    pore_depth=0.08,
    rib_depth=0.045,
    body=(0.89, 0.74, 0.64),       # pale peach-cream
    body_dark=(0.70, 0.54, 0.46),
    pore=(0.40, 0.24, 0.22),
    rim=(0.97, 0.90, 0.84),
    chamber=(0.42, 0.28, 0.28),
    cavity=(0.16, 0.10, 0.10),
    holdfast=(0.66, 0.56, 0.50),
    holdfast_lumps=[(0.0, 0.0, 0.02, 0.2, 0.18, 0.08), (0.14, -0.06, 0.02, 0.14, 0.12, 0.07),
                    (-0.11, -0.11, 0.02, 0.12, 0.11, 0.06)],
)


def build():
    return na.build_colony("Antarcticocyathus", CUPS, STYLE, random.Random(SEED))


if __name__ == "__main__":
    nh.run(build, "Antarcticocyathus", ground=(0.62, 0.58, 0.48), views=((20, 25), (70, 45), (10, 75)))
