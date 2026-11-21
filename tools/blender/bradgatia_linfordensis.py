"""
Procedural Bradgatia linfordensis (Ediacaran rangeomorph) for the map, Fixed style.

A low, cabbage-like bush: eight spoon-shaped, cupped frondlets fan out in every direction from
one buried base, each covered in the self-similar rangeomorph branching (oblique primary
furrows alternating either side of a midline, corrugated by secondaries). Pale pinkish tan.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Bradgatia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CREST = (0.90, 0.72, 0.60)
BLADE = (0.78, 0.56, 0.45)
FURROW = (0.38, 0.22, 0.17)
BASE = (0.55, 0.40, 0.32)


def frondlet(length, width, prim):
    def wfn(v):
        return math.sin(math.pi * min(1.0, v * 0.95 + 0.04)) ** 0.7 * (0.35 + 0.65 * v)

    def relief(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.9, secondaries=3)
        return 0.018 * (1 - f) * (0.7 + 0.3 * sec)

    def color(s, v, front):
        f, sec = ep.rangeo(s, v, prim, slant=0.9, secondaries=3)
        c = ep.nh.lerp(CREST, BLADE, 0.4 * (1 - sec))
        c = ep.nh.lerp(c, FURROW, f * 0.8)
        c = c if front else ep.nh.lerp(c, BLADE, 0.4)
        return ep.nh.lerp(c, BASE, nh.smoothstep(0.15, 0.0, v))

    return ep.blade(length, width, wfn, relief, color, nv=26, nu=14, thick=0.025, cup=0.35,
                    bend=lambda v: 0.12 * v * v)


def build():
    rng = random.Random(4)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.75)
    n = 9
    for i in range(n):
        yaw = i / n * 360 + rng.uniform(-10, 10)
        lean = rng.uniform(35, 62)
        L = rng.uniform(0.55, 0.75)
        bm = frondlet(L, L * 0.38, rng.randint(7, 9))
        ep.place(bm[0], 0, 0, yaw, -lean, z=0.02)
        ep.add(mb, bm)
    for i in range(4):   # a few young frondlets upright in the middle
        yaw = i * 90 + 45
        bm = frondlet(0.42, 0.15, 6)
        ep.place(bm[0], 0, 0, yaw, -14, z=0.02)
        ep.add(mb, bm)
    mb.add(nh.uv_ellipsoid((0, 0, 0.02), (0.13, 0.13, 0.07), 16, 6), BASE)
    return ep.finish(mb, "Bradgatia")


if __name__ == "__main__":
    ep.export(build, "Bradgatia")
