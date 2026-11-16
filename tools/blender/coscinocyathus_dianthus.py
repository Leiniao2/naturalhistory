"""
Procedural Coscinocyathus dianthus (early Cambrian regular archaeocyath, Sardinia) for the map:
a small group of solitary, conical, double-walled cups on a patch of lime mud and microbial crust.

Coscinocyathus is the textbook "regular" archaeocyath: an inverted cone with a porous outer wall
and a porous inner wall, the ring-shaped intervallum between them divided by straight, porous
radial septa AND by stacked, porous horizontal tabulae, so it is split into a lattice of small
chambers; the inner wall encloses the open central cavity. Unlike nh_archaeocyath.py's cups
(whose septa are only hinted at by sinking the lip), every part is real geometry here:
  * the front cup is cut away (a third of it, facing -Y, removed), showing both walls, the septa
    standing between them and the tabulae stacked like shelves;
  * the two intact cups behind show, seen from above, the flower-like ring of septa around the
    dark cavity, with the top tabula just below the rim closing the chambers.
Living colours are unknown; a cool pale grey calcite tone is used, darker in the chambers.
Fixed style: pivot at the base (z = 0). Seabed patch: nh_archaeo_reef.py.

Usage:
  blender --background --python tools/blender/coscinocyathus_dianthus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Coscinocyathus.fbx
"""

import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_archaeo_reef as nr  # noqa: E402

SEED = 11
BODY = (0.50, 0.47, 0.40)          # pale grey calcite
BODY_DARK = (0.33, 0.30, 0.25)
PORE = (0.12, 0.11, 0.10)
RIM = (0.66, 0.63, 0.55)
CHAMBER = (0.17, 0.16, 0.14)
CAVITY = (0.13, 0.12, 0.11)
TABULA = (0.52, 0.49, 0.42)
SPAN = math.tau * 2 / 3          # kept part of the cut-away cup (a third is removed)


@dataclass
class Cup:
    base: tuple
    height: float
    r_base: float
    r_rim: float
    lean: tuple = (0.0, 0.0)
    wall: float = 0.36           # intervallum width as a fraction of the outer radius
    sides: int = 36              # angular samples (over the kept part when cut)
    septa: int = 18              # over the full circle
    rings: int = 12
    tabulae: tuple = (0.86,)     # heights (fraction of the cup) of the tabulae
    cut: float = None            # azimuth (rad) of the removed third, or None
    depth: float = 0.55          # cavity depth (fraction of the height), intact cups
    th: float = 0.012            # wall / plate thickness


def radius(c, t):
    return c.r_base + (c.r_rim - c.r_base) * (1 - (1 - t) ** 1.35)


def centre(c, t):
    return Vector((c.base[0] + c.lean[0] * t ** 1.5, c.base[1] + c.lean[1] * t ** 1.5, c.height * t))


def t_of(c, z):
    return max(0.0, min(1.0, z / c.height))


