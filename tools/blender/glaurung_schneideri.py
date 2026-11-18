"""
Procedural Glaurung schneideri (Late Permian weigeltisaurid, ~40 cm) gliding, for map colonies.

A gliding reptile from the Kupferschiefer of Germany, named after Tolkien's first dragon: a
slender, lizard-like body with a long tail and broad gliding wings of skin stretched over
long rods of bone from the flanks, and a broad, spiky frill of bony points at the back of the
skull. Built on coelurosauravus_jaekeli.py (same weigeltisaurid body plan, wing rods and
frill helpers) with more rods, broader wings and a larger frill, and coloured differently:
olive-green body with black bands, wings dark green-black with a yellow-banded membrane.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/glaurung_schneideri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Glaurung.fbx
"""

import dataclasses
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
import coelurosauravus_jaekeli as co  # noqa: E402
from mathutils import Vector as V  # noqa: E402

co.ROD = (0.06, 0.07, 0.05)
co.WING = (0.80, 0.70, 0.22)
co.EDGE = (0.10, 0.14, 0.08)
co.FRILL = (0.30, 0.34, 0.18)
co.RODS = 18


def rod_end(sx, i):
    t = i / (co.RODS - 1)
    y0 = -0.27 + 0.44 * t
    ang = math.radians(-14 + 58 * t)
    ln = 0.34 + 0.24 * math.sin(math.pi * (0.15 + 0.7 * t))
    base = V((sx * 0.055, y0, 0.012))
    return base, base + V((sx * ln * math.cos(ang), ln * math.sin(ang), 0.03))


co.rod_end = rod_end
base_crisp = co.crisp


def crisp(mb, spec):
    base_crisp(mb, spec)
    for k in range(9):    # a second, larger row of frill spikes
        t = k / 8
        a = math.radians(-80 + 160 * t)
        b = V((0.045 * math.sin(a), -0.41 + 0.02 * math.cos(a), 0.03))
        tip = b + V((0.075 * math.sin(a), 0.06, 0.03 + 0.012 * math.cos(a)))
        mb.add(pt.cone(b, tip, 0.008), co.FRILL, smooth=False)


SPEC = dataclasses.replace(
    co.SPEC, name="Glaurung", crisp=crisp,
    back=(0.20, 0.26, 0.12), flank=(0.32, 0.38, 0.18), belly=(0.78, 0.76, 0.52), mark=(0.05, 0.06, 0.04),
    pattern="bands", pattern_freq=34.0, pattern_amount=0.75, eye_col=(0.85, 0.55, 0.10),
)

if __name__ == "__main__":
    pt.main(SPEC)
