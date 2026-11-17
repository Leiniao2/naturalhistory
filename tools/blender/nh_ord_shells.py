"""
Shell and colony helpers for the Ordovician batch: a turbiniform sea snail
(cyclonema_bilix.py) and a dome-shaped trepostome bryozoan (prasopora_simulatrix.py).
Fixed style, pivot on the sea floor (z = 0), facing -Y. Uses nh_ord_echino.mud_patch.

  * snail_shell(): a coiled tube along a conical helix whose radius and whorl section
    grow geometrically (Raup-style), painted with spiral cords and growth lines; the
    aperture end is open, with a little foot and head with tentacles peeking out.
  * bryozoan_dome(): a gumdrop-shaped colony heightfield dotted with tiny zooecial pits
    and regularly spaced low bumps (monticules).
"""

import math

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh


def snail_shell(mb, turns=4.0, w=2.6, spire=0.9, section=0.55, sides=12, steps_per_turn=24,
                shell=(0.78, 0.66, 0.48), cord=(0.56, 0.42, 0.28), cords=6, band=None,
                foot=(0.66, 0.56, 0.46), matrix=None):
    """Shell coiled around +Z, apex up. w: whorl expansion per turn; spire: height per
    radius; section: tube radius / coil radius. Built with the aperture radius ~0.3."""
    n = int(turns * steps_per_turn)
    rings = []
    cols = []
    r_end = 0.3
    for i in range(n + 1):
        th = i / steps_per_turn * math.tau
        k = w ** ((i - n) / steps_per_turn)       # 1 at the aperture
        R = r_end * k
        c = Vector((R * math.cos(th), R * math.sin(th), -spire * R))
        rt = R * section
        out = Vector((math.cos(th), math.sin(th), 0))
        up = Vector((0, 0, 1))
        ring, rc = [], []
        for j in range(sides):
            a = j / sides * math.tau
            p = c + (out * math.cos(a) + up * math.sin(a)) * rt
            ring.append(p)
            s = 0.5 + 0.5 * math.cos(a * cords)
            col = nh.lerp(shell, cord, 0.6 * nh.smoothstep(0.7, 1.0, s))
            if band is not None and abs(math.sin(a) - 0.3) < 0.18:
                col = nh.lerp(col, band, 0.7)
            g = 0.5 + 0.5 * math.sin(th * 14)
            col = tuple(x * (0.93 + 0.07 * g) for x in col)
            rc.append(col)
        rings.append(ring)
        cols.append(rc)
    bm = bmesh.new()
    cl = bm.loops.layers.color.new("Col")
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(n):
        for j in range(sides):
            jj = (j + 1) % sides
            f = bm.faces.new([vr[i][j], vr[i][jj], vr[i + 1][jj], vr[i + 1][j]])
            for l, (ii, kk) in zip(f.loops, [(i, j), (i, jj), (i + 1, jj), (i + 1, j)]):
                c3 = cols[ii][kk]
                l[cl] = (c3[0], c3[1], c3[2], 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ap = sum(rings[-1], Vector()) / sides
    ap_r = r_end * section
    if matrix is not None:
        nh.transform(bm, matrix)
    mb.add(bm, None)
    # soft body: dark aperture fill, foot and head with two tentacles
    parts = []
    fz = ap.z - ap_r * 0.85
    parts.append((nh.ellipsoid((ap.x * 0.6, ap.y - 0.05, fz), (ap_r * 1.3, ap_r * 1.6, ap_r * 0.35),
                               subdivisions=2), foot))
    for sx in (-1, 1):
        b = Vector((ap.x * 0.6 + sx * ap_r * 0.4, ap.y - ap_r * 1.2, fz + ap_r * 0.3))
        parts.append((nh.tube([b, b + Vector((sx * 0.04, -0.12, 0.06))], [0.02, 0.0], sides=5), foot))
    for bm2, c in parts:
        if matrix is not None:
            nh.transform(bm2, matrix)
        mb.add(bm2, c)


def bryozoan_dome(mb, centre, radius, height, color, dark, monticule=(0.80, 0.66, 0.50), n_r=14, n_a=44):
    cx, cy = centre
    bm = bmesh.new()
    rings = []
    for i in range(n_r + 1):
        t = i / n_r
        ring = []
        for j in range(n_a):
            a = j / n_a * math.tau
            r = radius * math.sin(t * math.pi / 2) * (1.0 + 0.03 * noise.noise(Vector((math.cos(a), math.sin(a), cx)) * 2))
            # gumdrop: flat base, steep sides, rounded top
            z = height * (1.0 - t ** 3) ** 0.6 + 0.015
            ring.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z)))
        rings.append(ring)
    top = bm.verts.new((cx, cy, height + 0.016))
    for j in range(n_a):
        bm.faces.new([top, rings[0][j], rings[0][(j + 1) % n_a]])
    for i in range(n_r):
        for j in range(n_a):
            jj = (j + 1) % n_a
            bm.faces.new([rings[i][j], rings[i + 1][j], rings[i + 1][jj], rings[i][jj]])
    bot = bm.verts.new((cx, cy, 0.0))
    for j in range(n_a):
        bm.faces.new([rings[-1][(j + 1) % n_a], rings[-1][j], bot])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        p = (co - Vector((cx, cy, 0))) * 60.0
        pit = 0.5 + 0.5 * noise.noise(p)
        c = nh.lerp(color, dark, 0.5 * nh.smoothstep(0.55, 0.75, pit))
        return c
    mb.add(bm, col)
    # monticules: small low bumps spaced over the surface
    k = 0
    for i in range(2, n_r, 2):
        t = i / n_r
        r = radius * math.sin(t * math.pi / 2)
        z = height * (1.0 - t ** 3) ** 0.6 + 0.015
        m = max(1, int(r / 0.05))
        for j in range(m):
            a = (j + 0.5 * (i % 4 == 0)) / m * math.tau
            mb.add(nh.ellipsoid((cx + r * math.cos(a), cy + r * math.sin(a), z), (0.018, 0.018, 0.012),
                                subdivisions=1), monticule)
            k += 1
