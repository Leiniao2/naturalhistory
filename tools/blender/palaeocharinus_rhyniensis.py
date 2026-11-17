"""
Procedural Palaeocharinus rhyniensis for the map: a trigonotarbid arachnid from the Early
Devonian (Pragian, about 410 million years ago) Rhynie chert of Aberdeenshire, Scotland;
a few millimetres long. Trigonotarbids were spider-like arachnids without silk glands or
venom and among the first land predators; the Rhynie chert preserves even their book
lungs, showing they breathed air.

A small, squarish carapace (prosoma) with a pair of median eyes on a small tubercle,
short chelicerae and pedipalps, four pairs of walking legs, and a broad, oval, flattened
opisthosoma whose tergites are split into a row of median plates and two rows of lateral
plates - the trigonotarbid hallmark.

Built with nh_dev_arthro pieces. Colours are unknown: dark chestnut brown.

Usage:
  blender --background --python tools/blender/palaeocharinus_rhyniensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeocharinus.fbx (Ground: pivot on the ground,
facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Palaeocharinus"

BODY = (0.30, 0.18, 0.10)
DARK = (0.09, 0.06, 0.04)
RIM = (0.48, 0.32, 0.18)
LEG = (0.36, 0.24, 0.14)
LEG_TIP = (0.50, 0.36, 0.22)
EYE = (0.70, 0.66, 0.55)

BASE = 0.10


def build():
    mb = nh.MeshBuilder()
    # carapace
    c = Vector((0, -0.24, BASE + 0.04))
    mb.add(nh.uv_ellipsoid(c, (0.17, 0.16, 0.055), 16, 8,
                           deform=lambda n: (1.0 + 0.12 * (abs(n.x) ** 3 + abs(n.y) ** 3)) * (0.7 if n.z < 0 else 1.0)),
           ar.glossy(BODY))
    t = c + Vector((0, -0.07, 0.05))
    mb.add(nh.uv_ellipsoid(t, (0.03, 0.03, 0.016), 8, 5), DARK)
    for s in (-1, 1):
        mb.add(nh.ellipsoid(t + Vector((s * 0.014, -0.01, 0.012)), (0.010,) * 3, 1), EYE)
        mb.add(nh.uv_ellipsoid(c + Vector((s * 0.035, -0.165, -0.02)), (0.028, 0.035, 0.022), 8, 5), ar.glossy(RIM))
    # opisthosoma: median and lateral tergite rows
    for i in range(7):
        y = -0.06 + i * 0.075
        w = 0.24 * (1.0 - ((i - 2.2) / 5.5) ** 2)
        for x, ww in ((0.0, w * 0.32), (w * 0.62, w * 0.36), (-w * 0.62, w * 0.36)):
            z = BASE + 0.05 - abs(x) * 0.15 - i * 0.003
            col = ar.glossy(BODY if x == 0 else nh.lerp(BODY, RIM, 0.2))
            ar.plate(mb, (x, y, z), (ww, 0.045, 0.040), col, 12, 6)
    mb.add(nh.uv_ellipsoid((0, 0.17, BASE + 0.02), (0.20, 0.27, 0.035), 12, 6), DARK)
    # pedipalps and legs
    for s in (-1, 1):
        root = Vector((s * 0.08, -0.38, BASE + 0.02))
        ar.jointed(mb, [root, root + Vector((s * 0.08, -0.06, 0.03)), root + Vector((s * 0.06, -0.15, -0.03))],
                   [0.020, 0.018, 0.010], ar.glossy(LEG), RIM)
        for hy, reach, splay in ((-0.33, -0.22, 0.42), (-0.28, -0.08, 0.48), (-0.22, 0.08, 0.48), (-0.16, 0.24, 0.44)):
            ar.leg(mb, s, (0.12, hy, BASE + 0.02), reach, splay, BASE + 0.13, 0.020, ar.glossy(LEG), RIM, LEG_TIP)
    return ar.finish_ground(mb, NAME, BASE + 0.02)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
