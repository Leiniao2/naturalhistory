"""
Procedural Vendoconularia triradiata (Ediacaran conulariid-like cnidarian) for the map, Fixed style.

Upright, six-sided pyramids standing on their points: each flat face crossed by fine
transverse ribs, the corners marked by grooves, and the wide top opening, where soft
tentacles may have spread, set back inside a raised rim. Three of different sizes; pale
horn-yellow walls with brown ribs. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Vendoconularia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402
import nh_edi_kit as kit  # noqa: E402

WALL = (0.94, 0.80, 0.52)
RIB = (0.66, 0.44, 0.24)
CORNER = (0.40, 0.30, 0.20)
INSIDE = (0.20, 0.14, 0.10)
TENT = (0.92, 0.70, 0.62)


def hexr(th):
    seg = math.pi / 3
    a = (th % seg) - seg / 2
    return math.cos(seg / 2) / math.cos(a)


def pyramid(H, R):
    def shape(u, v):
        th = u * math.tau
        k = hexr(th) * (1 - 0.06 * math.exp(-(((th % (math.pi / 3)) - 0) / 0.08) ** 2))
        if v <= 0.85:
            t = v / 0.85
            r = (0.01 + R * t) * k * (1 + 0.025 * math.cos(t * 36 * math.pi))
            return r, H * t
        t = (v - 0.85) / 0.15
        return R * k * (1 - 0.3 * t), H * (1 - 0.1 * t)

    def color(u, v, co):
        if v > 0.86:
            return nh.lerp(WALL, INSIDE, nh.smoothstep(0.86, 0.92, v))
        th = u * math.tau
        a = (th % (math.pi / 3))
        corner = math.exp(-(min(a, math.pi / 3 - a) / 0.06) ** 2)
        rib = 0.5 + 0.5 * math.cos(v / 0.85 * 36 * math.pi)
        c = nh.lerp(WALL, RIB, rib * 0.5)
        return nh.lerp(c, CORNER, corner * 0.8)

    return ep.lathe(48, 30, shape, color)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.6)
    for x, y, H, R, yaw, lean in [(0, 0.05, 1.2, 0.28, 0, 5), (0.36, -0.2, 0.8, 0.19, 20, -10), (-0.33, -0.15, 0.6, 0.14, 40, 12)]:
        p = pyramid(H, R)
        ep.place(p[0], x, y, yaw, lean, z=-0.04)
        ep.add(mb, p)
        # a short fringe of soft tentacles from the aperture
        top = (x, y + 0.0, H * 0.96 - 0.04)
        bm = nh.MeshBuilder()
        kit.crown(bm, (0, 0, 0), R * 0.45, 10, R * 1.1, R * 0.08, TENT, spread=22, droop=-0.1, seed=int(H * 10))
        s = bm.bm.copy()
        bm.bm.free()
        ep.place(s, 0, 0, 0, 0, z=H * 0.86)
        ep.place(s, x, y, yaw, lean, z=-0.04)
        mb.add(s, TENT)
    return ep.finish(mb, "Vendoconularia")


if __name__ == "__main__":
    ep.export(build, "Vendoconularia")
