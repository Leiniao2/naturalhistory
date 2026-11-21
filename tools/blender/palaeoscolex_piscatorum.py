"""
Procedural Palaeoscolex piscatorum (Early Ordovician palaeoscolecid worm, Wales) for map
colonies (Swim style, like the other sea-floor worms).

A slender, cylindrical worm several centimetres long, a cousin of the priapulid worms:
its body is divided into many fine rings (annuli), each studded with rows of tiny
phosphatic plates and bumps, giving it a beaded, armoured skin. At the front an eversible
proboscis (introvert) ringed with small hooks could be shot out to grip the mud or
seize prey as it burrowed through the sea floor. Shown in a loose S-curve with the
proboscis out. Dull pinkish-brown, paler plates. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/palaeoscolex_piscatorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeoscolexPiscatorum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "PalaeoscolexPiscatorum"
BODY = (0.66, 0.46, 0.40)
RING = (0.42, 0.28, 0.24)
PLATE = (0.88, 0.76, 0.62)
PROBO = (0.80, 0.56, 0.46)
HOOK = (0.30, 0.20, 0.14)


def path(t):
    """Centre line, t 0 (front) .. 1 (back)."""
    y = -0.85 + 1.7 * t
    x = 0.16 * math.sin(t * math.tau * 1.1 + 0.4)
    z = 0.02 * math.sin(t * math.tau * 2.0)
    return Vector((x, y, z))


def body_col(co, n):
    ann = 0.5 + 0.5 * math.cos(co.y * 230)
    c = nh.lerp(BODY, RING, 0.75 * nh.smoothstep(0.75, 1.0, ann))
    # rows of tiny plates: dots on the annuli
    dot = 0.5 + 0.5 * math.cos(math.atan2(n.z, n.x) * 14)
    c = nh.lerp(c, PLATE, 0.7 * nh.smoothstep(0.85, 1.0, dot) * (1 - nh.smoothstep(0.3, 0.6, ann)))
    return c


def build():
    mb = nh.MeshBuilder()
    n = 60
    pts = [path(i / n) for i in range(n + 1)]
    radii = []
    for i in range(n + 1):
        t = i / n
        r = 0.075 * (0.85 + 0.15 * math.sin(t * math.pi)) * (1 - nh.smoothstep(0.9, 1.0, t) * 0.6)
        radii.append(r)
    radii[-1] = 0.02
    mb.add(nh.tube(pts, radii, sides=14), body_col)
    # everted proboscis in front, with rings of small hooks
    p0 = pts[0]
    d = (pts[0] - pts[1]).normalized()
    probo = [p0, p0 + d * 0.06, p0 + d * 0.13, p0 + d * 0.18]
    mb.add(nh.tube(probo, [0.07, 0.065, 0.055, 0.035], sides=14), PROBO)
    side = d.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(d).normalized()
    for ring in range(3):
        c = p0 + d * (0.04 + 0.05 * ring)
        r = 0.068 - 0.01 * ring
        for k in range(10):
            a = k / 10 * math.tau + ring * 0.3
            o = side * math.cos(a) + up * math.sin(a)
            b = c + o * r
            mb.add(nh.tube([b, b + o * 0.025 - d * 0.02], [0.007, 0.0], sides=3), HOOK, smooth=False)
    # mouth
    mb.add(nh.ellipsoid(tuple(p0 + d * 0.18), (0.022, 0.022, 0.022), 1), HOOK)
    return kit.finish_swim(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.SWIM_VIEWS)
