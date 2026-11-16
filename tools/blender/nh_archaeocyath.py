"""
Shared helpers for the archaeocyath models (metaldetes_taylori.py, antarcticocyathus_webersi.py):
Cambrian reef sponges built as double-walled, cylindrical-conical cups ("ancient cups").

An archaeocyath cup is two nested porous walls (the outer wall and the inner wall) separated by
a ring-shaped space, the intervallum, which is crossed by radial vertical partitions (septa,
taeniae or pseudosepta depending on the group). The inner wall encloses an open central cavity
that filtered water left through.

Each cup is one parametric ring-stack, so its vertex grid lines up with the pore pattern (no
voxel fuse / decimation, which would smear the pores):
  * the outer wall rises from the base to the rim; pores are single vertices pushed slightly in
    and painted dark, on every other column of every other ring. "rows" keeps them in straight
    vertical rows (e.g. Metaldetes); "random" staggers and thins them out so they look scattered
    (e.g. Antarcticocyathus);
  * the lip crosses the intervallum in a few radial rings; the columns on a partition stay at
    rim height while the ones between are sunk and darkened, so seen from above the cup shows
    the typical wheel-like ring of chambers around the cavity;
  * the inner wall runs back down into the central cavity, darkening with depth, to a floor.
Cups stand in a lumpy holdfast (voxel-fused ellipsoids) that hides their overlapping bases.
Fixed style: pivot at the base (z = 0).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_coral as nc

WARP = Vector((2.3, 7.1, 4.9))
PROFILE = (0.0, 0.12, 0.28, 0.46, 0.64, 0.82, 0.94, 1.0)   # heights of Cup.radii, base -> rim


@dataclass
class Cup:
    base: tuple                  # (x, y) where the cup leaves the holdfast
    height: float
    radii: tuple                 # outer radius at each PROFILE height, base -> rim
    lean: tuple = (0.0, 0.0)     # horizontal offset of the rim relative to the base (curved axis)
    z0: float = 0.0              # height of the cup's base
    wall: float = 0.4            # intervallum width as a fraction of the local outer radius
    sides: int = 40              # must be a multiple of `septa` (and even)
    septa: int = 20              # radial partitions across the intervallum
    rings: int = 18              # outer-wall rings
    depth: float = 0.6           # cavity depth as a fraction of the height


@dataclass
class Style:
    pores: str = "rows"          # "rows" or "random"
    pore_depth: float = 0.08     # pores pushed in by this fraction of the local radius
    pore_keep: float = 0.8       # "random": fraction of pore sites that get a pore
    rib_depth: float = 0.05      # how deep the chambers between partitions are sunk
    body: tuple = (0.85, 0.66, 0.42)
    body_dark: tuple = (0.66, 0.46, 0.28)
    pore: tuple = (0.36, 0.22, 0.13)
    rim: tuple = (0.95, 0.82, 0.60)
    chamber: tuple = (0.30, 0.17, 0.10)
    cavity: tuple = (0.17, 0.10, 0.07)
    holdfast: tuple = (0.62, 0.50, 0.36)
    holdfast_lumps: list = field(default_factory=list)  # [(x, y, z, rx, ry, rz)]


def _radius(cup, t):
    for i in range(len(PROFILE) - 1):
        if t <= PROFILE[i + 1]:
            u = (t - PROFILE[i]) / (PROFILE[i + 1] - PROFILE[i])
            u = u * u * (3 - 2 * u) * 0.5 + u * 0.5    # soften the profile kinks
            return cup.radii[i] + (cup.radii[i + 1] - cup.radii[i]) * u
    return cup.radii[-1]


def _centre(cup, t):
    return Vector((cup.base[0] + cup.lean[0] * t ** 1.6, cup.base[1] + cup.lean[1] * t ** 1.6,
                   cup.z0 + cup.height * t))


def cup_mesh(cup, style, rng):
    """One archaeocyath cup as a closed bmesh with its own "Col" layer."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    n = cup.sides
    step = n // cup.septa
    vcol = {}
    rows = []

    def ring(c, r, z_of_k, col_of_k, r_of_k=None):
        vs = []
        for k in range(n):
            a = k / n * math.tau
            rr = r_of_k(k) if r_of_k else r
            v = bm.verts.new((c.x + math.cos(a) * rr, c.y + math.sin(a) * rr, z_of_k(k)))
            vcol[v] = col_of_k(k, v.co)
            vs.append(v)
        rows.append(vs)

    def body(co):
        c = nh.lerp(style.body, style.body_dark, nh.smoothstep(cup.z0 + 0.25, cup.z0, co.z))
        return nh.lerp(c, style.body_dark, 0.3 * nh.smoothstep(0.0, 0.6, noise.noise(Vector(co) * 5 + WARP)))

    # outer wall
    stagger = [rng.randrange(2) for _ in range(cup.rings)]
    for i in range(cup.rings):
        t = i / (cup.rings - 1)
        c, r = _centre(cup, t), _radius(cup, t)
        pore_ring = i % 2 == 1 and 1 <= i <= cup.rings - 3

        def is_pore(k, i=i, pore_ring=pore_ring):
            if not pore_ring:
                return False
            if style.pores == "rows":
                return k % 2 == 0
            return (k + stagger[i]) % 2 == 0 and rng.random() < style.pore_keep

        pores = [is_pore(k) for k in range(n)]
        ring(c, r, lambda k, c=c: c.z,
             lambda k, co, p=pores: style.pore if p[k] else body(co),
             lambda k, r=r, p=pores: r * (1 - style.pore_depth) if p[k] else r)

    # lip across the intervallum: partitions stay up, the chambers between them are sunk
    c, r = _centre(cup, 1.0), _radius(cup, 1.0)
    w = cup.wall * r
    for f in (0.2, 0.5, 0.8):
        sunk = 1.0 if f == 0.5 else 0.75
        ring(c, r - w * f,
             lambda k, s=sunk: c.z - (0.0 if k % step == 0 else style.rib_depth * s),
             lambda k, co, s=sunk: style.rim if k % step == 0 else nh.lerp(style.rim, style.chamber, s))
    # inner wall down into the cavity
    t_floor = 1.0 - cup.depth
    for j in range(5):
        t = 1.0 - (1.0 - t_floor) * (j / 4) ** 0.8
        ci, ri = _centre(cup, t), _radius(cup, t) * (1 - cup.wall)
        dark = nh.smoothstep(0.0, 0.5, j / 4)
        ring(ci, ri, lambda k, ci=ci: ci.z,
             lambda k, co, d=dark: nh.lerp(style.rim, style.cavity, 0.55 + 0.45 * d))
    for a, b in zip(rows, rows[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            cc = vcol[lp.vert]
            lp[col] = (cc[0], cc[1], cc[2], 1.0)
    return bm


def build_colony(name, cups, style, rng, rubble=True):
    """Cups + fused holdfast + rubble -> the finished, grounded Blender object."""
    hold = nh.MeshBuilder()
    for x, y, z, rx, ry, rz in style.holdfast_lumps:
        hold.add(nh.ellipsoid((x, y, z), (rx, ry, rz), subdivisions=3), style.holdfast)
    lumps = hold.fuse(voxel=0.03, smooth=6, max_tris=500)

    def hold_col(co, n):
        k = noise.noise(co * 9 + WARP)
        return nh.lerp(style.holdfast, style.body_dark, 0.3 + 0.3 * k)

    mb = nh.MeshBuilder()
    mb.add(lumps, hold_col)
    for cup in cups:
        mb.add(cup_mesh(cup, style, rng))
    if rubble:
        nc.rubble(mb, rng, 0.42, 0.65, count=7, size=(0.04, 0.08))
    obj = mb.to_object(name, roughness=0.8)
    nh.ground_to_zero(obj)
    return obj
