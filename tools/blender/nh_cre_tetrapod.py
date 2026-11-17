"""
Parametric reptile/dinosaur/mammal builder for the Cretaceous batch (thin species scripts
such as velociraptor_mongoliensis.py describe a Spec and call build()).

The body is one loft along the midline (tail tip -> torso -> neck -> snout) from rows
(y, z, half width, half height); an optional lower jaw is a second loft hinged open.
Limbs are smooth tapered chains (mirrored to both sides, with an optional stride) ending
in toes and claws. Extra fused blobs/tubes (muscles, crests, frills, humps) can be listed.
Everything fused is remeshed into one surface, sculpted, decimated and repainted with the
species' paint(co, n); crisp details (eyes, teeth, claws, horns, feathers) go on top.
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

from mathutils import Vector, Matrix

import nh_model as nh
import nh_cre_core as cc


@dataclass
class Limb:
    joints: list                  # right-side (x > 0) points: hip/shoulder -> ... -> ball of foot
    radii: list                   # radius per joint
    toes: int = 3
    toe_len: float = 0.1
    toe_r: float = 0.02
    spread: float = 0.45
    claw: float = 0.03
    stride: float = 0.0           # lower joints shift +y on one side, -y on the other
    hallux: bool = False
    sickle: float = 0.0
    flat: Optional[tuple] = None  # flipper cross-section squash
    toe_dir: tuple = (0, -1, 0)
    ground: Optional[float] = None
    mirror: bool = True
    free: bool = False            # toes follow toe_dir in 3D (hands) instead of lying on the ground


@dataclass
class Spec:
    name: str
    axis: list
    paint: Callable
    limbs: list = field(default_factory=list)
    power: float = 2.1
    sides: int = 22
    steps: int = 3
    jaw: Optional[list] = None        # rows (y, z, hw, hh), mouth closed; rotated open about hinge
    hinge: tuple = (0.0, 0.0)         # (y, z)
    jaw_open: float = 0.0             # degrees
    blobs: list = field(default_factory=list)   # (center, radii, mirror) fused ellipsoids
    tubes: list = field(default_factory=list)   # (points, radii, mirror) fused tubes
    lofts: list = field(default_factory=list)   # extra bmesh factories () -> bm, fused
    crisp: Optional[Callable] = None  # crisp(mb, spec) adds eyes/teeth/horns...
    eye: Optional[tuple] = None       # (x, y, z, r) right eye
    eye_col: tuple = (0.85, 0.55, 0.12)
    eye_ring: Optional[tuple] = None
    claw_col: tuple = cc.CLAW
    voxel: float = 0.012
    smooth: int = 5
    max_tris: int = 12000
    jaw_tris: int = 1500
    disp: Optional[Callable] = None
    pivot: str = "ground"             # or "centre"
    roughness: float = 0.65


def _limb_shells(lb, sx):
    pts = []
    for i, p in enumerate(lb.joints):
        k = i / max(1, len(lb.joints) - 1)
        dy = lb.stride * k * (1 if sx > 0 else -1)
        pts.append(Vector((sx * p[0], p[1] + dy, p[2])))
    parts = [cc.limb(pts, lb.radii, sides=12, flat=lb.flat)]
    claws = []
    if lb.toes > 0:
        f, c = cc.foot(pts[-1], toes=lb.toes, length=lb.toe_len, r=lb.toe_r, spread=lb.spread,
                       claw=lb.claw, side=sx, hallux=lb.hallux, sickle=lb.sickle,
                       direction=lb.toe_dir, ground=lb.ground, free=lb.free)
        parts += f
        claws += c
    return parts, claws


def build(spec: Spec):
    parts = [cc.axis(spec.axis, sides=spec.sides, power=spec.power, steps=spec.steps)]
    claws = []
    for lb in spec.limbs:
        for sx in ((1, -1) if lb.mirror else (1,)):
            p, c = _limb_shells(lb, sx)
            parts += p
            claws += c
    for center, radii, mir in spec.blobs:
        for sx in ((1, -1) if mir else (1,)):
            parts.append(nh.ellipsoid((sx * center[0], center[1], center[2]), radii, subdivisions=3))
    for pts, radii, mir in spec.tubes:
        for sx in ((1, -1) if mir else (1,)):
            parts.append(cc.limb([(sx * p[0], p[1], p[2]) for p in pts], radii, sides=10))
    for fn in spec.lofts:
        parts.append(fn())
    body = cc.fuse(parts, voxel=spec.voxel, smooth=spec.smooth, max_tris=spec.max_tris, disp=spec.disp)

    mb = nh.MeshBuilder()
    mb.add(body, spec.paint)
    rot = None
    if spec.jaw:
        hy, hz = spec.hinge
        h = Vector((0, hy, hz))
        rot = Matrix.Translation(h) @ Matrix.Rotation(math.radians(spec.jaw_open), 4, "X") @ Matrix.Translation(-h)
        jaw = cc.fuse([cc.axis(spec.jaw, sides=16, power=2.3)], voxel=spec.voxel * 0.7, smooth=3,
                      max_tris=spec.jaw_tris, disp=spec.disp)
        mb.add(nh.transform(jaw, rot), spec.paint)
    spec._jaw_rot = rot
    for c in claws:
        mb.add(c, spec.claw_col, smooth=False)
    if spec.eye:
        x, y, z, r = spec.eye
        cc.eye(mb, (x, y, z), r, iris=spec.eye_col, ring=spec.eye_ring)
    if spec.crisp:
        spec.crisp(mb, spec)
    obj = mb.to_object(spec.name, roughness=spec.roughness)
    if spec.pivot == "ground":
        nh.ground_to_zero(obj)
    else:
        cc.centre(obj)
    cc.bounds_report(obj)
    return obj


GROUND_VIEWS = dict(ground=(0.33, 0.42, 0.24), views=((35, 22), (-90, 6)), size=640)
SWIM_VIEWS = dict(background=(0.05, 0.18, 0.24), views=((35, 22), (-90, 6), (20, 70)), size=640)
AIR_VIEWS = dict(background=(0.30, 0.42, 0.55), views=((35, 30), (0, 80), (-90, 5)), size=640)


def run(spec_fn, name, preview=None):
    nh.run(lambda: build(spec_fn()), name, **(preview or GROUND_VIEWS))
