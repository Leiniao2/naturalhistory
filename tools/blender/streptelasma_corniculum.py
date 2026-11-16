"""
Procedural Streptelasma corniculum Hall, 1847 (Late Ordovician solitary rugose "horn coral",
type species of Streptelasma, from the Trenton Limestone of New York) for the map: three
horn-shaped corals of different ages lying on a patch of muddy sea floor, each resting on its
convex side with the pointed tip in the mud and curving up so its cup opens to the water.

S. corniculum is a solitary coral: one polyp in a curved, cone-shaped (ceratoid) skeleton about
1.5-2 cm across at the calice and several centimetres long, without attachment structures. The
outer wall (epitheca) is thin and marked by growth wrinkles; the deep, funnel-shaped calice is
lined with numerous radial septa, long major septa alternating with short minor septa (in
adults the major septa no longer meet in the middle). More septa are added as the coral grows.

Each horn is one parametric ring-stack along a curved (quadratic Bezier) axis, so its vertex
columns line up with the septa (no voxel fuse, which would smear them):
  * the outer wall runs from the point to the rim, widening quickly then more slowly, with
    uneven ring-by-ring swellings and darker grooves for the growth wrinkles (rugae) and faint
    lengthwise grooves between the septa;
  * a rounded lip, then the funnel-shaped calice descends to a small floor. Columns repeat in
    the pattern major septum / gap / minor septum / gap: major septa stand up as pale radial
    ridges all the way down, minor septa only near the wall, the gaps between are sunk and dark.
    The number of septa grows with the horn's size, as in real corals;
  * the middle-sized horn has its polyp extended: an orange-brown oral disc with a ring of
    tentacles (soft parts are never preserved: shape and colours are a speculative guess).
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/streptelasma_corniculum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Streptelasma.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 9
# horns: apex (x, y), heading (deg), length, rim radius, major septa, wall rings, polyp extended
HORNS = [
    ((-0.62, -0.22), 4, 1.10, 0.22, 13, 13, False),
    ((0.52, 0.02), 138, 0.80, 0.16, 10, 11, True),
    ((-0.58, 0.16), 58, 0.54, 0.11, 8, 9, False),
]
# calice funnel rings: (radius fraction, depth below the rim as a fraction of the rim radius)
FUNNEL = [(0.80, 0.10), (0.60, 0.34), (0.42, 0.56), (0.25, 0.74), (0.11, 0.84)]
FLOOR = 0.88          # depth of the calice floor (fraction of rim radius)
MAJOR_H = 0.13        # major septa stand this far above the funnel (fraction of rim radius)
MINOR_H = 0.08
GAP_SINK = 0.05
MINOR_REACH = 0.55    # minor septa only where the funnel radius fraction is above this
TENTACLES = 14

EPITHECA = (0.80, 0.66, 0.47)
RUGA = (0.56, 0.42, 0.28)       # growth-wrinkle grooves
APEX = (0.58, 0.48, 0.36)
SEPTUM = (0.96, 0.91, 0.80)
LIP = (0.90, 0.80, 0.62)
GAP = (0.36, 0.22, 0.13)
DEEP = (0.16, 0.10, 0.07)
DISC = (0.80, 0.46, 0.26)
MOUTH = (0.45, 0.20, 0.12)
TENTACLE = (0.92, 0.56, 0.32)
TENTACLE_TIP = (1.0, 0.86, 0.66)
MUD = (0.64, 0.58, 0.46)
UP = Vector((0, 0, 1))
WARP = Vector((1.7, 6.3, 4.1))


def bezier(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t


def frames(pts):
    """Parallel-transported (point, forward, side, up) frames along a polyline."""
    out, side = [], None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if side is None:
            side = fwd.cross(UP).normalized()
        else:
            side = (side - fwd * side.dot(fwd)).normalized()
        out.append((p, fwd, side, fwd.cross(side).normalized()))
    return out


def horn(apex, heading, length, rim_r, septa, rings, rng):
    """One horn coral as a closed bmesh with its own "Col" layer; returns (bm, rim frame)."""
    h = Vector((math.cos(math.radians(heading)), math.sin(math.radians(heading)), 0))
    p0 = Vector((apex[0], apex[1], 0.02))
    p1 = p0 + h * length * 0.55
    p2 = p0 + h * length * 0.80 + UP * length * 0.50
    ts = [(i / (rings - 1)) ** 0.85 for i in range(rings)]
    fr = frames([bezier(p0, p1, p2, t) for t in ts])
    n = septa * 4
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}
    rows = []

    def ring(c, side, up, radius_of_k, color_of_k):
        vs = []
        for k in range(n):
            a = k / n * math.tau
            v = bm.verts.new(c(k) + (side * math.cos(a) + up * math.sin(a)) * radius_of_k(k))
            vcol[v] = color_of_k(k, v.co)
            vs.append(v)
        rows.append(vs)

    # outer wall: apex point, then rings widening quickly then slowly, with growth wrinkles
    tip = bm.verts.new(fr[0][0] - fr[0][1] * rim_r * 0.05)
    vcol[tip] = APEX
    for i in range(1, rings):
        p, fwd, side, up = fr[i]
        t = ts[i]
        r = rim_r * (0.06 + 0.94 * t ** 0.62)
        ruga = rng.uniform(-1, 1) if i < rings - 1 else 0.6
        r *= 1 + 0.035 * ruga

        def wall_col(k, co, ruga=ruga, t=t):
            c = nh.lerp(EPITHECA, RUGA, nh.smoothstep(0.2, -0.8, ruga) * 0.8)
            c = nh.lerp(c, APEX, nh.smoothstep(0.35, 0.0, t))
            if k % 2 == 1:
                c = tuple(x * 0.96 for x in c)          # faint grooves between the septa
            return tuple(x * (0.95 + 0.1 * noise.noise(co * 6 + WARP)) for x in c)

        ring(lambda k, p=p: p, side, up,
             lambda k, r=r: r * (0.985 if k % 2 == 1 else 1.0), wall_col)

    p, fwd, side, up = fr[-1]

    def septum(k, frac):
        if k % 4 == 0:
            return "major"
        if k % 4 == 2 and frac >= MINOR_REACH:
            return "minor"
        return "gap"

    # rounded lip
    lip_rise = rim_r * 0.05
    ring(lambda k: p + fwd * (lip_rise + (rim_r * 0.03 if k % 2 == 0 else 0.0)), side, up,
         lambda k: rim_r * 0.93, lambda k, co: SEPTUM if k % 2 == 0 else LIP)
    # funnel-shaped calice lined with septa
    for frac, depth in FUNNEL:
        def lift(k, frac=frac):
            kind = septum(k, frac)
            if kind == "major":
                return MAJOR_H * rim_r
            if kind == "minor":
                return MINOR_H * rim_r
            return -GAP_SINK * rim_r

        def c_col(k, co, frac=frac, depth=depth):
            kind = septum(k, frac)
            dark = nh.smoothstep(0.0, FLOOR, depth)
            if kind == "gap":
                return nh.lerp(GAP, DEEP, dark)
            return nh.lerp(SEPTUM, nh.lerp(SEPTUM, GAP, 0.5), dark * 0.8)

        ring(lambda k, depth=depth, lift=lift: p - fwd * depth * rim_r + fwd * lift(k), side, up,
             lambda k, frac=frac: rim_r * frac, c_col)
    floor = bm.verts.new(p - fwd * FLOOR * rim_r)
    vcol[floor] = DEEP

    for k in range(n):
        bm.faces.new([tip, rows[0][(k + 1) % n], rows[0][k]])
        bm.faces.new([floor, rows[-1][k], rows[-1][(k + 1) % n]])
    for a, b in zip(rows, rows[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)
    return bm, fr[-1]


def polyp(mb, frame, rim_r, rng):
    """Extended polyp: a domed oral disc filling the calice and a ring of tentacles."""
    p, fwd, side, up = frame
    bm = bmesh.new()
    segs = 20
    centre = p + fwd * rim_r * 0.30
    top = bm.verts.new(centre)
    rim = [bm.verts.new(p + fwd * rim_r * 0.07 + (side * math.cos(a) + up * math.sin(a)) * rim_r * 0.9)
           for a in (k / segs * math.tau for k in range(segs))]
    mid = [bm.verts.new(p + fwd * rim_r * 0.22 + (side * math.cos(a) + up * math.sin(a)) * rim_r * 0.5)
           for a in (k / segs * math.tau for k in range(segs))]
    under = bm.verts.new(p - fwd * rim_r * 0.3)
    for k in range(segs):
        j = (k + 1) % segs
        bm.faces.new([top, mid[k], mid[j]])
        bm.faces.new([mid[k], rim[k], rim[j], mid[j]])
        bm.faces.new([under, rim[j], rim[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mb.add(bm, lambda co, n: nh.lerp(MOUTH, DISC, nh.smoothstep(0.05, 0.4, (co - centre).length / rim_r)))
    for i in range(TENTACLES):
        a = i / TENTACLES * math.tau + rng.uniform(-0.08, 0.08)
        radial = side * math.cos(a) + up * math.sin(a)
        base = p + fwd * rim_r * 0.12 + radial * rim_r * 0.78
        L = rim_r * rng.uniform(0.55, 0.75)
        pts = [base, base + fwd * L * 0.55 + radial * L * 0.25, base + fwd * L * 0.85 + radial * L * 0.7]
        t = nh.tube(pts, [rim_r * 0.12, rim_r * 0.09, rim_r * 0.045], sides=5)
        mb.add(t, lambda co, n, b=base, L=L: nh.lerp(TENTACLE, TENTACLE_TIP,
                                                     nh.smoothstep(0.3 * L, L, (co - b).length)))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    # muddy sea-floor patch the horns lie in
    mud = nh.uv_ellipsoid((0, 0, 0), (0.80, 0.72, 0.035), segments=24, rings=6,
                          deform=lambda n: 1.0 + 0.10 * noise.noise(n * 1.8 + WARP))
    mb.add(mud, lambda co, n: tuple(x * (0.88 + 0.2 * noise.noise(co * 7 + WARP)) for x in MUD))
    for apex, heading, length, rim_r, septa, rings, extended in HORNS:
        bm, frame = horn(apex, heading, length, rim_r, septa, rings, rng)
        mb.add(bm)
        if extended:
            polyp(mb, frame, rim_r, rng)
    nc.rubble(mb, rng, 0.70, 0.85, count=4, size=(0.035, 0.06))
    obj = mb.to_object("Streptelasma", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Streptelasma", ground=(0.75, 0.70, 0.55), views=((30, 25), (10, 70), (-100, 12)))
