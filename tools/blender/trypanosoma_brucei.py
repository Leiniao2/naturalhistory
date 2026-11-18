"""
Procedural low-poly Trypanosoma brucei, the blood-stream trypanosome of sleeping sickness.

A slender, spindle-shaped cell, pointed at both ends and bent in a gentle S. A frilly undulating
membrane runs the length of one side as a thin wavy fin, spiralling a little round the twisted
body, with the flagellum along its free edge: the flagellum leaves its pocket near the rear,
follows the fin forward and carries on free beyond the front tip. A darker oval nucleus shows in
the middle and a small dark kinetoplast dot near the rear, by the flagellar pocket. Pale
violet-purple, like a Giemsa-stained blood film. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/trypanosoma_brucei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Trypanosome.fbx
About 1.6 units long including the free flagellum. Faces -Y (the flagellum leads). Pivot at the
cell centre (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

LENGTH = 1.22          # body length, front tip to rear tip
RADIUS = 0.072         # body radius at its widest
BEND = 0.09            # sideways S-bend
SAMPLES = 40
FIN_T = (0.03, 0.84)   # stretch of the body the undulating membrane runs along
FIN_WIDTH = 0.095
FIN_WAVES = 6.5        # ruffles along the fin
FIN_RUFFLE = 0.03
TWIST = 1.2            # how far (radians) the fin spirals round the body front to back
FIN_PHI = 0.1          # where round the body the fin sits at the front (0 = +X side, pi/2 = top)
FREE_FLAGELLUM = 0.32
NUCLEUS_T = 0.50
KINETOPLAST_T = 0.88

BODY = (0.70, 0.60, 0.84)
BODY_DEEP = (0.60, 0.48, 0.76)
FIN = (0.80, 0.72, 0.91)
FLAG = (0.52, 0.38, 0.70)
NUCLEUS = (0.44, 0.22, 0.52)
KARYO = (0.30, 0.12, 0.38)
KINETO = (0.20, 0.07, 0.24)


def axis(t):
    """Point on the body axis, t from 0 (front tip) to 1 (rear tip)."""
    return Vector((BEND * math.sin(t * math.tau * 0.85 + 0.35),
                   -LENGTH / 2 + LENGTH * t,
                   0.035 * math.sin(t * math.pi * 1.6)))


def radius(t):
    return RADIUS * math.sin(math.pi * t) ** 0.85 * (1.0 + 0.12 * (t - 0.5))


def frame(t):
    """Tangent (toward the rear), side and up vectors of the body at t."""
    tan = (axis(min(t + 0.01, 1.0)) - axis(max(t - 0.01, 0.0))).normalized()
    side = tan.cross(Vector((0, 0, 1))).normalized()
    return tan, side, side.cross(tan).normalized()


def fin_phi(t):
    return FIN_PHI + TWIST * t


def fin_width(t):
    k = (t - FIN_T[0]) / (FIN_T[1] - FIN_T[0])
    return FIN_WIDTH * math.sin(math.pi * k) ** 0.6


def fin_point(t, s):
    """Point on the membrane at t, s = 0 (root, inside the body) .. 1 (free edge)."""
    tan, side, up = frame(t)
    phi = fin_phi(t)
    out = side * math.cos(phi) + up * math.sin(phi)
    normal = tan.cross(out)
    r = radius(t)
    ruffle = FIN_RUFFLE * math.sin(t * math.tau * FIN_WAVES) * s ** 1.5
    k = (t - FIN_T[0]) / (FIN_T[1] - FIN_T[0])
    ruffle *= math.sin(math.pi * k) ** 0.5
    return axis(t) + out * (r * 0.7 + (r * 0.3 + fin_width(t)) * s) + normal * ruffle, normal


def make_fin(thick=0.007):
    bm = bmesh.new()
    rows = (0.0, 0.35, 0.7, 1.0)
    n = 64
    grid = []
    for i in range(n + 1):
        t = FIN_T[0] + (FIN_T[1] - FIN_T[0]) * i / n
        top, bot = [], []
        for s in rows:
            p, nrm = fin_point(t, s)
            top.append(bm.verts.new(p + nrm * thick * 0.5))
            bot.append(bm.verts.new(p - nrm * thick * 0.5))
        grid.append((top, bot))
    for (ta, ba), (tb, bb) in zip(grid, grid[1:]):
        for j in range(len(rows) - 1):
            bm.faces.new([ta[j], tb[j], tb[j + 1], ta[j + 1]])
            bm.faces.new([ba[j], ba[j + 1], bb[j + 1], bb[j]])
        bm.faces.new([ta[0], ba[0], bb[0], tb[0]])      # root and free edges close the slab
        bm.faces.new([ta[-1], tb[-1], bb[-1], ba[-1]])
    for top, bot in (grid[0], grid[-1]):
        for j in range(len(rows) - 1):
            bm.faces.new([top[j], top[j + 1], bot[j + 1], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    for k in range(SAMPLES + 1):
        t = k / SAMPLES
        pts.append(axis(t))
        radii.append(radius(t) if 0 < k < SAMPLES else 0.0)

    def body_col(co, nrm):
        # nearest t along the (mostly Y-aligned) axis
        t = (co.y + LENGTH / 2) / LENGTH
        c = nh.lerp(BODY, BODY_DEEP, nh.smoothstep(0.2, 0.5, abs(t - 0.5)))
        return c

    mb.add(nh.tube(pts, radii, sides=11), body_col)

    # the nucleus bulges just through the body in the middle
    c = axis(NUCLEUS_T)
    tan, side, up = frame(NUCLEUS_T)
    r = radius(NUCLEUS_T)
    nuc = nh.uv_ellipsoid((0, 0, 0), (r * 0.95, 0.105, r * 1.1), segments=12, rings=8)
    for v in nuc.verts:
        v.co = c + side * v.co.x + tan * v.co.y + up * v.co.z

    def nuc_col(co, n):
        return nh.lerp(KARYO, NUCLEUS, nh.smoothstep(0.0, 0.06, abs((co - c).dot(tan))))

    mb.add(nuc, nuc_col)

    # kinetoplast: a small dark dot near the rear, by the root of the flagellum
    tan, side, up = frame(KINETOPLAST_T)
    phi = fin_phi(KINETOPLAST_T)
    out = side * math.cos(phi) + up * math.sin(phi)
    mb.add(nh.ellipsoid(axis(KINETOPLAST_T) + out * radius(KINETOPLAST_T) * 0.55, (0.026,) * 3,
                        subdivisions=2), KINETO)

    mb.add(make_fin(), FIN)

    # flagellum: from its pocket by the kinetoplast, along the fin's free edge, then free in front
    fl = []
    t = KINETOPLAST_T - 0.01
    fl.append(axis(t) + out * radius(t) * 0.5)
    for i in range(64):
        t = FIN_T[1] - (FIN_T[1] - FIN_T[0]) * i / 63
        fl.append(fin_point(t, 1.0)[0])
    tip = axis(0.0)
    tan0 = frame(0.0)[0]
    tan0 = -tan0
    side0 = frame(0.0)[1]
    start = fl[-1]
    for i in range(1, 9):
        u = i / 8
        fl.append(tip + (start - tip) * (1 - u) * 0.6 + tan0 * FREE_FLAGELLUM * u
                  + side0 * 0.035 * math.sin(u * math.tau * 1.2))
    radii = [0.011] * (len(fl) - 3) + [0.009, 0.007, 0.0]
    mb.add(nh.tube(fl, radii, sides=5), FLAG)
    return mb.to_object("Trypanosome", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "Trypanosome", views=((35, 35), (0, 80), (-90, 10)))
