"""
Shared helpers for the Devonian fish batch (the "dev" scripts: eusthenopteron_foordi.py,
panderichthys_rhombolepis.py, hyneria_lindae.py, holoptychius_nobilissimus.py,
cheirolepis_trailli.py, dipterus_valenciennesi.py, cladoselache_fyleri.py,
coccosteus_cuspidatus.py, materpiscis_attenboroughi.py, bothriolepis_canadensis.py,
pteraspis_rostrata.py, drepanaspis_gemuendenensis.py, cephalaspis_lyelli.py,
gemuendina_stuertzi.py, acanthostega_gunnari.py).

Thin layer over nh_early_fish (Profile, scale lattice, fin webs, eyes) and nh_fish:

  * skin(): smooth lofted body part painted by color(co, u, v) (naked skin, armour).
  * web(): a fin web hanging off the top or bottom outline of the profile between y0 and
    y1, with the edge given as (dy, dz) offsets per u in 0..1 - dorsal/anal fins and
    every kind of tail (heterocercal, hypocercal, diphycercal, lunate).
  * lobed_fin(): a fleshy, scaled lobe with a fringing web (lobe-finned fishes).
  * ray_fin(): a plain paired fin hinged on the flank.
  * teeth(): a row of conical teeth along the gape.
  * centre(): moves the pivot to the bounding-box centre (Swim style).
  * domed_slab(): flat, domed armour shield from a half outline (constrained Delaunay
    over the outline), generalising the galeaspid shield of yongdongaspis_littoralis.py,
    for the flat jawless fishes and the ray-like placoderm.

Fish are laid out like nh_early_fish: snout at -Y (facing -Y), height Z, width X,
about 1.6 units long.
"""

import math

import bmesh
from mathutils import Vector, geometry, noise

import nh_model as nh
import nh_early_fish as ef

PREVIEW = ef.PREVIEW


def skin(mb, prof, y0, y1, color, ny=40, na=24, grow=0.0, cap0=True, cap1=True, ease=True):
    def col(co, n):
        u, v = prof.rel(co)
        return color(co, u, v)
    mb.add(ef.loft(prof, y0, y1, ny, na, grow=grow, cap0=cap0, cap1=cap1, ease=ease), col)


def web(mb, prof, y0, y1, edge, color, side=1, n=13, rows=3, th0=0.010, th1=0.003, inset=0.004):
    """Midline fin web. side=1 on the top outline, -1 on the bottom. edge(u) -> (dy, dz)
    offset of the free edge from the base point at u (dz is signed: up is +)."""
    axis, out = [], []
    for i in range(n):
        u = i / (n - 1)
        y = y0 + (y1 - y0) * u
        z = prof.top(y) - inset if side > 0 else prof.bot(y) + inset
        dy, dz = edge(u)
        axis.append((0.0, y, z))
        out.append((0.0, y + dy, z + dz))
    ef.caudal_web(mb, axis, out, color, rows=rows, th0=th0, th1=th1)


def bump(u, power=0.7, lead=0.0):
    """0 at both ends, 1 in the middle-ish: a generic fin height shape."""
    return math.sin(math.pi * min(1.0, max(0.0, lead + (1 - lead) * u))) ** power


def lobed_fin(mb, prof, s, y, angle, direction, length, r0, lobe_paint, web_color, web_w=0.06,
              lead_w=0.02, lobe_frac=0.6, cols=9, toward=None):
    """Lobe-finned paired (or median) fin. Root on the profile at (y, angle); direction is
    the fin axis for the +X side (mirrored for s=-1)."""
    root = prof.point(y, angle, -0.004)
    root.x *= s
    d = Vector(direction).normalized()
    d.x *= s
    tip = root + d * length
    ef.lobe(mb, root, root.lerp(tip, lobe_frac), r0, lobe_paint, sides=8)
    tw = Vector(toward) if toward is not None else Vector((-s * 0.3, 1.0, -0.3))
    if toward is not None:
        tw.x *= s
    ef.lobe_fringe(mb, root, tip, tw, lambda t: lead_w * math.sin(math.pi * t) + 0.004,
                   lambda t: web_w * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7 + 0.004, web_color, cols=cols)


def ray_fin(mb, prof, s, y0, y1, angle, length, out, down, back, color, cols=9, rows=3):
    ef.paired_fin(mb, prof, s, y0, y1, angle, length, out, down, back, color, cols=cols, rows=rows)


