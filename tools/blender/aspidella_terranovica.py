"""
Procedural Aspidella terranovica (Ediacaran disc) for the map, Fixed style.

A scatter of small, low, rounded discs sunk into the mat, each with a raised rim, a shallow
moat, a central boss and fine radial creases, the buried holdfast-like bodies that crowd
Newfoundland's oldest seafloors. Seven discs of different sizes; grey-buff with darker creases.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Aspidella.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

LIGHT = (0.94, 0.84, 0.74)
BODY = (0.82, 0.64, 0.54)
DARK = (0.46, 0.30, 0.26)


def height(r, th):
    h = 0.16 * (1 - r * r) ** 0.6                          # low dome
    h += 0.05 * math.exp(-(r / 0.16) ** 2)                 # central boss
    h += 0.03 * math.exp(-((r - 0.84) / 0.1) ** 2)         # raised rim
    h += 0.02 + 0.012 * math.cos(th * 28) * nh.smoothstep(0.2, 0.6, r) * (1 - r)
    return h * 1.6


def color(r, th, co):
    crease = 0.5 + 0.5 * math.cos(th * 28)
    c = nh.lerp(BODY, DARK, crease * 0.35 * nh.smoothstep(0.25, 0.6, r) * (1 - nh.smoothstep(0.75, 0.85, r)))
    c = nh.lerp(c, LIGHT, math.exp(-((r - 0.82) / 0.1) ** 2) + math.exp(-(r / 0.15) ** 2))
    c = nh.lerp(c, DARK, math.exp(-((r - 0.55) / 0.12) ** 2) * 0.3)
    return ep.mottle(c, co)


def build():
    rng = random.Random(3)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.85)
    spots = [(0.0, 0.0, 0.26)]
    while len(spots) < 7:
        a, rr = rng.uniform(0, math.tau), rng.uniform(0.25, 0.62)
        R = rng.uniform(0.09, 0.18)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        if all(math.hypot(x - p, y - q) > R + s + 0.03 for p, q, s in spots):
            spots.append((x, y, R))
    for x, y, R in spots:
        d = ep.polar_disc(R, lambda r, th, R=R: height(r, th) * R * 1.6, color, rings=14, segs=40)
        ep.place(d[0], x, y, rng.uniform(0, 360))
        ep.add(mb, d)
    return ep.finish(mb, "Aspidella")


if __name__ == "__main__":
    ep.export(build, "Aspidella")
