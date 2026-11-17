"""
Parametric four-legged dinosaur for the Jurassic batch: sauropods (diplodocus_carnegii.py,
mamenchisaurus_hochuanensis.py) and thyreophorans (stegosaurus_stenops.py,
kentrosaurus_aethiopicus.py, scelidosaurus_harrisonii.py).

One loft runs from the tail tip over the hips and shoulders up the neck; the head is
its own loft on the end of the neck; pillar legs with padded feet, shoulder and thigh
masses are fused with it into one surface. Plates, spikes, scutes, eyes and nails are
crisp details added by the species' extras hook. Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass
from typing import Callable, Optional

from mathutils import Vector, Matrix

import nh_model as nh
import nh_jur_kit as kit


@dataclass
class Spec:
    name: str
    paint: Callable
    hip_h: float = 1.0            # hip joint height
    shoulder_h: float = 0.9       # shoulder joint height
    body_len: float = 1.0         # hip -> shoulder
    body_hw: float = 0.3
    body_hh: float = 0.32
    belly_drop: float = 0.05
    tail_len: float = 2.0
    tail_droop: float = 0.3       # how far the tail tip sinks below the hips
    tail_r: float = 0.8           # tail base radius as a fraction of the body
    tail_exp: float = 1.0         # >1 = whip-like taper
    neck: tuple = ((0.0, -0.5, 0.15), (0.0, -1.0, 0.3), (0.0, -1.5, 0.4))  # neck path offsets from the shoulder top
    neck_r: tuple = (0.18, 0.12, 0.08)
    head_len: float = 0.3
    head_h: float = 0.1
    head_w: float = 0.07
    head_pitch: float = 10.0      # degrees the head is tipped down from the line of the neck end
    head_power: float = 2.3
    snout_taper: float = 0.4
    thigh_r: float = 0.14
    shin_r: float = 0.09
    arm_r: float = 0.11
    forearm_r: float = 0.08
    foot_r: float = 0.1
    hand_r: float = 0.085
    hind_nails: int = 3
    front_nails: int = 1
    stride: float = 0.12
    knee_bend: float = 0.05
    elbow_bend: float = 0.04
    eye_r: float = 0.018
    eye_color: tuple = kit.EYE
    claw_color: tuple = kit.CLAW
    beak: Optional[tuple] = None  # colour of a horny beak at the snout tip
    voxel: float = 0.016
    max_tris: int = 16000
    extras: Optional[Callable] = None   # extras(ctx) -> (fused [(bm, col)], crisp [(bm, col)])
    pebble: float = 0.002


class Ctx:
    def __init__(self, spec, spine, head_m):
        self.spec, self.spine, self.head_m = spec, spine, head_m

    def head(self, t, x=0.0, z=0.0):
        """Head-local point: t 0 (back of skull) .. 1 (snout), z relative to the head axis."""
        return self.head_m @ Vector((x, -t * self.spec.head_len, z))

    def head_dir(self, v):
        return self.head_m.to_3x3() @ Vector(v)


def build(sp):
    hw, hh = sp.body_hw, sp.body_hh
    hip_c = Vector((0.0, 0.0, sp.hip_h + hh * 0.25))
    sh_c = Vector((0.0, -sp.body_len, sp.shoulder_h + hh * 0.3))
    rows = []
    for f in (1.0, 0.8, 0.6, 0.4, 0.22, 0.1):
        r = (1.0 - f) ** sp.tail_exp
        y = sp.tail_len * f
        z = hip_c.z - sp.tail_droop * f ** 1.6
        rows.append((0.0, y, z, 0.0 if f == 1.0 else hw * sp.tail_r * r + 0.008, 0.0 if f == 1.0 else hh * sp.tail_r * r + 0.008))
    mid = hip_c.lerp(sh_c, 0.5)
    rows += [
        (0.0, hip_c.y, hip_c.z, hw * 0.92, hh * 0.92),
        (0.0, mid.y, mid.z - sp.belly_drop, hw, hh),
        (0.0, sh_c.y, sh_c.z, hw * 0.85, hh * 0.88),
    ]
    neck_pts = [sh_c + Vector(o) for o in sp.neck]
    for p, r in zip(neck_pts, sp.neck_r):
        rows.append((p.x, p.y, p.z, r, r * 1.08))
    spine = kit.Spine(rows, steps=4)

    end = neck_pts[-1]
    d = (neck_pts[-1] - neck_pts[-2]).normalized()
    yaw_pitch = math.atan2(d.z, -d.y)  # angle of the neck end above horizontal
    elev = yaw_pitch - math.radians(sp.head_pitch)  # head axis angle above horizontal
    hdir = Vector((0, -math.cos(elev), math.sin(elev)))
    head_m = Matrix.Translation(end - hdir * sp.head_len * 0.12) @ Matrix.Rotation(-elev, 4, "X")
    ctx = Ctx(sp, spine, head_m)

    secs = []
    for t in (-0.1, 0.0, 0.2, 0.45, 0.7, 0.88, 0.97, 1.0):
        tt = max(0.0, t)
        h = sp.head_h * (1.0 - sp.snout_taper * tt)
        w = sp.head_w * (1.0 - 0.35 * tt)
        if t >= 0.97:
            k = 0.75 if t < 1.0 else 0.0
            h, w = h * k, w * k
        secs.append(((0.0, -t * sp.head_len, h * 0.15 * (1 - tt)), w, h))
    head = nh.transform(kit.loft(secs, sides=16, power=sp.head_power), head_m)
    fused = [(spine.mesh(sides=20), (0.5,) * 3), (head, (0.5,) * 3)]

    crisp = []
    for sx, st in ((1, 1.0), (-1, -1.0)):
        for front in (False, True):
            j = sh_c if front else hip_c
            top_h = sp.shoulder_h if front else sp.hip_h
            r0 = sp.arm_r if front else sp.thigh_r
            r1 = sp.forearm_r if front else sp.shin_r
            rf = sp.hand_r if front else sp.foot_r
            s = (-st if front else st) * sp.stride
            x = sx * hw * (0.72 if front else 0.68)
            top = Vector((x, j.y, top_h))
            bend = sp.elbow_bend if front else -sp.knee_bend
            kn = Vector((x * 1.04, j.y + s * 0.45 + bend, top_h * 0.5))
            ft = Vector((x, j.y + s, rf * 0.9))
            pts = [top + Vector((0, 0, r0 * 0.8)), top, top.lerp(kn, 0.5), kn, kn.lerp(ft, 0.5), ft]
            rad = [r0 * 0.8, r0, r0 * 0.85, r1 * 1.05, r1 * 0.95, rf * 0.9]
            fused.append((kit.limb(pts, rad, sides=12), (0.5,) * 3))
            fused.append((nh.ellipsoid(top.lerp(kn, 0.25), (r0 * 1.15, r0 * 1.3, r0 * 1.6), subdivisions=2), (0.5,) * 3))
            parts, nails = kit.pillar_foot(ft, rf, sx, nails=sp.front_nails if front else sp.hind_nails)
            fused += [(p, (0.5,) * 3) for p in parts]
            crisp += [(kit.cone(b, t, r, sides=5), sp.claw_color) for b, t, r in nails]

    if sp.extras:
        ef, ec = sp.extras(ctx)
        fused += ef
        crisp += ec
    body = kit.fuse_parts(fused, sp.voxel, sp.max_tris)
    if sp.pebble:
        kit.pebble(body, sp.pebble)

    mb = nh.MeshBuilder()
    mb.add(body, sp.paint)
    # eyes on the sides of the head, nostrils
    eh = sp.head_h * 0.3
    for sx in (1, -1):
        e = ctx.head(0.28, x=sx * sp.head_w * 0.82, z=eh)
        kit.eyes(mb, e, sp.eye_r, sx_list=(sx,), iris=sp.eye_color)
    if sp.beak:
        mb.add(nh.transform(kit.loft([((0, -0.86 * sp.head_len, 0.0), sp.head_w * 0.62, sp.head_h * 0.5),
                                      ((0, -0.96 * sp.head_len, -0.004), sp.head_w * 0.5, sp.head_h * 0.38),
                                      ((0, -1.03 * sp.head_len, -0.01), 0.0, 0.0)], sides=12), head_m), sp.beak)
    for bm, col in crisp:
        mb.add(bm, col, smooth=False)
    return kit.finish(mb, sp.name)


PREVIEW = dict(ground=(0.33, 0.42, 0.24), views=((35, 22), (-90, 6), (25, 65)))
