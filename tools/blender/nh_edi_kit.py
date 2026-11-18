"""
Small shared kit for the combat-distinctive Ediacaran / Cambrian batch (auroralumina_attenboroughii.py,
haootia_quadriformis.py, pambdelurion_whiteleggei.py, ...). Builds on nh_model.py and nh_edicam.py.

  * curve(p0, p1, p2, n)            points along a quadratic Bezier
  * tentacle(root, dirn, length, r) tapering, curling tentacle tube
  * crown(mb, centre, radius, ...)  ring of tentacles round an oral disc
  * ringed(c_light, c_dark, ...)    colour fn: bands along Z (tubes, stalks)
  * mottled(c, amount, scale)       colour fn: faint noise mottling
  * lobopod(mb, base, down, ...)    stubby annulated lobopod leg with a claw
  * align(bm, d)                    rotate a shell so its +Z axis points along d

All animals face -Y, Z up, colour in vertex colours.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402


def curve(p0, p1, p2, n=6):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t)
    return out


def tentacle(root, dirn, length, r, curl=(0, 0, -0.3), n=6, sides=5):
    """Tube from root along dirn, bending toward curl (a direction added at the tip)."""
    root, d = Vector(root), Vector(dirn).normalized()
    mid = root + d * length * 0.55
    tip = root + (d + Vector(curl)).normalized() * length
    pts = curve(root, mid, tip, n)
    radii = [r * (1 - i / n) ** 0.8 for i in range(n + 1)]
    radii[-1] = 0.0
    return nh.tube(pts, radii, sides=sides)


def crown(mb, centre, radius, count, length, r, color, up=(0, 0, 1), spread=55, droop=-0.35,
          jitter=0.15, seed=1, sides=5):
    """count tentacles evenly round a circle (centre, radius) in the plane normal to up,
    leaning out spread degrees from up and curling droop at the tips."""
    import random
    rng = random.Random(seed)
    c, u = Vector(centre), Vector(up).normalized()
    a0 = Vector((1, 0, 0)) if abs(u.x) < 0.9 else Vector((0, 1, 0))
    s1 = u.cross(a0).normalized()
    s2 = u.cross(s1).normalized()
    for k in range(count):
        a = k / count * math.tau + rng.uniform(-0.1, 0.1)
        out = s1 * math.cos(a) + s2 * math.sin(a)
        root = c + out * radius
        sp = math.radians(spread + rng.uniform(-12, 12))
        d = u * math.cos(sp) + out * math.sin(sp)
        ln = length * (1 + rng.uniform(-jitter, jitter))
        mb.add(tentacle(root, d, ln, r, curl=tuple(out * 0.2 + u * droop), sides=sides), color)


def ringed(light, dark, period=0.05, sharp=0.35, axis=2):
    def color(co, n):
        t = (co[axis] / period) % 1.0
        band = 1.0 - nh.smoothstep(0.0, sharp, min(t, 1.0 - t))
        return nh.lerp(light, dark, band)
    return color


def mottled(c, amount=0.12, scale=8.0, seed=0.0):
    def color(co, n):
        k = 1.0 + amount * noise.noise(Vector((co.x * scale + seed, co.y * scale, co.z * scale)))
        return tuple(min(1.0, x * k) for x in c)
    return color


def align(bm, d):
    rot = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_matrix().to_4x4()
    nh.transform(bm, rot)
    return bm


def lobopod(mb, base, down, length, r, color, claw=None, rings=4):
    """Stubby annulated lobopod: a tapering tube from base toward down, with optional claws."""
    base, d = Vector(base), Vector(down).normalized()
    pts, radii = [], []
    n = rings * 2
    for i in range(n + 1):
        t = i / n
        pts.append(base + d * length * t)
        radii.append(r * (1 - 0.45 * t) * (0.86 if i % 2 else 1.0))
    mb.add(nh.tube(pts, radii, sides=6), color)
    if claw is not None:
        tip = pts[-1]
        for s in (-1, 1):
            side = Vector((s * 0.4, -0.6, 0)).normalized()
            mb.add(nh.tube([tip, tip + d * r * 0.8 + side * r * 0.6, tip + d * r * 1.2 + side * r * 1.4],
                           [r * 0.3, r * 0.18, 0.0], sides=4), claw)
