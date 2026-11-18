"""
Procedural Eophalangium sheari for the map: the oldest known harvestman (Opiliones), from
the Early Devonian Rhynie chert of Scotland, about 410 million years ago; a body only about
half a centimetre long.

Already a typical harvestman: a compact, oval body in which the front (prosoma) and back
(opisthosoma) are broadly joined without a waist, a pair of eyes on a small central
tubercle, short pincer-like chelicerae, small leg-like pedipalps, and four pairs of very
long, thin, many-jointed legs held in high arches above the body.

Built with nh_dev_arthro. Colours are unknown: a mottled brown body with pale banded legs.

Usage:
  blender --background --python tools/blender/eophalangium_sheari.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eophalangium.fbx (Ground: pivot on the ground,
facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Eophalangium"

BODY = (0.42, 0.27, 0.14)
DARK = (0.14, 0.09, 0.05)
SADDLE = (0.22, 0.14, 0.08)
LEG = (0.40, 0.30, 0.18)
BAND = (0.74, 0.64, 0.46)
EYE = (0.05, 0.04, 0.03)

BASE = 0.20


def body_color(co, n):
    c = ar.glossy(BODY)(co, n)
    # dark saddle on the back and faint segment lines on the rear half
    saddle = nh.smoothstep(0.10, 0.02, abs(co.x) - 0.06 * (1 - abs(co.y + 0.02) * 2)) * nh.smoothstep(0.0, 0.5, n.z)
    c = nh.lerp(c, SADDLE, 0.6 * saddle)
    if co.y > -0.02 and n.z > 0.2:
        ph = (co.y + 0.02) / 0.05
        c = nh.lerp(c, DARK, 0.35 * (1 - nh.smoothstep(0.05, 0.15, abs(ph - round(ph)))))
    return c


def long_leg(mb, s, hip, foot, knee_h, r):
    """Harvestman leg: up from the hip to a high knee, then down a long shank to the foot."""
    h = Vector((s * hip[0], hip[1], hip[2]))
    f = Vector((s * foot[0], foot[1], 0.0))
    knee = h.lerp(f, 0.32)
    knee.z = knee_h
    mid = knee.lerp(f, 0.55)
    mid.z = knee_h * 0.55
    pts = [h, knee, mid, f]
    radii = [r, r * 0.85, r * 0.65, r * 0.35]
    for i in range(3):
        mb.add(nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=5), ar.glossy(LEG))
    for p, rr in ((knee, r * 1.25), (mid, r * 0.95)):
        mb.add(nh.ellipsoid(p, (rr,) * 3, 1), BAND)
    # pale band rings along the shank
    for t in (0.3, 0.7):
        mb.add(nh.ellipsoid(mid.lerp(f, t), (r * 0.7,) * 3, 1), BAND)


def build():
    mb = nh.MeshBuilder()
    c = Vector((0, 0.0, BASE))
    mb.add(nh.uv_ellipsoid(c, (0.15, 0.20, 0.085), 16, 9, deform=lambda n: 0.75 if n.z < 0 else 1.0), body_color)
    # eye tubercle with two eyes facing sideways
    t = c + Vector((0, -0.11, 0.075))
    mb.add(nh.uv_ellipsoid(t, (0.028, 0.026, 0.032), 8, 5), ar.glossy(BODY))
    for s in (-1, 1):
        mb.add(nh.ellipsoid(t + Vector((s * 0.022, -0.004, 0.010)), (0.011,) * 3, 1), EYE)
    # chelicerae and pedipalps
    for s in (-1, 1):
        root = Vector((s * 0.03, -0.19, BASE - 0.02))
        ar.jointed(mb, [root, root + Vector((0, -0.05, -0.02)), root + Vector((s * -0.01, -0.07, -0.05))],
                   [0.016, 0.013, 0.006], ar.glossy(BODY))
        root = Vector((s * 0.07, -0.17, BASE - 0.03))
        ar.jointed(mb, [root, root + Vector((s * 0.05, -0.08, 0.04)), root + Vector((s * 0.04, -0.15, -0.03)),
                        root + Vector((s * 0.03, -0.18, -0.14))], [0.014, 0.012, 0.010, 0.006], ar.glossy(LEG), BAND)
    # four pairs of very long legs; the second pair longest
    legs = [((0.10, -0.12, BASE - 0.02), (0.62, -0.62), 0.50, 0.014),
            ((0.12, -0.05, BASE - 0.02), (0.84, -0.18), 0.58, 0.015),
            ((0.12, 0.02, BASE - 0.02), (0.70, 0.30), 0.52, 0.014),
            ((0.10, 0.08, BASE - 0.02), (0.56, 0.72), 0.50, 0.010)]
    for s in (-1, 1):
        for hip, foot, kh, r in legs:
            long_leg(mb, s, hip, foot, kh, r)
    return ar.finish_ground(mb, NAME, BASE)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
