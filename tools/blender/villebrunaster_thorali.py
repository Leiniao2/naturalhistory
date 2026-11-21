"""
Procedural Villebrunaster thorali (Early Ordovician somasteroid, France and Morocco) for map
colonies (Fixed style).

A primitive starfish relative close to the ancestry of sea stars and brittle stars: a
flat, five-armed star several centimetres across, with broad, petal-shaped arms merging
into a small disc. Each arm has a central column of plates from which rows of rod-like
ossicles (virgals) run out to the edges like the ribs of a leaf, giving it a feathery,
herringbone look; between them ran the tube feet. It lay on the sea floor and probably fed
on detritus and organic films. Rust-orange with pale ribs. Pivot on the sea floor (z = 0),
facing -Y.

Usage:
  blender --background --python tools/blender/villebrunaster_thorali.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VillebrunasterThorali.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "VillebrunasterThorali"
BODY = (0.78, 0.42, 0.22)
GROOVE = (0.46, 0.20, 0.10)
RIB = (0.96, 0.78, 0.54)
AXIS = (0.62, 0.30, 0.16)

R = 0.78
Z0 = 0.03


def arm_frame(co):
    """(arm index, distance along the arm, lateral offset) of a point."""
    a = math.atan2(co.y, co.x)
    best = None
    for k in range(5):
        ak = k / 5 * math.tau - math.pi / 2
        d = Vector((math.cos(ak), math.sin(ak), 0))
        along = co.x * d.x + co.y * d.y
        lat = -co.x * d.y + co.y * d.x
        score = abs(math.atan2(math.sin(a - ak), math.cos(a - ak)))
        if best is None or score < best[0]:
            best = (score, k, along, lat)
    return best[1:]


def width(along):
    t = max(0.0, min(1.0, along / R))
    return 0.24 * (1 - t ** 1.6) ** 0.8 + 0.02


def h(x, y):
    k, along, lat = arm_frame(Vector((x, y, 0)))
    w = width(along)
    u = min(1.0, abs(lat) / w)
    hh = 0.07 * (1 - u ** 2) ** 0.6 * (1 - 0.5 * min(1.0, along / R))
    return Z0 + max(0.0, hh)


def col(co, n):
    if n.z < 0.1:
        return GROOVE
    k, along, lat = arm_frame(co)
    w = width(along)
    u = abs(lat) / w
    c = BODY
    if along > 0.12:
        # virgals: oblique rows running out and forward from the axis (herringbone)
        s = 0.5 + 0.5 * math.cos((along - abs(lat) * 0.7) * 70)
        c = nh.lerp(GROOVE, RIB, nh.smoothstep(0.35, 0.8, s))
        c = nh.lerp(c, AXIS, 1 - nh.smoothstep(0.08, 0.16, u))
    c = nh.lerp(c, GROOVE, nh.smoothstep(0.88, 1.0, u))
    if math.hypot(co.x, co.y) < 0.05:
        c = AXIS
    return c


def outline(a):
    best = 0.0
    for k in range(5):
        ak = k / 5 * math.tau - math.pi / 2
        da = math.atan2(math.sin(a - ak), math.cos(a - ak))
        # radius where the lateral offset equals the half width (petal outline)
        lo, hi = 0.0, R
        for _ in range(20):
            m = (lo + hi) / 2
            along = m * math.cos(da)
            lat = m * math.sin(da)
            if along > 0 and abs(lat) < width(along):
                lo = m
            else:
                hi = m
        best = max(best, lo)
    return max(best, 0.08)


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, R * 1.15)
    # sample the star outline per angle and use it to shape a heightfield disc
    star = kit.heightfield_disc(1.0, lambda x, y: h(x, y), n_r=26, n_a=200, outline=outline)
    mb.add(star, col)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
