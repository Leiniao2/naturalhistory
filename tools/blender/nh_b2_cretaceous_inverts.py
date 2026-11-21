"""
Shared bits for the batch-2 Cretaceous invertebrates (hippurites_radiosus.py,
micraster_coranguinum.py, uintacrinus_socialis.py, callichimaera_perplexa.py):
radially-ribbed solids of revolution, a fine spine fuzz and a sea-floor patch.
Frame as everywhere: Z up, faces -Y.
"""

import math

import bmesh
from mathutils import Vector, noise

import nh_model as nh


def revolve(profile, segments=32, radial=None, color=None):
    """Solid of revolution about Z from profile [(r, z), ...] (bottom -> top, r = 0 at the
    poles closes the ends). radial(theta, t) -> radius multiplier (ribs, grooves, heart
    shapes); color(theta, t, z) -> rgb is baked per vertex. Returns a bmesh with "Col"."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    rings = []
    vcol = {}
    n = len(profile)
    for i, (r, z) in enumerate(profile):
        t = i / (n - 1)
        if r <= 1e-6:
            v = bm.verts.new((0, 0, z))
            vcol[v] = color(0.0, t, z) if color else (0.5, 0.5, 0.5)
            rings.append([v])
            continue
        ring = []
        for k in range(segments):
            th = k / segments * math.tau
            m = radial(th, t) if radial else 1.0
            v = bm.verts.new((math.cos(th) * r * m, math.sin(th) * r * m, z))
            vcol[v] = color(th, t, z) if color else (0.5, 0.5, 0.5)
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(segments):
                bm.faces.new([a[0], b[(k + 1) % segments], b[k]])
        elif len(b) == 1:
            for k in range(segments):
                bm.faces.new([a[k], a[(k + 1) % segments], b[0]])
        else:
            for k in range(segments):
                j = (k + 1) % segments
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = vcol[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


def floor_patch(mb, radius, c0, c1, seed=2.0, height=0.02):
    """Low mottled disc of sediment, top at about z = height."""
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=radius, segments=28)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    sv = Vector((seed, seed * 0.7, 0))
    for v in bm.verts:
        r = v.co.length / radius
        v.co.z = height * (1 - r ** 4) + height * 0.5 * noise.noise(v.co * 5 + sv) * (1 - r)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    mb.add(bm, lambda co, n: nh.lerp(c0, c1, 0.5 + 0.5 * noise.noise(co * 6 + sv)))


def spine_fuzz(mb, points_normals, length, r, color, tilt=None):
    """Short spines (thin cones) at each (point, normal); tilt: optional vector added to the
    direction (spines lying back)."""
    from nh_cre_core import cone
    for p, n in points_normals:
        d = Vector(n)
        if tilt is not None:
            d = (d + Vector(tilt)).normalized()
        mb.add(cone(Vector(p), Vector(p) + d * length, r, sides=3), color, smooth=False)
