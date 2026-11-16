"""
Shared helpers for the Halysites chain-coral models (halysites_catenularia.py,
halysites_priscus.py): Ordovician-Silurian tabulate corals whose colonies are built of
palisade-like walls ("ranks"), each a single row of elliptical corallites joined side by side.
The ranks meet and branch to enclose open, window-like spaces (lacunae), so seen from above the
colony looks like a net of chains, hence the name (Greek halysis, chain).

The colony is built from a 2D network of lacunae:
  * a hexagonal lattice of cells (cell centres CELL apart) is clipped to a lumpy disc, and its
    shared vertices are jittered so the windows come out rounded-polygonal and uneven;
  * optionally some interior walls are removed so neighbouring cells merge into longer windows,
    preferring one direction (`merge_dir`), which gives the elongated lacunae in roughly parallel
    ranks of H. catenularia; `max_merge` caps how many cells one window may swallow;
  * every remaining wall becomes a chain of elliptical corallite tubes (long axis along the
    wall, neighbours overlapping a little so the chain reads as a row of beads with notches
    between them). Each tube is a smooth-shaded 8-sided prism plus a separate, hard-edged cap:
    a pale rim around a sunken dark calice. The tops follow a dome (`height` at the centre,
    `edge_height` at the margin) with a little noise, like the uneven growth surface of a real
    colony.
  * a share of the corallites carry an extended polyp: a small star of tentacles over the calice
    (soft parts are never preserved, so polyps and all colours are a speculative guess).
Real Halysites also has tiny mesocorallites (tubules) between the corallites; at map size they
are left out. The corallites are stylised (far larger relative to the colony than the real
1.5-2 mm tubes) so the chains read on a map tile. The colony stands on a low, dark mud pad that
shows through the windows. Fixed style: pivot at the base (z = 0).
"""

import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Vector, noise

import nh_model as nh

WARP = Vector((4.1, 8.3, 2.7))
SIDES = 8        # around each corallite tube
POLYP_ARMS = 5   # tentacles per polyp star


@dataclass
class Colony:
    name: str
    seed: int
    radius: float              # colony radius (lumpy)
    outline_noise: float       # how lumpy the outline is (fraction of radius)
    height: float              # wall height at the colony centre
    edge_height: float         # wall height at the margin
    dome_power: float          # >1: flatter top, steeper flanks
    cell: float                # lacuna lattice spacing (centre to centre)
    jitter: float              # vertex jitter as a fraction of the hexagon radius
    corallite: float           # target corallite length along the chain
    width_ratio: float         # corallite short / long axis (1 = round)
    merge: float = 0.0         # chance to remove an eligible interior wall
    merge_dir: float = 0.0     # preferred elongation of merged windows (degrees)
    max_merge: int = 1         # max cells per window
    polyp_frac: float = 0.6    # share of corallites with an extended polyp
    wall: tuple = (0.92, 0.87, 0.74)
    wall_dark: tuple = (0.66, 0.58, 0.45)
    rim: tuple = (0.97, 0.94, 0.84)
    calice: tuple = (0.30, 0.20, 0.13)
    polyp: tuple = (0.55, 0.62, 0.30)
    polyp_tip: tuple = (0.90, 0.92, 0.62)
    mud: tuple = (0.30, 0.27, 0.22)


# ---------------------------------------------------------------- lacuna network

def network(col, rng):
    """Returns (vertex positions {id: Vector2}, walls [(id_a, id_b)]) of the chain network."""
    s = col.cell
    hex_r = s / math.sqrt(3)
    span = int(col.radius / s) + 3
    seed = Vector((rng.random() * 40, rng.random() * 40, 0))

    def inside(c):
        a = math.atan2(c.y, c.x)
        lump = 1.0 + col.outline_noise * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 1.3 + seed)
        return c.length < col.radius * lump - hex_r * 0.6

    keys, pos = {}, {}
    cells = []    # list of vertex ids per kept cell
    centres = []
    for r in range(-span, span + 1):
        for q in range(-span, span + 1):
            c = Vector((s * (q + r * 0.5), s * r * math.sqrt(3) / 2))
            if not inside(c):
                continue
            ids = []
            for k in range(6):
                a = math.radians(30 + 60 * k)
                p = c + Vector((math.cos(a), math.sin(a))) * hex_r
                key = (round(p.x * 1000), round(p.y * 1000))
                if key not in keys:
                    keys[key] = len(keys)
                    pos[keys[key]] = p
                ids.append(keys[key])
            cells.append(ids)
            centres.append(c)
    for i in sorted(pos):
        a = rng.uniform(0, math.tau)
        pos[i] = pos[i] + Vector((math.cos(a), math.sin(a))) * hex_r * col.jitter * rng.random()

    # walls with the cells on either side
    side = {}
    for ci, ids in enumerate(cells):
        for k in range(6):
            e = tuple(sorted((ids[k], ids[(k + 1) % 6])))
            side.setdefault(e, []).append(ci)
    walls = sorted(side)
    degree = {}
    for a, b in walls:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1

    # merge neighbouring cells into longer windows (union-find, capped size)
    parent = list(range(len(cells)))
    size = [1] * len(cells)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    removed = set()
    if col.merge > 0:
        d = Vector((math.cos(math.radians(col.merge_dir)), math.sin(math.radians(col.merge_dir))))
        order = [e for e in walls if len(side[e]) == 2]
        rng.shuffle(order)
        for e in order:
            c0, c1 = side[e]
            along = abs((centres[c1] - centres[c0]).normalized().dot(d)) ** 4
            if rng.random() > col.merge * along:
                continue
            r0, r1 = find(c0), find(c1)
            if r0 == r1 or size[r0] + size[r1] > col.max_merge:
                continue
            if degree[e[0]] <= 2 or degree[e[1]] <= 2:
                continue
            parent[r1] = r0
            size[r0] += size[r1]
            degree[e[0]] -= 1
            degree[e[1]] -= 1
            removed.add(e)
    return pos, [e for e in walls if e not in removed]


