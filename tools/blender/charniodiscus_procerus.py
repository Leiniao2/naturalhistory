"""
Procedural Charniodiscus procerus (Ediacaran arboreomorph frond) for the map, Fixed style.

A tall, narrow, lance-shaped frond on a long bare stalk, anchored by a broad, ringed disc
holdfast. The leaf has a strong central axis and simple primary branches running straight out
to the margin, not the fractal rangeomorph branching of Charnia. Two fronds, one tall, one
young. Greyish rose, darker branch furrows. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Charniodiscus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CREST = (0.84, 0.66, 0.64)
BLADE = (0.70, 0.52, 0.50)
FURROW = (0.36, 0.22, 0.22)
AXIS = (0.60, 0.44, 0.40)
STALK = (0.55, 0.42, 0.38)
DISC = (0.66, 0.54, 0.46)


def leaf(length, prim):
    width = length * 0.17

    def wfn(v):
        return math.sin(math.pi * min(1.0, v)) ** 0.6 * (1.0 - 0.3 * v)

    def stripes(s, v):
        t = (v * prim - abs(s) * 0.25 + (0.5 if s < 0 else 0)) % 1.0
        return 1.0 - nh.smoothstep(0.0, 0.22, min(t, 1 - t))

    def relief(s, v, front):
        return 0.012 * length * (1 - stripes(s, v)) + 0.02 * length * nh.smoothstep(0.12, 0.0, abs(s))

    def color(s, v, front):
        f = stripes(s, v)
        c = nh.lerp(CREST, BLADE, 0.3 + 0.3 * abs(s))
        c = nh.lerp(c, FURROW, f * 0.8)
        return nh.lerp(c, AXIS, nh.smoothstep(0.1, 0.0, abs(s)))

    return ep.blade(length, width, wfn, relief, color, nv=56, nu=14, thick=0.03 * length)


def disc_height(r, th):
    return 0.05 * (1 - r ** 2) ** 0.6 + 0.006 * math.cos(r * 5 * math.tau) + 0.008


def disc_color(r, th, co):
    ring = 0.5 + 0.5 * math.cos(r * 5 * math.tau)
    c = nh.lerp(DISC, (0.48, 0.38, 0.32), ring * 0.55)
    return ep.mottle(nh.lerp(c, STALK, nh.smoothstep(0.2, 0.0, r)), co)


def frond(mb, x, y, h, yaw):
    stalk = h * 0.4
    mb.add(ep.place(nh.tube([(0, 0, 0.0), (0, 0, stalk * 0.5), (0, 0, stalk + 0.02)], [0.03 * h, 0.022 * h, 0.02 * h],
                            sides=8), x, y, yaw), STALK)
    p = leaf(h - stalk, round(26 * h / 1.6 + 6))
    ep.place(p[0], 0, 0, 0, 0, z=stalk)
    ep.place(p[0], x, y, yaw)
    ep.add(mb, p)
    d = ep.polar_disc(0.2 * h, lambda r, th: disc_height(r, th) * h, disc_color, rings=12, segs=32)
    ep.place(d[0], x, y)
    ep.add(mb, d)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.6)
    frond(mb, 0.0, 0.05, 1.7, 10)
    frond(mb, 0.36, -0.12, 0.85, -35)
    return ep.finish(mb, "Charniodiscus")


if __name__ == "__main__":
    ep.export(build, "Charniodiscus")
