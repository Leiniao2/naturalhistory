"""
Procedural Triticispongia diagonata (early Cambrian hexactinellid glass sponge from South China;
Mehl & Reitner in Steiner et al., 1993) for the map: a small, ovoid, wheat-grain-shaped
("Triticum" = wheat) thin-walled sac with a narrow osculum at its tip, its wall a diagonal
lattice of cross-shaped spicules ("diagonata"), a few long spicules sticking out of the wall
and a short tuft at the base, on a little patch of dark mud.

Compared with Diagoniella (an elongate open cone on a long root tuft) this is a closed,
plump grain: widest a little below the middle, tapering to a small rounded osculum, with a
finer diagonal net (more cells around) and only a short basal tuft. Warm ivory silica
strands over buff windows; the living colour is unknown. See nh_diagonal_sponge.py for the
shared builder. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/triticispongia_diagonata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Triticispongia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_diagonal_sponge as nds  # noqa: E402

SEED = 12
LIFT = 0.07            # short basal tuft below the body
# (radius, height): plump grain, widest below the middle, tapering to a small osculum
PROFILE = [(0.035, 0.0), (0.14, 0.07), (0.27, 0.24), (0.33, 0.44), (0.31, 0.64), (0.22, 0.84),
           (0.11, 0.98), (0.07, 1.03)]
PROFILE = [(r, z + LIFT) for r, z in PROFILE]
CELLS_AROUND = 10
NEEDLES = 8            # long protruding spicules
TUFT = 9

COLORS = {
    "RIB": (0.90, 0.85, 0.72),     # warm ivory silica strands
    "KNOT": (0.97, 0.93, 0.82),
    "WINDOW": (0.50, 0.42, 0.30),  # buff soft tissue
    "RIM": (0.86, 0.84, 0.78),
    "INSIDE": (0.18, 0.15, 0.11),
    "BASE": (0.55, 0.48, 0.37),
}
SPIC_BASE = (0.82, 0.80, 0.72)
SPIC_TIP = (0.97, 0.97, 0.93)


def build():
    mb, surface, rng = nds.build(PROFILE, CELLS_AROUND, m=4, ribs=(0.018, 0.008), knot=0.6,
                                 wall=0.025, colors=COLORS, wobble=0.025, seed=SEED, rmin=0.14,
                                 lip_rings=3, inner_rings=3, inner_bottom=0.88)
    # a few long spicules protruding obliquely upward from the wall
    for k in range(NEEDLES):
        th = (k + rng.uniform(-0.3, 0.3)) / NEEDLES * math.tau
        s = rng.uniform(0.35, 0.85)
        p, n = surface(th, s, -0.01)
        up = Vector((0, 0, 1))
        d = (n * rng.uniform(0.5, 0.8) + up * rng.uniform(0.6, 1.0)).normalized()
        length = rng.uniform(0.3, 0.5)
        nds.spicule(mb, [p, p + d * length * 0.5, p + d * length], 0.008, SPIC_BASE, SPIC_TIP, sides=3)
    # short basal tuft
    for k in range(TUFT):
        a = (k + rng.uniform(-0.3, 0.3)) / TUFT * math.tau
        out = Vector((math.cos(a), math.sin(a), 0.0))
        top = out * 0.02 + Vector((0, 0, LIFT + 0.06))
        tip = out * rng.uniform(0.1, 0.17) + Vector((0, 0, rng.uniform(0.0, 0.01)))
        nds.spicule(mb, [top, top.lerp(tip, 0.5) + Vector((0, 0, -0.01)), tip], 0.007, SPIC_BASE, SPIC_TIP, sides=3)
    return nds.finish(mb, "Triticispongia", rng, mud=(0.3, 0.5), mud_count=6, mud_size=(0.03, 0.06))


if __name__ == "__main__":
    nh.run(build, "Triticispongia", ground=(0.40, 0.38, 0.34), views=((15, 15), (75, 35), (10, 75)))
