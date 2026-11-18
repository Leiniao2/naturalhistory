"""
Procedural low-poly Arcella vulgaris (testate amoeba) for colony instancing.

A brown-amber, dome-shaped test (shell) like a flattened beret: a domed top with steep sides
rolling round a thick rim onto a concave underside that funnels up to a round central aperture
with a slightly raised lip. The test wall is finely pitted in a hexagonal pattern (dark pits in
paler ridges, painted in the colour), darker and browner over the older crown, paler toward the
rim. Inside the aperture the pale, granular cell shows, and four short blunt lobopodia
(pseudopods) poke out of it, reaching down and a little outward. Colour is in vertex colours
(see nh_model).

Usage:
  blender --background --python tools/blender/arcella_vulgaris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Arcella.fbx
About 1.6 units across, aperture facing down (-Z), front -Y. Pivot at the centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

SEED = 5
R = 0.78              # test radius at the rim
H = 0.46              # dome height above the rim
APERTURE = 0.19       # aperture radius
DENSITY = 80          # lathe vertices per unit of circumference radius (n = r * DENSITY)
PIT = 0.13            # spacing of the hexagonal pits

TEST = (0.70, 0.42, 0.14)        # amber
TEST_DARK = (0.44, 0.24, 0.08)   # older brown crown
TEST_PALE = (0.86, 0.62, 0.28)   # young rim
PIT_COL = (0.26, 0.13, 0.05)
LIP = (0.36, 0.20, 0.07)
CELL = (0.88, 0.86, 0.76)        # pale granular cytoplasm
CELL_GRAIN = (0.70, 0.68, 0.58)
POD = (0.96, 0.90, 0.76)         # clear hyaline lobopodia
POD_BASE = (0.88, 0.80, 0.64)


def profile():
    """(r, z, kind) from the crown down round the rim, under to the aperture, then the cell."""
    pts = [(0.0, H, "dome")]
    p = 2.6
    dense = []
    for i in range(201):
        a = i / 200 * math.pi / 2
        s, c = math.sin(a), math.cos(a)
        dense.append((R * 0.97 * s ** (2 / p), 0.06 + (H - 0.06) * c ** (2 / p)))
    # resample evenly by arc length so the pits keep their size from crown to rim
    acc = [0.0]
    for (r0, z0), (r1, z1) in zip(dense, dense[1:]):
        acc.append(acc[-1] + math.hypot(r1 - r0, z1 - z0))
    steps = 18
    j = 0
    for i in range(1, steps + 1):
        target = acc[-1] * i / steps
        while j < len(dense) - 2 and acc[j + 1] < target:
            j += 1
        t = (target - acc[j]) / (acc[j + 1] - acc[j])
        pts.append((*nh.lerp(dense[j], dense[j + 1], t), "dome"))
    # thick rounded rim curling under
    for a in (20, 55, 95, 135):
        t = math.radians(a)
        pts.append((R * 0.91 + 0.07 * math.cos(t), 0.0 - 0.07 * math.sin(t) + 0.01, "rim"))
    # concave underside funnelling up to the aperture
    for t in (0.2, 0.45, 0.7, 0.88):
        r = nh.lerp((R * 0.86,), (APERTURE + 0.04,), t)[0]
        z = -0.06 + 0.10 * t * t
        pts.append((r, z, "under"))
    # raised lip, then into the aperture
    pts += [(APERTURE + 0.015, 0.0, "lip"), (APERTURE, -0.015, "lip"), (APERTURE - 0.02, 0.01, "lip"),
            (APERTURE - 0.03, 0.07, "cell"), (APERTURE * 0.55, 0.10, "cell"), (0.0, 0.11, "cell")]
    return pts


def hex_pit(u, v):
    """0..1, 1 at the centre of a pit on a hexagonal lattice of spacing PIT."""
    # axial coordinates of the triangular lattice of pit centres
    q = (u * math.sqrt(3) / 3 - v / 3) / PIT * math.sqrt(3)
    r = (v * 2 / 3) / PIT * math.sqrt(3)
    # cube rounding
    x, z = q, r
    y = -x - z
    rx, ry, rz = round(x), round(y), round(z)
    dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry
    cu = (rx + rz / 2) * PIT
    cv = rz * PIT * math.sqrt(3) / 2
    d = math.hypot(u - cu, v - cv) / PIT
    return 1.0 - nh.smoothstep(0.22, 0.40, d)


def lathe(pts):
    """Surface of revolution; each ring gets a vertex count proportional to its radius so the
    mesh stays even (rings of different counts are stitched by angle)."""
    bm = bmesh.new()
    vcol = {}
    rings = []
    arc = 0.0
    prev = None
    for i, (r, z, kind) in enumerate(pts):
        if prev is not None:
            arc += math.hypot(r - prev[0], z - prev[1])
        prev = (r, z)
        if r < 1e-6:
            v = bm.verts.new((0.0, 0.0, z))
            rings.append([(0.0, v)])
            vcol[v] = shell_colour(kind, 0.0, 0.0, arc, z, Vector((0, 0, z)))
            continue
        n = max(6, int(round(r * DENSITY / 3)) * 3)
        off = (i % 2) * 0.5
        ring = []
        for k in range(n):
            a = (k + off) / n * math.tau
            co = Vector((math.cos(a) * r, math.sin(a) * r, z))
            v = bm.verts.new(co)
            vcol[v] = shell_colour(kind, r, a, arc, z, co)
            ring.append((a, v))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        stitch(bm, a, b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def stitch(bm, a, b):
    if len(a) == 1 or len(b) == 1:
        hub, ring = (a, b) if len(a) == 1 else (b, a)
        n = len(ring)
        for k in range(n):
            bm.faces.new([hub[0][1], ring[k][1], ring[(k + 1) % n][1]])
        return
    i = j = 0
    na, nb = len(a), len(b)
    while i < na or j < nb:
        ai, bj = a[i % na], b[j % nb]
        an = a[(i + 1) % na][0] + (math.tau if i + 1 >= na else 0)
        bn = b[(j + 1) % nb][0] + (math.tau if j + 1 >= nb else 0)
        if j >= nb or (i < na and an <= bn):
            bm.faces.new([ai[1], a[(i + 1) % na][1], bj[1]])
            i += 1
        else:
            bm.faces.new([ai[1], b[(j + 1) % nb][1], bj[1]])
            j += 1


def shell_colour(kind, r, a, arc, z, co):
    grain = noise.noise(co * 9.0)
    if kind == "cell":
        g = nh.smoothstep(0.2, 0.6, noise.noise(co * 40.0))
        return nh.lerp(CELL, CELL_GRAIN, g * 0.7)
    if kind == "lip":
        return LIP
    # pits on the azimuthal-equidistant map of the test (arc from the crown, angle round it)
    u, v = arc * math.cos(a), arc * math.sin(a)
    pit = hex_pit(u, v)
    crown = 1.0 - nh.smoothstep(0.0, 0.85, arc)
    c = nh.lerp(TEST, TEST_DARK, crown * 0.8)
    c = nh.lerp(c, TEST_PALE, nh.smoothstep(0.75, 1.1, arc) * 0.6)
    if kind == "under":
        c = nh.lerp(TEST, TEST_DARK, 0.35)
        pit *= 0.6
    c = tuple(min(1.0, x * (1.0 + 0.10 * grain)) for x in c)
    return nh.lerp(c, PIT_COL, pit * 0.75)


def lobopod(start, direction, length, radius, rng):
    d = Vector(direction).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    pts, radii = [], []
    for k in range(6):
        t = k / 5
        p = Vector(start) + d * (length * t) + side * 0.025 * math.sin(t * 3.0 + rng.uniform(0, 3))
        pts.append(p)
        radii.append(radius * (1.15 - 0.2 * t + 0.08 * math.sin(t * 7.0)))
    bm = nh.tube(pts, radii, sides=10, cap_start=False, cap_end=False)
    tip = nh.ellipsoid(tuple(pts[-1]), (radii[-1],) * 3, subdivisions=2)
    return bm, tip, pts[0]


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    bm, vcol = lathe(profile())
    nf.add_colored(mb, bm, vcol)

    # lobopodia: short and blunt, out of the aperture, reaching down and a little outward
    for k, (ang, length, rad) in enumerate(((-100, 0.46, 0.065), (-10, 0.38, 0.060),
                                            (95, 0.42, 0.062), (175, 0.30, 0.055))):
        a = math.radians(ang + rng.uniform(-10, 10))
        out = Vector((math.cos(a), math.sin(a), 0.0))
        start = out * 0.07 + Vector((0, 0, 0.09))
        d = out * rng.uniform(0.9, 1.3) + Vector((0, 0, -1.0))
        body, tip, base = lobopod(start, d, length, rad, rng)

        def col(co, n, base=base, length=length):
            t = nh.smoothstep(0.0, length, (co - base).length)
            return nh.lerp(POD_BASE, POD, t)

        mb.add(body, col)
        mb.add(tip, POD)

    obj = mb.to_object("Arcella", roughness=0.5)
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    for v in obj.data.vertices:
        for a in range(3):
            v.co[a] -= (lo[a] + hi[a]) / 2
    return obj


if __name__ == "__main__":
    nh.run(build, "Arcella", views=((35, -20), (-70, 35), (20, -70)))
