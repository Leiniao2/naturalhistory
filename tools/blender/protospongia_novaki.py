"""
Procedural Protospongia novaki (reticulosan glass sponge named by Pocta in 1898 from the Early
Ordovician Klabava Formation of the Prague Basin, Bohemia, Czech Republic) for the map: a small,
squat, bowl-like sac with a wide osculum and a very coarse lattice of a few big cross-shaped
spicules.

The species was founded on a small wall fragment holding a large cross-shaped spicule (stauract)
with narrow rays about 1.4-2.2 mm long, and is otherwise known from scattered fragments and
loose spicules in tuffaceous shales; its body shape is unknown. The model therefore keeps the
genus' thin-walled sac but stresses what is known: big spicules, so a coarse mesh of only a few
thick primary strands with no secondary strand between them. Ochre-grey ribs over dusky brown
windows. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/protospongia_novaki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtospongiaNovaki.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_protospongia as npr  # noqa: E402

SEED = 21
CELLS_AROUND = 9       # primary vertical strands (coarse mesh of big stauracts)
# (radius, height) from the attachment base up to the rim: squat bowl with a wide opening
PROFILE = [(0.08, 0.0), (0.3, 0.08), (0.48, 0.26), (0.52, 0.46), (0.45, 0.66), (0.34, 0.78), (0.3, 0.81)]
CELL_SAMPLES = (0.0, 0.11, 0.3, 0.5, 0.7, 0.89)   # extra window vertices keep the coarse body round

COLORS = {
    "RIB": (0.84, 0.77, 0.58),     # ochre-grey silica strands
    "KNOT": (0.95, 0.90, 0.74),    # centres of the big cross-shaped spicules
    "WINDOW": (0.47, 0.38, 0.28),  # dusky brown soft tissue
    "RIM": (0.80, 0.73, 0.55),
    "INSIDE": (0.16, 0.12, 0.09),
    "BASE": (0.38, 0.33, 0.27),
}


def build():
    return npr.build_sponge("ProtospongiaNovaki", PROFILE, CELLS_AROUND, ribs=(0.04, 0.0),
                            rib_width=(0.12, 0.1), secondary=False, wall=0.05, colors=COLORS,
                            seed=SEED, knot=0.3, row_scale=0.62, cell_samples=CELL_SAMPLES)


if __name__ == "__main__":
    nh.run(build, "ProtospongiaNovaki", ground=(0.42, 0.40, 0.36), views=((20, 25), (60, 55), (10, 80)))
