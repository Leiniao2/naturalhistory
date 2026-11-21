"""
Procedural Arkarua adami (Ediacaran possible echinoderm) for the map, Fixed style.

A tiny, button-like domed disc with five-fold symmetry: a sunken five-rayed star in the middle,
a smooth raised dome around it and a rim of many short radial ridges, a body plan that hints at
the first echinoderms. A small group of five. Creamy grey with darker star and ridges.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Arkarua.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

BODY = (0.84, 0.80, 0.70)
STAR = (0.36, 0.30, 0.26)
RIDGE = (0.62, 0.56, 0.46)


def star(r, th):
    a = (0.5 + 0.5 * math.cos(5 * th)) ** 10
    return a * (1 - nh.smoothstep(0.35, 0.6, r)) + math.exp(-(r / 0.1) ** 2)


def height(r, th):
    h = 0.3 * (1 - r ** 2) ** 0.7 + 0.05
    h -= 0.07 * star(r, th)
    h += 0.025 * math.cos(th * 30) * nh.smoothstep(0.7, 0.85, r)
    return h


def color(r, th, co):
    c = nh.lerp(BODY, STAR, min(1.0, star(r, th)) * 0.85)
    c = nh.lerp(c, RIDGE, (0.5 - 0.5 * math.cos(th * 30)) * nh.smoothstep(0.7, 0.85, r))
    return ep.mottle(c, co, 0.05)


def build():
    rng = random.Random(2)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.7)
    for x, y, R in [(0, 0, 0.22), (0.4, 0.15, 0.16), (-0.36, 0.2, 0.15), (0.12, -0.42, 0.14), (-0.3, -0.32, 0.12)]:
        d = ep.polar_disc(R, lambda r, th, R=R: height(r, th) * R, color, rings=18, segs=60)
        ep.place(d[0], x, y, rng.uniform(0, 72))
        ep.add(mb, d)
    return ep.finish(mb, "Arkarua")


if __name__ == "__main__":
    ep.export(build, "Arkarua")
