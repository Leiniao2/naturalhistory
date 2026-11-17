"""
Shared parametric early fish for the Silurian batch (tag "sil"): the anaspid
birkenia_elegans.py, jamoytius_kerwoodi.py, the thelodont loganellia_scotica.py and the
"maxillate" placoderms entelognathus_primordialis.py and qilinyu_rostrata.py.
Built from nh_early_fish pieces (Profile, scale_shell, fins, eyes).

Spec:
  * rows: Profile rows (y, half-width, top, bottom, centre z), snout at -Y; the centre
    line falls toward the tail for a hypocercal tail (anaspids, thelodonts: the body
    axis turns DOWN into the lower lobe) or rises for a heterocercal one.
  * skin: "scales" (separate rhombic scales on a lattice), "smooth" (painted loft, with
    optional chevron myomere bands) or "shagreen" (smooth loft with fine speckle);
  * armour: (y_back, plate seeds) - a smooth bony head/trunk shield painted with plate
    sutures, sitting proud of the scaled trunk behind it (placoderms);
  * tail: "hypo" | "hetero" | "fork", with lobe sizes;
  * fins: median fins, paired fins, lateral fin folds, spines, dorsal scutes, gill
    openings, rostrum, mouth line, eyes.
Faces -Y, pivot at the body centre (Swim).
"""

import math
from dataclasses import dataclass, field

from mathutils import Vector, noise

import nh_model as nh
import nh_early_fish as ef


@dataclass
class Spec:
    name: str
    rows: list
    power: float = 2.2
    skin: str = "scales"
    stations: int = 36
    around: int = 18
    head_back: float = -0.50          # end of the smooth head (scales start here)
    armour: tuple = None              # (y_back, [(y, phi) plate seeds])
    tail: str = "hypo"
    tail_y0: float = 0.40
    tail_main: float = 0.22           # main lobe length (the one the axis runs into... web side)
    tail_minor: float = 0.06
    median: list = field(default_factory=list)   # (y0, y1, height, sign, sweep)
    paired: list = field(default_factory=list)   # (y0, y1, angle, length, out, down, back)
    folds: tuple = None               # lateral fin fold: (y0, y1, width)
    spines: list = field(default_factory=list)   # (y, angle, (dx, dy, dz), r)  angle on the body; dx mirrored
    scutes: tuple = None              # (y0, y1, n, size)
    gills: tuple = None               # (y0, y1, n, angle, r)
    rostrum: float = 0.0
    eye_y: float = -0.65
    eye_a: float = 0.4
    eye_r: float = 0.03
    eye_look: tuple = (0.92, -0.25, 0.25)
    mouth: tuple = None               # (y0, y1, rel z of the gape in bottom half-heights)
    myomeres: int = 0
    # colours
    back: tuple = (0.26, 0.25, 0.17)
    flank: tuple = (0.52, 0.45, 0.30)
    belly: tuple = (0.80, 0.75, 0.60)
    blotch: tuple = (0.20, 0.18, 0.12)
    blotch_amount: float = 0.4
    bone: tuple = (0.55, 0.48, 0.34)
    suture: tuple = (0.14, 0.11, 0.08)
    fin: tuple = (0.42, 0.37, 0.26)
    fin_edge: tuple = (0.62, 0.57, 0.44)
    ray: tuple = (0.24, 0.20, 0.13)
    iris: tuple = (0.62, 0.50, 0.22)