# ---------------------------------------------------------------- parts

def dome_height(col, p, seed):
    t = min(1.0, p.length / col.radius)
    h = col.edge_height + (col.height - col.edge_height) * (1 - t ** col.dome_power) ** 0.6
    return h * (1.0 + 0.10 * noise.noise(Vector((p.x, p.y, 0)) * 3.0 + seed))


def corallite(mb, col, c, axis, a, b, top, rng, polyp):
    """One elliptical corallite tube at c (2D), long axis `axis` (unit 2D), semi-axes a, b."""
    side = Vector((-axis.y, axis.x))
    ring = [c + axis * math.cos(t) * a + side * math.sin(t) * b
            for t in (k / SIDES * math.tau for k in range(SIDES))]
    tint = rng.uniform(0.94, 1.04)

    def wall_col(co, _n):
        k = nh.smoothstep(0.0, top * 0.8, co.z)
        return tuple(min(1.0, x * tint) for x in nh.lerp(col.wall_dark, col.wall, k))

    # smooth sides
    bm = bmesh.new()
    lo = [bm.verts.new((p.x, p.y, -0.01)) for p in ring]
    hi = [bm.verts.new((p.x, p.y, top)) for p in ring]
    for k in range(SIDES):
        j = (k + 1) % SIDES
        bm.faces.new([lo[k], lo[j], hi[j], hi[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mb.add(bm, wall_col)

    # hard-edged cap: pale rim, sunken calice
    depth = min(a, b) * 0.45
    bm = bmesh.new()
    rim = [bm.verts.new((p.x, p.y, top)) for p in ring]
    inner = [bm.verts.new((c.x + (p.x - c.x) * 0.55, c.y + (p.y - c.y) * 0.55, top - depth * 0.6)) for p in ring]
    centre = bm.verts.new((c.x, c.y, top - depth))
    for k in range(SIDES):
        j = (k + 1) % SIDES
        bm.faces.new([rim[k], rim[j], inner[j], inner[k]])
        bm.faces.new([inner[k], inner[j], centre])
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()

    def cap_col(co, _n, c=c):
        r = (Vector((co.x, co.y)) - c).length / a
        return nh.lerp(col.calice, col.rim, nh.smoothstep(0.35, 0.75, r * a / b if b < a else r))

    mb.add(bm, cap_col, smooth=False)

    if polyp:
        polyp_star(mb, col, Vector((c.x, c.y, top - depth * 0.3)), b * rng.uniform(1.25, 1.6), rng)


def polyp_star(mb, col, centre, r, rng):
    """A small extended polyp: a low dome-shaped star of tentacles over the calice."""
    bm = bmesh.new()
    spin = rng.uniform(0, math.tau)
    top = bm.verts.new(centre + Vector((0, 0, r * 0.45)))
    under = bm.verts.new(centre + Vector((0, 0, -r * 0.05)))
    ring = []
    for k in range(POLYP_ARMS * 2):
        a = spin + k / (POLYP_ARMS * 2) * math.tau
        rr = r if k % 2 == 0 else r * 0.45
        lift = r * (0.30 if k % 2 == 0 else 0.22)
        ring.append(bm.verts.new(centre + Vector((math.cos(a) * rr, math.sin(a) * rr, lift))))
    n = len(ring)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new([top, ring[k], ring[j]])
        bm.faces.new([under, ring[j], ring[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col_fn(co, _n):
        d = (Vector((co.x, co.y)) - Vector((centre.x, centre.y))).length / r
        return nh.lerp(col.polyp, col.polyp_tip, nh.smoothstep(0.3, 0.95, d))

    mb.add(bm, col_fn)


# ---------------------------------------------------------------- colony

def build_colony(col):
    rng = random.Random(col.seed)
    seed = Vector((rng.random() * 30, rng.random() * 30, rng.random() * 30))
    pos, walls = network(col, rng)
    mb = nh.MeshBuilder()

    # dark mud pad under the colony (shows through the lacunae)
    pad = nh.uv_ellipsoid((0, 0, 0), (col.radius * 0.98, col.radius * 0.98, 0.035), segments=28, rings=6,
                          deform=lambda n: 1.0 + 0.06 * noise.noise(n * 2.0 + seed))
    mb.add(pad, lambda co, n: tuple(x * (0.9 + 0.2 * noise.noise(co * 8 + WARP)) for x in col.mud))

    count = 0
    for ia, ib in walls:
        pa, pb = pos[ia], pos[ib]
        length = (pb - pa).length
        axis = (pb - pa).normalized()
        n = max(1, round(length / col.corallite))
        step = length / n
        for i in range(n):
            c = pa + axis * step * (i + 0.5)
            a = step * 0.58
            b = col.corallite * 0.5 * col.width_ratio
            top = dome_height(col, c, seed)
            corallite(mb, col, c, axis, a, b, top, rng, rng.random() < col.polyp_frac)
            count += 1
    print(f"{col.name}: {len(walls)} ranks, {count} corallites")
    obj = mb.to_object(col.name, roughness=0.8)
    nh.ground_to_zero(obj)
    return obj
