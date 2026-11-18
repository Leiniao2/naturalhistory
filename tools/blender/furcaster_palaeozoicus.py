"""
Procedural Furcaster palaeozoicus for the map: a brittle star (ophiuroid) from the Early
Devonian Hunsrueck Slate of Germany, about 400 million years ago; about 10 cm across.

A small, rounded central disc with five very long, slender, flexible arms that it
snaked across the muddy sea floor to crawl, and that could be shed and regrown. Each arm
is a chain of vertebra-like ossicles with rows of short spines along its sides.

Low disc plus five sinuous tapering arm tubes with banded ossicles and side spines.
Colours are unknown: a reddish-brown disc and arms banded with paler joints.

Usage:
  blender --background --python tools/blender/furcaster_palaeozoicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Furcaster.fbx (Swim: pivot at the body centre,
facing -Y; it crawls on the sea floor).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

NAME = "Furcaster"

DISC = (0.58, 0.30, 0.20)
DISC_DARK = (0.34, 0.15, 0.10)
ARM = (0.62, 0.36, 0.24)
JOINT = (0.86, 0.70, 0.54)
SPINE = (0.90, 0.80, 0.66)

R = 0.80          # arm reach from the centre
R_DISC = 0.12
ARM_W = 0.040
Z0 = 0.0

# per-arm sinuous bend (amplitude, phase) so the star looks caught mid-crawl
BENDS = [(0.55, 0.0), (-0.35, 1.2), (0.70, 2.0), (-0.60, 0.4), (0.30, 2.8)]


def arm_path(a0, amp, ph, n=28):
    pts, dirs = [], []
    p = Vector((math.cos(a0), math.sin(a0), 0)) * R_DISC * 0.6
    ang = a0
    step = (R - R_DISC * 0.6) / (n - 1) * 1.08
    for i in range(n):
        t = i / (n - 1)
        pts.append(p.copy())
        dirs.append(Vector((math.cos(ang), math.sin(ang), 0)))
        ang = a0 + amp * math.sin(t * 3.4 + ph) * t
        p = p + Vector((math.cos(ang), math.sin(ang), 0)) * step
    return pts, dirs


def build():
    mb = nh.MeshBuilder()
    # disc: low, slightly pentagonal dome
    h = 0.05
    mb.add(nh.ellipsoid((0, 0, Z0 + h * 0.55), (R_DISC, R_DISC, h), subdivisions=3,
                        deform=lambda v: 1.0 + 0.08 * math.cos(5 * math.atan2(v.y, v.x) + math.pi / 2) * (1 - abs(v.z))),
           lambda co, n: nh.lerp(DISC, DISC_DARK, 0.5 * nh.smoothstep(-0.2, 0.6, noise.noise(co * 40))
                                 + 0.3 * nh.smoothstep(0.03, 0.0, Vector((co.x, co.y)).length)))
    for k in range(5):
        a0 = k / 5 * math.tau - math.pi / 2 + math.pi / 5  # no arm pointing straight forward
        amp, ph = BENDS[k]
        pts, dirs = arm_path(a0, amp, ph)
        n = len(pts)
        radii = []
        for i in range(n):
            t = i / (n - 1)
            radii.append(ARM_W * (1.0 - 0.85 * t) + 0.004)
        centre = [p + Vector((0, 0, Z0 + r * 0.65 + 0.025 * nh.smoothstep(0.75, 1.0, i / (n - 1))))
                  for i, (p, r) in enumerate(zip(pts, radii))]
        radii[-1] = 0.0
        L = [0.0]
        for i in range(1, n):
            L.append(L[-1] + (centre[i] - centre[i - 1]).length)

        def arm_col(co, nrm, centre=centre, L=L):
            j = min(range(len(centre)), key=lambda q: (centre[q] - co).length_squared)
            s = L[j] / 0.035
            joint = 1.0 - nh.smoothstep(0.08, 0.22, abs(s - round(s)))
            return nh.lerp(ARM, JOINT, 0.75 * joint)

        mb.add(nh.tube(centre, radii, sides=8, scale_xy=(1.0, 0.7)), arm_col)
        # short spines along both sides of the arm
        for i in range(1, n - 2):
            d = (centre[i + 1] - centre[i - 1]).normalized()
            side = Vector((-d.y, d.x, 0)).normalized()
            r = radii[i]
            for sg in (-1, 1):
                b = centre[i] + side * sg * r * 0.85
                tip = b + (side * sg * 0.8 + d * 0.5 + Vector((0, 0, 0.25))).normalized() * (r * 0.9 + 0.012)
                mb.add(nh.tube([b, tip], [0.006 * (1 - i / n) + 0.003, 0.0], sides=4), SPINE)
    obj = mb.to_object(NAME, roughness=0.55)
    vs = obj.data.vertices
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj

if __name__ == "__main__":
    nh.run(build, NAME, background=(0.05, 0.15, 0.18),
           views=((30, 30), (0, 80), (-90, 8)))
