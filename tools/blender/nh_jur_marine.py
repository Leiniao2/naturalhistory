"""
Parametric marine reptile for the Jurassic batch (cryptoclidus_eurymerus.py,
metriorhynchus_superciliosus.py, dakosaurus_maximus.py).

The body is one Spine loft (tail tip -> body -> neck -> snout) fused with flipper roots;
flippers are thin subdivided hydrofoil panels, the tail fin a vertical blade; teeth and
eyes are crisp details. Laid out horizontally, faces -Y, pivot at the body centre (Swim).
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

import bmesh
from mathutils import Vector, Matrix

import nh_model as nh
import nh_jur_kit as kit


@dataclass
class Spec:
    name: str
    rows: list                        # spine rings (x, y, z, half width, half height), tail tip -> snout tip
    paint: Callable
    flippers: list = field(default_factory=list)  # (root (x, y, z), length, chord, sweep deg, droop deg), right side
    flipper_color: Optional[Callable] = None
    flipper_thick: float = 0.012
    tail_fin: Optional[list] = None   # outline [(y, z), ...] of a vertical tail fin
    tail_fin_color: Optional[Callable] = None
    teeth: list = field(default_factory=list)     # (y0, y1, count, x, z_upper, z_lower, length)
    eye: tuple = (0.04, -0.6, 0.04)
    eye_r: float = 0.014
    eye_color: tuple = kit.EYE
    jaw_line: Optional[tuple] = None  # (y0, y1, z, x) dark mouth line
    voxel: float = 0.01
    max_tris: int = 12000
    extras: Optional[Callable] = None


def flipper(root, length, chord, sweep, droop, sx, thick):
    """Tapered, rounded hydrofoil from root, swept back by sweep deg, tipped down by droop deg."""
    out = []
    n = 9
    for i in range(n + 1):  # leading edge root -> tip
        t = i / n
        out.append((length * t, -chord * 0.5 * (1 - t ** 2.2) + chord * 0.1 * t))
    for i in range(n, -1, -1):  # trailing edge tip -> root
        t = i / n
        out.append((length * t, chord * 0.5 * (1 - t ** 1.4) * (1 + 0.3 * math.sin(t * math.pi))))
    out = out[:n + 1] + out[n + 2:]
    pts = [(x, y, 0.0) for x, y in out]
    bm = nh.flat_panel(pts, thickness=thick)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    m = Matrix.Rotation(math.radians(-sweep), 4, "Z") @ Matrix.Rotation(math.radians(-droop), 4, "Y")
    if sx < 0:
        m = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ m
    nh.transform(bm, m)
    nh.transform(bm, Matrix.Translation(Vector((sx * root[0], root[1], root[2]))))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build(sp):
    spine = kit.Spine(sp.rows, steps=4)
    fused = [(spine.mesh(sides=18), (0.5,) * 3)]
    crisp = []
    for root, ln, ch, sw, dr in sp.flippers:
        for sx in (1, -1):
            fused.append((nh.ellipsoid((sx * root[0] * 0.8, root[1] + ch * 0.05, root[2]), (ch * 0.35, ch * 0.45, ch * 0.18), subdivisions=2), (0.5,) * 3))
    if sp.extras:
        ef, ec = sp.extras(spine)
        fused += ef
        crisp += ec
    body = kit.fuse_parts(fused, sp.voxel, sp.max_tris, smooth=4)
    kit.pebble(body, 0.001)
    mb = nh.MeshBuilder()
    mb.add(body, sp.paint)
    fc = sp.flipper_color or sp.paint
    for root, ln, ch, sw, dr in sp.flippers:
        for sx in (1, -1):
            mb.add(flipper(root, ln, ch, sw, dr, sx, sp.flipper_thick), fc, smooth=True)
    if sp.tail_fin:
        bm = kit.blade(sp.tail_fin, sp.flipper_thick)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        mb.add(bm, sp.tail_fin_color or sp.paint, smooth=False)
    for y0, y1, cnt, x, zu, zl, ln in sp.teeth:
        for i in range(cnt):
            t = i / max(1, cnt - 1)
            y = y0 + (y1 - y0) * t
            xx = x(t) if callable(x) else x
            for sx in (1, -1):
                b = Vector((sx * xx, y, zu))
                kit.teeth(mb, [(b, b + Vector((sx * ln * 0.25, -ln * 0.1, -ln)), ln * 0.25)])
                if zl is not None:
                    b = Vector((sx * xx * 0.95, y + 0.006, zl))
                    kit.teeth(mb, [(b, b + Vector((sx * ln * 0.25, -ln * 0.1, ln)), ln * 0.25)])
    if sp.jaw_line:
        y0, y1, z, x = sp.jaw_line
        for sx in (1, -1):
            mb.add(nh.tube([(sx * x, y0, z), (sx * x * 0.5, y1, z)], [0.004, 0.002], sides=5), kit.MOUTH)
    kit.eyes(mb, sp.eye, sp.eye_r, iris=sp.eye_color)
    for bm, col in crisp:
        mb.add(bm, col, smooth=False)
    return kit.finish(mb, sp.name, pivot="center")


PREVIEW = dict(background=(0.04, 0.10, 0.13), views=((35, 25), (-90, 4), (30, 60)))
