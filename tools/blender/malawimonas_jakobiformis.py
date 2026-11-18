"""
Procedural low-poly Malawimonas jakobiformis, a malawimonad: a small excavate flagellate close to
the common root of the Discoba (euglenids, trypanosomes, jakobids) and the Metamonada.

A bean-shaped cell, rounded at both ends and bowed so the -X side is a little concave. Down that
side runs the deep ventral feeding groove that gives the excavates their name: a recessed, darker
channel with soft raised lips, open from just behind the front almost to the rear. Two flagella
leave the front end of the groove: a short anterior one curling forward and up, and a long
posterior one that lies along the floor of the groove, where it beats to draw in food, and then
trails out behind the cell, carrying a thin vane (a narrow fin) along its length. The nucleus
shows through near the front on the dorsal side and a few small vacuoles toward the rear. Pale
bluish-grey, the groove darker. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/malawimonas_jakobiformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Malawimonas.fbx
About 1.6 units long from the anterior flagellum's tip to the posterior flagellum's tip, the cell
~0.6 wide. Faces -Y. Pivot at the centre of the bounds (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

LENGTH = 0.80          # cell length along Y
RADIUS = 0.29          # widest radius
FLATTEN = 0.86         # Z scale of the cross-section
BEND = 0.09            # the axis bows toward +X so the groove side is concave (bean shape)
RINGS = 26
SIDES = 30
GROOVE_PHI = math.pi + 0.12   # -X side, a touch ventral
GROOVE_W = 0.50        # half-width of the groove floor, radians round the body
GROOVE_T = (0.07, 0.88)
GROOVE_DEPTH = 0.42    # fraction of the radius the floor sinks in
LIP = 0.07             # raised lips either side of the groove
ANT_FLAG = 0.28
POST_TRAIL = 0.60      # how far the posterior flagellum trails behind the cell
VANE_W = 0.026

BODY = (0.74, 0.80, 0.86)
BODY_DORSAL = (0.80, 0.85, 0.90)
LIP_COL = (0.66, 0.72, 0.80)
GROOVE = (0.30, 0.36, 0.50)
GROOVE_DEEP = (0.18, 0.22, 0.34)
NUCLEUS = (0.60, 0.66, 0.76)
NUCLEOLUS = (0.44, 0.50, 0.62)
VACUOLE = (0.88, 0.92, 0.96)
FLAG = (0.88, 0.91, 0.95)
VANE = (0.80, 0.85, 0.92)


def axis(t):
    return Vector((BEND * math.sin(math.pi * t), -LENGTH / 2 + LENGTH * t, 0.0))


def radius(t):
    t = min(max(t, 0.0), 1.0)
    return RADIUS * math.sin(math.pi * t) ** 0.55 * (1.0 - 0.08 * t)


def groove(t, phi):
    """(depth factor 0..1 of the groove floor, lip factor 0..1) at a point on the body."""
    d = (phi - GROOVE_PHI + math.pi) % math.tau - math.pi
    along = nh.smoothstep(GROOVE_T[0], GROOVE_T[0] + 0.12, t) * (1.0 - nh.smoothstep(GROOVE_T[1] - 0.15, GROOVE_T[1], t))
    # the groove widens a little toward the front, where it opens
    w = GROOVE_W * (1.15 - 0.3 * t)
    floor = math.exp(-(d / w) ** 4) * along
    lip = math.exp(-((abs(d) - w * 1.15) / 0.16) ** 2) * along
    return floor, lip


def surface(t, phi):
    floor, lip = groove(t, phi)
    r = radius(t) * (1.0 - GROOVE_DEPTH * floor + LIP * lip)
    r *= 1.0 + 0.03 * noise.noise(Vector((math.cos(phi) * 1.5, t * 4.0, math.sin(phi) * 1.5)))
    return axis(t) + Vector((math.cos(phi) * r, 0, math.sin(phi) * r * FLATTEN))


def outward(t, phi):
    return Vector((math.cos(phi), 0, math.sin(phi) / FLATTEN)).normalized()


def make_body():
    bm = bmesh.new()
    vcol = {}
    rings = []
    for i in range(RINGS + 1):
        u = i / RINGS
        t = 0.5 - 0.5 * math.cos(u * math.pi)
        if i == 0 or i == RINGS:
            v = bm.verts.new(axis(t))
            vcol[v] = BODY
            rings.append([v])
            continue
        ring = []
        for k in range(SIDES):
            phi = k / SIDES * math.tau
            v = bm.verts.new(surface(t, phi))
            floor, lip = groove(t, phi)
            c = nh.lerp(BODY, BODY_DORSAL, max(0.0, math.sin(phi)) * 0.7)
            c = nh.lerp(c, LIP_COL, lip * 0.8)
            c = nh.lerp(c, GROOVE, nh.smoothstep(0.05, 0.4, floor))
            c = nh.lerp(c, GROOVE_DEEP, nh.smoothstep(0.5, 0.95, floor) * nh.smoothstep(0.12, 0.4, t))
            vcol[v] = c
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def ribbon(pts, sides, widths, thick=0.006):
    """Thin vane: a strip from each point along its side vector, a little thickness for both faces."""
    bm = bmesh.new()
    rows = []
    for p, s, w in zip(pts, sides, widths):
        up = s.cross(Vector((0, 1, 0)))
        if up.length < 1e-4:
            up = Vector((0, 0, 1))
        up = up.normalized() * thick * 0.5
        rows.append([bm.verts.new(p + up), bm.verts.new(p + s * w + up),
                     bm.verts.new(p + s * w - up), bm.verts.new(p - up)])
    for a, b in zip(rows, rows[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    mb = nh.MeshBuilder()
    bm, vcol = make_body()
    nf.add_colored(mb, bm, vcol)

    # nucleus near the front on the dorsal side, a low bulge with a darker nucleolus
    np_, nn = surface(0.28, math.radians(70)), outward(0.28, math.radians(70))
    mb.add(nh.uv_ellipsoid(tuple(np_ - nn * 0.058), (0.08, 0.09, 0.07), segments=16, rings=10), NUCLEUS)
    mb.add(nh.uv_ellipsoid(tuple(np_ + Vector((0.0, 0.01, 0.0))), (0.03, 0.03, 0.022), segments=10, rings=6),
           NUCLEOLUS)
    # a few small pale vacuoles toward the rear
    for t, phi, r in ((0.66, math.radians(50), 0.045), (0.76, math.radians(110), 0.038),
                      (0.58, math.radians(-20), 0.040)):
        p, n = surface(t, phi), outward(t, phi)
        mb.add(nh.uv_ellipsoid(tuple(p - n * r * 0.8), (r, r * 1.1, r), segments=10, rings=6), VACUOLE)

    # both flagella leave the front end of the groove
    g0 = GROOVE_T[0] + 0.05
    root = surface(g0, GROOVE_PHI) - outward(g0, GROOVE_PHI) * 0.01
    # short anterior flagellum: forward and up in a gentle curl
    ant = [root]
    for k in range(1, 15):
        u = k / 14
        ant.append(root + Vector((-0.04 * u + 0.05 * u * u, -ANT_FLAG * u, 0.10 * math.sin(u * 2.2))))
    mb.add(nh.tube(ant, [0.014] * 14 + [0.0], sides=5), FLAG)

    # long posterior flagellum: along the floor of the groove, then trailing out behind
    post, sides = [], []
    n_in = 14
    for k in range(n_in + 1):
        t = g0 + (0.80 - g0) * k / n_in
        o = outward(t, GROOVE_PHI)
        post.append(surface(t, GROOVE_PHI) + o * 0.03)
        sides.append(o)
    # out of the back of the groove it runs on past the rear end in a slow wave
    end, o_end = post[-1], sides[-1]
    n_out = 18
    for k in range(1, n_out + 1):
        u = k / n_out
        post.append(end + Vector((0.07 * u * u + 0.06 * math.sin(u * math.tau * 1.1) * u ** 1.2,
                                  (POST_TRAIL + 0.18) * u, 0.015 * math.sin(u * math.tau * 0.8))))
        sides.append(o_end)
    radii = [0.015] * (len(post) - 4) + [0.013, 0.011, 0.008, 0.0]
    mb.add(nh.tube(post, radii, sides=5), FLAG)
    # the thin vane along it, narrowing to nothing at the tip
    widths = [VANE_W * (1.0 - nh.smoothstep(0.75, 1.0, i / (len(post) - 1))) * nh.smoothstep(0.0, 0.08, i / (len(post) - 1))
              for i in range(len(post))]
    mb.add(ribbon(post, sides, widths), VANE)

    obj = mb.to_object("Malawimonas", roughness=0.4)
    vs = obj.data.vertices
    mid = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Malawimonas", views=((-55, 30), (0, 85), (-90, 10), (35, 35)))
