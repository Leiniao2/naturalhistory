"""
Shared helpers for the Cloudina models (cloudina_hartmannae.py, cloudina_riemkeae.py,
cloudina_carinata.py): a terminal-Ediacaran calcified tube built "cone-in-cone" as a stack of
nested, slightly flared funnel-shaped collars, and a reef-like cluster of such tubes leaning in
every direction on a patch of microbial-mat seafloor.

A tube is one continuous ring-stack: for every collar, a ring where it emerges from inside the
collar below (shadowed), an optional mid ring giving the funnel its concave flare, and the
flared rim; a short inward ledge leads from each rim down to where the next collar emerges.
Each collar is set a little off-centre on the one below and the axis wanders slowly, so the
tube is wavy-walled and gently curved. Tubes may bud a daughter tube from inside one of their
collars. The last collar stays open: a rim lip and a short dark interior. Optional ornament:
longitudinal keels on the collars that stick out as spines at the rims (C. carinata).

Pale cream calcite on a darker olive-grey mat. Fixed style: pivot at the base (z = 0).
"""

import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh
import nh_fish as nf

CALCITE = (0.86, 0.83, 0.74)    # cream-white collar walls
RIM = (0.96, 0.94, 0.88)        # bright collar rims
SHADOW = (0.55, 0.53, 0.47)     # where a collar emerges from under the rim below
INSIDE = (0.20, 0.17, 0.14)     # open tube interior
BORE = (0.16, 0.13, 0.11)       # drill holes (possible early predation)
MAT = (0.26, 0.25, 0.19)        # dark olive microbial mat
MAT_LIGHT = (0.40, 0.37, 0.28)
SILT = (0.52, 0.48, 0.38)
UP = Vector((0, 0, 1))


@dataclass
class TubeStyle:
    radius: float = 0.035        # emergence radius of the first collar
    growth: float = 1.025        # radius multiplier per collar (tubes widen upward)
    collars: tuple = (9, 14)     # collar count range per tube
    height: float = 1.25         # collar height, in collar radii
    flare: float = 0.30          # rim radius = (1 + flare) * emergence radius
    sink: float = 0.25           # how deep (in collar heights) the next collar sits inside
    ecc: float = 0.10            # eccentric offset per collar, in collar radii
    curve: float = 0.07          # axis wander per collar (radians)
    sides: int = 8
    mid_ring: bool = True        # extra ring per collar for a concave funnel profile
    keels: int = 0               # longitudinal ridges per collar (0 = smooth)
    keel_amp: float = 0.0        # ridge height on the wall, in collar radii
    spine_amp: float = 0.0       # extra outward spike of the ridges at the rim
    bud_chance: float = 0.3      # chance a tube buds a daughter tube
    bore_chance: float = 0.0     # chance a tube carries a drill hole


def _frame(d, prev_side):
    if prev_side is None:
        ref = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
        side = d.cross(ref).normalized()
    else:
        side = (prev_side - d * prev_side.dot(d)).normalized()
    return side, d.cross(side).normalized()


