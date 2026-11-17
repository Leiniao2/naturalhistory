"""
Shared toothed whale for the Neogene batch (tag "neo"): Livyatan (a raptorial
sperm whale with huge teeth in both jaws) and Odobenocetops (a small,
walrus-faced whale with backward-pointing tusks).

A spindle-shaped body tube (snout at -Y), horizontal tail flukes, pectoral
flippers, optional dorsal hump, an open mouth with conical teeth, tusks.
Swimmer: pivot at the body centre. Faces -Y.
"""

import math
from dataclasses import dataclass, field

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.05, 0.04, 0.04)
TOOTH = (0.90, 0.86, 0.74)
MOUTH = (0.45, 0.22, 0.22)


@dataclass
class Spec:
    name: str
    length: float = 2.0
    radius: float = 0.22
    head_blunt: float = 0.7      # 1 = square sperm-whale head, 0 = pointed
    head_frac: float = 0.30      # share of the length taken by the head
    jaw_open: float = 0.0        # gape angle-ish (0 = closed)
    teeth: int = 0               # per side, per jaw
    tooth_len: float = 0.05
    tusks: list = field(default_factory=list)   # dicts: s, len, r, dir, bend
    flipper: float = 0.25
    fluke: float = 0.55          # fluke span
    dorsal: float = 0.05
    back: tuple = (0.25, 0.26, 0.28)
    belly: tuple = (0.70, 0.70, 0.68)
    scars: float = 0.0
    eye_fwd: float = 0.0         # eyes on the top front of the head (Odobenocetops)
    voxel: float = 0.02
    max_tris: int = 9000


def radius_at(s, t):
    """Body radius along t (0 = snout, 1 = fluke root)."""
    if t < s.head_frac:
        u = t / s.head_frac
        return s.radius * (s.head_blunt + (1 - s.head_blunt) * math.sin(u * math.pi / 2)) * (0.85 + 0.15 * u)
    u = (t - s.head_frac) / (1 - s.head_frac)
    return s.radius * (1.0 - 0.85 * u ** 1.6)


def build(s):
    b = nh.MeshBuilder()
    L = s.length
    y0 = -L / 2
    n = 14
    pts = [(0, y0 + L * i / n, 0) for i in range(n + 1)]
    rad = [max(radius_at(s, i / n), 0.02) for i in range(n + 1)]
    rad[0] *= 0.8
    gap = s.jaw_open * s.radius
    b.add(nh.tube(pts, rad, sides=18, scale_xy=(0.9, 1.0)), s.back)
    b.add(nh.ellipsoid((0, y0 + L * 0.015, 0), (rad[1] * 0.85, L * 0.05, rad[1] * 0.85)), s.back)
    # lower jaw
    if s.jaw_open > 0:
        jl = L * s.head_frac * 0.95
        a = s.jaw_open
        base = Vector((0, y0 + jl, -s.radius * 0.45))
        tip = Vector((0, y0 + L * 0.03, -s.radius * 0.55 - gap))
        b.add(nh.tube([tuple(base), tuple(base.lerp(tip, 0.6)), tuple(tip)],
                      [s.radius * 0.45, s.radius * 0.32, s.radius * 0.22], sides=12, scale_xy=(1.4, 0.8)), s.belly)
    # flippers
    for sx in (-1, 1):
        r0 = Vector((sx * s.radius * 0.8, y0 + L * (s.head_frac + 0.05), -s.radius * 0.5))
        b.add(nh.tube([tuple(r0), tuple(r0 + Vector((sx * s.flipper * 0.8, s.flipper * 0.5, -s.flipper * 0.35)))],
                      [s.radius * 0.18, s.radius * 0.06], sides=8, scale_xy=(1.0, 0.35)), s.back)
    if s.dorsal > 0:
        b.add(nh.ellipsoid((0, y0 + L * 0.68, rad[int(n * 0.68)] * 0.9), (s.radius * 0.12, L * 0.07, s.dorsal)), s.back)
    # flukes
    fy = y0 + L
    b.add(nh.flat_panel([(0, fy - L * 0.04, 0), (s.fluke * 0.5, fy + L * 0.05, 0), (s.fluke * 0.45, fy + L * 0.10, 0),
                         (0.02, fy + L * 0.06, 0), (-0.02, fy + L * 0.06, 0), (-s.fluke * 0.45, fy + L * 0.10, 0),
                         (-s.fluke * 0.5, fy + L * 0.05, 0)], thickness=0.04), s.back)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            p, nn = l.vert.co, l.vert.normal
            c = nh.lerp(s.back, s.belly, nh.smoothstep(-0.1, -0.6, nn.z))
            c = nh.lerp(c, nh.lerp(c, (1, 1, 1), 0.3), s.scars * max(0.0, noise.noise(Vector((p.x * 40, p.y * 6, p.z * 40)))))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    # mouth lining + teeth
    if s.teeth:
        jl = L * s.head_frac * 0.9
        for i in range(s.teeth):
            t = i / max(1, s.teeth - 1)
            y = y0 + L * 0.05 + jl * 0.8 * t
            for sx in (-1, 1):
                w = s.radius * (0.55 - 0.15 * (1 - t))
                zu = -s.radius * 0.30
                zl = -s.radius * 0.45 - gap * (1 - t) * 0.9
                mb.add(nh.tube([(sx * w, y, zu + 0.01), (sx * w, y, zu - s.tooth_len)], [s.tooth_len * 0.28, 0.0],
                               sides=6), TOOTH)
                mb.add(nh.tube([(sx * w * 0.9, y, zl - 0.01), (sx * w * 0.9, y, zl + s.tooth_len)],
                               [s.tooth_len * 0.28, 0.0], sides=6), TOOTH)
    for t in s.tusks:
        root = Vector((t["s"] * s.radius, y0 + L * t.get("y", 0.06), -s.radius * t.get("z", 0.35)))
        d = Vector(t["dir"]).normalized()
        pts, rr = [], []
        p = root.copy()
        for i in range(8):
            pts.append(tuple(p))
            rr.append(t["r"] * (1 - i / 7) + 0.004)
            d = (d + Vector(t.get("bend", (0, 0, 0))) / 7).normalized()
            p = p + d * t["len"] / 7
        mb.add(nh.tube(pts, rr, sides=8), TOOTH)
    for sx in (-1, 1):
        if s.eye_fwd:
            e = (sx * s.radius * 0.45, y0 + L * 0.07, s.radius * 0.55)
        else:
            e = (sx * s.radius * 0.82, y0 + L * s.head_frac * 0.85, -s.radius * 0.15)
        mb.add(nh.ellipsoid(e, (s.radius * 0.07,) * 3, subdivisions=2), EYE)
    return mb.to_object(s.name)


def main(spec):
    nh.run(lambda: build(spec), spec.name, views=((40, 20), (-90, 5), (20, -25)))
