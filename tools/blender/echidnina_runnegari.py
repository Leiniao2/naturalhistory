"""
Procedural low-poly Echidnina runnegari (Cambrian spherical radiolarian) for colony instancing.

A glassy, spherical lattice shell of silica: a geodesic meshwork of slender bars (92 pores,
hexagonal with twelve pentagons) round a pinkish-orange central capsule that shows faintly through the
pores, with 26 long, slender, tapering radial spines standing out from the bar junctions, each
about 0.6 of the shell radius long. Glassy white to pale blue, brightest on the bars and spine
tips. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/echidnina_runnegari.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Echidnina.fbx
~1.6 units across including the spines (shell radius 0.5). Front -Y (it is radially symmetric).
Pivot at the centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 6
SHELL_R = 0.50
BAR_R = 0.017
SPINES = 26
SPINE_LEN = (0.27, 0.34)   # 0.54-0.68 of the shell radius
SPINE_BASE = 0.022
CAPSULE_R = 0.30

BAR = (0.86, 0.93, 0.98)         # glassy silica
BAR_SHADE = (0.66, 0.78, 0.88)   # pale blue on the inner side
SPINE_TIP = (0.95, 0.98, 1.00)
CAPSULE = (0.96, 0.70, 0.58)     # pinkish-orange central capsule
CAPSULE_DEEP = (0.88, 0.56, 0.48)
FROTH = (0.96, 0.78, 0.66)


def geodesic(freq):
    """Frequency-`freq` geodesic sphere: each icosahedron face split into freq^2 triangles."""
    ico = bmesh.new()
    bmesh.ops.create_icosphere(ico, subdivisions=0, radius=1.0)
    bm = bmesh.new()
    verts = {}

    def vert(p):
        key = tuple(round(x, 5) for x in p.normalized())
        if key not in verts:
            verts[key] = bm.verts.new(p.normalized())
        return verts[key]

    for f in ico.faces:
        a, b, c = (v.co.copy() for v in f.verts)
        grid = {}
        for i in range(freq + 1):
            for j in range(freq + 1 - i):
                grid[i, j] = vert(a + (b - a) * (i / freq) + (c - a) * (j / freq))
        for i in range(freq):
            for j in range(freq - i):
                bm.faces.new([grid[i, j], grid[i + 1, j], grid[i, j + 1]])
                if i + j < freq - 1:
                    bm.faces.new([grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]])
    ico.free()
    return bm


def lattice(rng):
    """Nodes and bars of the dual of a frequency-3 geodesic sphere (a Goldberg polyhedron), so
    the 92 pores are hexagons with twelve pentagons."""
    geo = geodesic(3)
    geo.faces.ensure_lookup_table()
    geo.faces.index_update()
    nodes = []
    for f in geo.faces:
        c = f.calc_center_median().normalized()
        jit = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.02
        nodes.append((c + jit).normalized() * SHELL_R)
    bars = []
    for e in geo.edges:
        fa, fb = e.link_faces
        bars.append((fa.index, fb.index))
    geo.free()
    return nodes, bars


def spine_nodes(nodes, n, rng):
    """Farthest-point pick of n nodes, so the spines spread evenly."""
    picked = [rng.randrange(len(nodes))]
    while len(picked) < n:
        best = max(range(len(nodes)), key=lambda i: min((nodes[i] - nodes[j]).length for j in picked))
        picked.append(best)
    return picked


def bar_colour(co, n):
    out = max(0.0, n.dot(co.normalized()))
    return nh.lerp(BAR_SHADE, BAR, 0.4 + 0.6 * out)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # central capsule with a slightly frothy, mottled surface
    def capsule_col(co, n):
        k = 0.5 + 0.5 * math.sin(co.x * 31.0) * math.sin(co.y * 29.0) * math.sin(co.z * 33.0)
        return nh.lerp(nh.lerp(CAPSULE_DEEP, CAPSULE, k), FROTH, max(0.0, k - 0.7) * 1.5)
    mb.add(nh.ellipsoid((0, 0, 0), (CAPSULE_R,) * 3, subdivisions=2), capsule_col)

    # lattice shell: one slender bar per edge, run a touch past each node so the joints close
    nodes, bars = lattice(rng)
    for a, b in bars:
        pa, pb = nodes[a], nodes[b]
        d = (pb - pa).normalized()
        mb.add(nh.tube([pa - d * BAR_R * 0.6, pb + d * BAR_R * 0.6], [BAR_R, BAR_R], sides=3,
                       cap_start=False, cap_end=False), bar_colour)

    # long slender radial spines from the bar junctions
    for i in spine_nodes(nodes, SPINES, rng):
        d = nodes[i].normalized()
        base = nodes[i] * 0.97
        length = rng.uniform(*SPINE_LEN)
        pts = [base + d * (length * t) for t in (0.0, 0.08, 0.45, 1.0)]
        radii = [SPINE_BASE * 1.5, SPINE_BASE, SPINE_BASE * 0.55, 0.0]

        def spine_col(co, n, base=base, length=length):
            return nh.lerp(BAR, SPINE_TIP, nh.smoothstep(0.0, length, (co - base).length))
        mb.add(nh.tube(pts, radii, sides=4), spine_col)

    return mb.to_object("Echidnina", roughness=0.25)


if __name__ == "__main__":
    nh.run(build, "Echidnina", views=((35, 30), (-90, 10), (150, 70)))
