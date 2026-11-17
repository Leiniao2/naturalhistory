"""
Procedural Tshekardocoleus magnus (Early Permian protocoleopteran, Tshekarda, Urals) for map colonies.

One of the first beetle relatives: a flat, elongate insect whose forewings have
become elytra, but not yet the closed, smooth shield of a modern beetle. The
elytra are long, flat and sculptured with rows of window-like cells (drawn as
grids of dark pits between raised ribs); they reach a little beyond the tip of
the abdomen, and their inner edges meet only at the base, leaving a narrow gap
that widens toward the tips. A broad flat pronotum with flanged sides, a
forward-pointing head with big eyes and beaded antennae, six splayed running
legs. Dark chestnut brown, the ribs paler. Faces -Y, pivot on the ground (feet
at z = 0).

Usage:
  blender --background --python tools/blender/tshekardocoleus_magnus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tshekardocoleus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ELYTRON = (0.36, 0.20, 0.10)
RIB = (0.55, 0.36, 0.20)
PIT = (0.12, 0.06, 0.03)
PRONOTUM = (0.30, 0.17, 0.08)
FLANGE = (0.52, 0.34, 0.18)
BODY = (0.22, 0.12, 0.06)
LEG = (0.40, 0.24, 0.12)
LEG_DARK = (0.20, 0.11, 0.05)
EYE = (0.04, 0.03, 0.03)

BASE = 0.05                       # underside of the body above the ground
EL_Y0, EL_LEN, EL_W = -0.17, 0.76, 0.165
EL_Z = BASE + 0.05


def elytron(side):
    """One elytron: a flat slab, its inner edge on the midline at the base and drifting
    outward toward the tip (the elytra don't close), plus rows of cells: raised ribs
    along it with dark pits between."""
    parts = []
    n = 24

    def inner(t):              # x of the inner margin along the elytron (t 0 base .. 1 tip)
        return 0.004 + 0.035 * t * t

    def outer(t):
        return inner(t) + EL_W * max(0.0, 1.0 - t ** 5) ** 0.5 * (0.88 + 0.12 * math.sin(math.pi * min(1.0, t * 1.6))) + 0.002

    outline = []
    for k in range(n + 1):
        t = k / n
        outline.append((side * outer(t), EL_Y0 + EL_LEN * t, 0.0))
    for k in range(n, -1, -1):
        t = k / n
        outline.append((side * inner(t), EL_Y0 + EL_LEN * t, 0.0))
    slab = nh.flat_panel(outline, 0.008)
    for v in slab.verts:
        u = abs(v.co.x) / (EL_W + 0.04)
        v.co.z += EL_Z - 0.02 * u * u                # flat, bending down to the outer edge
    parts.append((slab, ELYTRON))

    # ribs and pits: 5 rows of cells
    rows = 5
    for r in range(rows + 1):
        f = r / rows
        pts = []
        for k in range(14):
            t = 0.03 + 0.92 * k / 13
            x = inner(t) + (outer(t) - inner(t)) * (0.08 + 0.84 * f)
            u = x / (EL_W + 0.04)
            pts.append(Vector((side * x, EL_Y0 + EL_LEN * t, EL_Z + 0.006 - 0.02 * u * u)))
        parts.append((nh.tube(pts, [0.006] * len(pts), sides=4, scale_xy=(1.0, 0.5)), RIB))
    for r in range(rows):
        f = (r + 0.5) / rows
        for k in range(12):
            t = 0.07 + 0.86 * k / 11
            x = inner(t) + (outer(t) - inner(t)) * (0.08 + 0.84 * f)
            u = x / (EL_W + 0.04)
            parts.append((nh.uv_ellipsoid((side * x, EL_Y0 + EL_LEN * t, EL_Z + 0.004 - 0.02 * u * u),
                                          (0.009, 0.020, 0.003), 6, 3), PIT))
    return parts


def leg(mb, s, hip, knee, foot):
    tarsus = foot + Vector((s * 0.035, (foot - knee).normalized().y * 0.05, 0.0))
    mb.add(nh.tube([hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.008)), knee], [0.015, 0.018, 0.012], sides=5,
                   scale_xy=(1.0, 0.6)), LEG)
    mb.add(nh.tube([knee, foot], [0.010, 0.007], sides=4), LEG)
    mb.add(nh.tube([foot, tarsus], [0.006, 0.003], sides=4), LEG_DARK)


def build():
    mb = nh.MeshBuilder()
    # abdomen under the elytra (slightly shorter than they are), thorax
    mb.add(nh.uv_ellipsoid((0, 0.18, BASE + 0.02), (0.13, 0.32, 0.022), 14, 8), BODY)
    mb.add(nh.uv_ellipsoid((0, -0.17, BASE + 0.025), (0.11, 0.10, 0.03), 12, 6), BODY)
    # pronotum: broad, flat, with paler flanged sides
    pc = Vector((0, -0.30, BASE + 0.045))
    outline = []
    for k in range(28):
        a = k / 28 * math.tau
        outline.append((pc.x + math.cos(a) * 0.15 * (1.0 - 0.12 * math.sin(a)), pc.y + math.sin(a) * 0.10, 0.0))
    pro = nh.flat_panel(outline, 0.02)
    for v in pro.verts:
        r = math.hypot(v.co.x / 0.15, (v.co.y - pc.y) / 0.10)
        v.co.z += pc.z + 0.02 * (1.0 - r * r)
    mb.add(pro, lambda co, n: nh.lerp(PRONOTUM, FLANGE, nh.smoothstep(0.7, 0.95, math.hypot(co.x / 0.15, (co.y - pc.y) / 0.10))))
    # head pointing forward, big eyes, short beaded antennae
    hc = Vector((0, -0.45, BASE + 0.035))
    mb.add(nh.uv_ellipsoid(hc, (0.075, 0.07, 0.032), 12, 8), PRONOTUM)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(hc + Vector((s * 0.062, 0.0, 0.008)), (0.022, 0.03, 0.02), 8, 5), EYE)
        mb.add(nh.tube([hc + Vector((s * 0.025, -0.06, -0.01)), hc + Vector((s * 0.04, -0.10, -0.02))],
                       [0.010, 0.003], sides=4), LEG_DARK)
        a0 = hc + Vector((s * 0.04, -0.05, 0.01))
        pts = [a0 + Vector((s * 0.06 * t + s * 0.05 * t * t, -0.24 * t, 0.03 * math.sin(t * math.pi))) for t in (k / 8 for k in range(9))]
        mb.add(nh.tube(pts, [0.009 - 0.004 * k / 8 for k in range(9)], sides=4), LEG_DARK)
        for p in pts[1:-1]:
            mb.add(nh.ellipsoid(p, (0.010,) * 3, 1), LEG_DARK)
    # six legs, splayed
    legs = [(-0.24, (0.18, -0.05), (0.24, -0.15)), (-0.14, (0.22, 0.02), (0.33, 0.06)),
            (-0.04, (0.22, 0.12), (0.33, 0.30))]
    for s in (-1, 1):
        for y, (kx, kdy), (fx, fdy) in legs:
            leg(mb, s, Vector((s * 0.06, y, BASE + 0.005)), Vector((s * kx, y + kdy, BASE + 0.03)), Vector((s * fx, y + fdy, 0.0)))
    # the elytra
    for s in (-1, 1):
        for bm, col in elytron(s):
            mb.add(bm, col, smooth=False)
    obj = mb.to_object("Tshekardocoleus", roughness=0.45)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.3f}, hip {BASE + 0.005:.3f} -> mapHip {(BASE + 0.005) / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "Tshekardocoleus", ground=(0.30, 0.26, 0.18), views=((35, 30), (0, 80), (-90, 10)))