def build(s):
    prof = ef.Profile(s.rows, power=s.power)
    mb = nh.MeshBuilder()

    def body_col(co, u, v):
        c = ef.countershade(v, s.back, s.flank, s.belly, co, s.blotch, s.blotch_amount)
        if s.myomeres:
            ph = co.y * s.myomeres + abs(v) * 1.2
            c = nh.lerp(c, s.blotch, 0.6 * nh.smoothstep(0.6, 0.9, math.cos(ph * math.tau)))
        if s.skin == "shagreen" and noise.noise(co * 90.0) > 0.35:
            c = nh.lerp(c, s.belly, 0.25)
        return c

    def smooth_col(co, n):
        u, v = prof.rel(co)
        return body_col(co, u, v)

    head_end = s.armour[0] if s.armour else s.head_back
    if s.armour:
        seeds = s.armour[1]

        def armour_col(co, n):
            u, v = prof.rel(co)
            phi = ef.phi_of(prof, co)
            c = nh.lerp(s.bone, s.suture, 0.25 * nh.smoothstep(0.1, 0.9, v))
            c = nh.lerp(c, s.belly, 0.5 * nh.smoothstep(-0.3, -0.9, v))
            c = nh.lerp(c, s.suture, 0.25 * nh.smoothstep(0.25, 0.6, ef.mottle(co, 45.0)))
            c = nh.lerp(c, s.suture, 0.85 * ef.plates(seeds, co.y, phi, sphi=0.10, width=0.022))
            return c
        ef.head_shell(mb, prof, head_end, armour_col, ny=18, na=28, grow=0.008)
    else:
        ef.head_shell(mb, prof, head_end, smooth_col, ny=14, na=24, grow=0.004)

    if s.skin == "scales":
        ef.scale_shell(mb, prof, head_end - 0.02, prof.y1, s.stations, s.around, body_col, lift=0.004,
                       fade_y=(prof.y1 - 0.3, prof.y1 - 0.05))
    else:
        mb.add(ef.loft(prof, head_end - 0.03, prof.y1, 34, 24, cap0=False, cap1=True), smooth_col)

    plain = ef.ray_color(s.fin, s.ray, s.fin_edge, 1, rays=False)
    rays = lambda n: ef.ray_color(s.fin, s.ray, s.fin_edge, n)  # noqa: E731

    for y0, y1, h, sign, sweep in s.median:
        ef.median_fin(mb, prof, y0, y1, lambda u, h=h: h * math.sin(math.pi * (0.2 + 0.8 * u)) ** 0.7 + 0.008,
                      rays(4), sign=sign, sweep=sweep, cols=ef.ray_cols(4), rows=2)

    # tail
    n = ef.ray_cols(8)
    y_end = prof.y1
    main, minor = [], []
    for i in range(n):
        u = i / (n - 1)
        y = s.tail_y0 + (y_end - s.tail_y0) * u
        Lm = s.tail_main * math.sin(math.pi * min(1.0, u * 1.05) ** 0.75) ** 1.2 * (1 - 0.3 * u) + 0.004
        Ln = s.tail_minor * math.sin(math.pi * u) + 0.003
        if s.tail == "hypo":      # web above the down-turned axis
            main.append(((0.0, y, prof.top(y) - 0.005), (0.0, y + 0.55 * Lm, prof.top(y) + Lm)))
            minor.append(((0.0, y, prof.bot(y) + 0.004), (0.0, y + 0.3 * Ln, prof.bot(y) - Ln)))
        elif s.tail == "hetero":
            main.append(((0.0, y, prof.bot(y) + 0.005), (0.0, y + 0.55 * Lm, prof.bot(y) - Lm)))
            minor.append(((0.0, y, prof.top(y) - 0.004), (0.0, y + 0.3 * Ln, prof.top(y) + Ln)))
        else:
            main.append(((0.0, y, prof.top(y) - 0.005), (0.0, y + 0.55 * Lm, prof.top(y) + Lm)))
            minor.append(((0.0, y, prof.bot(y) + 0.005), (0.0, y + 0.55 * Lm, prof.bot(y) - Lm)))
    ef.caudal_web(mb, [a for a, b in main], [b for a, b in main], rays(8), rows=3)
    ef.caudal_web(mb, [a for a, b in minor], [b for a, b in minor], rays(8) if s.tail == "fork" else plain, rows=2)

    for sgn in (1, -1):
        for y0, y1, ang, L, out, down, back in s.paired:
            ef.paired_fin(mb, prof, sgn, y0, y1, ang, lambda u, L=L: L * (1 - u) ** 0.6 + 0.01, out, down, back,
                          rays(4), cols=ef.ray_cols(4), rows=2)
        if s.folds:
            y0, y1, w = s.folds
            ef.paired_fin(mb, prof, sgn, y0, y1, -0.75, lambda u, w=w: w * math.sin(math.pi * u) ** 0.6 + 0.004,
                          1.0, 0.5, 0.25, plain, cols=12, rows=2)
        for y, ang, d, r in s.spines:
            p = prof.point(y, ang)
            p.x *= sgn
            dd = Vector((d[0] * sgn, d[1], d[2]))
            ef.spine(mb, p, p + dd, r, s.fin_edge, s.ray)
        if s.gills:
            y0, y1, k, ang, r = s.gills
            for i in range(k):
                y = y0 + (y1 - y0) * i / max(1, k - 1)
                p = prof.point(y, ang, 0.002)
                p.x *= sgn
                mb.add(nh.uv_ellipsoid(tuple(p), (r * 0.5, r * 0.7, r), 6, 4), s.suture)

    if s.scutes:
        y0, y1, k, sz = s.scutes
        for i in range(k):
            y = y0 + (y1 - y0) * i / max(1, k - 1)
            b = Vector((0.0, y, prof.top(y) - 0.004))
            # anaspid ridge scales: hook-shaped, pointing back
            ef.spine(mb, b, b + Vector((0.0, sz * 1.1, sz * 0.8)), sz * 0.45, s.fin_edge, s.ray, sides=5)

    if s.rostrum > 0:
        tip = Vector((0.0, prof.y0 - s.rostrum, prof.CZ(prof.y0) - 0.01))
        base = Vector((0.0, prof.y0 + 0.05, prof.CZ(prof.y0 + 0.05)))
        mb.add(nh.tube([base, base.lerp(tip, 0.5), tip], [0.04, 0.025, 0.0], sides=8, scale_xy=(1.0, 0.7)), s.bone)

    if s.mouth:
        y0, y1, k = s.mouth
        ef.mouth_line(mb, prof, y0, y1, lambda y: prof.CZ(y) - prof.HB(y) * k, s.suture, grow=0.008)

    ef.surface_eye(mb, prof, s.eye_y, s.eye_a, s.eye_r, s.eye_look, iris=s.iris)

    obj = mb.to_object(s.name, roughness=0.45)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


PREVIEW = ef.PREVIEW
