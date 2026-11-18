"""
Procedural low-poly Physarum polycephalum, the many-headed (plasmodial) slime mould.

One giant multinucleate cell spread low and flat over a disc of dark leaf litter: a bright
egg-yolk-yellow network of veins, thick tubes at the back (+Y) that fork again and again into
thinner and thinner veins as they fan forward, all running into a continuous fan-shaped sheet of
protoplasm at the advancing front (-Y), whose scalloped leading edge is paler and finely streaked.
Two pale beige oat flakes lie in its path: one already half engulfed by the sheet, one just
being reached by the front. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/physarum_polycephalum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Physarum.fbx
About 1.6 units across (the litter disc), very low (~0.1 high). Advances toward -Y.
Pivot at the bottom of the disc (Fixed).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 3
GROUND_R = 0.8
G = 0.03                      # top of the litter disc

FAN_C = Vector((0.0, 0.66, 0.0))   # the fan radiates from here toward -Y
SHEET_R0, SHEET_R1 = 0.72, 0.99    # the front sheet spans this band of the fan
FAN_HALF = math.radians(46)
VEIN_MIN = 0.013               # thinnest vein radius
PLASMODIUM_TRIS = 2400

YOLK = (1.0, 0.80, 0.06)
YOLK_DEEP = (0.92, 0.62, 0.02)
YOLK_PALE = (1.0, 0.92, 0.45)
LITTER = (0.19, 0.13, 0.08)
LITTER_DARK = (0.11, 0.08, 0.05)
LITTER_LEAF = (0.30, 0.20, 0.11)
OAT = (0.90, 0.83, 0.64)
OAT_EDGE = (0.78, 0.68, 0.48)

# oat flakes: (theta about the fan, distance from FAN_C, yaw, radii)
FLAKES = [(-0.30, 0.74, 0.6, (0.12, 0.085, 0.022)),
          (0.36, 1.03, -0.4, (0.10, 0.075, 0.02))]


def fan_point(rho, theta):
    return FAN_C + Vector((math.sin(theta) * rho, -math.cos(theta) * rho, 0.0))


def lathe(profile, segments):
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((math.cos(k / segments * math.tau) * r,
                                        math.sin(k / segments * math.tau) * r, z)) for k in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def front_edge(theta):
    """Outer radius of the sheet: scalloped lobes along the advancing front."""
    return SHEET_R1 + 0.035 * math.sin(theta * 15.0 + 0.7) + 0.02 * math.sin(theta * 7.0)


def sheet():
    """The advancing front: a thin domed fan-shaped slab, its edges thinning to the litter."""
    bm = bmesh.new()
    na, nr = 26, 6
    top, bot = [], []
    for i in range(na + 1):
        th = -FAN_HALF + 2 * FAN_HALF * i / na
        rt, rb = [], []
        r1 = front_edge(th)
        for j in range(nr + 1):
            u = j / nr
            rho = SHEET_R0 - 0.04 + (r1 - SHEET_R0 + 0.04) * u
            side = nh.smoothstep(0.0, 0.12, min(i, na - i) / na)        # lower toward the fan sides
            h = 0.026 * math.sin(math.pi * min(1.0, 0.08 + u * 1.05)) ** 0.5 * (0.5 + 0.5 * side)
            p = fan_point(rho, th)
            rt.append(bm.verts.new((p.x, p.y, G + max(h, 0.008))))
            rb.append(bm.verts.new((p.x, p.y, G - 0.004)))
        top.append(rt)
        bot.append(rb)
    for i in range(na):
        for j in range(nr):
            bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
            bm.faces.new([bot[i][j], bot[i + 1][j], bot[i + 1][j + 1], bot[i][j + 1]])
    ring = [(i, 0) for i in range(na)] + [(na, j) for j in range(nr)] + \
           [(i, nr) for i in range(na, 0, -1)] + [(0, j) for j in range(nr, 0, -1)]
    for (i0, j0), (i1, j1) in zip(ring, ring[1:] + ring[:1]):
        bm.faces.new([top[i0][j0], bot[i0][j0], bot[i1][j1], top[i1][j1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def sheet_col(co, n):
    d = co - FAN_C
    rho = Vector((d.x, d.y)).length
    th = math.atan2(d.x, -d.y)
    u = (rho - SHEET_R0) / (front_edge(th) - SHEET_R0)
    c = nh.lerp(YOLK_DEEP, YOLK, nh.smoothstep(-0.1, 0.4, u))
    streak = 0.5 + 0.5 * math.cos(th * 70.0 + 3.0 * noise.noise(co * 6.0))
    c = nh.lerp(c, YOLK_DEEP, streak * 0.35 * (1.0 - nh.smoothstep(0.55, 0.9, u)))
    return nh.lerp(c, YOLK_PALE, nh.smoothstep(0.7, 1.0, u))


def veins(rng):
    """Branching vein tree in fan coordinates, plus cross links (anastomoses) between
    neighbouring fine veins: a list of ((rho, theta), (rho, theta), r0, r1)."""
    segs, tips = [], []
    lim = FAN_HALF * 0.92

    def grow(rho, th, r, spread, depth):
        step = 0.12 + rng.uniform(-0.025, 0.025)
        rho2 = min(SHEET_R0 + 0.05, rho + step)
        th2 = max(-lim, min(lim, th + rng.uniform(-0.07, 0.07)))
        r2 = max(VEIN_MIN, r * 0.9)
        segs.append(((rho, th), (rho2, th2), r, r2))
        if rho2 >= SHEET_R0 + 0.04:
            return
        if depth > 1:
            tips.append((rho2, th2, r2))
        if depth > 0 and rng.random() < 0.15:      # sometimes run on without forking
            grow(rho2, th2, r2, spread, depth)
            return
        s = spread * rng.uniform(0.8, 1.2)
        grow(rho2, th2 - s, max(VEIN_MIN, r * 0.7), spread * 0.6, depth + 1)
        grow(rho2, th2 + s, max(VEIN_MIN, r * 0.7), spread * 0.6, depth + 1)

    for th in (-0.40, 0.0, 0.40):
        grow(0.04, th, 0.044, 0.24, 0)
    # anastomoses: join some neighbouring fine veins sideways, making the net
    for i, (r0, t0, ra) in enumerate(tips):
        best = None
        for j, (r1, t1, rb) in enumerate(tips):
            if j == i or abs(r1 - r0) > 0.12:
                continue
            d = (fan_point(r0, t0) - fan_point(r1, t1)).length
            if 0.04 < d < 0.2 and (best is None or d < best[0]):
                best = (d, r1, t1, rb)
        if best and rng.random() < 0.55:
            segs.append(((r0, t0), (best[1], best[2]), VEIN_MIN, VEIN_MIN))
    return segs


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # the plasmodium: veins (round tubes half sunk into the litter) and the front sheet,
    # fused into one seamless surface
    for (r0, t0), (r1, t1), ra, rb in veins(rng):
        a, b = fan_point(r0, t0), fan_point(r1, t1)
        m = (a + b) * 0.5 + Vector((rng.uniform(-0.012, 0.012), rng.uniform(-0.012, 0.012), 0))
        pts = [a, m, b]
        rs = [ra, (ra + rb) * 0.5, rb]
        for p, r in zip(pts, rs):
            p.z = G + r * 0.15
        mb.add(nh.tube(pts, rs, sides=8, scale_xy=(1.0, 0.7)), YOLK)
        mb.add(nh.ellipsoid(tuple(a), (ra * 1.05, ra * 1.05, ra * 0.75), subdivisions=1), YOLK)
    mb.add(sheet(), YOLK)
    body = mb.fuse(voxel=0.008, smooth=5, max_tris=PLASMODIUM_TRIS)
    # drop what remeshing left under the litter surface
    bmesh.ops.delete(body, geom=[f for f in body.faces
                                 if all(v.co.z < G + 0.001 for v in f.verts)], context="FACES")

    def body_col(co, n):
        d = co - FAN_C
        rho = Vector((d.x, d.y)).length
        th = math.atan2(d.x, -d.y)
        if rho > SHEET_R0 - 0.06:
            return sheet_col(co, n)
        h = co.z - G
        c = nh.lerp(YOLK, YOLK_DEEP, nh.smoothstep(0.012, 0.035, h) * 0.8)   # thick veins deeper
        return nh.lerp(c, YOLK_PALE, nh.smoothstep(0.6, 1.0, n.z) * 0.25 * (1 - nh.smoothstep(0.01, 0.03, h)))

    out = nh.MeshBuilder()
    out.add(body, body_col)

    # the leaf-litter disc
    prof = [(0.0, G)] + [(GROUND_R * f, G) for f in (0.3, 0.6, 0.85)]
    prof += [(GROUND_R, G * 0.5), (GROUND_R * 0.98, 0.0), (0.0, 0.0)]

    def litter(co, n):
        k = noise.noise(Vector((co.x * 6.0, co.y * 6.0, 0.7)))
        c = nh.lerp(LITTER, LITTER_DARK, 0.5 + 0.5 * k)
        leaf = nh.smoothstep(0.25, 0.6, noise.noise(Vector((co.x * 2.5 + 3, co.y * 2.5, 1.9))))
        return nh.lerp(c, LITTER_LEAF, leaf * 0.7)

    out.add(lathe(prof, 32), litter)

    # oat flakes: pale flat ovals, yellow where the sheet has crept over them
    for th, rho, yaw, radii in FLAKES:
        c = fan_point(rho, th)
        c.z = G + radii[2] * 0.65
        bm = nh.ellipsoid((0, 0, 0), radii, subdivisions=2,
                          deform=lambda v: 1.0 + 0.05 * math.sin(v.x * 9.0 + v.y * 5.0))
        cs, sn = math.cos(yaw), math.sin(yaw)
        for v in bm.verts:
            x, y = v.co.x, v.co.y
            v.co = Vector((c.x + cs * x - sn * y, c.y + sn * x + cs * y, c.z + v.co.z))

        def oat_col(co, n):
            col = nh.lerp(OAT_EDGE, OAT, nh.smoothstep(0.0, 0.8, n.z))
            d = co - FAN_C
            rho = Vector((d.x, d.y)).length
            th = math.atan2(d.x, -d.y)
            inside = nh.smoothstep(0.03, -0.03, rho - front_edge(th)) * nh.smoothstep(SHEET_R0 - 0.05, SHEET_R0 + 0.02, rho)
            return nh.lerp(col, YOLK, inside * 0.85)

        out.add(bm, oat_col)
    obj = out.to_object("Physarum", roughness=0.4)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Physarum", views=((35, 30), (-140, 25), (0, 80)))
