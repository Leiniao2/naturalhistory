"""
Procedural Primocandelabrum hiemaloranum (Ediacaran rangeomorph) for the map, Fixed style.

A tall, candelabra-like frond: a long bare stalk rising from a ringed disc holdfast, crowned by
a bushy head of branched rangeomorph frondlets that fan up and out like a shaving brush.
Ochre-tan crown on a darker stalk. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Primocandelabrum.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CREST = (0.92, 0.72, 0.48)
BLADE = (0.80, 0.56, 0.34)
FURROW = (0.40, 0.24, 0.14)
STALK = (0.56, 0.40, 0.28)
DISC = (0.60, 0.50, 0.38)


def frondlet(length, width, prim):
    def wfn(v):
        return math.sin(math.pi * min(1.0, v * 0.97 + 0.02)) ** 0.8 * (0.4 + 0.6 * v)

    def relief(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.8, secondaries=3)
        return 0.012 * (1 - f)

    def color(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.8, secondaries=3)
        c = nh.lerp(CREST, BLADE, 0.4 * (1 - sec))
        c = nh.lerp(c, FURROW, f * 0.75)
        return nh.lerp(c, STALK, nh.smoothstep(0.12, 0.0, v))

    return ep.blade(length, width, wfn, relief, color, nv=20, nu=12, thick=0.02, cup=0.25)


def disc_height(r, th):
    return 0.035 * (1 - r * r) + 0.004 * math.cos(r * 6 * math.tau) + 0.01


def disc_color(r, th, co):
    ring = 0.5 + 0.5 * math.cos(r * 6 * math.tau)
    return ep.mottle(nh.lerp(DISC, nh.lerp(DISC, ep.SAND, 0.5), ring * 0.6), co)


def one(mb, x, y, h, rng):
    top = h * 0.55
    mb.add(ep.place(nh.tube([(0, 0, 0.0), (0, 0, top * 0.5), (0.01, 0, top), (0.0, 0, top + 0.06)],
                            [0.035, 0.026, 0.022, 0.03], sides=8), x, y), STALK)
    ep.add(mb, (lambda p: (ep.place(p[0], x, y), p[1]))(ep.polar_disc(0.17, disc_height, disc_color, rings=10, segs=28)))
    n = 8
    for i in range(n):
        yaw = i / n * 360 + rng.uniform(-12, 12)
        L = h * rng.uniform(0.38, 0.48)
        p = frondlet(L, L * 0.28, 6)
        ep.place(p[0], 0, 0, yaw, -rng.uniform(18, 40))
        ep.place(p[0], x, y, 0, 0, z=top)
        ep.add(mb, p)
    for i in range(3):
        p = frondlet(h * 0.36, h * 0.09, 5)
        ep.place(p[0], 0, 0, i * 120, -6)
        ep.place(p[0], x, y, 0, 0, z=top)
        ep.add(mb, p)


def build():
    rng = random.Random(8)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.6)
    one(mb, 0.0, 0.05, 1.6, rng)
    one(mb, 0.32, -0.22, 1.05, rng)
    return ep.finish(mb, "Primocandelabrum")


if __name__ == "__main__":
    ep.export(build, "Primocandelabrum")
