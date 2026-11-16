"""
Procedural Protospongia fenestrata (the type species of Protospongia, a reticulosan glass sponge
named by Salter in 1864 from the Middle Cambrian Menevian beds of Porth-y-rhaw, St David's,
Wales) for the map: a single upright, thin-walled, egg-shaped sac with a small osculum, its
wall a square lattice of cross-shaped spicules - the "windows" of its name.

The species is known only from small, flattened fragments of the skeleton, showing at least
three size orders of cross-shaped spicules arranged in squares; the whole-body shape is not
known, so this is a generic, rather slender protospongiid sac. Compared with P. hicksi it is
taller and narrower with a medium mesh: fewer primary strands, each pair split by a secondary
strand. Cream-white silica ribs over grey-olive windows. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/protospongia_fenestrata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtospongiaFenestrata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_protospongia as npr  # noqa: E402

SEED = 11
CELLS_AROUND = 8       # primary vertical strands (medium mesh, three spicule orders)
# (radius, height) from the attachment base up to the rim: slender egg-shaped sac
PROFILE = [(0.06, 0.0), (0.2, 0.12), (0.33, 0.45), (0.35, 0.75), (0.3, 1.1), (0.2, 1.38), (0.16, 1.45)]

COLORS = {
    "RIB": (0.92, 0.90, 0.80),     # cream-white silica strands
    "KNOT": (1.00, 0.98, 0.92),    # centres of the big cross-shaped spicules
    "WINDOW": (0.38, 0.40, 0.32),  # grey-olive soft tissue between the strands
    "RIM": (0.88, 0.86, 0.76),
    "INSIDE": (0.17, 0.17, 0.13),
    "BASE": (0.42, 0.41, 0.33),
}


def build():
    return npr.build_sponge("ProtospongiaFenestrata", PROFILE, CELLS_AROUND, ribs=(0.026, 0.013),
                            wall=0.035, colors=COLORS, seed=SEED, row_scale=1.1)


if __name__ == "__main__":
    nh.run(build, "ProtospongiaFenestrata", ground=(0.40, 0.40, 0.36), views=((20, 25), (60, 55), (10, 80)))
