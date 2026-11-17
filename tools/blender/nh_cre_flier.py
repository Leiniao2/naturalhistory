"""
Gliding/soaring fliers for the Cretaceous batch (pterosaurs and early birds).

A Flier holds a midline body loft (rows (y, z, half width, half height), tail -> beak), wing
outlines (leading and trailing edge polylines for the right wing, mirrored), optional fused
blobs/tubes (shoulders, legs, crests) and crisp extras. Wings are spread along X so the map's
flap shader (wingRoot) can beat them. Pivot at the body centre, faces -Y.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from mathutils import Vector

import nh_model as nh
import nh_cre_core as cc
import nh_cre_tetrapod as tp


@dataclass
class Wing:
    lead: list
    trail: list
    color: Callable
    thickness: float = 0.014
    nv: int = 8
    billow: float = 0.0
    n: int = 24          # resampled points along the span
    bone: Optional[tuple] = None   # (color, radius) bony leading edge tube (pterosaurs)


@dataclass
class Flier:
    name: str
    axis: list
    paint: Callable
    wings: list = field(default_factory=list)
    blobs: list = field(default_factory=list)
    tubes: list = field(default_factory=list)
    crisp: Optional[Callable] = None
    eye: Optional[tuple] = None
    eye_col: tuple = (0.05, 0.04, 0.03)
    eye_ring: Optional[tuple] = None
    voxel: float = 0.01
    max_tris: int = 9000
    disp: Optional[Callable] = None
    power: float = 2.0


def add_wing(mb, w: Wing, sx):
    lead = cc.polyline([(sx * p[0], p[1], p[2]) for p in w.lead], w.n)
    trail = cc.polyline([(sx * p[0], p[1], p[2]) for p in w.trail], w.n)
    mb.add(cc.membrane(lead, trail, nv=w.nv, thickness=w.thickness, billow=w.billow), w.color)
    if w.bone:
        col, r = w.bone
        pts = [(sx * p[0], p[1], p[2]) for p in w.lead]
        pts = cc.polyline(pts, 16)
        radii = [r * (1 - 0.8 * i / 15) for i in range(16)]
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=7), col)


def to_spec(f: Flier) -> tp.Spec:
    user = f.crisp

    def crisp(mb, sp):
        for w in f.wings:
            for sx in (1, -1):
                add_wing(mb, w, sx)
        if user:
            user(mb, f)
    return tp.Spec(name=f.name, axis=f.axis, paint=f.paint, power=f.power, blobs=list(f.blobs),
                   tubes=list(f.tubes), crisp=crisp, eye=f.eye, eye_col=f.eye_col, eye_ring=f.eye_ring,
                   voxel=f.voxel, max_tris=f.max_tris, disp=f.disp, pivot="centre")


def run(make, name, preview=None):
    nh.run(lambda: tp.build(to_spec(make())), name, **(preview or tp.AIR_VIEWS))
