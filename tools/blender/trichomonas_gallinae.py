"""
Procedural low-poly Trichomonas gallinae, the parabasalid flagellate of canker (trichomonosis) in
pigeons, doves and birds of prey.

A pear-shaped cell, broad and rounded in front, tapering behind. Four free anterior flagella
sprout together from the front and wave forward and outward. Along one side an undulating
membrane runs about two-thirds of the way back as a thin ruffled fin, its root stiffened by the
darker costa and a recurrent flagellum running along its free edge (in this species it ends with
the membrane, with no free trailing part). The stiff, glassy axostyle rod runs through the body
and sticks out of the rear as a short pointed spike. An elongated nucleus shows through near the
front. Pale greenish-grey. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/trichomonas_gallinae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Trichomonas.fbx
About 1.6 units long from flagellum tips to axostyle spike. Faces -Y (flagella first). Pivot at
the centre of the bounds (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

LENGTH = 0.80          # body length, front to rear tip
RADIUS = 0.25          # widest radius
FLATTEN = 0.85         # Z scale of the cross-section
RINGS = 24
FIN_T = (0.06, 0.66)   # stretch of the body the undulating membrane runs along
FIN_PHI = 0.75         # where round the body it sits (0 = +X side, pi/2 = top)
FIN_WIDTH = 0.10
FIN_WAVES = 3.5
FIN_RUFFLE = 0.035
SPIKE = 0.24           # how far the axostyle sticks out behind
FLAGELLA = 4
FLAG_LEN = 0.55
NUCLEUS_T = 0.24

BODY = (0.72, 0.80, 0.68)
BODY_DEEP = (0.62, 0.70, 0.58)
NUCLEUS = (0.44, 0.52, 0.44)
NUCLEOLUS = (0.30, 0.37, 0.30)
FIN = (0.80, 0.87, 0.77)
COSTA = (0.50, 0.58, 0.50)
FLAG = (0.86, 0.91, 0.84)
AXOSTYLE = (0.90, 0.93, 0.88)


def axis(t):
    return Vector((0.0, -LENGTH / 2 + LENGTH * t, 0.0))


def radius(t):
    t = min(max(t, 0.0), 1.0)
    return RADIUS * math.sin(math.pi * t ** 0.75) ** 0.8


def body_point(t, phi):
    r = radius(t) * (1.0 + 0.04 * noise.noise(Vector((math.cos(phi) * 2, t * 5, math.sin(phi) * 2))))
    return axis(t) + Vector((math.cos(phi) * r, 0, math.sin(phi) * r * FLATTEN))


def fin_point(t, s):
    """Point on the membrane at t, s = 0 (root, inside the body) .. 1 (free edge), and its normal."""
    out = Vector((math.cos(FIN_PHI), 0, math.sin(FIN_PHI) * FLATTEN)).normalized()
    normal = Vector((0, 1, 0)).cross(out)
    k = (t - FIN_T[0]) / (FIN_T[1] - FIN_T[0])
    width = FIN_WIDTH * math.sin(math.pi * min(1.0, k * 0.85 + 0.08)) ** 0.5
    ruffle = FIN_RUFFLE * math.sin(k * math.tau * FIN_WAVES) * s ** 1.5 * math.sin(math.pi * k) ** 0.4
    root = body_point(t, FIN_PHI)
    return root - out * 0.02 + out * (0.02 + width) * s + normal * ruffle, normal


def make_body():
    bm = bmesh.new()
    sides = 16
    rings = []
    for i in range(RINGS + 1):
        t = i / RINGS
        t = t ** 1.15  # more rings toward the rounded front
        if i == 0 or i == RINGS:
            rings.append([bm.verts.new(axis(t))])
            continue
        rings.append([bm.verts.new(body_point(t, k / sides * math.tau)) for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        t = (co.y + LENGTH / 2) / LENGTH
        c = nh.lerp(BODY, BODY_DEEP, nh.smoothstep(0.45, 1.0, t))
        return tuple(k * (1.0 + 0.04 * noise.noise(co * 14.0)) for k in c)

    return bm, color


def nucleus_lens(rings=4, segs=16, dt=0.19, dphi=0.36, height=0.014):
    """A thin lens lying on the body where the nucleus shows through (an ellipse in (t, phi))."""
    bm = bmesh.new()
    t0, phi0 = NUCLEUS_T, math.pi / 2 + 0.25
    out = []

    def pt(rho, a):
        t, phi = t0 + dt * rho * math.sin(a), phi0 + dphi * rho * math.cos(a)
        p = body_point(t, phi)
        n = (p - axis(t)).normalized()
        return p + n * (height * (1 - rho * rho) + 0.002)

    centre = bm.verts.new(pt(0, 0))
    grid = [[bm.verts.new(pt(r / rings, k / segs * math.tau)) for k in range(segs)] for r in range(1, rings + 1)]
    for k in range(segs):
        bm.faces.new([centre, grid[0][k], grid[0][(k + 1) % segs]])
    for a, b in zip(grid, grid[1:]):
        for k in range(segs):
            j = (k + 1) % segs
            bm.faces.new([a[k], b[k], b[j], a[j]])
    bm.normal_update()
    for f in bm.faces:  # face outward
        if f.normal.dot(f.calc_center_median() - axis(NUCLEUS_T)) < 0:
            f.normal_flip()
    c = centre.co.copy()

    def color(co, n):
        return nh.lerp(NUCLEOLUS, NUCLEUS, nh.smoothstep(0.02, 0.05, (co - c).length))

    return bm, color


def make_fin(thick=0.008):
    bm = bmesh.new()
    rows = (0.0, 0.4, 0.75, 1.0)
    n = 40
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
        bm.faces.new([ta[-1], tb[-1], bb[-1], ba[-1]])
    for top, bot in (grid[0], grid[-1]):
        for j in range(len(rows) - 1):
            bm.faces.new([top[j], top[j + 1], bot[j + 1], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    mb = nh.MeshBuilder()
    mb.add(*make_body())

    # elongated nucleus near the front, a low lens following the upper surface
    mb.add(*nucleus_lens())

    # undulating membrane, the costa along its root and the recurrent flagellum along its edge
    mb.add(make_fin(), FIN)
    costa = [body_point(FIN_T[0] + (FIN_T[1] - FIN_T[0]) * i / 12, FIN_PHI) for i in range(13)]
    mb.add(nh.tube(costa, [0.012] * 12 + [0.0], sides=5), COSTA)
    rec = [axis(0.02) + Vector((0.03, 0, 0.03))]
    for i in range(41):
        rec.append(fin_point(FIN_T[0] + (FIN_T[1] - FIN_T[0]) * i / 40, 1.0)[0])
    mb.add(nh.tube(rec, [0.010] * (len(rec) - 2) + [0.007, 0.0], sides=5), FLAG)

    # axostyle: a glassy rod through the body, poking out behind as a pointed spike
    mb.add(nh.tube([axis(0.55), axis(0.9), axis(1.0) + Vector((0, 0.02, 0)), axis(1.0) + Vector((0, SPIKE, 0))],
                   [0.030, 0.026, 0.022, 0.0], sides=8), AXOSTYLE)

    # four free anterior flagella fanning forward from the front
    base = axis(0.0) + Vector((0.0, 0.03, 0.02))
    for i in range(FLAGELLA):
        a = (i + 0.5) / FLAGELLA * math.tau + 0.4
        spread = Vector((math.cos(a), 0, math.sin(a) * 0.8))
        pts = []
        n = 12
        for k in range(n + 1):
            u = k / n
            p = base + Vector((0, -FLAG_LEN * u, 0)) + spread * (0.30 * u ** 1.3)
            # whip-like wave across the flagellum's plane, growing toward the tip
            side = spread.cross(Vector((0, 1, 0)))
            p += side * 0.05 * math.sin(u * math.tau * 1.1 + i * 1.3) * u
            pts.append(p)
        mb.add(nh.tube(pts, [0.011] * (n - 1) + [0.007, 0.0], sides=5), FLAG)

    obj = mb.to_object("Trichomonas", roughness=0.45)
    vs = obj.data.vertices
    mid = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Trichomonas", views=((35, 35), (0, 80), (-90, 10)))
