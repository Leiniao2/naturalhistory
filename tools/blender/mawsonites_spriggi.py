"""
Procedural Mawsonites spriggi (Ediacaran disc) for the map, Fixed style.

A large, flower-like disc: a smooth central dome surrounded by rings of rounded lobes that
grow bigger and more numerous toward the margin, so the whole looks like a rosette or a
cauliflower seen from above. One big individual and a young one. Warm sandy-pink, the lobes
picked out by darker furrows. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Mawsonites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

LOBE = (0.88, 0.70, 0.56)
BODY = (0.74, 0.55, 0.42)
FURROW = (0.42, 0.28, 0.20)
CORE = (0.92, 0.80, 0.64)
RINGS = [(0.30, 8), (0.48, 12), (0.66, 16), (0.85, 22)]


def lobes(r, th):
    """0..1 lobe bump field and furrow strength."""
    best = 0.0
    for i, (rc, n) in enumerate(RINGS):
        w = 0.08 + 0.015 * i
        radial = math.exp(-((r - rc) / w) ** 2)
        ang = 0.5 + 0.5 * math.cos(th * n + i * 0.7)
        best = max(best, radial * ang ** 0.6)
    return best


def height(r, th):
    h = 0.10 * (1 - r * r) ** 0.5 + 0.02
    h += 0.10 * math.exp(-(r / 0.18) ** 2)
    h += 0.05 * lobes(r, th) * nh.smoothstep(0.15, 0.25, r)
    return h


def color(r, th, co):
    b = lobes(r, th) * nh.smoothstep(0.15, 0.25, r)
    c = nh.lerp(FURROW, LOBE, nh.smoothstep(0.15, 0.7, b))
    c = nh.lerp(c, CORE, math.exp(-(r / 0.18) ** 2))
    return ep.mottle(c, co, 0.06)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.9)
    d = ep.polar_disc(0.62, height, color, rings=36, segs=110)
    ep.place(d[0], -0.1, 0.05)
    ep.add(mb, d)
    d = ep.polar_disc(0.22, lambda r, th: height(r, th) * 0.5, color, rings=20, segs=60)
    ep.place(d[0], 0.6, -0.4, 40)
    ep.add(mb, d)
    return ep.finish(mb, "Mawsonites")


if __name__ == "__main__":
    ep.export(build, "Mawsonites")
