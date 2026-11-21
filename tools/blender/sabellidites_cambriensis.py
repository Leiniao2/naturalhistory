"""
Procedural Sabellidites cambriensis (latest Ediacaran tube worm) for the map, Fixed style.

Long, thin, flexible tubes of tough organic material, finely ringed and bending as they rise
from the mat or lie sprawled over it, built by a small worm-like animal that may be one of
the first annelids. A tangle of eleven tubes; dark chestnut with paler rings and open tops.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Sabellidites.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402
from mathutils import Vector  # noqa: E402

DARK = (0.36, 0.22, 0.14)
LIGHT = (0.62, 0.44, 0.30)
MOUTH = (0.10, 0.06, 0.04)


def tube(rng, start, d, L, r, n=18):
    pts, radii = [], []
    p, d = Vector(start), Vector(d).normalized()
    bend = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 0.3))) * 0.06
    for i in range(n + 1):
        pts.append(p.copy())
        radii.append(r * (0.85 + 0.15 * i / n))
        d = (d + bend + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.03).normalized()
        p = p + d * L / n
    bm = nh.tube(pts, radii, sides=7, cap_end=True)
    top, axis = pts[-1], (pts[-1] - pts[-2]).normalized()
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + (b - a).length)

    def col(co, n_):
        k = min(range(len(pts)), key=lambda i: (pts[i] - co).length)
        if (co - top).dot(axis) > -r * 0.2 and (co - top).length < r * 1.05:
            return MOUTH
        ring = 0.5 + 0.5 * math.cos(s[k] / (r * 1.6) * math.tau)
        return nh.lerp(DARK, LIGHT, ring * 0.55 * (0.6 + 0.4 * k / n))

    return bm, col


def build():
    rng = random.Random(14)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.65)
    for i in range(11):
        a, rr = rng.uniform(0, math.tau), rng.uniform(0, 0.42)
        p = (math.cos(a) * rr, math.sin(a) * rr, 0.0)
        if i < 7:
            el = math.radians(rng.uniform(45, 85))
            L = rng.uniform(0.8, 1.4)
        else:
            el = math.radians(rng.uniform(3, 8))
            L = rng.uniform(0.6, 0.9)
        az = rng.uniform(0, math.tau)
        d = (math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))
        bm, col = tube(rng, p, d, L, rng.uniform(0.022, 0.03))
        mb.add(bm, col)
    return ep.finish(mb, "Sabellidites")


if __name__ == "__main__":
    ep.export(build, "Sabellidites")