def cup(c, rng):
    p = nr.Painter()
    n = c.sides
    if c.cut is None:
        angles = [k / n * math.tau for k in range(n)]
        wrap = True
    else:
        a0 = c.cut + math.pi / 3
        angles = [a0 + k / n * (SPAN) for k in range(n + 1)]
        wrap = False
    th = c.th

    def radial(sign):
        def want(q):
            m = nr.centroid(q)
            d = m - centre(c, t_of(c, m.z))
            d.z = 0
            return d * sign
        return want

    def pt(t, r, a, dz=0.0):
        ce = centre(c, t)
        return Vector((ce.x + math.cos(a) * r, ce.y + math.sin(a) * r, ce.z + dz))

    def body(co):
        k = nh.smoothstep(0.25, 0.0, co.z)
        col = nh.lerp(BODY, BODY_DARK, 0.6 * k)
        return nh.lerp(col, BODY_DARK, 0.3 * nh.smoothstep(0.0, 0.6, noise.noise(co * 6 + nr.WARP)))

    def shade(t, lo, hi):
        """chamber/cavity walls darken with depth below the rim"""
        return nh.lerp(lo, hi, nh.smoothstep(1.0, 0.75, t))

    cut = c.cut is not None
    t_lo = 0.03
    rings_in = 4 if cut else 2
    t_in = t_lo if cut else 0.78
    t_floor = 0.12 if cut else 1.0 - c.depth

    # outer wall, outside: porous
    ext = []
    for i in range(c.rings):
        t = t_lo + (1 - t_lo) * i / (c.rings - 1)
        r = radius(c, t)
        row = []
        for k, a in enumerate(angles):
            pore = i % 2 == 1 and 1 <= i <= c.rings - 3 and k % 2 == 0
            co = pt(t, r * (1 - 0.08 * pore), a)
            row.append(p.v(co, PORE if pore else body(co)))
        ext.append(row)
    p.grid(ext, radial(1), wrap)

    def wall_rows(r_of, t0, t1, col_of, count):
        rows = []
        for i in range(count):
            t = t0 + (t1 - t0) * i / (count - 1)
            rows.append([p.v(pt(t, r_of(t), a), col_of(t)) for a in angles])
        return rows

    # outer wall, inside (faces the intervallum)
    oin = wall_rows(lambda t: radius(c, t) - th, t_in, 1.0, lambda t: shade(t, BODY, CHAMBER), rings_in)
    p.grid(oin, radial(-1), wrap)
    # inner wall, outside (faces the intervallum)
    r_in = lambda t: radius(c, t) * (1 - c.wall)  # noqa: E731
    iout = wall_rows(r_in, t_in, 1.0, lambda t: shade(t, BODY, CHAMBER), rings_in)
    p.grid(iout, radial(1), wrap)
    # inner wall, inside (faces the central cavity), down to the cavity floor
    iin = wall_rows(lambda t: r_in(t) - th, t_floor, 1.0, lambda t: shade(t, RIM, CAVITY), 4 if cut else 5)
    p.grid(iin, radial(-1), wrap)
    up = Vector((0, 0, 1))
    # rims
    p.grid([ext[-1], [p.v(v.co, RIM) for v in oin[-1]]], lambda q: up, wrap)
    p.grid([iout[-1], [p.v(v.co, RIM) for v in iin[-1]]], lambda q: up, wrap)
    # cavity floor
    fc = centre(c, t_floor)
    ring = [p.v(v.co, CAVITY) for v in iin[0]]
    mid = p.v(fc, CAVITY)
    for k in range(len(ring) if wrap else len(ring) - 1):
        p.face([ring[k], ring[(k + 1) % len(ring)], mid], up)
    if cut:
        # cut faces: one polygon per wall per side, in the cut's radial plane
        for col_idx, a, sgn in ((0, angles[0], -1), (-1, angles[-1], 1)):
            tang = Vector((-math.sin(a), math.cos(a), 0)) * sgn
            for outer, inner in ((ext, oin), (iout, iin)):
                vs = [p.v(r[col_idx].co, RIM) for r in outer] + [p.v(r[col_idx].co, RIM) for r in reversed(inner)]
                p.face(vs, tang)
            # the cavity floor's cut edge
            p.face([p.v(fc, CAVITY), p.v(iin[0][col_idx].co, CAVITY),
                    p.v(iin[0][col_idx].co - Vector((0, 0, 0.03)), CAVITY), p.v(fc - Vector((0, 0, 0.03)), CAVITY)], tang)

    # septa: thin radial plates between the walls, porous where the cut shows them
    s_count = c.septa
    hseg = 5 if cut else 2
    rseg = 2 if cut else 1
    for s in range(s_count):
        a = s / s_count * math.tau + math.pi / s_count
        if cut:
            rel = (a - angles[0]) % math.tau
            if rel < 0.06 or rel > SPAN - 0.06:
                continue
        tang = Vector((-math.sin(a), math.cos(a), 0))
        for sgn in (1, -1):
            rows = []
            for i in range(hseg + 1):
                t = t_lo + (1 - t_lo) * i / hseg
                r0, r1 = r_in(t), radius(c, t) - th
                row = []
                for j in range(rseg + 1):
                    co = pt(t, r0 + (r1 - r0) * j / rseg, a) + tang * (sgn * th * 0.45)
                    pore = 0 < i < hseg and 0 < j < rseg and i % 2 == 1
                    row.append(p.v(co, PORE if pore else shade(t, RIM, BODY)))
                rows.append(row)
            p.grid(rows, lambda q, w=tang * sgn: w)
        # top edge of the septum (reads as a light spoke from above)
        r0, r1 = r_in(1.0), radius(c, 1.0) - th
        e = [p.v(pt(1.0, r0, a) + tang * (sg * th * 0.45), RIM) for sg in (1, -1)]
        f = [p.v(pt(1.0, r1, a) + tang * (sg * th * 0.45), RIM) for sg in (-1, 1)]
        p.face(e + f, up)

    # tabulae: porous horizontal plates across the intervallum
    tab_angles = angles if not cut else [angles[0] + k / (n // 2) * SPAN for k in range(n // 2 + 1)]
    for tt in c.tabulae:
        for sgn in (1, -1):
            rows = []
            rsteps = 2 if cut else 1     # porous middle row only where the cut shows it
            for j in range(rsteps + 1):
                row = []
                for k, a in enumerate(tab_angles):
                    r = r_in(tt) + (radius(c, tt) - th - r_in(tt)) * j / rsteps
                    co = pt(tt, r, a, sgn * th * 0.5)
                    pore = 0 < j < rsteps and k % 2 == 0
                    dark = TABULA if cut else nh.lerp(TABULA, CHAMBER, 0.45)
                    row.append(p.v(co, PORE if pore else dark))
                rows.append(row)
            p.grid(rows, lambda q, w=Vector((0, 0, sgn)): w, wrap)
        if cut:
            for col_idx, sgnc in ((0, -1), (-1, 1)):
                a = tab_angles[col_idx]
                tang = Vector((-math.sin(a), math.cos(a), 0)) * sgnc
                r0, r1 = r_in(tt), radius(c, tt) - th
                p.face([p.v(pt(tt, r0, a, th * 0.5), RIM), p.v(pt(tt, r1, a, th * 0.5), RIM),
                        p.v(pt(tt, r1, a, -th * 0.5), RIM), p.v(pt(tt, r0, a, -th * 0.5), RIM)], tang)
    return p.mesh()


CUPS = [
    # front: the cut-away cup, wedge removed toward the viewer (-Y)
    Cup(base=(0.02, -0.08), height=0.92, r_base=0.035, r_rim=0.30, lean=(0.0, -0.03),
        sides=30, septa=18, rings=11, tabulae=(0.3, 0.5, 0.7, 0.9), cut=-math.pi / 2),
    # intact cups behind, rims tipped a little toward the viewer
    Cup(base=(-0.34, 0.22), height=0.72, r_base=0.03, r_rim=0.24, lean=(-0.06, -0.02),
        sides=26, septa=13, rings=10, tabulae=(0.88,)),
    Cup(base=(0.33, 0.25), height=0.55, r_base=0.025, r_rim=0.19, lean=(0.05, -0.03),
        sides=22, septa=11, rings=9, tabulae=(0.88,)),
]

CLOTS = [(0.02, -0.08, 0.05, 0.15, 0.14, 0.07), (-0.34, 0.22, 0.05, 0.12, 0.12, 0.06),
         (0.33, 0.25, 0.04, 0.11, 0.11, 0.06), (-0.15, 0.05, 0.03, 0.14, 0.1, 0.05),
         (0.2, 0.05, 0.03, 0.12, 0.09, 0.045), (-0.25, -0.2, 0.02, 0.09, 0.07, 0.035)]


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    nr.seabed(mb, rng, 0.62, CLOTS)
    for c in CUPS:
        mb.add(cup(c, rng))
    return nr.finish(mb, "Coscinocyathus")


if __name__ == "__main__":
    nh.run(build, "Coscinocyathus", ground=(0.62, 0.58, 0.48), views=((15, 25), (60, 50), (10, 78)))
