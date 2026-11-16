"""
Procedural Favosites gothlandicus Lamarck, 1816 (Silurian "honeycomb coral", type species of
Favosites, originally from Gotland, Sweden) for the map: a massive, low-domed colony whose whole
upper surface is a honeycomb of polygonal corallite openings, on a little patch of reef rubble.

Favosites is a cerioid tabulate coral: its corallites are long, thin-walled prismatic tubes
(about 2-3 mm across in F. gothlandicus) packed together like the cells of a honeycomb, sharing
their walls, crossed inside by flat tabulae and connected through tiny mural pores in the walls.
Colonies are massive: domes, hemispheres or irregular lumps, typically a few to a few tens of
centimetres across, with a wrinkled basal skin (epitheca) underneath.

Here: a smooth lathe body from a Catmull-Rom (r, z) profile (narrow foot, flaring underside,
rounded margin, broad dome), slightly lobed and leaning, painted pale cream: that colour shows as
the shared walls. The corallites are hexagonal cups laid in staggered (hex-packed) rows over the
upward- and outward-facing surface, touching so their pale rim bands join into the shared
walls; each is a hexagonal fan with two inner rings (a pale wall band at the rim, then a drop to
a dark brown pit with a small olive-brown polyp disc in the middle; living colours are a
guess), its rim a little proud of the body and its centre lower. The underside is left bare: buff epitheca with darker concentric growth wrinkles.
The real corallites are millimetres wide, so the cells are stylised (much larger) to read at
map size. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/favosites_gothlandicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Favosites.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 21
SEGMENTS = 30         # around the colony body
SAMPLES = 20          # along the profile
CELL = 0.155          # corallite spacing (centre to centre)
CELL_R = 0.59         # hexagon radius as a fraction of CELL (0.577 = touching)
WALL_IN = 0.84        # inner edge of the pale wall band, as a fraction of the hexagon radius
PROUD = 0.011         # how far the cup rims sit above the body surface
CENTRE_PROUD = 0.0045 # ...and the cup centres (lower than the rims: a pit)
MIN_NZ = -0.05        # no corallites on surfaces facing further down than this
# (r, z) profile from the foot to the crown: narrow foot, flaring underside, rounded margin, dome
PROFILE = [
    (0.00, 0.00), (0.22, 0.00), (0.32, 0.03), (0.50, 0.08), (0.64, 0.14), (0.72, 0.21),
    (0.73, 0.28), (0.70, 0.38), (0.62, 0.51), (0.48, 0.63), (0.28, 0.71), (0.00, 0.74),
]
LEAN = Vector((0.04, 0.03, 0.0))   # crown offset at the top
LOBES = 0.07                        # lumpiness of the outline

WALL = (0.93, 0.89, 0.78)      # pale cream corallite walls (the body colour)
RIM = (0.90, 0.84, 0.70)       # cup rims
PIT = (0.24, 0.15, 0.09)       # dark inside the corallite
POLYP = (0.42, 0.36, 0.18)     # small olive-brown polyp disc in the centre
EPITHECA = (0.70, 0.60, 0.45)  # bare underside
WRINKLE = (0.52, 0.42, 0.30)   # growth wrinkles on the epitheca

WARP = Vector((6.1, 2.9, 3.3))


def catmull(points, n):
    """Resamples a polyline with a Catmull-Rom spline to n points, evenly in arc length."""
    pts = [Vector((p[0], p[1])) for p in points]
    dense = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for k in range(20):
            t = k / 20
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense.append(pts[-1])
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + (b - a).length)
    out, j = [], 0
    for i in range(n):
        s = acc[-1] * i / (n - 1)
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        t = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        out.append(dense[j].lerp(dense[j + 1], t))
    return out


def surface(p, a, top_z):
    """Point on the (lobed, leaning) colony body for profile point p at angle a."""
    h = p.y / top_z
    d = Vector((math.cos(a), math.sin(a), 0.0))
    lump = 1.0 + LOBES * noise.noise(d * 1.4 + Vector((0, 0, h * 1.5)) + WARP)
    return d * p.x * lump + Vector((0, 0, p.y)) + LEAN * h * h


def lathe(profile, segments):
    """Closed surface of revolution; poles at the first and last profile points (r = 0)."""
    top_z = profile[-1].y
    bm = bmesh.new()
    bottom = bm.verts.new((0, 0, profile[0].y))
    top = bm.verts.new(Vector((0, 0, top_z)) + LEAN)
    rings = [[bm.verts.new(surface(p, k / segments * math.tau, top_z)) for k in range(segments)]
             for p in profile[1:-1]]
    for k in range(segments):
        j = (k + 1) % segments
        bm.faces.new([bottom, rings[0][j], rings[0][k]])
        bm.faces.new([top, rings[-1][k], rings[-1][j]])
    for a, b in zip(rings, rings[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def on_body(tree, co, fallback_n, lift):
    """Snaps co onto the body surface (nearest point) and lifts it along the surface normal."""
    hit, n, _i, _d = tree.find_nearest(co)
    if hit is None:
        return co + fallback_n * lift
    return hit + n * lift


def corallites(mb, tree, rng):
    """Hex-packed rows of hexagonal pits over the body's upward/outward faces."""
    fine = catmull(PROFILE, 400)
    top_z = fine[-1].y
    acc = [0.0]
    for a, b in zip(fine, fine[1:]):
        acc.append(acc[-1] + (b - a).length)
    row_step = CELL * 0.866
    # start the rows at the margin and work up to the crown, so the crown gets a full cell
    row, s, j = 0, 0.0, 0
    count = 0
    while s < acc[-1] - row_step * 0.45:
        while acc[j + 1] < s:
            j += 1
        p, q = fine[j], fine[j + 1]
        tan2 = (q - p).normalized()             # profile tangent in (r, z)
        nrm2 = Vector((tan2.y, -tan2.x))        # outward normal in (r, z)
        if nrm2.y >= MIN_NZ and p.x > CELL * 0.4:
            n = max(1, round(math.tau * p.x / CELL))
            off = 0.5 * (row % 2) + rng.uniform(-0.1, 0.1)
            for k in range(n):
                a = (k + off) / n * math.tau
                d = Vector((math.cos(a), math.sin(a), 0.0))
                c = surface(p, a, top_z)
                nn = (d * nrm2.x + Vector((0, 0, nrm2.y))).normalized()
                tu = Vector((-d.y, d.x, 0.0))   # around the colony
                tv = nn.cross(tu).normalized()  # along the profile
                r = CELL * CELL_R * min(1.0, (math.tau * p.x / n) / CELL) * rng.uniform(0.95, 1.03)
                count += pit(mb, tree, c, nn, tu, tv, r, rng)
        row += 1
        s += row_step
    # crown cell
    c = surface(fine[-1], 0.0, top_z)
    count += pit(mb, tree, c, Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)), CELL * CELL_R * 0.9, rng)
    return count


