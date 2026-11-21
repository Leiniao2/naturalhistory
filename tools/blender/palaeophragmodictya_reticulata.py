"""
Procedural Palaeophragmodictya reticulata (Ediacaran possible glass sponge) for the map, Fixed style.

A low, round dome sitting on the seabed, its surface netted with a raised lattice of fine
spicule bundles: radial struts crossed by concentric rings, with a small opening at the top.
One large and two small. Pale ivory lattice over a buff-grey body. Pivot at the base
(z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Palaeophragmodictya.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.62, 0.58, 0.50)
LATTICE = (0.95, 0.92, 0.84)
OSCULUM = (0.18, 0.16, 0.14)


def net(r, th):
    radial = (0.5 + 0.5 * math.cos(th * 28)) ** 8
    ring = (0.5 + 0.5 * math.cos(r * 9 * math.tau)) ** 8
    return max(radial, ring) * nh.smoothstep(0.08, 0.16, r)


def height(r, th):
    h = 0.45 * (1 - r ** 2) ** 0.6 + 0.02
    h += 0.018 * net(r, th)
    h -= 0.06 * math.exp(-(r / 0.07) ** 2)
    return h


def color(r, th, co):
    c = nh.lerp(BODY, LATTICE, net(r, th))
    c = nh.lerp(c, OSCULUM, math.exp(-(r / 0.07) ** 2))
    return ep.mottle(c, co, 0.05)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.8)
    for x, y, R in [(-0.05, 0.05, 0.5), (0.5, -0.32, 0.22), (-0.45, -0.38, 0.17)]:
        d = ep.polar_disc(R, lambda r, th, R=R: height(r, th) * R, color, rings=int(26 * R / 0.5) + 8, segs=int(84 * R / 0.5) + 28)
        ep.place(d[0], x, y)
        ep.add(mb, d)
    return ep.finish(mb, "Palaeophragmodictya")


if __name__ == "__main__":
    ep.export(build, "Palaeophragmodictya")
