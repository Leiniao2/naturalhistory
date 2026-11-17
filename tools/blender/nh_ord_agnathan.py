"""
Ordovician jawless vertebrates for the Ordovician batch: armoured "ostracoderms"
(sacabambaspis_janvieri.py, arandaspis_prionotolepis.py, astraspis_desiderata.py) and a
conodont animal (promissum_pulchrum.py). Built on nh_early_fish (Profile, loft, scale
shell, fins, eyes).

Fish are laid out in side view: length along Y (snout at -Y, facing -Y), height Z,
thickness X. Pivot at the body centre (Swim style).

  * Spec + build_ostracoderm(spec): a smooth head-armour loft (dorsal and ventral
    shields painted with tubercles - dots or star-shaped - and a dark suture between
    them), a row of gill openings / branchial plates along each side, eyes, an optional
    pair of pineal spots, then a trunk of rhombic scales and a tail of thin fin webs:
    a hypocercal tail (axis bends down, broad upper web) or the arandaspid tail with a
    long median lobe between upper and lower webs. No paired fins, no jaws.
  * build_conodont(spec): an eel-like soft body with painted V-shaped muscle blocks,
    large eyes at the front, and a ray-supported fin round the tail.
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh
import nh_fish as fish
import nh_early_fish as ef


@dataclass
class Spec:
    name: str
    rows: tuple                      # Profile rows (y, half_w, top_h, bot_h, centre_z)
    power: float = 2.2
    shield_end: float = -0.10        # back edge of the head armour
    suture_z: float = 0.0            # z (relative to centre) of the dorsal/ventral shield join
    trunk_end: float = 0.62          # where the scaled body ends (tail axis continues)
    tail: str = "hypocercal"         # or "arandaspid"
    tail_len: float = 0.40
    tail_h: float = 0.16
    eye_y: float = -0.68
    eye_a: float = 0.25              # body angle of the eye (0 = flank, pi/2 = top)
    eye_r: float = 0.035
    eye_look: tuple = (0.6, -0.6, 0.3)
    pineal: bool = True
    gills: int = 8
    gill_y: tuple = (-0.30, -0.14)
    gill_a: float = -0.15
    branchial_plates: bool = False   # many small plates instead of round openings
    tubercles: str = "dots"          # "dots", "stars", "ridges"
    shield: tuple = (0.55, 0.48, 0.38)
    shield_dark: tuple = (0.32, 0.27, 0.21)
    tubercle: tuple = (0.80, 0.74, 0.62)
    back: tuple = (0.30, 0.27, 0.22)
    flank: tuple = (0.45, 0.40, 0.32)
    belly: tuple = (0.70, 0.64, 0.52)
    fin: tuple = (0.42, 0.37, 0.30)
    fin_edge: tuple = (0.62, 0.56, 0.46)
    ray: tuple = (0.25, 0.21, 0.16)
    gill_col: tuple = (0.10, 0.07, 0.06)


def _star(co, scale, seed):
    """Star-shaped tubercle mask (Astraspis): distance to a jittered grid point, with
    6 rays."""
    p = Vector((co.y * scale, (co.z + co.x * 0.4) * scale, seed))
    cx, cy = math.floor(p.x) + 0.5, math.floor(p.y) + 0.5
    jx = 0.2 * noise.noise(Vector((cx, cy, seed)))
    dx, dy = p.x - cx - jx, p.y - cy
    r = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    lim = 0.18 + 0.12 * max(0.0, math.cos(a * 6))
    return 1.0 - nh.smoothstep(lim * 0.8, lim, r)


def _dots(co, scale, seed):
    p = Vector((co.y * scale, (co.z + co.x * 0.4) * scale, seed))
    cx, cy = math.floor(p.x) + 0.5, math.floor(p.y) + 0.5
    r = math.hypot(p.x - cx, p.y - cy)
    return 1.0 - nh.smoothstep(0.18, 0.26, r)


def _tubercles(mb, prof, s):
    """Crisp pale tubercles scattered over the head armour (stars: bigger, sparser)."""
    big = s.tubercles == "stars"
    step = 0.045 if big else 0.035
    r = 0.011 if big else 0.006
    y = prof.y0 + 0.05
    row = 0
    while y < s.shield_end - 0.02:
        n = 9 if big else 11
        for k in range(n):
            a = -0.9 + (math.pi / 2 + 0.9) * (k + 0.5 * (row % 2)) / n
            for sx in (1, -1):
                p = prof.point(y, a, 0.004)
                p.x *= sx
                if p.x == 0 and sx < 0:
                    continue
                j = 0.4 * noise.noise(p * 13.0)
                mb.add(nh.ellipsoid(tuple(p), (r * (1 + j), r * (1 + j), r * 0.6), subdivisions=1), s.tubercle)
        y += step
        row += 1


def build_ostracoderm(s):
    prof = ef.Profile(list(s.rows), power=s.power)
    mb = nh.MeshBuilder()

    def shield_col(co, n):
        u, v = prof.rel(co)
        rel_z = co.z - prof.CZ(co.y)
        c = nh.lerp(s.shield, s.shield_dark, 0.25 + 0.25 * ef.mottle(co, 7.0))
        if rel_z < s.suture_z:
            c = nh.lerp(c, s.belly, 0.45)
        if s.tubercles == "ridges":   # fine longitudinal ridges
            r = 0.5 + 0.5 * math.sin(math.atan2(co.z - prof.CZ(co.y), co.x) * 34.0)
            c = nh.lerp(c, s.tubercle, 0.45 * nh.smoothstep(0.6, 0.95, r))
        # dark suture between dorsal and ventral shields
        c = nh.lerp(c, s.shield_dark, 0.9 * math.exp(-((rel_z - s.suture_z) / 0.008) ** 2))
        # dark band where the shield ends
        c = nh.lerp(c, s.shield_dark, 0.8 * nh.smoothstep(s.shield_end - 0.03, s.shield_end, co.y))
        return c

    ef.head_shell(mb, prof, s.shield_end, shield_col, ny=26, na=32, grow=0.005)
    if s.tubercles in ("stars", "dots"):
        _tubercles(mb, prof, s)

    def scale_col(co, u, v):
        c = ef.countershade(v, s.back, s.flank, s.belly)
        # narrow, elongate scales: light ridged streaks
        r = 0.5 + 0.5 * math.sin(math.atan2(co.z - prof.CZ(co.y), co.x) * 18.0)
        return nh.lerp(c, s.fin_edge, 0.25 * r)

    ef.scale_shell(mb, prof, s.shield_end - 0.04, s.trunk_end, 34, 16, scale_col, lift=0.003,
                   shade=0.3, fade_y=(s.trunk_end - 0.2, s.trunk_end))

    # gill openings / branchial plates along each side
    for sx in (1, -1):
        n = s.gills
        for i in range(n):
            y = s.gill_y[0] + (s.gill_y[1] - s.gill_y[0]) * i / max(1, n - 1)
            p = prof.point(y, s.gill_a, 0.003)
            p.x *= sx
            if s.branchial_plates:
                mb.add(nh.uv_ellipsoid(tuple(p), (0.006, 0.016, 0.032), 8, 5),
                       lambda co, nn: nh.lerp(s.shield, s.shield_dark, 0.5))
            else:
                mb.add(nh.uv_ellipsoid(tuple(p), (0.006, 0.010, 0.012), 8, 5), s.gill_col)
    # eyes
    ef.surface_eye(mb, prof, s.eye_y, s.eye_a, s.eye_r, s.eye_look, sink=0.5,
                   iris=(0.55, 0.50, 0.32), rim=(0.15, 0.12, 0.10))
    if s.pineal:
        for sx in (1, -1):
            p = prof.point(s.eye_y + 0.04, math.pi / 2 - 0.12, 0.002)
            p.x *= sx
            mb.add(nh.uv_ellipsoid(tuple(p), (0.010, 0.010, 0.004), 6, 4), s.gill_col)
    # mouth: a small dark slit under the snout
    y0 = prof.y0
    mb.add(nh.uv_ellipsoid((0, y0 + 0.03, prof.CZ(y0 + 0.03) - prof.HB(y0 + 0.03) * 0.5),
                           (0.03, 0.012, 0.01), 8, 5), s.gill_col)

    _tail(mb, prof, s)
    return _finish(mb, s.name)


def _tail(mb, prof, s):
    rays = ef.ray_color(s.fin, s.ray, s.fin_edge, 8)
    y_start = s.trunk_end - 0.10
    n = ef.ray_cols(8)
    if s.tail == "hypocercal":
        axis_t, edge_t, axis_b, edge_b = [], [], [], []
        for i in range(n):
            u = i / (n - 1)
            y = y_start + s.tail_len * u
            zc = prof.CZ(min(y, prof.y1)) - 0.10 * u * u
            ht = s.tail_h * math.sin(math.pi * min(1.0, u * 1.02) ** 0.7) * (1 - 0.2 * u) + 0.004
            hb = s.tail_h * 0.45 * math.sin(math.pi * min(1.0, u * 1.02) ** 0.9) + 0.004
            axis_t.append((0, y, zc))
            edge_t.append((0, y + 0.35 * ht, zc + ht))
            axis_b.append((0, y, zc))
            edge_b.append((0, y + 0.2 * hb, zc - hb))
        ef.caudal_web(mb, axis_t, edge_t, rays, rows=3)
        ef.caudal_web(mb, axis_b, edge_b, rays, rows=2)
    else:
        # arandaspid tail: long median lobe (axis) between upper and lower webs
        axis, et, eb = [], [], []
        for i in range(n):
            u = i / (n - 1)
            y = y_start + s.tail_len * u
            zc = prof.CZ(min(y, prof.y1))
            h = s.tail_h * math.sin(math.pi * min(1.0, u * 1.15) ** 0.8) * (1 - 0.3 * u) + 0.003
            axis.append((0, y, zc))
            et.append((0, y + 0.5 * h, zc + h))
            eb.append((0, y + 0.5 * h, zc - h))
        ef.caudal_web(mb, axis, et, rays, rows=3)
        ef.caudal_web(mb, axis, eb, rays, rows=3)
        # median lobe: a slender scaled tube running out past the webs
        pts = [Vector((0, y_start + s.tail_len * t, prof.CZ(min(y_start + s.tail_len * t, prof.y1))))
               for t in (0.0, 0.4, 0.8, 1.15)]
        mb.add(nh.tube(pts, [0.018, 0.014, 0.008, 0.0], sides=6, scale_xy=(0.7, 1.0)), s.flank)


def _finish(mb, name):
    obj = mb.to_object(name, roughness=0.5)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


# ---------------------------------------------------------------- conodont

@dataclass
class ConodontSpec:
    name: str
    length: float = 1.8
    depth: float = 0.07              # half-height of the trunk
    width: float = 0.035
    eye_r: float = 0.045
    body: tuple = (0.62, 0.52, 0.48)
    body_dark: tuple = (0.38, 0.30, 0.28)
    belly: tuple = (0.80, 0.72, 0.66)
    fin: tuple = (0.70, 0.62, 0.56)
    ray: tuple = (0.45, 0.36, 0.32)
    eye_rim: tuple = (0.10, 0.08, 0.08)


def build_conodont(s):
    L = s.length
    y0, y1 = -L / 2, L / 2
    rows = [
        (y0, 0.006, 0.006, 0.006, 0.0),
        (y0 + 0.04, s.width * 0.9, s.depth * 0.6, s.depth * 0.6, 0.0),
        (y0 + 0.12, s.width * 1.1, s.depth * 0.85, s.depth * 0.8, 0.0),
        (y0 + 0.3, s.width, s.depth, s.depth, 0.0),
        (y1 - 0.45, s.width * 0.9, s.depth * 0.95, s.depth * 0.95, 0.0),
        (y1 - 0.12, s.width * 0.45, s.depth * 0.5, s.depth * 0.5, 0.0),
        (y1, 0.004, 0.004, 0.004, 0.0),
    ]
    prof = ef.Profile(rows, power=2.0)
    mb = nh.MeshBuilder()

    def col(co, n):
        u, v = prof.rel(co)
        c = ef.countershade(v, s.body_dark, s.body, s.belly)
        # V-shaped (chevron) muscle blocks pointing forward
        phase = (co.y - 0.9 * abs(co.z) + 0.2) * 34.0
        k = 0.5 + 0.5 * math.cos(phase * math.pi)
        c = nh.lerp(c, s.body_dark, 0.35 * nh.smoothstep(0.85, 1.0, k) * nh.smoothstep(y0 + 0.14, y0 + 0.2, co.y))
        # notochord line
        c = nh.lerp(c, s.body_dark, 0.3 * math.exp(-(v / 0.12) ** 2) * nh.smoothstep(y0 + 0.14, y0 + 0.2, co.y))
        return c

    mb.add(ef.loft(prof, y0, y1, 60, 18, cap0=True, cap1=True), col)
    # large eyes at the front (Promissum preserves the eye muscles and sclerotic cartilages)
    for sx in (1, -1):
        p = prof.point(y0 + 0.07, 0.15, 0.0)
        p.x *= sx
        ef.eye(mb, p + Vector((sx * 0.005, 0, 0)), (sx * 0.8, -0.4, 0.2), s.eye_r,
               iris=(0.30, 0.26, 0.22), pupil=(0.02, 0.02, 0.03), rim=s.eye_rim)
    # tail fin with rays, above and below the last third
    rays = ef.ray_color(s.fin, s.ray, s.fin, 14, ray_amount=0.6, edge_amount=0.2)
    n = ef.ray_cols(14)
    for sign in (1, -1):
        base, edge = [], []
        for i in range(n):
            u = i / (n - 1)
            y = y1 - 0.62 + 0.62 * u
            h = (0.09 if sign > 0 else 0.07) * math.sin(math.pi * min(1.0, 0.1 + u)) ** 0.7 + 0.005
            z = prof.top(y) if sign > 0 else prof.bot(y)
            base.append((0, y, z - sign * 0.004))
            edge.append((0, y + h * 0.4, z + sign * h))
        fish.fin(mb, base, edge, rays, rows=2, th0=0.008, th1=0.003, normal=(1, 0, 0))
    return _finish(mb, s.name)


PREVIEW = dict(background=(0.04, 0.12, 0.15), views=((35, 25), (-90, 4), (0, 80)))
