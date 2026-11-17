"""
Procedural Yongdongaspis littoralis for the map: a small galeaspid (a jawless,
armoured "stem-gnathostome" fish of the order Eugaleaspidiformes, family
Yongdongaspididae) from the early Silurian (Llandovery, Telychian, about 436 million
years ago) Huixingshao Formation at Yongdong, Xiushan County, Chongqing, China
(Chen et al. 2022). About 5 cm long; it lived in shallow coastal seas.

The holotype is a head shield, so the shield follows the eugaleaspidiform plan
(the order is defined by these features): a broad, flat, bony head shield, rounded in
front, drawn out at the back corners into long backward-pointing cornual processes,
with shorter inner cornual processes between them and the trunk; a longitudinal,
oval median dorsal opening on the snout (the galeaspid nasohypophysial opening); the
eyes on top of the shield, set out toward the sides; sensory-canal grooves and a
tuberculate bone surface. The body behind follows Tujiaaspis, the first galeaspid
known with its body preserved (also Silurian, from Chongqing and Hunan): a tapering,
scale-covered trunk with a pair of long, continuous ventrolateral fin folds from
behind the shield to the tail, a small dorsal fin and a roughly symmetrical tail
whose body axis bends down (hypocercal). No jaws and no paired pectoral fins.

The shield is a thin domed slab triangulated from its outline (constrained
Delaunay), heights from the distance to the rim; the trunk uses the rhombic scale
lattice from nh_early_fish. Colours are unknown: a sandy grey-brown shield and a
darker trunk.

Usage:
  blender --background --python tools/blender/yongdongaspis_littoralis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Yongdongaspis.fbx (map style Swim: pivot at
the body centre, facing -Y, shield up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, geometry, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Yongdongaspis"

SHIELD = (0.58, 0.52, 0.40)
SHIELD_DARK = (0.38, 0.34, 0.26)
SHIELD_UNDER = (0.74, 0.70, 0.60)
TUBERCLE = (0.70, 0.65, 0.52)
CANAL = (0.18, 0.15, 0.11)
OPENING = (0.05, 0.04, 0.04)
BACK = (0.24, 0.22, 0.17)
FLANK = (0.44, 0.40, 0.31)
BELLY = (0.76, 0.72, 0.62)
BLOTCH = (0.18, 0.16, 0.12)
FIN = (0.40, 0.37, 0.30)
FIN_EDGE = (0.62, 0.58, 0.48)
RAY = (0.22, 0.20, 0.15)

# half outline of the head shield (x >= 0), front midline to back midline
HALF_OUTLINE = [
    (0.00, -0.82), (0.08, -0.815), (0.16, -0.79), (0.23, -0.745), (0.29, -0.68), (0.335, -0.60),
    (0.365, -0.51), (0.385, -0.41), (0.398, -0.31), (0.408, -0.21), (0.414, -0.12), (0.412, -0.05),
    (0.400, 0.02),                                   # cornual process tip
    (0.382, -0.02), (0.362, -0.08), (0.338, -0.15), (0.312, -0.205),
    (0.285, -0.215),                                 # notch
    (0.262, -0.18), (0.246, -0.12),                  # inner cornual process tip
    (0.226, -0.15), (0.200, -0.21), (0.165, -0.245), (0.120, -0.262),
    (0.060, -0.266), (0.00, -0.262),
]
DOME_H = 0.075
RIM = 0.10       # distance over which the shield rises from its rim
Z_SHIELD = 0.0
EYE_Y, EYE_X = -0.50, 0.150
MDO_Y = -0.665   # median dorsal opening

TRUNK = ef.Profile([
    (-0.50, 0.080, 0.045, 0.045, -0.006),
    (-0.30, 0.110, 0.050, 0.050, -0.006),
    (-0.15, 0.105, 0.062, 0.058, -0.008),
    (0.05, 0.082, 0.064, 0.056, -0.012),
    (0.25, 0.055, 0.048, 0.042, -0.026),
    (0.42, 0.034, 0.032, 0.028, -0.044),
    (0.60, 0.016, 0.018, 0.015, -0.080),
    (0.80, 0.003, 0.004, 0.003, -0.130),
], power=lambda y: 2.6 if y < 0.0 else 2.2)


def outline():
    right = [Vector(p) for p in HALF_OUTLINE]
    left = [Vector((-p[0], p[1])) for p in reversed(HALF_OUTLINE[1:-1])]
    return right + left


def rim_distance(p, poly):
    d = 1e9
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
        d = min(d, (a + ab * t - p).length)
    return d


def top_z(p, d):
    """Domed shield top: rises from the rim, highest along the midline over the orbits."""
    rise = nh.smoothstep(0.0, RIM, d) ** 0.7
    mid = 1.0 - nh.smoothstep(0.0, 0.32, abs(p.x))
    along = nh.smoothstep(-0.84, -0.55, p.y) * (1.0 - 0.6 * nh.smoothstep(-0.30, -0.10, p.y))
    return Z_SHIELD + DOME_H * rise * (0.55 + 0.45 * mid * along)


def bot_z(p, d):
    """Flatter underside, deeper toward the back where the gill chamber and trunk sit."""
    deep = 0.28 + 0.6 * nh.smoothstep(-0.55, -0.27, p.y) * (1.0 - nh.smoothstep(0.10, 0.22, abs(p.x)))
    return Z_SHIELD - deep * DOME_H * nh.smoothstep(0.0, RIM * 1.2, d) ** 0.8


def canal(p):
    """0..1 on the sensory-canal grooves of the shield (painted)."""
    x, y = abs(p.x), p.y
    g = 0.0
    # paired longitudinal (infraorbital/dorsal) canals running back from the snout
    xl = 0.20 + 0.06 * nh.smoothstep(-0.75, -0.25, y)
    if -0.75 < y < -0.20:
        g = max(g, 1.0 - nh.smoothstep(0.006, 0.016, abs(x - xl)))
    # transverse canals branching out to the rim
    for ty in (-0.60, -0.46, -0.34):
        if x > xl and x < 0.36:
            g = max(g, 1.0 - nh.smoothstep(0.006, 0.016, abs(y - (ty + 0.12 * (x - xl)))))
    # median transverse commissure behind the orbits
    if x < xl:
        g = max(g, 1.0 - nh.smoothstep(0.006, 0.016, abs(y + 0.30 - 0.15 * x)))
    return g


def shield_color(p, d, top):
    if not top:
        return nh.lerp(SHIELD_UNDER, SHIELD, 0.3 * nh.smoothstep(0.03, 0.0, d))
    c = nh.lerp(SHIELD, SHIELD_DARK, 0.5 * nh.smoothstep(0.02, 0.15, d))
    c = nh.lerp(c, TUBERCLE, 0.45 * nh.smoothstep(0.1, 0.45, noise.noise(Vector((p.x * 70, p.y * 70, 0.3)))))
    c = nh.lerp(c, SHIELD_DARK, 0.3 * nh.smoothstep(0.2, 0.6, noise.noise(Vector((p.x * 9, p.y * 9, 5.1)))))
    return nh.lerp(c, CANAL, 0.75 * canal(p))


def posterior(p):
    """Outline points on the shield's back margin over the trunk (a thick wall, not a thin rim)."""
    return p.y > -0.275 and abs(p.x) <= 0.17


