"""
Procedural Protopharetra polymorpha (early Cambrian irregular archaeocyath, first described from
Sardinia) for the map: a sprawling clump of crooked, budding cups grown together on a patch of
lime mud and microbial crust.

Protopharetra is an "irregular" archaeocyath: its double-walled cups are bent, lumpy and very
variable in shape ("polymorpha"), they bud new cups from their sides so a single individual
becomes a branching or bushy clump, and its intervallum is filled with a tangled network of thin,
curved, porous plates (taeniae) instead of neat straight septa. So, unlike nh_archaeocyath.py's
straight cups (whose lips show a regular wheel of septa), each cup here follows a wandering,
crooked axis with an irregular cross-section and scattered pores, and its lip is broken into an
irregular mesh of ridges and pits from a noise network rather than spokes. Three cups rise from
the crust (one low and leaning, almost encrusting); buds branch off their flanks.
Living colours are unknown; a warm cream-tan calcite tone is used, darker in the pits.
Fixed style: pivot at the base (z = 0). Seabed patch: nh_archaeo_reef.py.

Usage:
  blender --background --python tools/blender/protopharetra_polymorpha.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protopharetra.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_archaeo_reef as nr  # noqa: E402

SEED = 4
BODY = (0.60, 0.48, 0.32)          # warm cream-tan
BODY_DARK = (0.40, 0.30, 0.19)
PORE = (0.14, 0.10, 0.06)
RIM = (0.74, 0.63, 0.46)
PIT = (0.16, 0.11, 0.07)
CAVITY = (0.07, 0.05, 0.03)


def crooked_path(rng, start, direction, length, steps, wander):
    pts = [Vector(start)]
    d = Vector(direction).normalized()
    for _ in range(steps):
        d = (d + Vector((rng.gauss(0, wander), rng.gauss(0, wander), 0.12))).normalized()
        if d.z < 0.6:                        # crooked, but always growing upward
            d.z = 0.6
            d.normalize()
        pts.append(pts[-1] + d * (length / steps))
    return pts


def frames(pts):
    out, prev = [], None
    for i, p in enumerate(pts):
        if i == 0:
            fwd = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            fwd = (pts[-1] - pts[-2]).normalized()
        else:
            fwd = (pts[i + 1] - pts[i - 1]).normalized()
        if prev is None:
            ref = Vector((0, 0, 1)) if abs(fwd.z) < 0.9 else Vector((1, 0, 0))
            side = fwd.cross(ref).normalized()
        else:
            side = (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        out.append((fwd, side, side.cross(fwd).normalized()))
    return out


def cup(rng, pts, r0, r1, sides, wall=0.5, depth=0.5):
    """Closed ring-stack: crooked porous outer wall, tangled lip, inner wall down to the cavity."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    vcol = {}
    rows = []
    fr = frames(pts)
    m = len(pts)
    seed = Vector((rng.random() * 90, rng.random() * 90, rng.random() * 90))

    def rad(i, k):
        t = i / (m - 1)
        r = r0 + (r1 - r0) * (1 - (1 - t) ** 1.5)
        a = k / sides * math.tau
        lump = noise.noise(Vector((math.cos(a) * 1.3, math.sin(a) * 1.3, t * 2.5)) + seed)
        return r * (1 + 0.13 * lump)

    def at(i, k, r, lift=0.0):
        fwd, side, up = fr[i]
        a = k / sides * math.tau
        return pts[i] + (side * math.cos(a) + up * math.sin(a)) * r + fwd * lift

    def body(co):
        c = nh.lerp(BODY, BODY_DARK, nh.smoothstep(0.18, 0.0, co.z))
        return nh.lerp(c, BODY_DARK, 0.2 * nh.smoothstep(-0.1, 0.6, noise.noise(co * 7 + seed)))

    def row(cos, cols):
        vs = []
        for co, c in zip(cos, cols):
            v = bm.verts.new(co)
            vcol[v] = c
            vs.append(v)
        rows.append(vs)

    # outer wall: lumpy, with scattered pores
    for i in range(m):
        cos, cols = [], []
        for k in range(sides):
            pore = 0 < i < m - 1 and rng.random() < 0.3
            r = rad(i, k) * (0.86 if pore else 1.0)
            co = at(i, k, r)
            cos.append(co)
            cols.append(PORE if pore else body(co))
        row(cos, cols)

    # lip across the intervallum: an irregular network of ridges (taeniae) and pits
    top = m - 1
    sink = 0.5 * r1 * wall
    for f in (0.2, 0.42, 0.64, 0.86):
        cos, cols = [], []
        for k in range(sides):
            r = rad(top, k) * (1 - wall * f)
            p = at(top, k, r)
            net = abs(noise.noise(p * (9.0 / r1 * 0.12) + seed * 1.7))
            ridge = net < 0.22 or (rng.random() < 0.12)
            co = at(top, k, r, 0.0 if ridge else -sink * (0.7 + 0.3 * rng.random()))
            cos.append(co)
            cols.append(RIM if ridge else PIT)
        row(cos, cols)

    # inner wall back down the crooked axis into the cavity
    i_floor = max(1, int(round((m - 1) * (1 - depth))))
    steps = list(range(top, i_floor - 1, -1))
    for n_, i in enumerate(steps):
        d = n_ / max(1, len(steps) - 1)
        cos = [at(i, k, rad(i, k) * (1 - wall)) for k in range(sides)]
        row(cos, [nh.lerp(RIM, CAVITY, 0.5 + 0.5 * nh.smoothstep(0.0, 0.5, d))] * sides)

    for a, b in zip(rows, rows[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)
    return bm


# primary cups: (base, direction, length, r_base, r_rim, sides, buds)
# buds: (position along the parent 0..1, side angle (deg), length, r_base, r_rim)
PRIMARY = [
    ((0.0, 0.0, 0.0), (0.05, -0.1, 1.0), 0.95, 0.07, 0.15, 20,
     [(0.45, 200, 0.42, 0.05, 0.10), (0.55, 40, 0.34, 0.045, 0.085)]),
    ((-0.24, 0.1, 0.0), (-0.45, 0.15, 0.8), 0.62, 0.06, 0.12, 18,
     [(0.55, 120, 0.3, 0.04, 0.08)]),
    ((0.22, 0.08, 0.0), (0.8, 0.3, 0.45), 0.45, 0.08, 0.15, 18, []),   # low, sprawling
]

CLOTS = [(0.0, 0.0, 0.04, 0.16, 0.14, 0.06), (-0.28, 0.12, 0.04, 0.13, 0.12, 0.055),
         (0.26, 0.1, 0.03, 0.15, 0.12, 0.05), (-0.05, -0.22, 0.02, 0.12, 0.08, 0.035),
         (0.1, 0.28, 0.02, 0.1, 0.08, 0.035)]


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    nr.seabed(mb, rng, 0.6, CLOTS, pebbles=4)
    for base, d, length, r0, r1, sides, buds in PRIMARY:
        pts = crooked_path(rng, base, d, length, 10, 0.16)
        mb.add(cup(rng, pts, r0, r1, sides))
        fr = frames(pts)
        for pos, ang, blen, br0, br1 in buds:
            i = int(round(pos * (len(pts) - 1)))
            fwd, side, up = fr[i]
            a = math.radians(ang)
            out = side * math.cos(a) + up * math.sin(a)
            r_here = r0 + (r1 - r0) * pos
            start = pts[i] + out * (r_here * 0.45)
            bd = (out * 0.75 + Vector((0, 0, 1.0))).normalized()
            bpts = crooked_path(rng, start, bd, blen, 8, 0.18)
            mb.add(cup(rng, bpts, br0, br1, 16))
    return nr.finish(mb, "Protopharetra")


if __name__ == "__main__":
    nh.run(build, "Protopharetra", ground=(0.62, 0.58, 0.48), views=((20, 25), (110, 35), (10, 75)))
