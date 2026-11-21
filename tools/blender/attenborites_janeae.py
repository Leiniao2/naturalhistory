"""
Procedural Attenborites janeae (Ediacaran problematic animal) for the map, Fixed style.

Tiny, plump ovals, under a centimetre long, lying in small groups on the mat, their surface
wrinkled by irregular lengthwise grooves and ridges like a raisin. What they were remains a
mystery. A cluster of eight. Plum-brown with darker grooves. Pivot at the base (z = 0),
faces -Y.

Output: Assets/Resources/Models/Species/Attenborites.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SKIN = (0.58, 0.36, 0.30)
LIGHT = (0.78, 0.54, 0.44)
GROOVE = (0.30, 0.16, 0.14)


def raisin(rng, L):
    seed = Vector((rng.uniform(0, 50), rng.uniform(0, 50), 0))

    def wr(n):
        a = math.atan2(n.z, n.x)
        w = math.cos(a * 7 + 1.5 * noise.noise(n * 2.0 + seed))
        return 1.0 + 0.06 * w + 0.04 * noise.noise(n * 3.0 + seed)

    bm = nh.ellipsoid((0, 0, 0), (L * 0.36, L * 0.5, L * 0.26), subdivisions=3, deform=wr)

    def col(co, n):
        d = Vector((co.x / (L * 0.36), co.y / (L * 0.5), co.z / (L * 0.26))).normalized()
        a = math.atan2(d.z, d.x)
        w = math.cos(a * 7 + 1.5 * noise.noise(d * 2.0 + seed))
        c = nh.lerp(SKIN, LIGHT, nh.smoothstep(0.3, 1.0, w))
        return nh.lerp(c, GROOVE, nh.smoothstep(-0.5, -1.0, w))

    return bm, col


def build():
    rng = random.Random(12)
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.7)
    spots = []
    while len(spots) < 8:
        a, rr = rng.uniform(0, math.tau), rng.uniform(0, 0.5)
        L = rng.uniform(0.25, 0.42)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        if all(math.hypot(x - p, y - q) > (L + s) * 0.45 for p, q, s in spots):
            spots.append((x, y, L))
    for x, y, L in spots:
        bm, col = raisin(rng, L)
        ep.place(bm, x, y, rng.uniform(0, 180), rng.uniform(-10, 10), z=L * 0.18)
        mb.add(bm, col)
    return ep.finish(mb, "Attenborites")


if __name__ == "__main__":
    ep.export(build, "Attenborites")
