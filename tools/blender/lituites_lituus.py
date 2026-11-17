"""
Procedural Lituites lituus (Middle Ordovician lituitid nautiloid of Sweden and the Baltic
region) for map colonies (Swim style).

A nautiloid shaped like a bishop's crook: the shell starts as a small, loosely touching
planispiral coil of a few whorls, then straightens into a long, slowly widening tube
ending at an aperture with a pair of side lappets. The animal peers out of the aperture
(head, eyes, ten short arms and funnel from nh_orthocone.soft_body), arms forward; the
coil rides above the back end. Cream shell with brown transverse bands (colour
conjectural). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/lituites_lituus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LituitesLituus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

CREAM = (0.90, 0.82, 0.66)
BAND = (0.52, 0.26, 0.14)
FLESH = (0.62, 0.34, 0.28)
FLESH_LIGHT = (0.86, 0.64, 0.54)

R_AP = 0.10
STRAIGHT = 1.10   # length of the straight part (aperture at y = 0)
R0 = 0.17         # coil radius where it leaves the straight part
TURNS = 2.6


def centreline():
    pts = []
    n = 40
    for i in range(n + 1):
        t = i / n
        pts.append((Vector((0, STRAIGHT * t, 0)), t * 0.55))     # (point, growth parameter 0..1)
    c = Vector((0, STRAIGHT, R0))
    m = 80
    for i in range(1, m + 1):
        th = i / m * TURNS * math.tau
        r = R0 * math.exp(-0.16 * th)
        pts.append((c + Vector((0, math.sin(th) * r, -math.cos(th) * r)), 0.55 + 0.45 * i / m))
    return pts


def build():
    mb = nh.MeshBuilder()
    cl = centreline()
    pts = [p for p, _ in cl]
    radii = [R_AP * (1.0 - 0.93 * g ** 0.8) for _, g in cl]
    radii[-1] = 0.0

    def col(co, n):
        # nearest centreline sample -> growth parameter for the bands
        k = min(range(len(pts)), key=lambda i: (pts[i] - co).length)
        g = cl[k][1]
        w = math.sin(g * 70.0)
        c = nh.lerp(CREAM, BAND, 0.8 * nh.smoothstep(0.3, 0.8, w))
        c = nh.lerp(c, (0.98, 0.94, 0.86), 0.5 * nh.smoothstep(0.2, -0.8, n.z) * (1 if g < 0.55 else 0))
        return c

    mb.add(nh.tube(pts, radii, sides=14, cap_start=False), col)
    # apertural lappets: two flaring ear-like lobes at the sides of the aperture
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * R_AP * 0.95, -0.01, 0.02), (0.02, 0.06, 0.09), subdivisions=2), CREAM)
    oc.soft_body(mb, 0.0, R_AP * 0.95, FLESH, FLESH_LIGHT, arms=10, arm_len=2.2, arm_r=0.12,
                 eye_r=0.26, spot=(0.45, 0.22, 0.18))
    obj = mb.to_object("LituitesLituus", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "LituitesLituus", views=((35, 25), (-90, 8), (0, 85)))
