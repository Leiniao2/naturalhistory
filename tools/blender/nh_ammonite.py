"""
Shared pieces for the ammonite models (asteroceras.py, nipponites_mirabilis.py).

  * grid_mesh(): a closed swept surface from rings of points with a colour per
    vertex, so shells can carry rib/band colours that follow the coil.
  * soft_body(): the living animal in the aperture - a fleshy head with large
    eyes and a crown of ten tapering arms.
"""

import math

import bmesh
from mathutils import Vector

import nh_model as nh

FLESH = (0.56, 0.26, 0.27)
FLESH_LIGHT = (0.80, 0.52, 0.46)
EYE = (0.06, 0.05, 0.05)
IRIS = (0.85, 0.66, 0.25)


def grid_mesh(rings, colors, cap_start=True, cap_end=True):
    """rings: list of equal-length point lists (each a closed loop); colors: same shape, rgb."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    n = len(rings[0])
    verts = [[bm.verts.new(p) for p in ring] for ring in rings]

    def face(vs, cs):
        f = bm.faces.new(vs)
        for loop, c in zip(f.loops, cs):
            loop[col] = (c[0], c[1], c[2], 1.0)

    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            face([verts[i][k], verts[i][j], verts[i + 1][j], verts[i + 1][k]],
                 [colors[i][k], colors[i][j], colors[i + 1][j], colors[i + 1][k]])
    for use, i in ((cap_start, 0), (cap_end, len(rings) - 1)):
        if not use:
            continue
        c = sum((Vector(p) for p in rings[i]), Vector()) / n
        cv = bm.verts.new(c)
        cc = tuple(sum(colors[i][k][a] for k in range(n)) / n for a in range(3))
        for k in range(n):
            j = (k + 1) % n
            face([verts[i][k], verts[i][j], cv], [colors[i][k], colors[i][j], cc])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def frame(fwd, up_hint):
    """Orthonormal (fwd, side, up) with up as close to up_hint as possible."""
    f = Vector(fwd).normalized()
    s = f.cross(Vector(up_hint)).normalized()
    u = s.cross(f).normalized()
    return f, s, u


def soft_body(mb, origin, fwd, up, r, arm_len=2.0, droop=0.5):
    """Head emerging from an aperture of radius r at origin, facing fwd; up is the
    dorsal side (toward the shell). arm_len and droop are in units of r."""
    f, s, u = frame(fwd, up)
    o = Vector(origin)

    def at(a, b, c):  # along fwd, side, up
        return o + f * (a * r) + s * (b * r) + u * (c * r)

    def flesh(co, n):
        # darker dorsally, paler underneath
        k = nh.smoothstep(-0.6, 0.6, (co - o).dot(u) / r)
        return nh.lerp(FLESH_LIGHT, FLESH, k)

    mb.add(nh.tube([at(-0.5, 0, 0), at(0.15, 0, 0), at(0.6, 0, -0.05), at(0.95, 0, -0.1), at(1.15, 0, -0.12)],
                   [0.86 * r, 0.9 * r, 0.82 * r, 0.62 * r, 0.42 * r], sides=12, scale_xy=(1.0, 0.92)),
           flesh)
    # funnel (hyponome) under the head
    mb.add(nh.tube([at(0.2, 0, -0.55), at(0.75, 0, -0.78)], [0.2 * r, 0.14 * r], sides=6), FLESH_LIGHT)

    for side in (-1, 1):
        c = at(0.45, side * 0.74, 0.12)
        out = s * side

        def eye_col(co, n, out=out, f=f):
            d = n.dot((out * 0.8 + f * 0.6).normalized())
            return EYE if d > 0.72 else (IRIS if d > 0.45 else FLESH)

        mb.add(nh.ellipsoid(c, (0.27 * r,) * 3, subdivisions=2), eye_col)

    arms = 10
    for i in range(arms):
        a = (i + 0.5) / arms * math.tau
        ca, sa = math.cos(a), math.sin(a)
        base = at(0.95, 0.42 * ca, 0.34 * sa - 0.12)
        spread = (s * ca + u * sa * (0.45 if sa > 0 else 1.0)) * 0.32
        length = arm_len * r * (1.15 if i in (2, 7) else 1.0)
        pts, radii = [], []
        steps = 5
        for k in range(steps + 1):
            t = k / steps
            d = (f + spread * (1 + t) - u * droop * t * t).normalized()
            pts.append(base + d * (length * t))
            radii.append(0.19 * r * (1 - t) ** 0.8 + 0.035 * r)

        def arm_col(co, n, base=base, length=length):
            t = min(1.0, (co - base).length / length)
            return nh.lerp(FLESH, FLESH_LIGHT, t)

        mb.add(nh.tube(pts, radii, sides=5), arm_col)
