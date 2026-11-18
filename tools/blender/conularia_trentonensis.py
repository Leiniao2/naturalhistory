"""
Procedural Conularia trentonensis Hall, 1847 (Late Ordovician conulariid of the Trenton and
Collingwood beds of Ontario, Quebec and New York) for the map (Fixed style).

Conulariids were cnidarians, relatives of jellyfish, that lived in a tall, slender, four-sided
pyramid of thin, flexible, phosphatic skeleton, several centimetres long. Each face is crossed by
fine, closely spaced transverse ribs that bend in a shallow chevron at a groove down the middle
of the face, and the corners are sunk in deep grooves. The narrow end was fixed to a shell or the
sea floor; at the wide end four triangular flaps could fold shut over the opening, and when open
a crown of stinging tentacles reached out to catch prey. Three on a mud patch, one attached to a
brachiopod shell, two with tentacles out (soft parts speculative). Golden-brown skeleton.

Usage:
  blender --background --python tools/blender/conularia_trentonensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ConulariaTrentonensis.fbx (pivot on the sea floor, z = 0)
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

GOLD = (0.78, 0.58, 0.30)
GOLD_LIGHT = (0.94, 0.80, 0.52)
RIB_DARK = (0.48, 0.32, 0.16)
GROOVE = (0.30, 0.20, 0.10)
INSIDE = (0.22, 0.12, 0.08)
TENT = (0.92, 0.70, 0.62)
TENT_TIP = (1.0, 0.92, 0.86)
BRACH = (0.70, 0.66, 0.56)
BRACH_RIB = (0.52, 0.48, 0.40)

RINGS = 44
PER_SIDE = 6          # vertices along each face
TENTACLES = 16


def pyramid(height, r0, r1, rng):
    """Four-sided tapering skeleton along +Z, apex at z = 0. Returns bmesh with its own colours."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    n = PER_SIDE * 4
    rows, cols = [], []
    for i in range(RINGS + 1):
        t = i / RINGS
        z = height * t
        r = r0 + (r1 - r0) * t ** 0.9
        ring, rc = [], []
        for j in range(n):
            face, u = divmod(j, PER_SIDE)
            u = u / PER_SIDE * 2 - 1                         # -1 .. 1 across the face
            a = face * math.pi / 2
            nrm = Vector((math.cos(a), math.sin(a), 0))
            tan = Vector((-math.sin(a), math.cos(a), 0))
            # corners sunk in grooves, a faint groove down the face middle
            inset = 0.10 * math.exp(-((abs(u) - 1) / 0.12) ** 2) + 0.03 * math.exp(-(u / 0.08) ** 2)
            rib = 0.5 + 0.5 * math.cos((z / height * 22 - abs(u) * 1.4) * math.pi)   # chevron ribs
            k = 1.0 - inset + 0.015 * rib
            p = (nrm * r + tan * u * r) * k
            p.z = z
            ring.append(p)
            c = nh.lerp(GOLD, GOLD_LIGHT, 0.5 * rib)
            c = nh.lerp(c, RIB_DARK, 0.5 * nh.smoothstep(0.3, 0.0, rib))
            c = nh.lerp(c, GROOVE, nh.smoothstep(0.75, 0.95, abs(u)) + 0.6 * math.exp(-(u / 0.06) ** 2))
            rc.append(c)
        rows.append(ring)
        cols.append(rc)
    vs = [[bm.verts.new(p) for p in ring] for ring in rows]
    tip = bm.verts.new((0, 0, -r0 * 0.5))
    for i in range(RINGS):
        for j in range(n):
            jj = (j + 1) % n
            f = bm.faces.new([vs[i][j], vs[i][jj], vs[i + 1][jj], vs[i + 1][j]])
            for lp, (a, b) in zip(f.loops, [(i, j), (i, jj), (i + 1, jj), (i + 1, j)]):
                c = cols[a][b]
                lp[col] = (*c, 1.0)
    for j in range(n):
        f = bm.faces.new([tip, vs[0][(j + 1) % n], vs[0][j]])
        for lp in f.loops:
            lp[col] = (*GROOVE, 1.0)
    # dark inside: a cap a little below the rim
    top = [bm.verts.new(p * 0.92 + Vector((0, 0, -height * 0.01))) for p in rows[-1]]
    for p in top:
        p.co.z = height * 0.985
    for j in range(n):
        jj = (j + 1) % n
        f = bm.faces.new([vs[-1][j], vs[-1][jj], top[jj], top[j]])
        for lp in f.loops:
            lp[col] = (*GOLD_LIGHT, 1.0)
    mid = bm.verts.new((0, 0, height * 0.9))
    for j in range(n):
        f = bm.faces.new([top[j], top[(j + 1) % n], mid])
        for lp in f.loops:
            lp[col] = (*INSIDE, 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def lappets(mb, m, height, r1, closed):
    """Four triangular apertural flaps, leaning in (closed) or out (open)."""
    for face in range(4):
        a = face * math.pi / 2
        nrm = Vector((math.cos(a), math.sin(a), 0))
        tan = Vector((-math.sin(a), math.cos(a), 0))
        base = nrm * r1 * 0.95 + Vector((0, 0, height))
        lean = -0.9 if closed else 0.35
        tip = base + (Vector((0, 0, 1)) + nrm * lean).normalized() * r1 * 1.1
        pts = [base + tan * r1 * 0.85, tip, base - tan * r1 * 0.85]
        bm = nh.flat_panel([tuple(p) for p in pts], thickness=0.012)
        nh.transform(bm, m)
        mb.add(bm, GOLD, smooth=False)


def tentacles(mb, m, height, r1, rng):
    for i in range(TENTACLES):
        a = i / TENTACLES * math.tau + rng.uniform(-0.1, 0.1)
        out = Vector((math.cos(a), math.sin(a), 0))
        base = out * r1 * 0.55 + Vector((0, 0, height * 0.97))
        L = r1 * rng.uniform(2.2, 3.0)
        pts = [base, base + out * L * 0.35 + Vector((0, 0, L * 0.45)),
               base + out * L * 0.85 + Vector((0, 0, L * 0.55)), base + out * L * 1.15 + Vector((0, 0, L * 0.35))]
        bm = nh.tube(pts, [0.016, 0.012, 0.008, 0.0], sides=5)
        nh.transform(bm, m)
        b0 = m @ base
        mb.add(bm, lambda co, n, b0=b0, L=L: nh.lerp(TENT, TENT_TIP, nh.smoothstep(0.0, L * m.to_scale().x, (co - b0).length)))


def brachiopod(mb, at, r):
    bm = nh.ellipsoid(at, (r, r * 0.85, r * 0.35), subdivisions=3)
    mb.add(bm, lambda co, n: nh.lerp(BRACH, BRACH_RIB, 0.5 + 0.5 * math.cos(math.atan2(co.y - at[1], co.x - at[0]) * 18)))


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.9, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    brachiopod(mb, (-0.12, -0.05, 0.04), 0.16)
    # (x, y, z, tilt deg, yaw deg, height, open)
    for x, y, z, tilt, yaw, h, open_ in ((-0.12, -0.05, 0.08, 14, 30, 1.25, True),
                                         (0.42, 0.30, 0.0, 28, 200, 0.95, True),
                                         (-0.45, 0.38, 0.07, 80, 120, 0.8, False)):
        m = Matrix.Translation(Vector((x, y, z))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Rotation(math.radians(tilt), 4, "X")
        r1 = 0.11 * h
        bm = pyramid(h, 0.012, r1, rng)
        nh.transform(bm, m)
        mb.add(bm, None)
        lappets(mb, m, h, r1, closed=not open_)
        if open_:
            tentacles(mb, m, h, r1, rng)
    obj = mb.to_object("ConulariaTrentonensis", roughness=0.4)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ConulariaTrentonensis", **ec.VIEWS)