def pit(mb, tree, c, nn, tu, tv, r, rng):
    """One hexagonal corallite opening: a pale wall band at the rim (shared with the neighbours),
    a steep drop to a dark pit, an olive-brown polyp disc in the middle."""
    bm = bmesh.new()
    angles = [i / 6 * math.tau + math.pi / 6 + rng.uniform(-0.05, 0.05) for i in range(6)]

    def hexring(scale, lift):
        return [bm.verts.new(on_body(tree, c + (tu * math.cos(t) + tv * math.sin(t)) * r * scale, nn, lift))
                for t in angles]

    rim = hexring(1.0, PROUD)
    wall = hexring(WALL_IN, PROUD * 0.9)
    deep = hexring(0.62, CENTRE_PROUD + (PROUD - CENTRE_PROUD) * 0.2)
    cpos = on_body(tree, c, nn, CENTRE_PROUD)
    ring = sum((v.co for v in deep), Vector()) / 6
    cpos += nn * max(0.0, (ring - cpos).dot(nn) - 0.001)
    centre = bm.verts.new(cpos)
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new([centre, deep[i], deep[j]])
        bm.faces.new([deep[i], wall[i], wall[j], deep[j]])
        bm.faces.new([wall[i], rim[i], rim[j], wall[j]])
    for f in bm.faces:
        f.normal_update()
        if f.normal.dot(nn) < 0:
            f.normal_flip()
    tint = rng.uniform(0.92, 1.06)

    def col(co, _n, c=c, r=r, tint=tint):
        t = (co - c).length / r
        k = POLYP if t < 0.3 else (PIT if t < WALL_IN - 0.05 else RIM)
        return tuple(min(1.0, x * tint) for x in k)

    mb.add(bm, col)
    return 1


def build():
    rng = random.Random(SEED)
    profile = catmull(PROFILE, SAMPLES)
    body = lathe(profile, SEGMENTS)
    body.normal_update()
    tree = BVHTree.FromBMesh(body)

    def body_col(co, n):
        under = nh.smoothstep(MIN_NZ + 0.15, MIN_NZ - 0.15, n.z)
        wrinkle = 0.5 + 0.5 * math.sin(math.hypot(co.x, co.y) * 70 + noise.noise(co * 4 + WARP) * 2)
        c = nh.lerp(WALL, nh.lerp(EPITHECA, WRINKLE, wrinkle * 0.7), under)
        k = 0.95 + 0.1 * noise.noise(co * 3 + WARP)
        return tuple(min(1.0, x * k) for x in c)

    mb = nh.MeshBuilder()
    mb.add(body, body_col)
    n = corallites(mb, tree, rng)
    print(f"Favosites: {n} corallites")
    nc.rubble(mb, rng, 0.62, 0.85, count=4, size=(0.05, 0.09))
    obj = mb.to_object("Favosites", roughness=0.85)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Favosites", ground=(0.75, 0.70, 0.55), views=((35, 25), (10, 65), (-90, 8)))
