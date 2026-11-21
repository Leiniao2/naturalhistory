"""
Procedural Hallopora elegantula (a trepostome bryozoan - a "stony moss animal" colony -
from the Silurian of North America and Britain) for map colonies (Fixed).

A colony of thousands of tiny filter-feeding zooids living in tubes packed into
slender, cylindrical, forking stony branches a few millimetres thick, forming small
bushy thickets a few centimetres high on the reef floor. The branch surfaces are
covered with tiny round openings of the zooid tubes, with low, regularly spaced
bumps (monticules). Shown as two bushy colonies on a patch of mud; tan-orange.
Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/hallopora_elegantula.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HalloporaElegantula.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "HalloporaElegantula"
BODY = (0.82, 0.58, 0.36)
PIT = (0.42, 0.24, 0.14)
TIP = (0.94, 0.80, 0.62)


def col(co, n):
    # tiny zooecial openings as a dotted lattice, paler monticule bumps, pale growing tips
    k = noise.noise(co * 60.0)
    c = nh.lerp(BODY, PIT, 0.7 * nh.smoothstep(0.25, 0.45, k))
    c = nh.lerp(c, TIP, 0.35 * nh.smoothstep(0.3, 0.5, noise.noise(co * 12.0 + Vector((4, 1, 2)))))
    return c


def branch(mb, rnd, p, d, L, r, level):
    steps = 4
    pts = [p.copy()]
    q, dd = p.copy(), d.copy()
    for i in range(steps):
        dd = (dd + Vector((rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), 0.12))).normalized()
        q = q + dd * (L / steps)
        pts.append(q.copy())
    mb.add(nh.tube(pts, [r] * steps + [r * (0.9 if level < 3 else 0.6)], sides=8), col)
    mb.add(nh.ellipsoid(tuple(q), (r * 0.9, r * 0.9, r * 0.9), subdivisions=1), TIP)
    if level < 3:
        side = dd.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = Vector((1, 0, 0))
        side.normalize()
        rot = rnd.uniform(0, math.tau)
        side = side * math.cos(rot) + dd.cross(side) * math.sin(rot)
        for sg in (-1, 1):
            branch(mb, rnd, q, (dd + side * sg * 0.7).normalized(), L * 0.8, r * 0.88, level + 1)


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.95, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    rnd = random.Random(4)
    for x, y, k in ((-0.20, -0.10, 1.0), (0.40, 0.30, 0.75)):
        base = Vector((x, y, 0.0))
        branch(mb, rnd, base, Vector((0, 0, 1)), 0.32 * k, 0.045 * k, 0)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