def tube(rng, style, start, direction, radius=None, collars=None, tips=None, bores=None, depth=0):
    """Builds one cone-in-cone tube (and any buds). Returns a list of (bm, {vert: rgb})."""
    s = style
    r = s.radius if radius is None else radius
    n = collars or rng.randint(*s.collars)
    bm = bmesh.new()
    vcol = {}
    rings = []
    d = direction.normalized()
    c = start.copy()
    side = None
    bend = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized()
    phase = rng.uniform(0, math.tau)
    tone = rng.uniform(0.94, 1.04)
    bud_at = rng.randint(2, max(2, n - 4)) if (depth == 0 and rng.random() < s.bud_chance) else -1
    out = []

    def ring(center, d, side, up, rad, col, keel=0.0):
        vs = []
        for k in range(s.sides):
            a = k / s.sides * math.tau + phase
            rr = rad
            if s.keels and keel:
                ridge = max(0.0, math.cos((a - phase) * s.keels)) ** 6  # keels stay on vertices
                rr = rad * (1.0 + keel * ridge)
            v = bm.verts.new(center + (side * math.cos(a) + up * math.sin(a)) * rr)
            k_n = 1.0 + 0.05 * noise.noise(v.co * 40.0)
            vcol[v] = tuple(min(1.0, x * tone * k_n) for x in col)
            vs.append(v)
        rings.append(vs)

    for i in range(n):
        side, up = _frame(d, side)
        h = r * s.height
        ring(c, d, side, up, r, SHADOW, s.keel_amp)
        if s.mid_ring:
            ring(c + d * h * 0.6, d, side, up, r * (1 + s.flare * 0.35), CALCITE, s.keel_amp)
        rim = c + d * h
        ring(rim, d, side, up, r * (1 + s.flare), RIM, s.keel_amp + s.spine_amp)
        if i == bud_at:
            # a daughter tube grows out of this collar, diverging from the parent
            ba = rng.uniform(0, math.tau)
            perp = (side * math.cos(ba) + up * math.sin(ba)).normalized()
            bd = (d + perp * rng.uniform(0.5, 0.9)).normalized()
            out += tube(rng, s, rim - d * h * 0.5, bd, r * 0.85, max(4, (n - i) - rng.randint(0, 3)),
                        tips, bores, depth + 1)
        # next collar: sunk a little inside this one, nudged off-centre, axis wandering
        if i < n - 1:
            r *= s.growth
            off = (side * math.cos(i * 2.1 + phase) + up * math.sin(i * 2.1 + phase)) * r * s.ecc
            d = (d + bend * s.curve + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * s.curve * 0.6).normalized()
            c = rim - d * h * s.sink + off
    # open top: rim lip, then a short dark interior and floor
    rim_r = r * (1 + s.flare)
    ring(rim - d * h * 0.06, d, side, up, rim_r * 0.82, CALCITE, s.keel_amp)
    ring(rim - d * h * 0.5, d, side, up, r * 0.9, INSIDE)
    floor = bm.verts.new(rim - d * h * 1.2)
    vcol[floor] = INSIDE
    for a, b in zip(rings, rings[1:]):
        for k in range(s.sides):
            j = (k + 1) % s.sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    for k in range(s.sides):
        bm.faces.new([rings[-1][k], rings[-1][(k + 1) % s.sides], floor])
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if tips is not None:
        tips.append(rim)
    if bores is not None and rng.random() < s.bore_chance:
        # one drill hole on a collar wall partway up the tube
        bores.append(rings[len(rings) // 2][rng.randrange(s.sides)].co.copy())
    out.append((bm, vcol))
    return out


def seafloor(mb, radius, seed=(2.0, 5.0, 1.0)):
    """Low, wrinkled microbial-mat patch the tubes are rooted in."""
    sv = Vector(seed)
    bm = nh.uv_ellipsoid((0.0, 0.0, -0.03), (radius, radius * 0.88, 0.055), 22, 6,
                         deform=lambda n: 1.0 + 0.08 * noise.noise(n * 4.0 + sv))

    def col(co, n):
        m = noise.noise(co * 5.0 + sv) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 20.0 + sv))
        c = nh.lerp(MAT, MAT_LIGHT, 0.2 + 0.5 * m)
        c = nh.lerp(c, (0.17, 0.17, 0.12), nh.smoothstep(0.08, 0.0, wrinkle) * 0.6)  # wrinkle marks
        return nh.lerp(c, SILT, nh.smoothstep(0.55, 0.95, math.hypot(co.x, co.y / 0.88) / radius))

    mb.add(bm, col)


def cluster(style, seed, count, radius, tilt=(15, 65), lying=0, name="Cloudina", fragments=0):
    """A reef-like clump: `count` tubes rooted on the mat leaning every which way, `lying` tubes
    toppled onto the mat, and `fragments` broken collar stacks scattered around."""
    rng = random.Random(seed)
    mb = nh.MeshBuilder()
    seafloor(mb, radius * 1.25)
    parts, bores = [], []
    roots = []
    for i in range(count):
        # rooting points spread apart a little so the tubes don't all grow through each other
        for _try in range(30):
            a = rng.uniform(0, math.tau)
            rr = radius * math.sqrt(rng.random()) * 0.85
            p = Vector((math.cos(a) * rr, math.sin(a) * rr, -0.02))
            if all((p - q).length > style.radius * 2.6 for q in roots):
                break
        roots.append(p)
        # lean mostly outward from the clump centre, so the thicket fans open
        az = a + rng.uniform(-1.0, 1.0) if rr > radius * 0.2 else rng.uniform(0, math.tau)
        el = math.radians(90 - rng.uniform(*tilt))
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        k = rng.uniform(0.75, 1.15)
        parts += tube(rng, style, p, d, style.radius * k, bores=bores)
    for i in range(lying + fragments):
        a = rng.uniform(0, math.tau)
        rr = radius * rng.uniform(0.3, 1.05)
        az = rng.uniform(0, math.tau)
        el = math.radians(rng.uniform(2, 9))
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        r0 = style.radius * rng.uniform(0.8, 1.1)
        p = Vector((math.cos(a) * rr, math.sin(a) * rr, r0 * 0.6))
        n = rng.randint(*style.collars) if i < lying else rng.randint(3, 5)
        parts += tube(rng, style, p, d, r0, n, bores=bores)
    for bm, vcol in parts:
        if bores:
            for v in bm.verts:
                for b in bores:
                    dist = (v.co - b).length
                    if dist < style.radius * 0.6:
                        vcol[v] = nh.lerp(BORE, vcol[v], nh.smoothstep(style.radius * 0.3, style.radius * 0.6, dist))
        nf.add_colored(mb, bm, vcol, smooth=True)
    obj = mb.to_object(name, roughness=0.75)
    for v in obj.data.vertices:  # flatten the buried undersides of the mat and tube bases
        v.co.z = max(v.co.z, -0.012)
    nh.ground_to_zero(obj)
    return obj


VIEWS = ((25, 30), (70, 45), (10, 75), (-90, 6))
