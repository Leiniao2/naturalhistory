"""
Procedural Protospongia rhenana (glass sponge named by Schlueter in 1892 from the Early Devonian
Hunsrueck Slate of Bundenbach, Rhineland-Palatinate, Germany; moved to Cyathophycus by Mehl in
1996) for the map: a tall, vase- or flask-shaped sac with a narrowed neck and a flaring rim
around the osculum, its wall a dense, rectangular weave of strands.

In the pyritised Hunsrueck fossils the wall is mostly made of bundled long diactine spicules
woven into vertical and horizontal strands (a rectangular mesh), with many small hexactine and
possibly cross-shaped spicules between them - a step from the protospongiid towards the
dictyospongiid skeleton. So this is the tallest and most finely, evenly woven of the four
Protospongia models: many strands, slightly taller than wide, no separate secondary order.
Pale golden-ivory strands over ochre windows. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/protospongia_rhenana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtospongiaRhenana.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_protospongia as npr  # noqa: E402

SEED = 31
CELLS_AROUND = 11      # vertical strands of bundled diactines
# (radius, height) from the attachment base up to the rim: vase / flask with a neck
PROFILE = [(0.05, 0.0), (0.2, 0.15), (0.36, 0.5), (0.38, 0.85), (0.3, 1.2), (0.21, 1.48), (0.22, 1.66),
           (0.28, 1.78)]
FLARE = (0.86, 0.06)   # the rim flares outward above the neck

COLORS = {
    "RIB": (0.95, 0.88, 0.62),     # golden-ivory strands of bundled spicules
    "KNOT": (1.00, 0.95, 0.76),
    "WINDOW": (0.62, 0.47, 0.24),  # ochre windows
    "RIM": (0.93, 0.85, 0.60),
    "INSIDE": (0.24, 0.17, 0.08),
    "BASE": (0.50, 0.40, 0.24),
}


def build():
    return npr.build_sponge("ProtospongiaRhenana", PROFILE, CELLS_AROUND, ribs=(0.022, 0.0),
                            rib_width=(0.12, 0.1), secondary=False, wall=0.035, colors=COLORS,
                            seed=SEED, knot=0.15, row_scale=0.9, flare=FLARE,
                            inner_rings=8, inner_bottom=0.55)


if __name__ == "__main__":
    nh.run(build, "ProtospongiaRhenana", ground=(0.36, 0.37, 0.38), views=((20, 25), (60, 55), (10, 80)))
