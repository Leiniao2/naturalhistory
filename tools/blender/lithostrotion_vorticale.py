"""
Procedural Lithostrotion vorticale (Early Carboniferous colonial rugose coral) for map colonies
(Fixed style).

A low, rounded fasciculate colony: a dense bundle of several dozen slender, cylindrical
corallites growing up side by side from a shared base on the sea floor, some splitting into
two, each tube ringed with fine growth wrinkles. Every open top shows a cup with radiating
septa and a raised central columella, and the living polyp spreads a crown of short orange-
brown tentacles. Tan / grey-brown stony tubes. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lithostrotion_vorticale.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lithostrotion.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "Lithostrotion"
TUBE_A = (0.74, 0.62, 0.44)
TUBE_B = (0.56, 0.45, 0.32)
CUP = (0.30, 0.22, 0.15)
SEPTA = (0.80, 0.72, 0.58)
POLYP = (0.82, 0.46, 0.18)
POLYP_TIP = (0.95, 0.75, 0.45)
BASE = (0.40, 0.36, 0.30)
SEABED = (0.52, 0.50, 0.42)
SEABED_DARK = (0.38, 0.37, 0.32)
R = 0.036   # corallite radius


def corallite(mb, rng, p0, top, r):
    """Wrinkled tube from p0 to top, cup with septa, polyp crown."""
    axis = (top - p0)
    L = axis.length
    n = max(4, int(L / 0.06))
    pts, rads = [], []
    for i in range(n + 1):
        t = i / n
        q = p0.lerp(top, t) + Vector((noise.noise(p0 * 9 + Vector((t, 0, 0))) * 0.01, 0, 0))
        pts.append(q)
        rads.append(r * (1.0 + (0.12 if i % 2 else 0.0)) * (1.15 if i == n else 1.0))

    def tube_col(co, nn, p0=p0):
        k = 0.5 + 0.5 * noise.noise(co * 25.0)
        return nh.lerp(TUBE_B, TUBE_A, k)
    mb.add(nh.tube(pts, rads, sides=7, cap_end=False), tube_col)
    d = axis.normalized()
    # cup: dark disc just under the rim, septa radiating, columella
    mb.add(nh.ellipsoid(tuple(top - d * 0.004), (r * 1.05, r * 1.05, r * 0.25), 1), CUP)
    side = d.cross(Vector((0, 1, 0))).normalized()
    up = d.cross(side).normalized()
    for k in range(6):
        a = k / 6 * math.tau
        e = side * math.cos(a) + up * math.sin(a)
        mb.add(nh.tube([top + e * r * 0.25, top + e * r * 1.05], [0.004, 0.003], sides=3), SEPTA)
    mb.add(nh.ellipsoid(tuple(top + d * 0.004), (r * 0.25, r * 0.25, r * 0.3), 1), SEPTA)
    # polyp crown on most corallites
    if rng.random() < 0.75:
        for k in range(6):
            a = k / 6 * math.tau + rng.uniform(-0.2, 0.2)
            e = side * math.cos(a) + up * math.sin(a)
            b = top + e * r * 0.8 + d * 0.004
            tip = b + (e * 0.55 + d).normalized() * r * 1.2

            def pc(co, nn, b=b):
                return nh.lerp(POLYP, POLYP_TIP, min(1.0, (co - b).length / (R * 1.2)))
            mb.add(nh.tube([b, b.lerp(tip, 0.5), tip], [0.007, 0.005, 0.0], sides=4), pc)


def build():
    rng = random.Random(3)
    mb = nh.MeshBuilder()

    def bed(n):
        return 1.0 + 0.12 * noise.noise(n * 2.5)
    mb.add(nh.ellipsoid((0, 0, 0.01), (0.70, 0.64, 0.05), subdivisions=3, deform=bed),
           lambda co, n: nh.lerp(SEABED_DARK, SEABED, 0.5 + 0.5 * noise.noise(co * 8.0)))
    # shared base of old, dead corallite stumps
    mb.add(nh.ellipsoid((0, 0, 0.05), (0.42, 0.38, 0.09), 2, deform=lambda n: 1 + 0.1 * noise.noise(n * 4)), BASE)

    # corallites on a hex-ish grid within an ellipse; heights form a dome
    pts = []
    step = R * 2.35
    for i in range(-8, 9):
        for j in range(-8, 9):
            x = (i + (0.5 if j % 2 else 0)) * step
            y = j * step * 0.87
            if (x / 0.40) ** 2 + (y / 0.36) ** 2 > 1.0:
                continue
            pts.append(Vector((x + rng.uniform(-0.006, 0.006), y + rng.uniform(-0.006, 0.006), 0.06)))
    for p in pts:
        rr = math.sqrt((p.x / 0.40) ** 2 + (p.y / 0.36) ** 2)
        h = 0.48 * (1 - 0.55 * rr * rr) + rng.uniform(-0.04, 0.04)
        lean = Vector((p.x, p.y, 0)) * 0.35
        top = p + Vector((0, 0, h)) + lean
        if rng.random() < 0.18 and h > 0.3:
            # branching: a short trunk splitting in two
            fork = p.lerp(top, 0.55)
            corallite_trunk = [p, fork]
            mb.add(nh.tube(corallite_trunk, [R * 1.1, R * 1.1], sides=7, cap_end=False), TUBE_B)
            off = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)).normalized() * R * 1.1
            corallite(mb, rng, fork + off * 0.3, top + off, R * 0.85)
            corallite(mb, rng, fork - off * 0.3, top - off - Vector((0, 0, 0.05)), R * 0.85)
        else:
            corallite(mb, rng, p, top, R)

    obj = mb.to_object(NAME, roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.25, 0.32, 0.30), views=((35, 30), (-90, 8), (10, 75)))
