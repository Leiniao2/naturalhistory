"""
Procedural Gigatitan vulcanicus (Late Triassic titanopteran insect, ~40 cm wingspan).

One of the giant "titan" insects of Madygen in Kyrgyzstan, relatives of grasshoppers and
crickets: a long body, a small head with long thread-like antennae, long, spiny, grasping
forelegs for seizing other insects, and two pairs of large wings. The forewings carried a
broad, ribbed patch that was probably rubbed to make loud sounds or flashed as a display.
In flight, wings spread. Faces -Y, pivot at the body centre (flier).

Output: Assets/Resources/Models/Species/Gigatitan.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_car_palaeodicty as pd  # noqa: E402

BODY = (0.30, 0.36, 0.18)
BODY_MARK = (0.48, 0.52, 0.26)
LEG = (0.36, 0.40, 0.20)
SPINE = (0.12, 0.10, 0.06)
EYE = (0.10, 0.08, 0.06)
FORE = (0.62, 0.62, 0.42)
FORE_VEIN = (0.30, 0.30, 0.18)
PATCH = (0.36, 0.20, 0.10)
HIND = (0.84, 0.80, 0.66)
HIND_MARK = (0.40, 0.30, 0.20)


def fore_col(u, v):
    c = nh.lerp(FORE_VEIN, FORE, nh.smoothstep(0.0, 0.15, u))
    # ribbed sound/display patch near the base of the forewing
    if 0.12 < u < 0.38 and 0.3 < v < 0.9:
        rib = 0.5 + 0.5 * math.sin(u * 140.0)
        c = nh.lerp(c, PATCH, 0.6 + 0.3 * rib)
    if v < 0.1 or abs(v - 0.5) < 0.04:
        c = nh.lerp(c, FORE_VEIN, 0.6)
    return c


def hind_col(u, v):
    c = nh.lerp(FORE_VEIN, HIND, nh.smoothstep(0.0, 0.12, u))
    m = math.exp(-((u - 0.75) / 0.12) ** 2) * math.exp(-((v - 0.45) / 0.3) ** 2)
    c = nh.lerp(c, HIND_MARK, 0.7 * m)
    if v < 0.08:
        c = nh.lerp(c, FORE_VEIN, 0.6)
    return c


def leg(mb, sx, pts, r, spines=0):
    P = [Vector((sx * p[0], p[1], p[2])) for p in pts]
    mb.add(nh.tube(P, [r, r * 0.8, r * 0.6, r * 0.4][:len(P)], sides=6), LEG)
    for i in range(spines):
        t = (i + 0.5) / spines
        seg = 1 if len(P) > 2 else 0
        b = P[seg].lerp(P[seg + 1], t)
        mb.add(nh.tube([b, b + Vector((0, 0.0, -0.035)) + Vector((sx * 0.01, -0.01, 0))], [r * 0.35, 0.0], sides=3),
               SPINE, smooth=False)


def build():
    mb = nh.MeshBuilder()
    body = nh.MeshBuilder()
    body.add(nh.ellipsoid((0, -0.40, 0.0), (0.045, 0.045, 0.055), 2), BODY)               # head
    body.add(nh.uv_ellipsoid((0, -0.31, 0.005), (0.050, 0.07, 0.055), 12, 8), BODY)        # pronotum
    body.add(nh.uv_ellipsoid((0, -0.18, 0.0), (0.055, 0.09, 0.055), 12, 8), BODY)         # thorax
    for i in range(9):                                                                   # abdomen
        t = i / 8
        r = 0.05 * (1.0 - 0.45 * t)
        body.add(nh.ellipsoid((0, -0.07 + t * 0.48, -0.005), (r, 0.035, r * 0.9), 2), BODY_MARK if i % 2 else BODY)
    mb.add(body.fuse(voxel=0.008, smooth=3, max_tris=3000))
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * 0.035, -0.425, 0.02), (0.02, 0.025, 0.025), 2), EYE)
        ant = [Vector((sx * (0.015 + 0.10 * t), -0.44 - 0.42 * t, 0.03 + 0.10 * math.sin(t * 2.0))) for t in
               [k / 8 for k in range(9)]]
        mb.add(nh.tube(ant, [0.004] * 8 + [0.001], sides=4), SPINE)
        # cerci
        mb.add(nh.tube([(sx * 0.01, 0.40, 0.0), (sx * 0.05, 0.50, 0.01)], [0.008, 0.0], sides=4), BODY)
        # long grasping forelegs reaching forward, spiny
        leg(mb, sx, [(0.03, -0.30, -0.04), (0.09, -0.40, -0.06), (0.07, -0.55, -0.06), (0.05, -0.64, -0.09)], 0.014,
            spines=4)
        leg(mb, sx, [(0.04, -0.18, -0.04), (0.14, -0.16, -0.06), (0.20, -0.10, -0.14)], 0.012)
        leg(mb, sx, [(0.04, -0.10, -0.04), (0.16, 0.02, -0.04), (0.22, 0.14, -0.13)], 0.013)
        # wings: narrower forewing in front, broad fan-like hind wing
        for root_y, chord, sweep, span, col in ((-0.24, 0.16, 2, 0.75, fore_col), (-0.15, 0.26, 10, 0.70, hind_col)):
            w = pd.wing_grid((0.04, root_y, 0.04), span, chord, sweep, col, nu=18, nv=7, th=0.005)
            mb.add(pd.mirror(w) if sx < 0 else w, smooth=False)
    obj = mb.to_object("Gigatitan", roughness=0.5)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "Gigatitan", background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
