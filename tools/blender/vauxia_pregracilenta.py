"""
Procedural Vauxia pregracilenta (early Cambrian aspiculate demosponge, Chengjiang Biota, Yunnan)
for the map: a low, irregular bush of tubular branches of very different sizes, rising from a
broad, fan-like holdfast spread over a little patch of dark mud.

Described in 2021 as one of the oldest Vauxia, the species was named for its likeness to the
younger V. gracilenta: the same two-layered, spicule-free net skeleton, but with a distinctive
fan-like holdfast and branches of various sizes. Here that reads as one stout leading tube with
a couple of medium and several thin side tubes that splay outward more than in V. gracilenta,
on a flat fan of radiating root lobes. Each branch is a near-cylindrical tube with an open
spongocoel and an osculum at its tip; the hexagonal endosomal net is painted as pale fibres
with darker pores. Absolute size is poorly known; the colony is drawn a bit shorter and
stockier than V. gracilenta. Living colour unknown: a rusty orange-brown is used to tell the
two species apart.
Fixed style: pivot at the base (z = 0). See nh_vauxia.py for the shared builder.

Usage:
  blender --background --python tools/blender/vauxia_pregracilenta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VauxiaPregracilenta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_vauxia as nv  # noqa: E402
from nh_vauxia import Branch  # noqa: E402

SEED = 11
MAX_TRIS = 4300

PALETTE = {
    "body": (0.80, 0.42, 0.20),      # rusty orange
    "shade": (0.52, 0.26, 0.13),     # lower stem, creases
    "fibre": (0.96, 0.70, 0.45),     # pale spongin fibres
    "pore": (0.45, 0.22, 0.11),      # pore centres
    "rim": (0.98, 0.80, 0.58),       # osculum lips
    "vent": (0.18, 0.09, 0.05),      # inside the spongocoel
    "holdfast": (0.46, 0.30, 0.20),
}

# branches of very different sizes: one stout leader, medium and thin side tubes splaying out
BRANCHES = [
    Branch(-1, 0.0, 0, 8, 1.20, 0.090, 0.110, 0.35, start=(0.0, 0.02)),       # 0 stout leader
    Branch(0, 0.18, 160, 48, 0.85, 0.062, 0.078, 0.45),                     # 1 medium
    Branch(0, 0.30, 330, 50, 0.70, 0.050, 0.064, 0.45),                     # 2 medium-thin
    Branch(1, 0.40, 220, 45, 0.42, 0.034, 0.044, 0.55),                     # 3 thin
    Branch(0, 0.55, 80, 46, 0.45, 0.036, 0.046, 0.5),                       # 4 thin
    Branch(2, 0.50, 20, 40, 0.36, 0.030, 0.040, 0.55),                      # 5 thin
    Branch(-1, 0.0, 250, 30, 0.40, 0.040, 0.052, 0.5, start=(-0.05, -0.08)),  # 6 small bud
]
FAN_LOBES = 11         # radiating lobes of the fan-like holdfast
FAN_SPREAD = 220       # degrees covered by the fan
FAN_LENGTH = 0.32


def holdfast():
    """A central pad plus flattened lobes radiating like the ribs of a fan."""
    parts = [((0.0, 0.0, 0.02), (0.16, 0.15, 0.07)), ((0.0, -0.08, 0.01), (0.2, 0.14, 0.035))]
    for i in range(FAN_LOBES):
        a = math.radians(-90 - FAN_SPREAD / 2 + FAN_SPREAD * i / (FAN_LOBES - 1))
        length = FAN_LENGTH * (0.75 + 0.25 * math.cos(i * 1.7))
        r = length * 0.55
        parts.append(((math.cos(a) * r, math.sin(a) * r, 0.008), (length * 0.5, 0.06, 0.03), a))
    return parts


def build():
    return nv.build("VauxiaPregracilenta", BRANCHES, holdfast(), PALETTE, wall=0.028, voxel=0.0105,
                    max_tris=MAX_TRIS, net_freq=40.0, seed=SEED, mud=(0.4, 0.6))


if __name__ == "__main__":
    nh.run(build, "VauxiaPregracilenta", ground=(0.40, 0.38, 0.34), views=((20, 20), (110, 25), (10, 70)))
