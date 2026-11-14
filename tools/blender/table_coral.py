"""
Procedural table coral (Acropora hyacinthus) for the map: a broad, lobed horizontal plate on a
short stalk, its top a dense carpet of tiny upturned branchlet tips with pale blue-violet
growing edges, plus a smaller second tier, planted on a little rubble patch.
Ground style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/table_coral.py -- [--render out.png]
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

SEED = 5

TAN = (0.58, 0.42, 0.22)         # tan-brown branchlet carpet
OCHRE = (0.78, 0.60, 0.30)
DEEP = (0.42, 0.30, 0.17)        # gaps between branchlets / underside
EDGE = (0.64, 0.62, 0.88)        # pale blue-violet growing rim
TIP = (0.86, 0.80, 0.66)         # pale branchlet tips


def plate(center, radius, spacing, seed, tilt=(0.0, 0.0)):
    """One table as a closed shell: a top surface of roughly even triangles (rings whose vertex
    count grows with radius, so there is no pinched centre), a coarser underside and a rim.
    Returns (bmesh, edge_r(a), top_z(x, y)) so branchlets can be planted on the top."""
    cx, cy, cz = center
    off = Vector((seed * 3.1, seed * 1.7, seed * 0.9))

    def edge_r(a):
        d = Vector((math.cos(a), math.sin(a), 0.0))
        lobes = 0.06 * math.sin(5 * a + seed) + 0.04 * math.sin(9 * a + seed * 2.0)
        return radius * (1.0 + 0.10 * noise.noise(d * 1.4 + off) + lobes + 0.035 * noise.noise(d * 6.0 + off))

    def surf(t, a, top):
        r = t * edge_r(a)
        x, y = math.cos(a) * r, math.sin(a) * r
        z = cz + 0.05 * t * t + tilt[0] * x + tilt[1] * y  # rim curls up slightly
        # gentle undulation of the table surface
        z += 0.012 * noise.noise(Vector((x, y, 0.0)) * 4.0 + off)
        if not top:
            z -= 0.075 * (1 - t) + 0.02
        return Vector((cx + x, cy + y, z))

    bm = bmesh.new()

    def rings_for(n_rings, top):
        centre = bm.verts.new(surf(0.0, 0.0, top))
        rings = []
        for i in range(1, n_rings + 1):
            t = i / n_rings
            n = max(6, round(math.tau * t * radius / spacing))
            ph = (i % 2) * 0.5 / n * math.tau
            rings.append([bm.verts.new(surf(t, j / n * math.tau + ph, top)) for j in range(n)])
        return centre, rings

    def angle(v):
        return math.atan2(v.co.y - cy, v.co.x - cx) % math.tau

    def bridge(r0, r1, flip):
        """Triangulates between two closed rings with different vertex counts by angle."""
        i = j = 0
        n0, n1 = len(r0), len(r1)
        while i < n0 or j < n1:
            a0 = (i + 1) / n0 if i < n0 else 9.0
            a1 = (j + 1) / n1 if j < n1 else 9.0
            if a0 <= a1:
                tri = [r0[i % n0], r1[j % n1], r0[(i + 1) % n0]]
                i += 1
            else:
                tri = [r0[i % n0], r1[j % n1], r1[(j + 1) % n1]]
                j += 1
            try:
                bm.faces.new(tri if not flip else list(reversed(tri)))
            except ValueError:
                pass

    def fan(c, ring, flip):
        n = len(ring)
        for j in range(n):
            q = [c, ring[j], ring[(j + 1) % n]]
            bm.faces.new(q if not flip else list(reversed(q)))

    n_top = max(3, round(radius / spacing))
    ct, top = rings_for(n_top, True)
    cb, bot = rings_for(max(3, n_top // 3), False)
    fan(ct, top[0], False)
    for r0, r1 in zip(top, top[1:]):
        bridge(r0, r1, False)
    fan(cb, bot[0], True)
    for r0, r1 in zip(bot, bot[1:]):
        bridge(r0, r1, True)
    bridge(top[-1], bot[-1], False)  # rim
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def top_z(x, y):
        a = math.atan2(y - cy, x - cx)
        t = math.hypot(x - cx, y - cy) / edge_r(a)
        return surf(min(t, 1.0), a, True).z, t

    return bm, edge_r, top_z


def branchlets(center, radius, edge_r, top_z, spacing, rng):
    """Tiny upturned corallite branchlets: a 4-sided spike per tip, jittered on a hex grid,
    shorter and leaning outward toward the rim."""
    cx, cy, _ = center
    bm = bmesh.new()
    tips = []
    row = 0
    y = -radius * 1.2
    while y < radius * 1.2:
        x = -radius * 1.2 + (row % 2) * spacing * 0.5
        while x < radius * 1.2:
            px = cx + x + rng.uniform(-0.3, 0.3) * spacing
            py = cy + y + rng.uniform(-0.3, 0.3) * spacing
            a = math.atan2(py - cy, px - cx)
            if math.hypot(px - cx, py - cy) < edge_r(a) * 0.96:
                z, t = top_z(px, py)
                h = rng.uniform(0.025, 0.045) * (1.0 - 0.4 * t)
                w = spacing * 0.28
                lean = Vector((math.cos(a), math.sin(a), 0.0)) * (0.35 * t * h)
                base = Vector((px, py, z - 0.004))
                tip = base + Vector((0, 0, h)) + lean
                ring = [bm.verts.new(base + Vector((math.cos(k * math.pi / 2 + a) * w,
                                                      math.sin(k * math.pi / 2 + a) * w, 0.0)))
                        for k in range(4)]
                apex = bm.verts.new(tip)
                for k in range(4):
                    bm.faces.new([ring[k], ring[(k + 1) % 4], apex])
                tips.append((tip, t))
            x += spacing
        y += spacing * 0.866
        row += 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    def add_plate(center, radius, seed, tilt=(0.0, 0.0)):
        bm, edge_r, top_z = plate(center, radius, 0.034, seed, tilt)
        cx, cy, _ = center

        def rim_t(co):
            a = math.atan2(co.y - cy, co.x - cx)
            return math.hypot(co.x - cx, co.y - cy) / edge_r(a)

        def color(co, n):
            t = rim_t(co)
            if n.z < -0.2:  # underside: dark with faint radial corallite streaks
                a = math.atan2(co.y - cy, co.x - cx)
                streak = 0.5 + 0.5 * math.sin(a * 70)
                return nh.lerp(DEEP, TAN, 0.25 * streak + 0.3 * t)
            mott = 0.5 + 0.5 * noise.noise(co * 3.0)
            c = nh.lerp(TAN, OCHRE, mott)
            gap = noise.cell(co * 26.0)  # dark specks between branchlets
            c = nh.lerp(c, DEEP, 0.45 * nh.smoothstep(0.55, 0.9, gap))
            return nh.lerp(c, EDGE, nh.smoothstep(0.9, 1.0, t))  # narrow pale growing rim

        mb.add(bm, color)
        tips = branchlets(center, radius, edge_r, top_z, 0.062, rng)

        def tip_color(co, n):
            t = rim_t(co)
            z0, _ = top_z(co.x, co.y)
            up = nh.smoothstep(0.0, 0.035, co.z - z0)  # 0 at the root, 1 at the tip
            c = nh.lerp(nh.lerp(TAN, OCHRE, 0.5), TIP, up * 0.8)
            return nh.lerp(c, EDGE, nh.smoothstep(0.75, 1.0, t) * up)

        mb.add(tips, tip_color)

    add_plate((0.0, 0.0, 0.36), 0.80, seed=1, tilt=(-0.03, 0.04))
    add_plate((0.82, -0.58, 0.19), 0.36, seed=4, tilt=(0.05, -0.04))

    # short, slightly flared stalks fused into the plates' undersides
    def stalk(base, top, r0, r1):
        pts = [base, base.lerp(top, 0.35), base.lerp(top, 0.75), top]
        rads = [r0 * 1.35, r0, r1 * 0.9, r1 * 1.4]
        bm = nh.tube(pts, rads, sides=12)
        for v in bm.verts:
            v.co += v.normal * 0.012 * noise.noise(v.co * 18.0)

        def col(co, n):
            return nh.lerp(DEEP, TAN, 0.35 + 0.25 * noise.noise(co * 20.0))

        mb.add(bm, col)

    stalk(Vector((0.0, 0.0, -0.01)), Vector((0.0, 0.0, 0.32)), 0.085, 0.09)
    stalk(Vector((0.82, -0.58, -0.01)), Vector((0.82, -0.58, 0.15)), 0.05, 0.05)

    nc.rubble(mb, rng, 0.12, 0.35, count=5, size=(0.04, 0.08))   # around the stalk
    nc.rubble(mb, rng, 0.75, 1.05, count=8, size=(0.04, 0.10))   # spilling out past the rim
    obj = mb.to_object("TableCoral", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "TableCoral", ground=(0.75, 0.70, 0.55), views=((35, 30), (10, 70), (-90, 8)))
