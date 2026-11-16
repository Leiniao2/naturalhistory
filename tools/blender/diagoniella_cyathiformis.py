"""
Procedural Diagoniella cyathiformis (Middle Cambrian reticulosan glass sponge; Dawson & Hinde,
1889; Burgess Shale of British Columbia, also the Wheeler and Marjum formations of Utah) for the
map: a thin-walled, elongate inverted cone / cup ("cyathiformis" = cup-shaped) whose wall is a
regular net of diagonally arranged cross-shaped spicules (stauracts), raised on a tuft of long
anchoring root spicules that splay out on the mud.

The diagonal lattice is what separates Diagoniella from Protospongia (whose square spicule net
runs vertically and horizontally): here large stauracts form a coarse lattice at +-45 degrees
with a finer secondary strand halfway across each cell, and knots where the strands cross. D.
cyathiformis is the larger, more elongate and conical species of the genus (up to about 12 cm),
with long spicules forming a tuft-like root at the base. Pale silvery-cream silica strands over
greyish-tan windows, a dark osculum. See nh_diagonal_sponge.py for the shared builder.
Fixed style: pivot at the base of the root tuft (z = 0).

Usage:
  blender --background --python tools/blender/diagoniella_cyathiformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Diagoniella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_diagonal_sponge as nds  # noqa: E402

SEED = 7
LIFT = 0.36            # height of the cone's base above the mud (root tuft below it)
# (radius, height) of the body: elongate inverted cone flaring gently to a wide osculum
PROFILE = [(0.035, 0.0), (0.10, 0.14), (0.19, 0.45), (0.27, 0.85), (0.32, 1.18), (0.33, 1.28)]
PROFILE = [(r, z + LIFT) for r, z in PROFILE]
CELLS_AROUND = 8
ROOT_SPICULES = 16

COLORS = {
    "RIB": (0.88, 0.86, 0.78),     # pale silica strands
    "KNOT": (0.98, 0.97, 0.92),    # stauract centres
    "WINDOW": (0.40, 0.36, 0.29),  # greyish-tan soft tissue
    "RIM": (0.86, 0.83, 0.74),
    "INSIDE": (0.20, 0.17, 0.13),
    "BASE": (0.55, 0.50, 0.41),
}
SPIC_BASE = (0.78, 0.75, 0.66)
SPIC_TIP = (0.96, 0.95, 0.90)


def build():
    mb, surface, rng = nds.build(PROFILE, CELLS_AROUND, m=4, ribs=(0.022, 0.010), knot=0.6,
                                 wall=0.03, colors=COLORS, wobble=0.035, seed=SEED, rmin=0.12,
                                 inner_rings=5, inner_bottom=0.5)
    # root tuft: long spicules rooted in the base of the cone, gathered into a stalk, then
    # splaying out over the mud
    for k in range(ROOT_SPICULES):
        a = (k + rng.uniform(-0.3, 0.3)) / ROOT_SPICULES * math.tau
        out = Vector((math.cos(a), math.sin(a), 0.0))
        side = Vector((-out.y, out.x, 0.0))
        twist = side * rng.uniform(-0.02, 0.02)
        top = out * 0.025 + Vector((0, 0, LIFT + rng.uniform(0.08, 0.16)))
        mid = out * 0.03 + twist + Vector((0, 0, LIFT * 0.45))
        low = out * rng.uniform(0.09, 0.14) + twist * 2 + Vector((0, 0, LIFT * 0.1))
        tip = out * rng.uniform(0.2, 0.34) + twist * 3 + Vector((0, 0, rng.uniform(-0.005, 0.01)))
        nds.spicule(mb, [top, mid, low, tip], rng.uniform(0.008, 0.011), SPIC_BASE, SPIC_TIP)
    return nds.finish(mb, "Diagoniella", rng, mud=(0.28, 0.5), mud_count=6)


if __name__ == "__main__":
    nh.run(build, "Diagoniella", ground=(0.40, 0.38, 0.34), views=((15, 15), (75, 35), (10, 75)))
