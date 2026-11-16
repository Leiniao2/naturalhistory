"""
Procedural Vauxia gracilenta (middle Cambrian aspiculate demosponge, Burgess Shale, British
Columbia) for the map: a slender, well-branched bush of tall, nearly cylindrical tubes rising
from a small knobby holdfast on a little patch of dark mud.

Specimens range from unbranched to highly branched and reach about 8 cm tall; this is a
mature, highly branched one. Each branch is deeply conical, almost cylindrical, with a simple
open central cavity ending in an osculum at its tip. Side branches leave their parent low to
mid-way up and curve back upright, so the colony reads as a loose candelabra of thin open
tubes ("gracilenta" = slender). The spongin net skeleton (no spicules) is painted as a fine
polygonal mesh of pale fibres with darker pores. Warm ochre-tan with paler rims and dark
oscula; the living colour is unknown, this is a plausible keratose-sponge tone.
Fixed style: pivot at the base (z = 0). See nh_vauxia.py for the shared builder.

Usage:
  blender --background --python tools/blender/vauxia_gracilenta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VauxiaGracilenta.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_vauxia as nv  # noqa: E402
from nh_vauxia import Branch  # noqa: E402

SEED = 3
MAX_TRIS = 4300

PALETTE = {
    "body": (0.82, 0.60, 0.30),      # warm ochre
    "shade": (0.58, 0.40, 0.20),     # lower stem, creases
    "fibre": (0.95, 0.80, 0.52),     # pale spongin fibres
    "pore": (0.50, 0.33, 0.17),      # pore centres
    "rim": (0.98, 0.88, 0.65),       # osculum lips
    "vent": (0.20, 0.12, 0.07),      # inside the spongocoel
    "holdfast": (0.50, 0.38, 0.24),
}

# slim tubes: base radius -> rim radius, tall and nearly vertical
BRANCHES = [
    Branch(-1, 0.0, 0, 4, 1.70, 0.058, 0.072, 0.4, start=(0.0, 0.0)),        # 0 main stem
    Branch(0, 0.12, 200, 34, 1.15, 0.050, 0.064, 0.55),                    # 1
    Branch(0, 0.22, 35, 30, 1.25, 0.050, 0.066, 0.5),                      # 2
    Branch(0, 0.40, 300, 30, 0.90, 0.044, 0.058, 0.55),                    # 3
    Branch(0, 0.52, 120, 28, 0.70, 0.040, 0.054, 0.6),                     # 4
    Branch(1, 0.45, 150, 30, 0.55, 0.038, 0.050, 0.6),                     # 5
    Branch(2, 0.50, 70, 28, 0.55, 0.038, 0.050, 0.6),                      # 6
    Branch(-1, 0.0, 235, 14, 0.85, 0.050, 0.062, 0.4, start=(-0.10, -0.09)),  # 7 young sprout
]
HOLDFAST = [((0.0, 0.0, 0.02), (0.13, 0.12, 0.06)), ((-0.07, -0.06, 0.015), (0.10, 0.09, 0.05)),
            ((0.06, 0.05, 0.01), (0.08, 0.08, 0.04))]


def build():
    return nv.build("VauxiaGracilenta", BRANCHES, HOLDFAST, PALETTE, wall=0.028, voxel=0.0105,
                    max_tris=MAX_TRIS, net_freq=40.0, seed=SEED)


if __name__ == "__main__":
    nh.run(build, "VauxiaGracilenta", ground=(0.40, 0.38, 0.34), views=((20, 20), (110, 25), (10, 70)))