def edge_distance(p, poly):
    """Distance to the thin part of the rim (all edges except the posterior margin)."""
    d = 1e9
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if posterior(a) and posterior(b):
            continue
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
        d = min(d, (a + ab * t - p).length)
    return d


def head_shield(mb, spacing=0.034):
    """Domed shield slab: constrained Delaunay triangulation of the outline plus an
    interior lattice, lifted into a top and a flatter bottom surface that meet at the
    thin rim; the back margin over the trunk is a short wall."""
    poly = outline()
    pts2 = [p.copy() for p in poly]
    xmin, xmax = min(p.x for p in poly), max(p.x for p in poly)
    ymin, ymax = min(p.y for p in poly), max(p.y for p in poly)
    tri = [(p.x, p.y) for p in poly]
    j = 0
    y = ymin + spacing * 0.5
    while y < ymax:
        x = xmin + spacing * (0.5 + 0.5 * (j % 2))
        while x < xmax:
            q = Vector((x, y))
            if _inside(q, tri) and rim_distance(q, poly) > spacing * 0.45:
                pts2.append(q)
            x += spacing
        y += spacing * 0.866
        j += 1
    verts, _e, faces, orig, _oe, _of = geometry.delaunay_2d_cdt(pts2, [], [list(range(len(poly)))], 1, 1e-7)
    rim_of = {}
    for i, o in enumerate(orig):
        for k in o:
            if k < len(poly):
                rim_of[i] = k
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    top_v, bot_v, info = {}, {}, {}
    for i, v2 in enumerate(verts):
        p = Vector((v2[0], v2[1]))
        d = 0.0 if i in rim_of else edge_distance(p, poly)
        if i in rim_of and posterior(p):
            d = edge_distance(p, poly)
        tv = bm.verts.new((p.x, p.y, top_z(p, d)))
        info[tv] = (p, d, True)
        top_v[i] = tv
        if d <= 1e-6:
            bot_v[i] = tv
        else:
            bv = bm.verts.new((p.x, p.y, bot_z(p, d)))
            info[bv] = (p, d, False)
            bot_v[i] = bv
    for f in faces:
        for vs, is_top in ((top_v, True), (bot_v, False)):
            loop = [vs[i] for i in f]
            if not is_top:
                loop.reverse()
            try:
                face = bm.faces.new(loop)
            except ValueError:
                continue
            for l in face.loops:
                p, d, _t = info[l.vert]
                c = shield_color(p, d, is_top)
                l[col] = (c[0], c[1], c[2], 1.0)
    # back wall between the top and bottom along the posterior margin
    by_rim = {k: i for i, k in rim_of.items()}
    n = len(poly)
    for k in range(n):
        a, b = by_rim.get(k), by_rim.get((k + 1) % n)
        if a is None or b is None or not (posterior(poly[k]) or posterior(poly[(k + 1) % n])):
            continue
        quad = [top_v[a], bot_v[a], bot_v[b], top_v[b]]
        loop = []
        for v in quad:
            if v not in loop:
                loop.append(v)
        if len(loop) < 3:
            continue
        try:
            face = bm.faces.new(loop)
        except ValueError:
            continue
        for l in face.loops:
            c = nh.lerp(SHIELD_DARK, CANAL, 0.4)
            l[col] = (c[0], c[1], c[2], 1.0)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mb.add(bm, None)
    return poly


