"""
Procedural low-poly Funisia dorothea (Ediacaran tubular organism, Ediacara, South Australia).

A tight clump of slender, flexible, upright tubes of near-identical size, each
divided along its length into short serial units (bead-like rings) and rooted
on a small holdfast; tubes sway slightly apart towards their tips. Pale
olive-tan tubes with darker ring creases on sandy holdfasts.
Pivot on the seabed (Fixed).

Output: Assets/Resources/Models/Species/Funisia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

TUBE = (0.74, 0.70, 0.50)
RING = (0.48, 0.44, 0.30)
TIP = (0.86, 0.82, 0.64)
HOLD = (0.62, 0.54, 0.40)


def build():
    rnd = random.Random(7)
    mb = nh.MeshBuilder()
    n_tubes = 11
    for i in range(n_tubes):
        a = i * 2.39996
        rr = 0.06 * math.sqrt(i + 0.5)
        base = Vector((rr * math.cos(a), rr * math.sin(a), 0.0))
        h = 1.0 + rnd.uniform(-0.12, 0.12)
        lean = Vector((math.cos(a), math.sin(a), 0)) * (0.12 + 0.25 * rr) + \
            Vector((rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06), 0))
        units = 16
        pts, radii = [], []
        for k in range(units * 2 + 1):
            t = k / (units * 2)
            p = base + lean * (t * t) + Vector((0, 0, h * t))
            pts.append(p)
            radii.append(0.03 * (0.8 if k % 2 == 0 else 1.0) * (1 - 0.25 * t))
        radii[-1] = 0.018

        def col(co, n, h=h):
            t = co.z / h
            ring = 0.5 + 0.5 * math.cos(co.z * math.tau * 16 / h)
            c = nh.lerp(TUBE, RING, 0.6 * nh.smoothstep(0.7, 1.0, ring))
            return nh.lerp(c, TIP, nh.smoothstep(0.8, 1.0, t))

        mb.add(nh.tube(pts, radii, sides=7), col)
        mb.add(nh.ellipsoid(base, (0.05, 0.05, 0.02), subdivisions=1), HOLD)
    return ec.ground(mb.to_object("Funisia", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Funisia", fixed=True)
