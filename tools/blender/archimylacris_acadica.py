"""
Procedural Archimylacris acadica (Carboniferous roachoid, an early cockroach relative) for map colonies.

A flat, broad cockroach-like insect scuttling on the ground: a large, near-oval
shield-like pronotum covers the head, darker in the middle with a pale
translucent rim; behind it the two long leathery forewings (tegmina) lie folded
flat over the abdomen, the left overlapping the right, each a brown slab with
thicker dark vein ribbons on top (subcosta and radius running along the broad
costal field, branching media and cubitus fanning out to the tip, and the
curved anal veins of the clavus), so the venation stays crisp. Long thin
antennae sweep forward from under the pronotum, the six legs splay out with
flattened femora and spiny tibiae, and a pair of beaded cerci sticks out
behind the wing tips. Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/archimylacris_acadica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archimylacris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

PRONOTUM = (0.30, 0.18, 0.09)
RIM = (0.66, 0.52, 0.32)          # pale translucent pronotum / costal margin
WING = (0.46, 0.30, 0.15)
WING_BASE = (0.30, 0.18, 0.09)
VEIN = (0.17, 0.10, 0.05)
BODY = (0.24, 0.15, 0.08)
LEG = (0.42, 0.26, 0.13)
LEG_DARK = (0.22, 0.13, 0.06)
EYE = (0.05, 0.04, 0.04)
LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()

BASE = 0.055                      # underside of the body above the ground
WING_Y0, WING_LEN, WING_W = -0.20, 0.80, 0.215
WING_Z = BASE + 0.062
T_WING, T_VEIN = 0.006, 0.010


# ---------------------------------------------------------------- body

def build_body(mb):
    # abdomen and thorax under the wings
    mb.add(nh.uv_ellipsoid((0, 0.16, BASE + 0.022), (0.15, 0.34, 0.024), 14, 8), BODY)
    mb.add(nh.uv_ellipsoid((0, -0.16, BASE + 0.03), (0.13, 0.12, 0.035), 12, 6), BODY)
    # head tucked under the front of the pronotum, angled down
    hc = Vector((0, -0.42, BASE + 0.018))
    mb.add(nh.uv_ellipsoid(hc, (0.075, 0.060, 0.040), 12, 8), PRONOTUM)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(hc + Vector((s * 0.058, -0.012, 0.010)), (0.022, 0.030, 0.022), 8, 5), EYE)
        # mouthparts
        mb.add(nh.tube([hc + Vector((s * 0.02, -0.05, -0.02)), hc + Vector((s * 0.03, -0.07, -0.035))],
                       [0.010, 0.004], sides=4), LEG_DARK)
        # long filiform antennae, gently curving forward and out
        a0 = hc + Vector((s * 0.035, -0.055, 0.012))
        pts = []
        for k in range(9):
            t = k / 8
            pts.append(a0 + Vector((s * (0.08 * t + 0.20 * t * t), -0.58 * t + 0.08 * t * t,
                                    0.05 * math.sin(t * math.pi * 0.9))))
        mb.add(nh.tube(pts, [0.008 - 0.0055 * k / 8 for k in range(9)], sides=4), LEG_DARK)


def build_pronotum(mb):
    """Broad shield over the head: flattened disc, slightly upturned pale rim."""
    c = Vector((0.0, -0.315, BASE + 0.055))
    rx, ry = 0.205, 0.150
    bm = bmesh.new()
    rings, sides = 6, 28
    centre = bm.verts.new((c.x, c.y, c.z + 0.040))
    prev = None
    for i in range(1, rings + 1):
        r = i / rings
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            x, y = math.cos(a) * rx * r, math.sin(a) * ry * r
            y += 0.020 * r * r * (1 if math.sin(a) > 0 else 0.4)  # hind margin a bit straighter
            z = 0.040 * (1 - r * r) + 0.006 * nh.smoothstep(0.75, 1.0, r)
            ring.append(bm.verts.new((c.x + x, c.y + y, c.z + z)))
        for k in range(sides):
            j = (k + 1) % sides
            if prev is None:
                bm.faces.new([centre, ring[k], ring[j]])
            else:
                bm.faces.new([prev[k], ring[k], ring[j], prev[j]])
        prev = ring
    under = [bm.verts.new((v.co.x * 0.92, c.y + (v.co.y - c.y) * 0.92, c.z - 0.012)) for v in prev]
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new([prev[j], prev[k], under[k], under[j]])
    bm.faces.new(list(reversed(under)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        r = math.hypot((co.x - c.x) / rx, (co.y - c.y) / ry)
        k = nh.lerp(PRONOTUM, RIM, nh.smoothstep(0.80, 0.97, r))
        h = max(0.0, n.dot(LIGHT_DIR)) ** 12
        return nh.lerp(k, (0.62, 0.48, 0.34), h * 0.45)
    mb.add(bm, col)


# ---------------------------------------------------------------- tegmina

WING_CX = WING_W * 0.40
WING_CY = WING_Y0 + WING_LEN * 0.5


def wing_point(a):
    """Margin of the right tegmen at angle a (0 = outer side, 90 = tip, 180 = inner side, -90 = base):
    an elongate oval, narrower toward the base, x out from the midline."""
    narrow = 1.0 - 0.40 * max(0.0, -math.sin(a)) ** 2
    x = WING_CX + WING_W * 0.50 * math.cos(a) * narrow
    y = WING_CY + WING_LEN * 0.5 * math.sin(a)
    return (x, y)


def wing_z(x):
    """Tegmina lie flat, bending down toward the outer margin."""
    u = max(0.0, x) / WING_W
    return WING_Z - 0.045 * u * u


def ribbon(points, w0, w1, thickness):
    pts = [Vector(p) for p in points]
    bm = bmesh.new()
    rows = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        w = w0 + (w1 - w0) * i / max(len(pts) - 1, 1)
        rows.append([bm.verts.new((q.x, q.y, z)) for q in (p + nrm * w, p - nrm * w)
                     for z in (thickness / 2, -thickness / 2)])
    for (lt, lb, rt, rb), (lt2, lb2, rt2, rb2) in zip(rows, rows[1:]):
        bm.faces.new([lt, rt, rt2, lt2])
        bm.faces.new([lb, lb2, rb2, rb])
    return bm


def bezier(a, c, b, n=6):
    a, c, b = Vector(a), Vector(c), Vector(b)
    return [tuple(a * (1 - t) ** 2 + c * 2 * t * (1 - t) + b * t * t) for t in (k / n for k in range(n + 1))]


def build_wing():
    """[(bmesh, colour)] for the right tegmen (flat, z = 0 before draping)."""
    outline = [(*wing_point(math.radians(-90 + 360 * k / 40)), 0.0) for k in range(40)]

    def membrane(co, n):
        t = (co.y - WING_Y0) / WING_LEN
        c = nh.lerp(WING_BASE, WING, nh.smoothstep(0.0, 0.3, t))
        # pale, slightly thickened costal margin along the outer edge
        return nh.lerp(c, RIM, 0.55 * nh.smoothstep(0.80, 0.97, co.x / WING_W) * (t < 0.75))

    parts = [(nh.flat_panel(outline, T_WING), membrane)]

    def end(deg):
        x, y = wing_point(math.radians(deg))
        return Vector((WING_CX + (x - WING_CX) * 0.96, WING_CY + (y - WING_CY) * 0.97))

    def vein(a, b, w0, w1, bow=0.0):
        a, b = Vector(a), Vector(b)
        ctrl = a.lerp(b, 0.5) + Vector((bow, 0.0))
        parts.append((ribbon(bezier(a, ctrl, b), w0, w1, T_VEIN), VEIN))

    y0 = WING_Y0 + 0.05
    # subcosta: short, curving out into the broad costal field
    sc0 = Vector((WING_W * 0.62, y0))
    vein(sc0, end(-28), 0.0040, 0.0022, bow=-0.01)
    for deg in (-50, -10):
        vein(sc0.lerp(end(-28), 0.45), end(deg), 0.0026, 0.0018)
    # radius: long stem near the front, branches running to the outer margin and tip
    r0, rf = Vector((WING_W * 0.52, y0)), Vector((WING_W * 0.62, WING_CY + 0.02))
    vein(r0, rf, 0.0045, 0.0035)
    for deg in (8, 30, 52, 72):
        vein(rf, end(deg), 0.0030, 0.0018, bow=0.01)
    # media: forks twice toward the apex
    m0, mf = Vector((WING_W * 0.40, y0)), Vector((WING_W * 0.44, WING_CY + 0.10))
    vein(m0, mf, 0.0040, 0.0032)
    for deg in (88, 106):
        vein(mf, end(deg), 0.0028, 0.0017)
    # cubitus: toward the inner margin behind the clavus
    c0, cf = Vector((WING_W * 0.28, y0 + 0.02)), Vector((WING_W * 0.22, WING_CY + 0.02))
    vein(c0, cf, 0.0038, 0.0030)
    for deg in (124, 142, 160):
        vein(cf, end(deg), 0.0026, 0.0016)
    # claval furrow and the short curved anal veins of the clavus
    cl = end(196)
    vein((WING_W * 0.22, y0), cl, 0.0042, 0.0028, bow=0.02)
    for k, deg in enumerate((205, 214, 223)):
        vein((WING_W * (0.16 - k * 0.025), y0 + 0.01), end(deg), 0.0026, 0.0016, bow=0.008)
    return parts


def place_wing(mb, parts, mirror, lift):
    for bm, col in parts:
        for v in bm.verts:
            v.co.z += wing_z(v.co.x) + lift
            if mirror:
                v.co.x = -v.co.x
        if mirror:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        mb.add(bm, col, smooth=False)


# ---------------------------------------------------------------- legs and cerci

def spiny_leg(mb, s, hip, knee, foot, spines=3):
    tarsus = foot + Vector((s * 0.04, (foot - knee).normalized().y * 0.05, 0.0))
    mb.add(nh.tube([hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.008)), knee], [0.017, 0.020, 0.013], sides=5,
                   scale_xy=(1.0, 0.6)), LEG)
    mb.add(nh.tube([knee, foot], [0.011, 0.008], sides=4), LEG)
    mb.add(nh.tube([foot, tarsus], [0.006, 0.003], sides=4), LEG_DARK)
    d = (foot - knee)
    for k in range(spines):
        p = knee + d * ((k + 0.7) / (spines + 0.5))
        out = Vector((s, 0, 0.6)).normalized()
        mb.add(nh.tube([p, p + out * 0.028 + d.normalized() * 0.012], [0.004, 0.0], sides=3), LEG_DARK)
        mb.add(nh.tube([p, p + Vector((-s * 0.3, 0, 0.8)).normalized() * 0.022 + d.normalized() * 0.01],
                       [0.0035, 0.0], sides=3), LEG_DARK)


def build_legs(mb):
    legs = [  # hip y, knee (x, dy), foot (x, dy)
        (-0.25, (0.20, -0.06), (0.25, -0.16)),
        (-0.15, (0.24, 0.02), (0.36, 0.06)),
        (-0.05, (0.25, 0.12), (0.37, 0.32)),
    ]
    for s in (-1, 1):
        for y, (kx, kdy), (fx, fdy) in legs:
            hip = Vector((s * 0.07, y, BASE + 0.005))
            knee = Vector((s * kx, y + kdy, BASE + 0.035))
            foot = Vector((s * fx, y + fdy, 0.0))
            spiny_leg(mb, s, hip, knee, foot)
    # cerci: beaded, splayed, poking out behind the wing tips
    for s in (-1, 1):
        b = Vector((s * 0.03, 0.48, BASE + 0.03))
        pts = [b + Vector((s * 0.05 * k, 0.05 * k, 0.012 * k)) for k in range(5)]
        mb.add(nh.tube(pts, [0.012, 0.011, 0.009, 0.007, 0.0], sides=4), LEG_DARK)
        for p in pts[1:-1]:
            mb.add(nh.ellipsoid(p, (0.010,) * 3, 1), LEG_DARK)


def build():
    mb = nh.MeshBuilder()
    build_body(mb)
    build_legs(mb)
    place_wing(mb, build_wing(), mirror=False, lift=0.0)
    place_wing(mb, build_wing(), mirror=True, lift=0.008)   # left tegmen overlaps the right
    build_pronotum(mb)
    obj = mb.to_object("Archimylacris", roughness=0.45)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.3f}, hip {BASE + 0.005:.3f} -> mapHip {(BASE + 0.005) / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "Archimylacris", ground=(0.30, 0.26, 0.18), views=((35, 30), (0, 80), (-90, 10)))
