"""
Procedural Caryocrinites ornatus (a rhombiferan "cystoid" echinoderm, theca about
3-4 cm across, from the Silurian of New York, Ontario and Britain) for map colonies
(Fixed).

A walnut-like echinoderm on a stalk: a stem of round columnals carries an egg-shaped
cup (theca) built of a few large, six-sided plates arranged in rings, each plate
decorated with fine ridges radiating to its edges; diamond-shaped pore rhombs straddle
some of the sutures and served for breathing. At the top, around the mouth, a ring of
long, slender, upright arms (brachioles) gathered food from the water.
Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/caryocrinites_ornatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CaryocrinitesOrnatus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "CaryocrinitesOrnatus"
PLATE = (0.80, 0.68, 0.50)
PLATE_DARK = (0.62, 0.50, 0.34)
SUTURE = (0.30, 0.22, 0.14)
RHOMB = (0.22, 0.14, 0.09)
STEM = (0.66, 0.56, 0.42)
STEM_DARK = (0.42, 0.34, 0.24)
ARM = (0.72, 0.60, 0.44)

STEM_H = 0.55
R = 0.26


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.45, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    for k in range(5):
        a = k / 5 * math.tau + 0.2
        d = Vector((math.cos(a), math.sin(a), 0))
        mb.add(nh.tube([Vector((0, 0, 0.05)), d * 0.10 + Vector((0, 0, 0.012)), d * 0.18],
                       [0.03, 0.018, 0.0], sides=5), STEM_DARK)
    pts = [Vector((0.025 * math.sin(t * 2.5), 0.0, STEM_H * t)) for t in [i / 10 for i in range(11)]]
    mb.add(nh.tube(pts, [0.035 * (1.0 - 0.15 * i / 10) for i in range(11)], sides=8),
           lambda co, n: STEM_DARK if math.cos(co.z * 180.0) > 0.6 else STEM)
    top = pts[-1]
    c0 = top + Vector((0, 0, R * 1.15))

    rnd = random.Random(5)
    sb = bmesh.new()
    bmesh.ops.create_icosphere(sb, subdivisions=1, radius=1.0)
    seeds = [(v.co.normalized(), rnd.random()) for v in sb.verts]
    sb.free()

    def col(co, n):
        d = Vector(((co.x - c0.x) / R, (co.y - c0.y) / R, (co.z - c0.z) / (R * 1.25))).normalized()
        ds = sorted(((d - s).length, s, k) for s, k in seeds)[:2]
        (d0, s0, k0), (d1, s1, _k1) = ds
        c = nh.lerp(PLATE, PLATE_DARK, 0.5 * k0)
        # fine ridges radiating from each plate centre
        v = d - s0
        ang = math.atan2(v.dot(s0.cross(Vector((0, 0, 1))).normalized() if abs(s0.z) < 0.99 else Vector((1, 0, 0))),
                         v.dot(Vector((0, 0, 1))))
        c = nh.lerp(c, PLATE_DARK, 0.45 * nh.smoothstep(0.6, 1.0, math.cos(ang * 12)) * nh.smoothstep(0.04, 0.15, d0))
        # pore rhombs: diamonds across some sutures
        if k0 > 0.55 and d1 - d0 < 0.10 and (d - (s0 + s1) * 0.5).length < 0.13:
            c = nh.lerp(c, RHOMB, 0.8)
        return nh.lerp(c, SUTURE, 1.0 - nh.smoothstep(0.01, 0.035, d1 - d0))

    mb.add(nh.ellipsoid(tuple(c0), (R, R, R * 1.25), subdivisions=5), col)
    # mouth and ring of long upright brachioles
    apex = c0 + Vector((0, 0, R * 1.22))
    mb.add(nh.ellipsoid(tuple(apex), (0.05, 0.05, 0.02), subdivisions=2), SUTURE)
    for k in range(9):
        a = k / 9 * math.tau
        o = Vector((math.cos(a), math.sin(a), 0))
        b = apex + o * 0.05 - Vector((0, 0, 0.01))
        pts = [b, b + o * 0.05 + Vector((0, 0, 0.18)), b + o * 0.10 + Vector((0, 0, 0.38)),
               b + o * 0.16 + Vector((0, 0, 0.55))]
        mb.add(nh.tube(pts, [0.018, 0.015, 0.011, 0.0], sides=5),
               lambda co, n: nh.lerp(ARM, STEM_DARK, 0.4 * nh.smoothstep(0.7, 1.0, math.cos(co.z * 200))))
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