def teeth(mb, prof, y0, y1, zfn, n, h, color, r=None, inward=0.55, up=-1):
    """Conical teeth on both sides along the gape (upper teeth point down: up=-1)."""
    r = r if r is not None else h * 0.35
    for s in (1, -1):
        for k in range(n):
            y = y0 + (y1 - y0) * (k + 0.5) / n
            z = zfn(y)
            x = s * prof.W(y) * inward
            # find the flank x at that height
            best = min((abs(prof.point(y, a).z - z), a) for a in [-math.pi / 2 + q / 60 * math.pi for q in range(61)])[1]
            p = prof.point(y, best)
            x = s * abs(p.x) * 0.92
            mb.add(nh.tube([(x, y, z), (x, y, z + up * h)], [r, 0.0], sides=5), color)


def centre(obj):
    vs = obj.data.vertices
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


def finish(mb, name, roughness=0.45):
    return centre(mb.to_object(name, roughness=roughness))


# ---------------------------------------------------------------- flat shields

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


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (a + ab * t - p).length


def full_outline(half):
    """Mirror a half outline [(x>=0, y)] from the front midline to the back midline."""
    right = [Vector(p) for p in half]
    left = [Vector((-p[0], p[1])) for p in reversed(half[1:-1])]
    return right + left


def domed_slab(mb, half, top_z, bot_z, color, spacing=0.03, posterior=None):
    """Thin domed armour slab over a mirrored outline.

    top_z(p, d), bot_z(p, d): heights at 2D point p, d = distance to the thin rim.
    color(p, d, is_top) -> rgb. posterior(p) -> True on outline points of a thick back
    margin (where a trunk attaches): there the top and bottom do not meet but are joined
    by a short wall. Returns the outline polygon (list of 2D Vectors)."""
    poly = full_outline(half)
    posterior = posterior or (lambda p: False)
    thin = [(a, b) for a, b in zip(poly, poly[1:] + poly[:1]) if not (posterior(a) and posterior(b))]

    def edge_distance(p):
        return min((_seg_dist(p, a, b) for a, b in thin), default=1.0)

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
            if _inside(q, tri) and min(_seg_dist(q, a, b) for a, b in zip(poly, poly[1:] + poly[:1])) > spacing * 0.45:
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
        if i in rim_of and not posterior(p):
            d = 0.0
        else:
            d = edge_distance(p)
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
                c = color(p, d, is_top)
                l[col] = (c[0], c[1], c[2], 1.0)
    by_rim = {k: i for i, k in rim_of.items()}
    n = len(poly)
    for k in range(n):
        a, b = by_rim.get(k), by_rim.get((k + 1) % n)
        if a is None or b is None or not (posterior(poly[k]) and posterior(poly[(k + 1) % n])):
            continue
        loop = []
        for v in (top_v[a], bot_v[a], bot_v[b], top_v[b]):
            if v not in loop:
                loop.append(v)
        if len(loop) < 3:
            continue
        try:
            face = bm.faces.new(loop)
        except ValueError:
            continue
        for l in face.loops:
            p, d, _t = info[l.vert]
            c = tuple(x * 0.6 for x in color(p, d, True))
            l[col] = (c[0], c[1], c[2], 1.0)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mb.add(bm, None)
    return poly


def rise(d, rim):
    return nh.smoothstep(0.0, rim, d) ** 0.7


def tubercles(p, scale=70.0, seed=0.3):
    return nh.smoothstep(0.1, 0.45, noise.noise(Vector((p.x * scale, p.y * scale, seed))))


def _hash(a, b):
    x = math.sin(a * 12.9898 + b * 78.233) * 43758.5453
    return x - math.floor(x)


def tesserae(p, cell=0.05, width=0.15):
    """0..1 groove between small polygonal plates (a mosaic of tesserae) - Voronoi-ish."""
    x, y = p.x / cell, p.y / cell
    best = [9.0, 9.0]
    ix, iy = math.floor(x), math.floor(y)
    for a in range(ix - 1, ix + 2):
        for b in range(iy - 1, iy + 2):
            h = _hash(a, b)
            g = _hash(b + 17, a - 31)
            cx, cy = a + 0.1 + 0.8 * h, b + 0.1 + 0.8 * g
            d = math.hypot(x - cx, y - cy)
            if d < best[0]:
                best = [d, best[0]]
            elif d < best[1]:
                best[1] = d
    return 1.0 - nh.smoothstep(0.0, width, best[1] - best[0])
