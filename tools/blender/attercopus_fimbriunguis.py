"""
Procedural Attercopus fimbriunguis for the map: a uraraneid arachnid, a close relative of
true spiders, from the Middle Devonian (Givetian, about 386 million years ago) of Gilboa,
New York; a few millimetres long. Its name means "poison-head with fringed claws".

It could already make silk - its fossil cuticle shows rows of silk spigots on plates under
the abdomen - but it lacked true spinnerets, so it probably laid down sheets of silk to
line burrows or wrap eggs rather than spinning webs. Unlike spiders it kept a segmented
opisthosoma (with separate tergite plates) and a long, jointed whip-like tail
(flagellum), like that of Chimerarachne. A rounded carapace with eyes, fanged
chelicerae, pedipalps and four pairs of long legs complete it.

Built with nh_dev_arthro pieces. Colours are unknown: dark grey-brown with paler joints.

Usage:
  blender --background --python tools/blender/attercopus_fimbriunguis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Attercopus.fbx (Ground: pivot on the ground,
facing -Y).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Attercopus"

BODY = (0.20, 0.17, 0.14)
DARK = (0.06, 0.05, 0.04)
RIM = (0.46, 0.38, 0.28)
LEG = (0.26, 0.22, 0.17)
LEG_TIP = (0.44, 0.36, 0.26)
FANG = (0.10, 0.06, 0.04)
EYE = (0.72, 0.70, 0.62)
SILK = (0.86, 0.84, 0.78)

BASE = 0.11


def build():
    mb = nh.MeshBuilder()
    c = Vector((0, -0.28, BASE + 0.045))
    mb.add(nh.uv_ellipsoid(c, (0.13, 0.15, 0.06), 16, 8, deform=lambda n: 0.7 if n.z < 0 else 1.0), ar.glossy(BODY))
    for s in (-1, 1):
        for k in range(3):
            mb.add(nh.ellipsoid(c + Vector((s * (0.018 + 0.02 * k), -0.11 + 0.012 * k, 0.045 - 0.008 * k)),
                                (0.010,) * 3, 1), EYE)
        # chelicerae with fangs
        ch = c + Vector((s * 0.035, -0.15, -0.02))
        mb.add(nh.uv_ellipsoid(ch, (0.030, 0.035, 0.035), 8, 5), ar.glossy(BODY))
        mb.add(nh.tube([ch + Vector((0, -0.02, -0.02)), ch + Vector((-s * 0.015, -0.03, -0.06))], [0.010, 0.0],
                       sides=5), FANG)
    # segmented opisthosoma
    for i in range(8):
        y = -0.12 + i * 0.055
        w = 0.15 * (1.0 - ((i - 2.5) / 6.0) ** 2)
        ar.plate(mb, (0, y, BASE + 0.05 - i * 0.004), (w, 0.04, 0.05), ar.glossy(nh.lerp(BODY, RIM, 0.15 * (i % 2))),
                 12, 6)
    # silk spigot plates underneath
    for k in range(2):
        mb.add(nh.uv_ellipsoid((0, 0.06 + 0.06 * k, BASE + 0.005), (0.05, 0.02, 0.008), 8, 4), SILK)
    # flagellum: jointed whip tail curving up and back
    pts = [Vector((0, 0.30 + 0.06 * k, BASE + 0.04 + 0.02 * k - 0.003 * k * k)) for k in range(10)]
    ar.jointed(mb, pts, [0.020 - 0.0018 * k for k in range(10)], ar.glossy(BODY), RIM, sides=5)
    for s in (-1, 1):
        root = Vector((s * 0.06, -0.40, BASE + 0.02))
        ar.jointed(mb, [root, root + Vector((s * 0.08, -0.06, 0.05)), root + Vector((s * 0.06, -0.16, 0.0))],
                   [0.018, 0.016, 0.010], ar.glossy(LEG), RIM)
        for hy, reach, splay in ((-0.36, -0.36, 0.48), (-0.31, -0.14, 0.58), (-0.25, 0.10, 0.58), (-0.19, 0.34, 0.50)):
            ar.leg(mb, s, (0.10, hy, BASE + 0.02), reach, splay, BASE + 0.18, 0.016, ar.glossy(LEG), RIM, LEG_TIP)
    return ar.finish_ground(mb, NAME, BASE + 0.02)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
