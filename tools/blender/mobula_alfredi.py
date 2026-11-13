"""
Procedural low-poly reef manta ray (Mobula alfredi) for map colonies (Swim style).

A broad diamond of wing-like pectoral fins (wingspan ~2.4x body length) with
swept, slightly upturned tips caught mid-flap, two cephalic fins unfurled in
front of a wide terminal mouth, a small dorsal fin and a short whip tail.
Charcoal back with the pale shoulder patches behind the head that mark reef
mantas, white underside with dark wing margins and gill slits.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/mobula_alfredi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MantaRay.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BACK = (0.07, 0.075, 0.09)       # charcoal
BACK_EDGE = (0.03, 0.03, 0.04)
PATCH = (0.82, 0.84, 0.86)       # pale shoulder patches
BELLY = (0.94, 0.94, 0.92)
BELLY_MARGIN = (0.22, 0.23, 0.26)
GILL = (0.30, 0.30, 0.33)
MOUTH = (0.04, 0.04, 0.05)
EYE = (0.01, 0.01, 0.01)

# Half outline (x >= 0), front (-Y) to back (+Y); mirrored for the left side.
HALF_OUTLINE = [
    (0.00, -0.38), (0.15, -0.39), (0.32, -0.34), (0.52, -0.26), (0.72, -0.13),
    (0.89, 0.00), (1.02, 0.11), (0.95, 0.14), (0.78, 0.13), (0.56, 0.15),
    (0.36, 0.22), (0.22, 0.32), (0.10, 0.40), (0.00, 0.42),
]

RINGS = 14
SAMPLES = 80


def catmull(points, n):
    """Closed Catmull-Rom resample of a 2D polygon to n points."""
    out = []
    m = len(points)
    for i in range(n):
        t = i / n * m
        k = int(t)
        u = t - k
        p0, p1, p2, p3 = (Vector(points[(k + j) % m]) for j in (-1, 0, 1, 2))
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u))
    return out


def outline():
    right = HALF_OUTLINE
    left = [(-x, y) for x, y in reversed(HALF_OUTLINE[1:-1])]
    return catmull(right + left, SAMPLES)


def thickness(x, y):
    """Thick central disc, thin wings."""
    body = math.exp(-(x / 0.26) ** 2 - ((y + 0.02) / 0.34) ** 2)
    return 0.10 * body + 0.014


def flap(x, y):
    """Wings caught on the upstroke: tips curl up, trailing edge slightly lower."""
    ax = abs(x)
    return 0.16 * ax ** 2.2 + 0.03 * ax * y


def body_shell():
    bm = bmesh.new()
    rim = outline()
    top_c = bm.verts.new((0, 0, thickness(0, 0) * 0.62))
    bot_c = bm.verts.new((0, 0, -thickness(0, 0) * 0.38))
    tops, bots = [], []
    for k in range(1, RINGS):
        s = k / RINGS
        tr, br = [], []
        for p in rim:
            x, y = p.x * s, p.y * s
            edge = 1.0 - s ** 6
            t = thickness(x, y) * edge
            z0 = flap(x, y)
            tr.append(bm.verts.new((x, y, z0 + t * 0.62)))
            br.append(bm.verts.new((x, y, z0 - t * 0.38)))
        tops.append(tr)
        bots.append(br)
    edge_ring = [bm.verts.new((p.x, p.y, flap(p.x, p.y))) for p in rim]

    n = SAMPLES
    for ring_list, centre, flip in ((tops, top_c, False), (bots, bot_c, True)):
        rings = ring_list + [edge_ring]
        for j in range(n):
            a, b = rings[0][j], rings[0][(j + 1) % n]
            bm.faces.new([centre, b, a] if flip else [centre, a, b])
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(n):
                q = [r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]]
                bm.faces.new(list(reversed(q)) if flip else q)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def patch_strength(x, y):
    """Reef-manta shoulder patches: pale bands sweeping out and back from behind the head,
    split by a dark midline."""
    ax = abs(x)
    # rotate into the patch's frame (angled back toward the wing)
    a = math.radians(28)
    px = (ax - 0.27) * math.cos(a) - (y + 0.14) * math.sin(a)
    py = (ax - 0.27) * math.sin(a) + (y + 0.14) * math.cos(a)
    d = (px / 0.26) ** 2 + (py / 0.10) ** 2
    p = 1.0 - nh.smoothstep(0.35, 1.0, d)
    return min(1.0, p * 1.3) * nh.smoothstep(0.03, 0.09, ax)


def body_color(co, n):
    x, y = co.x, co.y
    r = max(abs(x) / 1.02, 0.0)
    if n.z >= 0.0:
        c = nh.lerp(PATCH, BACK, 1.0 - patch_strength(x, y))
        # darker leading/trailing margins
        rim_d = nh.smoothstep(0.75, 1.0, r) * 0.6
        return nh.lerp(c, BACK_EDGE, rim_d)
    c = BELLY
    # dark trailing margin and wingtips on the underside
    trailing = nh.smoothstep(0.0, 0.08, y - 0.04 - 0.06 * abs(x)) * nh.smoothstep(0.25, 0.5, abs(x))
    c = nh.lerp(c, BELLY_MARGIN, max(trailing * 0.8, nh.smoothstep(0.8, 1.0, r)))
    # five gill slits each side of the belly
    if 0.10 < abs(x) < 0.22 and -0.30 < y < -0.08:
        f = ((y + 0.30) / 0.045) % 1.0
        if f < 0.25:
            c = GILL
    return c


def cephalic_fin(side):
    pts = [(side * 0.125, -0.33, 0.0), (side * 0.13, -0.44, -0.005), (side * 0.12, -0.54, 0.0), (side * 0.105, -0.60, 0.012)]
    bm = nh.tube(pts, [0.055, 0.058, 0.045, 0.0], sides=8, scale_xy=(0.5, 1.0))
    # roll the paddles so their flat faces turn inward-down, like a scoop
    c = Vector(pts[1])
    nh.transform(bm, Matrix.Translation(c) @ Matrix.Rotation(math.radians(25 * side), 4, "Y") @ Matrix.Translation(-c))
    return bm


def cephalic_color(side):
    def color(co, n):
        inward = n.x * -side
        return nh.lerp(BACK, PATCH, nh.smoothstep(0.1, 0.8, inward) * 0.8)
    return color


def dorsal_fin():
    bm = nh.flat_panel([(0.0, 0.0, 0), (0.07, 0.0, 0), (0.0, 0.09, 0)], thickness=0.012)
    # panel is drawn in XY; stand it up in the YZ plane with the tip leaning back
    nh.transform(bm, Matrix.Rotation(math.radians(-90), 4, "Y"))
    nh.transform(bm, Matrix.Rotation(math.radians(90), 4, "X"))
    nh.transform(bm, Matrix.Translation((0, 0.30, thickness(0, 0.3) * 0.55)))
    return bm


def build():
    mb = nh.MeshBuilder()
    mb.add(body_shell(), body_color)
    for side in (-1, 1):
        mb.add(cephalic_fin(side), cephalic_color(side))
        mb.add(nh.ellipsoid((side * 0.165, -0.33, 0.035), (0.018, 0.022, 0.018), subdivisions=1), EYE)
    # wide terminal mouth between the cephalic fins
    mb.add(nh.ellipsoid((0, -0.385, 0.0), (0.105, 0.03, 0.022), subdivisions=2), MOUTH)
    mb.add(dorsal_fin(), BACK, smooth=False)
    tail = nh.tube([(0, 0.38, 0.01), (0, 0.55, 0.02), (0, 0.72, 0.035), (0, 0.86, 0.05)], [0.022, 0.012, 0.006, 0.0], sides=5)
    mb.add(tail, BACK)

    obj = mb.to_object("MantaRay", roughness=0.45)
    # pivot at the body centre
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "MantaRay", background=(0.05, 0.22, 0.30), views=((35, 30), (-90, 6), (0, 80), (20, -40)))
