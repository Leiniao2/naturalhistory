"""
Procedural low-poly sunbittern (Eurypyga helias) in its wing-spread display.

A slim, heron-like wader on orange legs: long thin neck, long straight bill,
black head with white stripes above and below the eye, finely barred grey-brown
body. Both wings are fanned wide and raised, tilted to face forward and up so the
big "sunburst" eyespots (buff-yellow centre ringed with black and chestnut-orange
bands) read from the front and from a high map camera; the tail is fanned too.

Usage:
  blender --background --python tools/blender/sunbittern.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sunbittern.fbx
Faces -Y, pivot on the ground (feet at z = 0).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

BROWN = (0.42, 0.36, 0.27)       # barred grey-brown plumage
BROWN_DARK = (0.18, 0.14, 0.10)
GREY = (0.58, 0.56, 0.50)
BUFF = (0.92, 0.80, 0.48)        # eyespot centre
CHESTNUT = (0.80, 0.38, 0.10)
ORANGE = (0.95, 0.55, 0.15)
BLACK = (0.04, 0.04, 0.04)
WHITE = (0.95, 0.94, 0.90)
LEGS = (0.95, 0.55, 0.15)
BILL_TOP = (0.12, 0.11, 0.10)
BILL_LOW = (0.92, 0.55, 0.18)
EYE = (0.75, 0.10, 0.05)

BODY_C = Vector((0.0, 0.0, 0.42))
HEAD_C = Vector((0.0, -0.36, 0.56))


def barred(base, coord, freq=70.0, depth=0.45):
    """Fine dark barring across `coord`."""
    b = 0.5 + 0.5 * math.sin(coord * freq)
    return nh.lerp(base, BROWN_DARK, nh.smoothstep(0.55, 0.95, b) * depth)


def fan(origin, u_axis, v_axis, radius, a0, a1, color, n_r=9, n_t=18, thickness=0.012, scallop=0.05):
    """Two-sided fan (half disc) in the plane spanned by u_axis/v_axis, centred on origin.
    color(r_frac, t_frac) -> rgb. The outer edge is scalloped like feather tips."""
    bm = bmesh.new()
    origin, u, v = Vector(origin), Vector(u_axis).normalized(), Vector(v_axis).normalized()
    normal = u.cross(v).normalized()
    cols = {}
    layers = []
    for side in (1, -1):
        grid = []
        for i in range(n_r + 1):
            rf = i / n_r
            row = []
            for j in range(n_t + 1):
                tf = j / n_t
                a = math.radians(a0 + (a1 - a0) * tf)
                # feather scallops on the outer rim
                lobes = max(3, n_t // 3)
                r = radius * rf * (1.0 - scallop * (0.5 - 0.5 * math.cos(tf * lobes * math.tau)) * rf ** 6)
                p = origin + (u * math.cos(a) + v * math.sin(a)) * r + normal * (thickness * 0.5 * side * (1 - rf * 0.6))
                if i == 0 and j > 0:
                    row.append(row[0])
                    continue
                vert = bm.verts.new(p)
                cols[vert] = color(rf, tf)
                row.append(vert)
            grid.append(row)
        layers.append(grid)
        for i in range(n_r):
            for j in range(n_t):
                a, b, c, d = grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]
                quad = [a, d, c, b] if side > 0 else [a, b, c, d]
                quad = list(dict.fromkeys(quad))
                if len(quad) >= 3:
                    bm.faces.new(quad)
    # stitch the rim between the two sides
    top, bot = layers[0][n_r], layers[1][n_r]
    for j in range(n_t):
        bm.faces.new([top[j], top[j + 1], bot[j + 1], bot[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lookup = {tuple(round(c, 5) for c in vv.co): col for vv, col in cols.items()}
    return bm, (lambda co, n: lookup.get(tuple(round(c, 5) for c in co), BROWN))


def wing_color(rf, tf):
    """Sunburst: eyespot centred mid-wing, banded chestnut/black, barred grey-brown elsewhere."""
    # eyespot centre in (r, t) space
    dr, dt = (rf - 0.58) / 0.42, (tf - 0.5) / 0.55
    d = math.sqrt(dr * dr + dt * dt)
    base = barred(nh.lerp(GREY, BROWN, 0.6), rf * 6 + tf * 2, freq=9.0, depth=0.55)
    if d < 0.27:
        return nh.lerp(BUFF, ORANGE, nh.smoothstep(0.1, 0.27, d) * 0.4)
    if d < 0.42:
        return BLACK
    if d < 0.66:
        return nh.lerp(ORANGE, CHESTNUT, nh.smoothstep(0.42, 0.66, d))
    if d < 0.82:
        return BLACK
    # dark, finely barred flight feathers toward the rim
    return nh.lerp(base, BROWN_DARK, nh.smoothstep(0.75, 1.0, rf) * 0.6)


def tail_color(rf, tf):
    base = nh.lerp(GREY, BROWN, 0.4)
    if 0.55 < rf < 0.68:
        return BLACK
    if 0.68 <= rf < 0.82:
        return CHESTNUT
    if rf >= 0.92:
        return BLACK
    return barred(base, tf * 12, freq=6.0, depth=0.5)


def body_color(co, n):
    base = nh.lerp(BROWN, GREY, nh.smoothstep(0.0, -0.8, n.z) * 0.6)  # paler underneath
    return barred(base, co.y * 1.3 + co.z, freq=95.0, depth=0.5)


def head_color(co, n):
    rel = co - HEAD_C
    col = BLACK
    if abs(rel.x) > 0.018:
        # white stripe above the eye (supercilium) and below it (malar)
        if abs(rel.z - 0.017) < 0.0055 or abs(rel.z + 0.013) < 0.0055:
            col = WHITE
    if n.z < -0.6 and rel.y < 0.02:
        col = WHITE  # pale throat
    return col


def build():
    mb = nh.MeshBuilder()

    # Slim body, tilted slightly tail-up as in display
    body = nh.ellipsoid((0, 0, 0), (0.085, 0.19, 0.09), subdivisions=3)
    nh.transform(body, Matrix.Rotation(math.radians(-12), 4, "X"))
    nh.transform(body, Matrix.Translation(BODY_C))
    mb.add(body, body_color)

    # Long thin neck curving forward and down to a level head
    neck_pts = [BODY_C + Vector(p) for p in ((0, -0.14, 0.03), (0, -0.21, 0.09), (0, -0.27, 0.13), (0, -0.32, 0.14))]
    neck_pts.append(HEAD_C + Vector((0, 0.02, -0.005)))
    mb.add(nh.tube(neck_pts, [0.055, 0.035, 0.028, 0.027, 0.028], sides=8),
           lambda co, n: barred(nh.lerp(BROWN, GREY, 0.3), co.z, freq=120.0, depth=0.4))

    mb.add(nh.ellipsoid(HEAD_C, (0.04, 0.056, 0.04), subdivisions=4), head_color)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(HEAD_C + Vector((sx * 0.036, -0.014, 0.003)), (0.008, 0.009, 0.009), subdivisions=1), EYE)

    # Long straight dagger bill: dark upper, orange lower mandible
    bill_pts = [HEAD_C + Vector(p) for p in ((0, -0.035, -0.004), (0, -0.09, -0.008), (0, -0.15, -0.013), (0, -0.19, -0.016))]
    mb.add(nh.tube(bill_pts, [0.013, 0.010, 0.006, 0.0], sides=6, scale_xy=(0.7, 1.0)),
           lambda co, n: BILL_LOW if n.z < -0.2 else BILL_TOP)

    # Fanned wings, tilted to face forward and up
    for sx in (-1, 1):
        shoulder = BODY_C + Vector((sx * 0.06, -0.02, 0.06))
        u = Vector((sx * 1.0, 0.0, 0.0))
        v = Vector((0.0, 0.35, 0.94))
        mb.add(*fan(shoulder, u, v, 0.42, -22, 100, wing_color, n_r=14, n_t=26), smooth=True)

    # Fanned tail behind, raised
    tail_o = BODY_C + Vector((0, 0.15, 0.02))
    mb.add(*fan(tail_o, Vector((1, 0, 0)), Vector((0, 0.75, 0.66)), 0.2, 25, 155, tail_color, n_r=6, n_t=12))

    # Orange legs with a backward-bending ankle and three forward toes
    for sx in (-1, 1):
        hip = BODY_C + Vector((sx * 0.035, 0.03, -0.06))
        knee = Vector((sx * 0.045, 0.06, 0.2))
        foot = Vector((sx * 0.05, 0.0, 0.012))
        mb.add(nh.tube([hip, knee, foot], [0.016, 0.011, 0.01], sides=5), LEGS)
        for ang in (-28, 0, 28):
            a = math.radians(ang)
            tip = foot + Vector((math.sin(a) * 0.06, -math.cos(a) * 0.06, -0.008))
            mb.add(nh.tube([foot, tip], [0.008, 0.0], sides=4), LEGS)
        mb.add(nh.tube([foot, foot + Vector((0, 0.04, -0.008))], [0.007, 0.0], sides=4), LEGS)

    obj = mb.to_object("Sunbittern", roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Sunbittern", ground=(0.30, 0.42, 0.24), views=((30, 20), (-90, 8), (15, 65)))
