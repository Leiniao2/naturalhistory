"""
Procedural Aegirocassis benmoulai (Early Ordovician hurdiid radiodont from the Fezouata
Biota of Morocco, about 480 million years ago; around 2 m long, one of the largest
animals of its time) for map colonies (Swim style).

A giant filter-feeding radiodont: a long, blade-like dorsal head carapace (the central
H-element) jutting forward over the head, with a pair of lateral carapace plates; small
stalked eyes; a pair of frontal appendages whose long endites carry dense rows of fine
auxiliary spines, a comb for sieving plankton; a body of eleven segments, each with two
pairs of swimming flaps - large ventral ones and smaller dorsal ones (evidence that
arthropod limbs combine two branches) - and a short tail. Reddish-brown (colour
conjectural). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/aegirocassis_benmoulai.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AegirocassisBenmoulai.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402

BODY = (0.56, 0.30, 0.22)
BODY_DARK = (0.36, 0.17, 0.12)
FLAP = (0.66, 0.40, 0.30)
FLAP_EDGE = (0.84, 0.62, 0.48)
CARAPACE = (0.62, 0.42, 0.30)
SPINE = (0.90, 0.78, 0.62)
EYE = (0.05, 0.05, 0.05)

SEGS = 11
Y0, Y1 = -0.35, 0.80


def seg_y(i):
    return Y0 + (Y1 - Y0) * (i + 0.5) / SEGS


def seg_w(i):
    t = i / (SEGS - 1)
    return 0.16 * (1.0 - 0.55 * t ** 1.5)


def flap(mb, sx, y, w, length, z, tilt, color_in, color_out):
    """Oval swimming flap from the body side, sloping back."""
    pts = []
    for k in range(14):
        a = k / 14 * math.tau
        pts.append((length * 0.5 * (1 + math.cos(a)), 0.5 * w * math.sin(a) + 0.15 * w * (1 + math.cos(a)), 0.0))
    bm = nh.flat_panel(pts, thickness=0.01)
    for v in bm.verts:
        x, yy = v.co.x, v.co.y
        v.co = Vector((sx * (x + 0.02), y + yy, z - tilt * x))
    mb.add(bm, lambda co, n, x0=sx: nh.lerp(color_in, color_out, nh.smoothstep(0.05, length, abs(co.x) - 0.05)),
           smooth=False)


def build():
    mb = nh.MeshBuilder()
    # trunk: overlapping segment ellipsoids
    for i in range(SEGS):
        y = seg_y(i)
        w = seg_w(i)
        mb.add(nh.uv_ellipsoid((0, y, 0), (w * 0.75, (Y1 - Y0) / SEGS * 0.75, w * 0.55), 12, 8),
               lambda co, n: nh.lerp(BODY, BODY_DARK, 0.5 * nh.smoothstep(0.0, 1.0, n.z)))
        for sx in (-1, 1):
            L = 0.36 * (1.0 - 0.6 * (i / (SEGS - 1)) ** 1.3) + 0.04
            flap(mb, sx, y, (Y1 - Y0) / SEGS * 1.5, L, -0.03, 0.12, FLAP, FLAP_EDGE)       # ventral flaps
            flap(mb, sx, y + 0.01, (Y1 - Y0) / SEGS * 1.0, L * 0.55, 0.05, -0.05, BODY, FLAP)  # dorsal flaps
    # short tail
    mb.add(nh.tube([(0, Y1 - 0.03, 0), (0, Y1 + 0.08, 0), (0, Y1 + 0.16, 0.0)], [0.035, 0.025, 0.0], sides=8), BODY_DARK)
    # head
    mb.add(nh.uv_ellipsoid((0, -0.46, -0.01), (0.13, 0.14, 0.10), 14, 8), BODY)
    # long blade-like central carapace element jutting forward
    pts = []
    n = 12
    for k in range(n + 1):
        t = k / n
        y = -0.36 - 0.70 * t
        w = 0.10 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.6 * (1 - 0.6 * t) + 0.01
        pts.append((w, y))
    outline = [(x, y, 0.0) for x, y in pts] + [(-x, y, 0.0) for x, y in reversed(pts)]
    bm = nh.flat_panel(outline, thickness=0.02)
    for v in bm.verts:
        t = (-0.36 - v.co.y) / 0.70
        v.co.z += 0.10 + 0.04 * math.sin(math.pi * t) - 0.03 * (v.co.x / 0.1) ** 2
    mb.add(bm, lambda co, n: nh.lerp(CARAPACE, FLAP_EDGE, 0.4 * nh.smoothstep(0.03, 0.09, abs(co.x))), smooth=False)
    # lateral carapace plates
    for sx in (-1, 1):
        pl = [(sx * (0.06 + 0.12 * math.cos(a) ** 2 * 0 + 0.10 * (0.5 + 0.5 * math.cos(a))),
               -0.50 + 0.12 * math.sin(a), 0.0) for a in [k / 12 * math.tau for k in range(12)]]
        bm = nh.flat_panel(pl, thickness=0.015)
        for v in bm.verts:
            v.co.z = 0.04 - 0.4 * (abs(v.co.x) - 0.06) + (v.co.z)
        mb.add(bm, CARAPACE, smooth=False)
        # stalked eyes behind the lateral plates
        b = Vector((sx * 0.10, -0.40, 0.03))
        e = b + Vector((sx * 0.10, -0.02, 0.03))
        mb.add(nh.tube([b, e], [0.02, 0.016], sides=6), BODY)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * 0.02, 0, 0))), (0.03, 0.028, 0.026), subdivisions=2), EYE)
        # frontal appendage: curving forward and down, endites with comb spines
        pa = [Vector((sx * 0.06, -0.56, -0.05)), Vector((sx * 0.10, -0.70, -0.08)),
              Vector((sx * 0.12, -0.84, -0.14)), Vector((sx * 0.10, -0.94, -0.22)), Vector((sx * 0.07, -0.98, -0.30))]
        mb.add(nh.tube(pa, [0.04, 0.035, 0.028, 0.02, 0.0], sides=8), BODY)
        for k in range(5):
            t = 0.15 + 0.8 * k / 4
            i = min(3, int(t * 4))
            p = pa[i].lerp(pa[i + 1], t * 4 - i)
            d = Vector((-sx * 0.6, -0.2, -0.5)).normalized()
            L = 0.22 * (1 - 0.3 * t)
            end = p + d * L
            mb.add(nh.tube([p, p.lerp(end, 0.5), end], [0.012, 0.009, 0.0], sides=5), SPINE)
            for j in range(6):
                q = p.lerp(end, (j + 1) / 7)
                mb.add(nh.tube([q, q + Vector((0, 0.02, -0.06))], [0.004, 0.0], sides=3), SPINE, smooth=False)
    obj = mb.to_object("AegirocassisBenmoulai", roughness=0.55)
    vs = obj.data.vertices
    zs, ys = [v.co.z for v in vs], [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "AegirocassisBenmoulai", background=(0.05, 0.18, 0.22), views=((35, 30), (0, 85), (-90, 8)))
