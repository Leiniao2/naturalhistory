"""
Spread wings for the flight models of birds that walk, wade, swim or perch in their colony.

The map shows such a bird with its own resting model on the ground or water and swaps to a flight
model (species.json "flightModel") when it takes off in the sky view. The flight model has its
wings spread out along X, so the map's wing-beat shader (MapFeatureFlap.cginc: everything beyond
_FlapRoot along |x| swings up and down) beats them like the soarers'.

Conventions as for the soarers (wandering_albatross.py): faces -Y, pivot at the body centre.
"""

import math

import bmesh
from mathutils import Vector

import nh_model as nh

# chord positions (0 = leading edge, 1 = trailing edge) for the top and bottom surface
CHORD = (0.0, 0.12, 0.35, 0.6, 0.78, 0.9, 1.0)


def interp(keys, t):
    """Piecewise-smooth interpolation through (t, value) keyframes."""
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            s = nh.smoothstep(t0, t1, t) if t1 > t0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


def airfoil(c):
    """0..1 thickness profile along the chord: blunt nose, thin trailing edge."""
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def make_wing(side, half_span, color, root_x=0.04, y0=0.0, z0=0.0,
              leading=((0.0, -0.10), (0.45, -0.14), (0.8, -0.06), (1.0, 0.08)),
              chord=((0.0, 0.30), (0.45, 0.26), (0.8, 0.20), (1.0, 0.04)),
              dihedral=((0.0, 0.0), (0.45, 0.05), (1.0, 0.03)),
              thickness=((0.0, 0.06), (0.45, 0.03), (1.0, 0.006)),
              stations=14, chord_points=CHORD):
    """One spread wing lofted from airfoil sections; side = +1 (right, +X) or -1.

    leading / chord / dihedral / thickness: (span fraction, value) keyframes, values in model
    units. color(t, c, top) -> rgb, with t the span fraction (0 root .. 1 tip), c the chord
    fraction (0 leading .. 1 trailing edge) and top whether it is the upper surface.
    stations / chord_points: sections along the span / points along each section's chord (more
    of both for wings with detailed patterns, such as eyespots).
    Returns (bmesh, colour function) for MeshBuilder.add.
    """
    bm = bmesh.new()
    colors = {}
    rings = []
    for i in range(stations + 1):
        t = (i / stations) ** 0.9  # a little denser toward the root
        x = root_x + t * (half_span - root_x)
        le = y0 + interp(leading, t)
        ch = interp(chord, t)
        z = z0 + interp(dihedral, t)
        th = interp(thickness, t)
        if i == stations:
            v = bm.verts.new(Vector((side * x, le + ch * 0.5, z)))
            colors[v] = color(t, 0.5, True)
            rings.append([v])
            continue
        top = [(c, z + th * airfoil(c)) for c in chord_points]
        bottom = [(c, z - th * 0.35 * airfoil(c)) for c in reversed(chord_points[1:-1])]
        ring = []
        for k, (c, zz) in enumerate(top + bottom):
            v = bm.verts.new(Vector((side * x, le + ch * c, zz)))
            colors[v] = color(t, c, k < len(top))
            ring.append(v)
        rings.append(ring)

    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            if len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    lookup = {tuple(round(c, 5) for c in v.co): col for v, col in colors.items()}
    first = next(iter(colors.values()))
    return bm, (lambda co, nrm: lookup.get(tuple(round(c, 5) for c in co), first))