def _inside(q, poly):
    x, y = q.x, q.y
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                inside = not inside
    return inside


def shield_details(mb, poly):
    """Eyes on top of the shield, the oval median dorsal opening, the pineal spot."""
    for s in (1, -1):
        p = Vector((s * EYE_X, EYE_Y))
        z = top_z(p, edge_distance(p, poly))
        # raised orbit rim
        mb.add(nh.uv_ellipsoid((s * EYE_X, EYE_Y, z - 0.004), (0.040, 0.044, 0.016), 10, 5),
               lambda co, n: nh.lerp(SHIELD_DARK, TUBERCLE, 0.4 * n.z))
        ef.eye(mb, (s * EYE_X, EYE_Y, z + 0.004), (s * 0.45, -0.15, 0.88), 0.026, iris=(0.55, 0.48, 0.28))
    p = Vector((0.0, MDO_Y))
    z = top_z(p, edge_distance(p, poly))
    mb.add(nh.uv_ellipsoid((0.0, MDO_Y, z - 0.002), (0.017, 0.066, 0.006), 10, 5), OPENING)
    mb.add(nh.uv_ellipsoid((0.0, MDO_Y, z - 0.003), (0.025, 0.075, 0.006), 10, 4), CANAL)
    p = Vector((0.0, -0.52))
    mb.add(nh.uv_ellipsoid((0.0, -0.52, top_z(p, edge_distance(p, poly)) - 0.001), (0.010, 0.012, 0.004), 6, 3), CANAL)


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)


def trunk(mb):
    ef.scale_shell(mb, TRUNK, -0.30, 0.80, 32, 14, scale_color, lift=0.003, shade=0.35, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    plain = ef.ray_color(FIN, RAY, FIN_EDGE, 1, rays=False)
    # small dorsal fin
    ef.median_fin(mb, TRUNK, 0.12, 0.26, lambda u: 0.055 * math.sin(math.pi * (0.2 + 0.8 * u)) ** 0.6 + 0.006,
                  plain, sweep=0.9, cols=6, rows=2)
    # hypocercal tail: the axis bends down; webs above (broad) and below it
    axis_b, edge_b, axis_t, edge_t = [], [], [], []
    n = ef.ray_cols(6)
    for i in range(n):
        u = i / (n - 1)
        y = 0.40 + 0.40 * u
        ht = 0.15 * math.sin(math.pi * min(1.0, u * 1.03) ** 0.8) ** 1.1 * (1 - 0.3 * u) + 0.004
        hb = 0.11 * math.sin(math.pi * min(1.0, u * 1.03) ** 0.8) ** 1.1 * (1 - 0.2 * u) + 0.004
        axis_t.append((0.0, y, TRUNK.top(y) - 0.004))
        edge_t.append((0.0, y + 0.5 * ht, TRUNK.top(y) + ht))
        axis_b.append((0.0, y, TRUNK.bot(y) + 0.004))
        edge_b.append((0.0, y + 0.5 * hb, TRUNK.bot(y) - hb))
    ef.caudal_web(mb, axis_t, edge_t, rays(6), rows=2)
    ef.caudal_web(mb, axis_b, edge_b, rays(6), rows=2)
    # paired, continuous ventrolateral fin folds from behind the shield to the tail
    for s in (1, -1):
        ef.paired_fin(mb, TRUNK, s, -0.22, 0.42,
                      -0.55, lambda u: 0.045 * math.sin(math.pi * (0.08 + 0.92 * u)) ** 0.5 + 0.006,
                      1.0, 0.25, 0.25, rays(8), cols=ef.ray_cols(8), rows=2)


def build():
    mb = nh.MeshBuilder()
    poly = head_shield(mb)
    shield_details(mb, poly)
    trunk(mb)
    obj = mb.to_object(NAME, roughness=0.5)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
