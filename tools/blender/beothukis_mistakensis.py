"""
Procedural Beothukis mistakensis (Ediacaran rangeomorph) for the map, Fixed style.

Spoon- or paddle-shaped fronds, widest toward the rounded top, on a very short stem: a few
large first-order branches climb obliquely from the midline, each crossed by clearly visible
secondary branches. A small stand of three fronds of different heights. Pale salmon-grey.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Beothukis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CREST = (0.88, 0.74, 0.66)
BLADE = (0.72, 0.56, 0.50)
FURROW = (0.34, 0.22, 0.20)
STEM = (0.52, 0.40, 0.36)


def frond(length, prim):
    width = length * 0.24

    def wfn(v):
        return (min(1.0, v * 4.0) ** 0.6) * (0.25 + 0.75 * math.sin(math.pi * 0.5 * min(1.0, v / 0.72))) \
            * math.sqrt(max(0.0, 1 - max(0.0, (v - 0.72) / 0.28) ** 2))

    def relief(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.7, secondaries=4)
        return (0.018 * (1 - f) + 0.006 * sec) * length

    def color(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.7, secondaries=4)
        c = nh.lerp(CREST, BLADE, 0.55 * (1 - sec))
        c = nh.lerp(c, FURROW, f * 0.85)
        c = nh.lerp(c, FURROW, nh.smoothstep(0.06, 0.0, abs(s)) * 0.5)
        return nh.lerp(c, STEM, nh.smoothstep(0.12, 0.02, v))

    return ep.blade(length, width, wfn, relief, color, nv=40, nu=16, thick=0.03 * length, cup=0.12,
                    bend=lambda v: 0.08 * length * v * v)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.65)
    for x, y, h, yaw, lean, prim in [(0, 0.05, 1.5, 8, 6, 6), (0.36, 0.2, 1.05, -40, 10, 5), (-0.33, 0.18, 0.8, 55, 12, 5)]:
        p = frond(h, prim)
        ep.place(p[0], x, y, yaw, -lean)
        ep.add(mb, p)
        mb.add(nh.uv_ellipsoid((x, y, 0.0), (0.06 * h, 0.06 * h, 0.03), 12, 5), STEM)
    return ep.finish(mb, "Beothukis")


if __name__ == "__main__":
    ep.export(build, "Beothukis")
