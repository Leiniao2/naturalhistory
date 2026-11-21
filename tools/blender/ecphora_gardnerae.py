"""
Procedural Ecphora gardnerae (Miocene of the Chesapeake Bay region) for map
colonies: a predatory sea snail, Maryland's state fossil.

A fist-sized murex relative whose rust-red shell (one of the few fossil shells
that keeps its original colour) carries four tall, flat, T-topped spiral ribs
running round the whorls, with a low stepped spire and a short front canal. It
drilled into clams and barnacles to eat them. Shown crawling on its foot, the
siphon raised. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ecphora_gardnerae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EcphoraGardnerae.fbx
"""

import math
import sys
from pathlib import Path

import bmesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.86, 0.66, 0.50)
RIB = (0.62, 0.26, 0.12)
FOOT = (0.62, 0.52, 0.42)
FOOT_DARK = (0.38, 0.30, 0.24)
SIPHON = (0.70, 0.50, 0.36)
EYE = (0.03, 0.03, 0.03)

Y0, YA = -0.50, 0.40      # tip of the front canal, spire apex
ZC = 0.23
RIBS = (-0.20, -0.06, 0.08, 0.20)   # spiral ribs (as rings round the body whorl and spire)
RIB_H, RIB_W = 0.07, 0.012


def base_radius(y):
    if y < -0.32:                                        # short siphonal canal
        t = max(0.0, (y - Y0) / 0.18)
        return 0.04 + 0.08 * t
    if y < 0.16:                                         # body whorl: swelling then tapering to the shoulder
        t = (y + 0.32) / 0.48
        return 0.12 + 0.12 * math.sin(min(1.0, t * 1.15) * math.pi * 0.5)
    t = min(1.0, max(0.0, (y - 0.16) / (YA - 0.16)))   # low stepped spire
    step = 0.02 * (math.sin(t * math.pi * 3.0) ** 2)
    return max(0.0, 0.22 * (1.0 - t) ** 1.2 + step * (1 - t))


def radius(y):
    r = base_radius(y)
    for ry in RIBS:
        d = abs(y - ry)
        if d < RIB_W * 1.8:
            # tall flat flange with a T-shaped crest
            k = 1.0 - nh.smoothstep(RIB_W * 0.7, RIB_W * 1.8, d)
            r += RIB_H * k * (r / 0.24) ** 0.5
    return r


def shell():
    bm = bmesh.new()
    nseg = 56
    ys = []
    n = 160
    for i in range(1, n):
        ys.append(Y0 + (YA - Y0) * i / n)
    tipf = bm.verts.new((0, Y0, ZC))
    tipb = bm.verts.new((0, YA, ZC))
    rings = []
    for y in ys:
        r = radius(y)
        ring = []
        for k in range(nseg):
            a = k / nseg * math.tau
            x, z = math.cos(a) * r, math.sin(a) * r
            if z < 0:
                z *= 0.85
            ring.append(bm.verts.new((x, y, ZC + z)))
        rings.append(ring)
    for k in range(nseg):
        j = (k + 1) % nseg
        bm.faces.new([tipf, rings[0][j], rings[0][k]])
        bm.faces.new([tipb, rings[-1][k], rings[-1][j]])
    for a, b in zip(rings, rings[1:]):
        for k in range(nseg):
            j = (k + 1) % nseg
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def shell_color(co, n):
    y = co.y
    r = (Vector((co.x, 0, co.z - ZC))).length
    over = r - base_radius(y)
    c = nh.lerp(SHELL, RIB, nh.smoothstep(0.01, 0.04, over))
    c = nh.lerp(c, RIB, 0.25 * max(0.0, noise.noise(Vector((co.x * 20, y * 40, co.z * 20)))))
    # fine growth lines
    c = nh.lerp(c, RIB, 0.15 * (0.5 + 0.5 * math.sin(math.atan2(co.z - ZC, co.x) * 40)))
    if co.z < ZC - 0.14 and abs(co.x) < 0.07 and -0.4 < y < 0.1:      # aperture below
        c = (0.70, 0.45, 0.32)
    return c


def foot_color(co, n):
    return nh.lerp(FOOT, FOOT_DARK, 0.6 * max(0.0, noise.noise(co * 25.0)))


def build():
    mb = nh.MeshBuilder()
    mb.add(shell(), shell_color)
    mb.add(nh.ellipsoid((0, -0.12, 0.045), (0.19, 0.44, 0.05), subdivisions=3), foot_color)
    mb.add(nh.ellipsoid((0, -0.52, 0.07), (0.07, 0.07, 0.045), subdivisions=2), foot_color)
    for sx in (-1, 1):
        base = Vector((sx * 0.04, -0.56, 0.08))
        tip = base + Vector((sx * 0.05, -0.08, 0.02))
        mb.add(nh.tube([tuple(base), tuple(tip)], [0.012, 0.007], sides=6), FOOT)
        mb.add(nh.ellipsoid(tuple(base + Vector((sx * 0.012, -0.02, 0.01))), (0.01,) * 3, subdivisions=1), EYE)
    pts = [Vector((0, -0.44, 0.20)), Vector((0, -0.54, 0.26)), Vector((0, -0.60, 0.34))]
    mb.add(nh.tube([tuple(p) for p in pts], [0.026, 0.024, 0.028], sides=10, cap_end=False), SIPHON)
    obj = mb.to_object("EcphoraGardnerae", roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "EcphoraGardnerae", ground=(0.74, 0.70, 0.56), views=((35, 30), (-90, 8), (160, 30)))
