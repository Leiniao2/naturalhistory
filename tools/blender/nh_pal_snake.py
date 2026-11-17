"""
Parametric giant snake for the Paleogene species in tools/blender/
(titanoboa_cerrejonensis.py, gigantophis_garstini.py).

A straight body along Y (the game bends it into the slither wave), slightly flattened
underneath, with a broad head, a pale belly and dorsal saddles / bands painted
procedurally, then crisp eyes and a forked tongue. Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.55, 0.42, 0.12)
PUPIL = (0.02, 0.02, 0.02)
TONGUE = (0.35, 0.08, 0.10)


@dataclass
class Spec:
    name: str
    length: float = 2.4
    girth: float = 0.07          # max body radius
    head_len: float = 0.12
    head_w: float = 0.055
    neck: float = 0.65           # neck radius fraction of the girth
    tail: float = 0.15           # tail fraction of the length
    base: tuple = (0.35, 0.33, 0.22)
    saddle: tuple = (0.15, 0.12, 0.08)
    belly: tuple = (0.75, 0.70, 0.55)
    saddles: int = 22
    saddle_w: float = 0.45       # 0-1 fraction of the period that is dark
    side_spots: float = 0.6
    head_col: tuple = None
    voxel: float = 0.014
    max_tris: int = 10000


def build(s):
    b = nh.MeshBuilder()
    n = 50
    y0 = -s.length / 2 + s.head_len * 0.6
    pts, rr = [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (s.length / 2 - y0) * t
        r = s.girth * (s.neck + (1 - s.neck) * nh.smoothstep(0.0, 0.25, t))
        r *= 1.0 - nh.smoothstep(1 - s.tail - 0.05, 1.0, t) * 0.92
        r = max(r, s.voxel * 1.2)
        pts.append((0, y, r * 0.88))
        rr.append(r)
    b.add(nh.tube(pts, rr, sides=16, scale_xy=(1.12, 0.88)), s.base)
    hy = -s.length / 2 + s.head_len * 0.5
    hz = rr[0] * 0.8
    b.add(nh.ellipsoid((0, hy, hz), (s.head_w, s.head_len * 0.55, s.head_w * 0.62)), s.base)
    b.add(nh.ellipsoid((0, hy + s.head_len * 0.35, hz), (s.head_w * 0.9, s.head_len * 0.35, s.head_w * 0.62)), s.base)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5)  # no decimation: keeps the bands crisp

    period = (s.length - s.head_len) / s.saddles

    def paint(co, nrm):
        c = s.base
        u = (co.y - (-s.length / 2 + s.head_len)) / period
        if co.y > -s.length / 2 + s.head_len * 1.1:
            ph = (u + 0.15 * noise.noise(co * 6)) % 1.0
            top = nh.smoothstep(0.1, 0.6, nrm.z)
            dark = 1.0 - nh.smoothstep(s.saddle_w - 0.06, s.saddle_w + 0.06, ph)
            c = nh.lerp(c, s.saddle, dark * top)
            side = nh.smoothstep(0.55, 0.15, abs(nrm.z)) * s.side_spots
            ph2 = (u + 0.5) % 1.0
            c = nh.lerp(c, s.saddle, side * (1.0 - nh.smoothstep(0.2, 0.3, abs(ph2 - 0.5))))
        elif s.head_col is not None:
            c = nh.lerp(c, s.head_col, nh.smoothstep(0.0, 0.5, nrm.z))
        c = nh.lerp(c, s.belly, nh.smoothstep(-0.2, -0.6, nrm.z))
        return c

    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for sx in (-1, 1):
        e = Vector((sx * s.head_w * 0.82, hy - s.head_len * 0.2, hz + s.head_w * 0.22))
        mb.add(nh.ellipsoid(tuple(e), (s.head_w * 0.16,) * 3, subdivisions=2), EYE)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * s.head_w * 0.1, 0, 0))), (s.head_w * 0.05, s.head_w * 0.1, s.head_w * 0.13),
                            subdivisions=1), PUPIL)
    tip = Vector((0, -s.length / 2 - s.head_len * 0.05, hz - s.head_w * 0.25))
    fork = tip + Vector((0, -s.head_len * 0.45, -s.head_w * 0.1))
    mb.add(nh.tube([tuple(tip + Vector((0, s.head_len * 0.1, 0))), tuple(fork)], [s.head_w * 0.05, s.head_w * 0.04], sides=5),
           TONGUE)
    for sx in (-1, 1):
        mb.add(nh.tube([tuple(fork), tuple(fork + Vector((sx * s.head_w * 0.18, -s.head_len * 0.15, 0)))],
                       [s.head_w * 0.035, 0.0], sides=5), TONGUE)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    return obj


def main(spec, ground=(0.30, 0.38, 0.24)):
    nh.run(lambda: build(spec), spec.name, ground=ground, views=((35, 30), (-90, 8), (0, 75)))
