"""
Procedural Metaldetes taylori (early Cambrian archaeocyath, South Australia) for the map: a small
clump of double-walled, cylindrical-conical cups rising from one lumpy holdfast.

Metaldetes (family Metacyathidae) has a cylindrical-conical cup with two porous walls whose
pores sit in neat straight vertical rows; the intervallum between the walls is crossed by
porous radial partitions (taeniae) and horizontal tabulae. It could live solitary or form
modular clumps by external budding, which is what is shown here: one tall parent cup with two
shorter daughter cups leaning out from its foot. Each cup is open at the top,
showing the wheel-like ring of chambers around the dark central cavity, and the outer walls
carry the straight vertical rows of pores. Living colours are
unknown; a warm ochre-orange sponge tone is used, with darker pores.
Fixed style: pivot at the base (z = 0). Shared cup builder: nh_archaeocyath.py.

Usage:
  blender --background --python tools/blender/metaldetes_taylori.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Metaldetes.fbx
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_archaeocyath as na  # noqa: E402

SEED = 7
CUPS = [
    # parent cup: tall, widening steadily upward
    na.Cup(base=(0.0, 0.0), height=1.15, radii=(0.11, 0.15, 0.19, 0.22, 0.245, 0.26, 0.268, 0.27),
           lean=(0.02, 0.05), sides=36, septa=18, rings=16),
    # daughters budded from the foot of the parent, leaning out
    na.Cup(base=(-0.19, -0.08), height=0.74, radii=(0.08, 0.11, 0.14, 0.165, 0.18, 0.19, 0.196, 0.2),
           lean=(-0.2, -0.08), sides=32, septa=16, rings=14),
    na.Cup(base=(0.19, -0.1), height=0.54, radii=(0.07, 0.10, 0.12, 0.14, 0.152, 0.16, 0.166, 0.17),
           lean=(0.18, -0.12), sides=28, septa=14, rings=12),
]

STYLE = na.Style(
    pores="rows",
    pore_depth=0.07,
    rib_depth=0.05,
    body=(0.88, 0.62, 0.34),       # warm ochre-orange
    body_dark=(0.68, 0.42, 0.22),
    pore=(0.36, 0.18, 0.09),
    rim=(0.97, 0.80, 0.55),
    chamber=(0.40, 0.20, 0.10),
    cavity=(0.16, 0.08, 0.04),
    holdfast=(0.64, 0.48, 0.32),
    holdfast_lumps=[(0.0, 0.0, 0.02, 0.27, 0.25, 0.09), (-0.17, -0.08, 0.02, 0.16, 0.14, 0.08),
                    (0.17, -0.09, 0.02, 0.14, 0.13, 0.07), (0.06, 0.16, 0.02, 0.13, 0.11, 0.06)],
)


def build():
    return na.build_colony("Metaldetes", CUPS, STYLE, random.Random(SEED))


if __name__ == "__main__":
    nh.run(build, "Metaldetes", ground=(0.62, 0.58, 0.48), views=((20, 25), (70, 45), (10, 75)))
