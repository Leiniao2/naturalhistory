"""
Procedural low-poly Quetzalcoatlus northropi (giant azhdarchid pterosaur), gliding.

Enormous leathery wings (membrane from the elongated fourth finger back to the
ankle, with a small propatagium in front of the arm), a small body, a very long
stiff neck, and a huge pointed toothless beak with a red-orange crest. Legs
trail behind. Built to be read mostly from above while circling.

Usage:
  blender --background --python tools/blender/quetzalcoatlus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Quetzalcoatlus.fbx (faces -Y, pivot at the body centre)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BODY = (0.46, 0.34, 0.24)
BODY_DARK = (0.28, 0.24, 0.20)
BELLY = (0.70, 0.64, 0.55)
MEMBRANE = (0.50, 0.34, 0.22)
MEMBRANE_EDGE = (0.74, 0.58, 0.42)   # thinner, lighter trailing edge
LEADING = (0.22, 0.14, 0.09)         # bony leading edge
CREST = (0.85, 0.30, 0.12)
BEAK_BASE = (0.90, 0.52, 0.18)
BEAK_TIP = (0.80, 0.76, 0.66)
EYE = (0.03, 0.03, 0.03)

HALF_SPAN = 2.8

# (span x, y) along the leading edge (shoulder -> propatagium -> wrist -> wing finger tip)
LEADING_EDGE = [(0.09, -0.10), (0.45, -0.30), (0.95, -0.24), (1.45, -0.15), (1.95, -0.03), (2.40, 0.12), (2.80, 0.36)]
# trailing edge: body flank -> ankle -> concave sweep to the narrow tip
TRAILING_EDGE = [(0.09, 0.30), (0.20, 0.56), (0.55, 0.50), (1.00, 0.38), (1.50, 0.26), (2.00, 0.20), (2.40, 0.24), (2.80, 0.36)]


def dihedral(x):
    """Wing height at span position |x|: rises gently, tips droop a touch."""
    ax = abs(x)
    return 0.10 * ax - 0.018 * ax * ax


def interp(table, x):
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return table[-1][1]


def wing_membrane(sx, nu=18, nv=6, thickness=0.014, camber=0.035):
    """Closed, gently cambered membrane between the leading and trailing edges for one side."""
    bm = bmesh.new()
    x0, x1 = LEADING_EDGE[0][0], HALF_SPAN
    grid = {}
    for side, dz in (("top", thickness * 0.5), ("bot", -thickness * 0.5)):
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (x1 - x0) * (1 - (1 - u) ** 1.3)   # denser toward the tip
            yl, yt = interp(LEADING_EDGE, x), interp(TRAILING_EDGE, x)
            taper = 1.0 - u * 0.7
            for j in range(nv + 1):
                v = j / nv
                y = yl + (yt - yl) * v
                z = dihedral(x) + camber * math.sin(math.pi * v) * taper + dz * taper
                grid[side, i, j] = bm.verts.new((sx * x, y, z))
    for i in range(nu):
        for j in range(nv):
            q = [grid["top", i, j], grid["top", i + 1, j], grid["top", i + 1, j + 1], grid["top", i, j + 1]]
            bm.faces.new(q)
            bm.faces.new([grid["bot", i, j], grid["bot", i, j + 1], grid["bot", i + 1, j + 1], grid["bot", i + 1, j]])
    # stitch the rim (root, tip, leading and trailing edges)
    rim = ([(i, 0) for i in range(nu + 1)] + [(nu, j) for j in range(1, nv + 1)]
           + [(i, nv) for i in range(nu - 1, -1, -1)] + [(0, j) for j in range(nv - 1, 0, -1)])
    for a, b in zip(rim, rim[1:] + rim[:1]):
        try:
            bm.faces.new([grid["top", a[0], a[1]], grid["bot", a[0], a[1]], grid["bot", b[0], b[1]], grid["top", b[0], b[1]]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, normal):
        x = abs(co.x)
        yl, yt = interp(LEADING_EDGE, x), interp(TRAILING_EDGE, x)
        v = 0.0 if yt == yl else max(0.0, min(1.0, (co.y - yl) / (yt - yl)))
        c = nh.lerp(LEADING, MEMBRANE, nh.smoothstep(0.0, 0.25, v))
        c = nh.lerp(c, MEMBRANE_EDGE, nh.smoothstep(0.6, 1.0, v))
        # faint actinofibril streaks running toward the trailing edge
        streak = 0.5 + 0.5 * math.sin(x * 22.0 + v * 3.0)
        c = nh.lerp(c, BODY_DARK, streak * 0.28 * nh.smoothstep(0.15, 0.5, v) * (1 - nh.smoothstep(0.85, 1.0, v)))
        if normal.z < -0.5:   # underside a touch lighter
            c = nh.lerp(c, BELLY, 0.25)
        return c
    return bm, color


def panel(outline, thickness, colors):
    """Closed slab from a planar-ish 3D outline (concave ok); colors: rgb per outline point."""
    bm = bmesh.new()
    n = len(outline)
    top = [bm.verts.new(Vector(p) + Vector((0, 0, thickness * 0.5))) for p in outline]
    bot = [bm.verts.new(Vector(p) - Vector((0, 0, thickness * 0.5))) for p in outline]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lookup = [(Vector(p), c) for p, c in zip(outline, colors)]

    def color(co, normal):
        return min(lookup, key=lambda pc: (Vector((pc[0].x, pc[0].y)) - Vector((co.x, co.y))).length_squared)[1]
    return bm, color


def sagittal_panel(outline_yz, x_half, color):
    """Thin plate in the YZ plane (crests): outline of (y, z) points, thickness 2*x_half."""
    bm = bmesh.new()
    left = [bm.verts.new((-x_half, y, z)) for y, z in outline_yz]
    right = [bm.verts.new((x_half, y, z)) for y, z in outline_yz]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    n = len(outline_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, color


def build():
    mb = nh.MeshBuilder()

    # ---- small torso, slightly fuzzy (pycnofibres)
    def body_color(co, n):
        return nh.lerp(BELLY, nh.lerp(BODY, BODY_DARK, max(0.0, n.z) * 0.4), nh.smoothstep(-0.06, 0.03, co.z))
    mb.add(nh.uv_ellipsoid((0, 0.02, 0), (0.10, 0.26, 0.09), segments=14, rings=9,
                           deform=lambda n: 1 + noise.noise(n * 3.0) * 0.04), body_color)
    # stubby tail
    mb.add(nh.tube([(0, 0.26, 0.0), (0, 0.36, -0.01)], [0.03, 0.0], sides=6), BODY_DARK)

    # ---- long stiff neck rising a little, then the giant head
    neck = [(0, -0.20, 0.03), (0, -0.55, 0.10), (0, -0.90, 0.15), (0, -1.08, 0.17)]
    mb.add(nh.tube(neck, [0.06, 0.045, 0.04, 0.045], sides=8), body_color)
    skull = [(0, -1.06, 0.18), (0, -1.22, 0.17), (0, -1.55, 0.11), (0, -1.88, 0.03), (0, -2.18, -0.03)]

    def beak_color(co, n):
        t = nh.smoothstep(-1.3, -1.95, co.y)
        return nh.lerp(BEAK_BASE, BEAK_TIP, t)
    mb.add(nh.tube(skull, [0.08, 0.07, 0.05, 0.027, 0.0], sides=8, scale_xy=(0.75, 1.0)), beak_color)
    # back of the skull (rounded) so the head isn't just a cone
    mb.add(nh.uv_ellipsoid((0, -1.08, 0.19), (0.055, 0.08, 0.065), segments=10, rings=7),
           lambda co, n: nh.lerp(BODY, CREST, nh.smoothstep(0.17, 0.24, co.z)))
    # crest sweeping up and back from the skull
    crest = [(-1.02, 0.22), (-1.14, 0.22), (-1.30, 0.20), (-1.15, 0.30), (-1.00, 0.40), (-0.95, 0.33)]
    mb.add(*sagittal_panel(crest, 0.012, CREST))
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.045, -1.13, 0.20), (0.014, 0.018, 0.014), subdivisions=1), EYE)

    # ---- wings: membrane grid from the bony leading edge back to the ankle, bones on top
    for sx in (-1, 1):
        mb.add(*wing_membrane(sx), smooth=True)

        def P(x, y, lift=0.012):
            return Vector((sx * x, y, dihedral(x) + lift))
        shoulder, wrist = P(0.09, -0.10), P(0.95, -0.24)
        finger = [P(x, interp(LEADING_EDGE, x)) for x in (1.45, 1.95, 2.40)] + [P(HALF_SPAN, interp(LEADING_EDGE, HALF_SPAN), 0.0)]
        mb.add(nh.tube([shoulder, P(0.50, -0.22), wrist], [0.05, 0.038, 0.036], sides=6), LEADING)
        mb.add(nh.tube([wrist, *finger], [0.034, 0.026, 0.018, 0.010, 0.0], sides=5), LEADING)
        # small clawed fingers folded at the wrist
        for k, dx in enumerate((-0.03, 0.0, 0.03)):
            mb.add(nh.tube([wrist, wrist + Vector((sx * dx, -0.11 - 0.01 * k, 0.01))], [0.014, 0.0], sides=4), BODY_DARK)

        # ---- legs trailing back to the ankle, where the membrane attaches
        ankle = Vector((sx * 0.20, 0.56, dihedral(0.20) - 0.02))
        leg = [Vector((sx * 0.06, 0.20, -0.04)), Vector((sx * 0.13, 0.40, -0.03)), ankle]
        mb.add(nh.tube(leg, [0.032, 0.024, 0.018], sides=6), BODY_DARK)
        mb.add(nh.tube([ankle, ankle + Vector((sx * 0.01, 0.11, -0.02))], [0.02, 0.0], sides=4), BODY_DARK)

    return mb.to_object("Quetzalcoatlus")


if __name__ == "__main__":
    nh.run(build, "Quetzalcoatlus", views=((35, 25), (20, 70), (180, -35)))
