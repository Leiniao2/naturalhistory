"""
Procedural Moorowipora chamberensis (early Cambrian colonial coral, Moorowie Formation, Mt
Chambers Gorge area, Flinders Ranges, South Australia) for the map: a pagoda-like colony rising
from a narrow foot in stacked, overhanging tiers and ending in a low dome, planted on a little
patch of reef rubble.

The colony is cerioid: its corallites are packed tightly together, each a polygonal tube sharing
its walls with its neighbours (with tabulae inside and short septal spines in the real fossil).
The colony body is a smooth lathe surface built from a Catmull-Rom (r, z) profile with
overhanging ledges (fossil colonies in the reef grew 'mushroom-shaped' or pagoda-like), slightly
lumpy and leaning so it isn't perfectly round, painted pale buff: that colour shows through as
the shared corallite walls. The corallites themselves are little hexagonal cups laid on the
surface in staggered (hex-packed) rows on every upward- and outward-facing surface: each is a
hexagonal fan with one inner ring (18 triangles) snapped onto the body (rim a little proud, centre lower, so it is a shallow
cup that follows the curvature), tan at the rim and ochre-brown at the centre where the polyp sat. The real corallites are only millimetres
wide, so the cells are stylised (much larger) to read at map size. Downward-facing ledge
undersides and the foot are left bare and a little darker. Colours are a living-coral guess.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/moorowipora_chamberensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Moorowipora.fbx
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

SEED = 7
SEGMENTS = 40         # around the colony body
SAMPLES = 32          # along the profile
CELL = 0.12           # corallite spacing (centre to centre)
CELL_R = 0.52         # hexagon radius as a fraction of CELL (thin gaps between show the walls)
PROUD = 0.011         # how far the cup rims sit above the body surface
CENTRE_PROUD = 0.006  # ...and the cup centres (lower than the rims: a shallow cup)
MIN_NZ = -0.35        # no corallites on surfaces facing further down than this
# (r, z) profile from the foot to the crown; overhanging ledges make the pagoda tiers
PROFILE = [
    (0.00, 0.00), (0.17, 0.00), (0.15, 0.08), (0.17, 0.18), (0.27, 0.28), (0.44, 0.36),
    (0.53, 0.41), (0.52, 0.46), (0.42, 0.48), (0.33, 0.51), (0.33, 0.57), (0.40, 0.64),
    (0.45, 0.69), (0.43, 0.73), (0.33, 0.75), (0.26, 0.78), (0.27, 0.85), (0.30, 0.90),
    (0.25, 0.97), (0.13, 1.02), (0.00, 1.04),
]
LEAN = Vector((0.06, -0.03, 0.0))   # crown offset at the top

WALL = (0.92, 0.86, 0.70)      # pale buff corallite walls (the body colour)
CUP = (0.78, 0.60, 0.38)       # cup rims
POLYP = (0.50, 0.28, 0.15)     # ochre-brown polyp centres
SHADE = (0.70, 0.60, 0.46)     # bare ledge undersides and foot

WARP = Vector((2.3, 7.9, 4.4))


def catmull(points, n):
    """Resamples a polyline with a Catmull-Rom spline to n points, evenly in arc length.
    Returns (points, cumulative arc length per point)."""
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
    """Point on the (lumpy, leaning) colony body for profile point p at angle a."""
    h = p.y / top_z
    d = Vector((math.cos(a), math.sin(a), 0.0))
    lump = 1.0 + 0.07 * noise.noise(d * 1.6 + Vector((0, 0, h * 2.5)) + WARP)
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
    """Hex-packed rows of shallow hexagonal cups over the body's upward/outward faces."""
    fine = catmull(PROFILE, 400)
    top_z = fine[-1].y
    acc = [0.0]
    for a, b in zip(fine, fine[1:]):
        acc.append(acc[-1] + (b - a).length)
    row_step = CELL * 0.866
    row, s, j = 0, row_step * 1.2, 0
    count = 0
    while s < acc[-1] - row_step * 0.5:
        while acc[j + 1] < s:
            j += 1
        p, q = fine[j], fine[j + 1]
        tan2 = (q - p).normalized()             # profile tangent in (r, z)
        nrm2 = Vector((tan2.y, -tan2.x))        # outward normal in (r, z)
        if nrm2.y >= MIN_NZ and p.y > 0.12 and p.x > CELL * 0.6:
            n = max(3, round(math.tau * p.x / CELL))
            off = 0.5 * (row % 2) + rng.uniform(-0.1, 0.1)
            for k in range(n):
                a = (k + off) / n * math.tau
                d = Vector((math.cos(a), math.sin(a), 0.0))
                c = surface(p, a, top_z)
                nn = (d * nrm2.x + Vector((0, 0, nrm2.y))).normalized()
                tu = Vector((-d.y, d.x, 0.0))   # around the colony
                tv = nn.cross(tu).normalized()  # along the profile
                r = CELL * CELL_R * min(1.0, (math.tau * p.x / n) / CELL) * rng.uniform(0.92, 1.05)
                bm = bmesh.new()
                angles = [i / 6 * math.tau + math.pi / 6 for i in range(6)]
                rim = [bm.verts.new(on_body(tree, c + (tu * math.cos(t) + tv * math.sin(t)) * r, nn, PROUD))
                       for t in angles]
                mid = [bm.verts.new(on_body(tree, c + (tu * math.cos(t) + tv * math.sin(t)) * r * 0.55, nn,
                                            (PROUD + CENTRE_PROUD) * 0.5)) for t in angles]
                # the centre never sinks below the inner ring (on sharply convex ledges it would
                # otherwise dip under the body and let the pale wall colour show through)
                cpos = on_body(tree, c, nn, CENTRE_PROUD)
                ring = sum((v.co for v in mid), Vector()) / 6
                cpos += nn * max(0.0, (ring - cpos).dot(nn) - 0.001)
                centre = bm.verts.new(cpos)
                for i in range(6):
                    j = (i + 1) % 6
                    bm.faces.new([centre, mid[i], mid[j]])
                    bm.faces.new([mid[i], rim[i], rim[j], mid[j]])
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                # make the faces point outward (the fan is shallow, recalc can't tell)
                for f in bm.faces:
                    if f.normal.dot(nn) < 0:
                        f.normal_flip()
                tint = rng.uniform(0.9, 1.08)

                def col(co, _n, c=c, r=r, tint=tint):
                    t = nh.smoothstep(r * 0.15, r * 0.9, (co - c).length)
                    return tuple(min(1.0, x * tint) for x in nh.lerp(POLYP, CUP, t))

                mb.add(bm, col)
                count += 1
        row += 1
        s += row_step
    return count


def build():
    rng = random.Random(SEED)
    profile = catmull(PROFILE, SAMPLES)
    body = lathe(profile, SEGMENTS)
    body.normal_update()
    tree = BVHTree.FromBMesh(body)

    def body_col(co, n):
        c = nh.lerp(WALL, SHADE, nh.smoothstep(MIN_NZ + 0.1, MIN_NZ - 0.3, n.z))
        c = nh.lerp(c, SHADE, nh.smoothstep(0.16, 0.06, co.z))
        k = 0.95 + 0.1 * noise.noise(co * 3 + WARP)
        return tuple(min(1.0, x * k) for x in c)

    mb = nh.MeshBuilder()
    mb.add(body, body_col)
    n = corallites(mb, tree, rng)
    print(f"Moorowipora: {n} corallites")
    nc.rubble(mb, rng, 0.26, 0.5, count=8, size=(0.05, 0.09))
    obj = mb.to_object("Moorowipora", roughness=0.85)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Moorowipora", ground=(0.75, 0.70, 0.55), views=((35, 25), (10, 65), (-90, 10)))
