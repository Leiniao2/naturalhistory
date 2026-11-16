"""
Procedural Protospongia hicksi (Middle Cambrian reticulosan glass sponge; named by Hinde in 1888
from St David's, Wales, and also known from the Burgess Shale of British Columbia and the Marjum
Formation of Utah) for the map: a single thin-walled, globular-to-conical sac with a wide
osculum, its wall a fine square lattice of cross-shaped spicules.

Burgess Shale specimens are only fragments (the largest about 5 cm across) with spicules in up
to six size orders, so the whole-body shape here follows the usual reconstruction: a broad,
rounded sac narrowing to a small attachment base. The lattice is the finest of the four
Protospongia models: many primary strands with a secondary strand between each pair.
Pale buff silica ribs over darker tan windows. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/protospongia_hicksi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtospongiaHicksi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_protospongia as npr  # noqa: E402

SEED = 3
CELLS_AROUND = 10      # primary vertical strands (fine mesh: six spicule orders in the fossils)
# (radius, height) from the attachment base up to the rim: globular-conical sac
PROFILE = [(0.07, 0.0), (0.25, 0.1), (0.42, 0.32), (0.47, 0.55), (0.42, 0.8), (0.3, 1.0), (0.24, 1.08)]

COLORS = {
    "RIB": (0.90, 0.84, 0.68),     # pale buff silica strands
    "KNOT": (0.98, 0.95, 0.84),    # centres of the big cross-shaped spicules
    "WINDOW": (0.55, 0.43, 0.30),  # tan soft tissue between the strands
    "RIM": (0.86, 0.79, 0.62),
    "INSIDE": (0.22, 0.16, 0.11),
    "BASE": (0.50, 0.41, 0.30),
}


def build():
    return npr.build_sponge("ProtospongiaHicksi", PROFILE, CELLS_AROUND, ribs=(0.024, 0.012),
                            wall=0.04, colors=COLORS, seed=SEED)


if __name__ == "__main__":
    nh.run(build, "ProtospongiaHicksi", ground=(0.45, 0.43, 0.38), views=((20, 25), (60, 55), (10, 80)))
