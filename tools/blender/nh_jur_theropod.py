"""
Parametric bipedal theropod for the Jurassic batch (allosaurus_fragilis.py,
ceratosaurus_nasicornis.py, dilophosaurus_wetherilli.py, compsognathus_longipes.py,
guanlong_wucaii.py ...).

A Spec describes proportions (hip height 1 = the unit), colours and a hook for the
species' own head ornaments. The body is one loft from the tail tip through the hips
and chest up the S-curved neck; skull, legs, arms and muscle masses are overlapping
parts fused into one surface; the lower jaw is its own piece (mouth slightly open);
teeth, eyes and claws are crisp details. Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

from mathutils import Vector, Matrix

import nh_model as nh
import nh_jur_kit as kit


@dataclass
class Spec:
    name: str
    paint: Callable                    # kit.paint(...) colour function for the body
    body_len: float = 0.62             # hips -> chest
    body_hw: float = 0.17              # torso half width
    body_hh: float = 0.22              # torso half height
    tail_len: float = 1.45
    tail_lift: float = 0.0             # tail tip height above the hips
    neck_len: float = 0.42
    neck_angle: float = 45.0           # degrees above horizontal
    neck_r: float = 0.085
    head_len: float = 0.46
    head_h: float = 0.19               # skull depth above the mouth line (at the back)
    head_w: float = 0.10
    snout_taper: float = 0.55          # how much the skull shallows toward the snout
    head_pitch: float = -8.0           # degrees, nose down
    jaw_h: float = 0.07
    jaw_open: float = 12.0
    teeth: int = 10
    tooth_len: float = 0.035
    thigh_r: float = 0.15
    shin_r: float = 0.075
    meta_r: float = 0.045
    toe_len: float = 0.17
    stride: float = 0.12
    arm_len: float = 0.34
    arm_r: float = 0.045
    fingers: int = 3
    finger_len: float = 0.09
    claw_color: tuple = kit.CLAW
    eye_color: tuple = kit.EYE
    eye_r: float = 0.022
    mouth: tuple = kit.MOUTH
    tooth_color: tuple = kit.TOOTH
    voxel: float = 0.012
    max_tris: int = 14000
    neck_frill: float = 0.0            # extra throat depth
    extras: Optional[Callable] = None  # extras(ctx) -> (fused [(bm, col)], crisp [(bm, col)])
    detail: Optional[Callable] = None  # detail(mb, ctx): add more crisp parts
    pebble: float = 0.0015


class Ctx:
    """What the extras hooks get: the spine and a head-local -> world mapping."""

    def __init__(self, spec, spine, head_m, head_rows):
        self.spec, self.spine, self.head_m, self.head_rows = spec, spine, head_m, head_rows

    def head(self, t, x=0.0, z=None, frac=None):
        """World point on the head: t 0 (back of skull) .. 1 (snout tip); z above the mouth
        line in model units, or frac of the skull depth there (1 = skull top)."""
        top, bot, w = self.head_row(t)
        if z is None:
            z = bot + (top - bot) * (1.0 if frac is None else frac)
        return self.head_m @ Vector((x, -t * self.spec.head_len, z))

    def head_row(self, t):
        rows = self.head_rows
        for (t0, a0, b0, w0), (t1, a1, b1, w1) in zip(rows, rows[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / max(1e-9, t1 - t0)
                return a0 + (a1 - a0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
        return rows[-1][1], rows[-1][2], rows[-1][3]

    def head_dir(self, v):
        """Head-local direction/offset -> world (not normalised)."""
        return self.head_m.to_3x3() @ Vector(v)


def skull_rows(sp):
    """(t, top z, bottom z, half width) of the skull in head-local coordinates (mouth line z = 0)."""
    rows = []
    for t in (-0.12, 0.0, 0.12, 0.25, 0.4, 0.55, 0.7, 0.82, 0.92, 1.0):
        tt = max(0.0, t)
        depth = sp.head_h * (1.0 - sp.snout_taper * tt ** 1.1)
        if t > 0.9:
            depth *= 1.0 - (t - 0.9) * 3.5
        w = sp.head_w * (1.0 - 0.45 * tt ** 1.3)
        if t < 0.0:
            w *= 0.85
            depth *= 0.9
        rows.append((t, depth, -0.012, w))
    return rows


def jaw_rows(sp):
    rows = []
    for t in (0.0, 0.15, 0.35, 0.55, 0.75, 0.9, 0.98):
        d = sp.jaw_h * (1.0 - 0.5 * t)
        w = sp.head_w * 0.92 * (1.0 - 0.45 * t ** 1.3)
        rows.append((t, 0.0, -d, w))
    return rows


def head_loft(sp, rows, power):
    secs = [((0.0, -t * sp.head_len, (a + b) * 0.5), w, (a - b) * 0.5) for t, a, b, w in rows]
    return kit.loft(secs, sides=18, power=power)


def build(sp):
    H = 1.0
    hw, hh = sp.body_hw, sp.body_hh
    # --- spine: tail tip -> hips -> chest -> neck
    rows = []
    for f in (1.0, 0.82, 0.62, 0.42, 0.24, 0.1):
        r = (1.0 - f) ** 0.85
        rows.append((0.0, sp.tail_len * f, H + sp.tail_lift * f ** 1.4 + hh * 0.15 * (1 - f),
                     0.0 if f == 1.0 else hw * 0.85 * r + 0.006, 0.0 if f == 1.0 else hh * 0.85 * r + 0.006))
    rows += [
        (0.0, 0.0, H + hh * 0.12, hw * 0.92, hh * 0.92),
        (0.0, -sp.body_len * 0.5, H - hh * 0.05, hw, hh),
        (0.0, -sp.body_len, H + hh * 0.05, hw * 0.8, hh * 0.85),
    ]
    a = math.radians(sp.neck_angle)
    base = Vector((0.0, -sp.body_len - 0.05, H + hh * 0.35))
    ndir = Vector((0.0, -math.cos(a), math.sin(a)))
    neck_end = base + ndir * sp.neck_len
    for k, f in enumerate((0.0, 0.35, 0.7, 1.0)):
        p = base + ndir * (sp.neck_len * f)
        p.y += 0.03 * math.sin(f * math.pi)  # gentle S
        r = sp.neck_r * (1.55 - 0.55 * f)
        rows.append((p.x, p.y, p.z, r * 0.95, r * (1.1 + sp.neck_frill * (1 - f))))
    spine = kit.Spine(rows, steps=4)

    # --- head frame: back of the skull sits on the neck end
    pitch = math.radians(sp.head_pitch)
    head_m = Matrix.Translation(neck_end + Vector((0.0, sp.head_len * 0.05, -sp.head_h * 0.35))) @ Matrix.Rotation(-pitch, 4, "X")
    srows = skull_rows(sp)
    jrows = jaw_rows(sp)
    ctx = Ctx(sp, spine, head_m, srows)

    fused = [(spine.mesh(sides=20), (0.5, 0.5, 0.5))]
    skull = nh.transform(head_loft(sp, srows, 2.6), head_m)
    fused.append((skull, (0.5, 0.5, 0.5)))
    # throat filling between jaw and neck
    fused.append((nh.ellipsoid(ctx.head(0.08, z=-sp.jaw_h * 0.6), (sp.head_w * 0.8, sp.head_len * 0.2, sp.jaw_h * 1.1), subdivisions=2), (0.5,) * 3))

    # --- legs (mid-stride)
    crisp_claws = []
    hip_y = 0.02
    for sx, st in ((1, 1.0), (-1, -1.0)):
        x = sx * hw * 0.78
        hip = Vector((x, hip_y, H - hh * 0.05))
        knee = Vector((sx * hw * 0.9, hip_y - 0.24 + st * sp.stride * 0.4, 0.56))
        ankle = Vector((sx * hw * 0.85, hip_y + 0.05 + st * sp.stride, 0.22))
        ball = Vector((sx * hw * 0.82, hip_y - 0.07 + st * sp.stride * 1.3, sp.meta_r * 0.8))
        pts = [hip + Vector((0, 0.02, 0.08)), hip, hip.lerp(knee, 0.45), knee, knee.lerp(ankle, 0.35), ankle, ankle.lerp(ball, 0.5), ball]
        rad = [sp.thigh_r * 0.7, sp.thigh_r, sp.thigh_r * 0.82, sp.shin_r * 1.15, sp.shin_r * 1.1, sp.meta_r * 1.15, sp.meta_r, sp.meta_r * 1.05]
        fused.append((kit.limb(pts, rad, sides=12), (0.5,) * 3))
        # thigh muscle
        fused.append((nh.ellipsoid(hip.lerp(knee, 0.3) + Vector((0, 0.03, 0)), (sp.thigh_r * 0.95, sp.thigh_r * 1.25, sp.thigh_r * 1.4), subdivisions=2), (0.5,) * 3))
        toes, cl = kit.bird_foot(ball, sx, sp.toe_len, sp.meta_r * 0.6)
        fused += [(t, (0.5,) * 3) for t in toes]
        crisp_claws += cl
        # tail-base muscle
        fused.append((nh.ellipsoid((sx * hw * 0.45, 0.35, H + hh * 0.1), (hw * 0.55, 0.3, hh * 0.6), subdivisions=2), (0.5,) * 3))

    # --- arms
    arm_parts = []
    for sx in (1, -1):
        sh = spine.side_pt(spine.s_at_y(-sp.body_len * 0.92), sx, height=-0.25, inset=0.25)
        el = sh + Vector((sx * 0.03, sp.arm_len * 0.15, -sp.arm_len * 0.5))
        wr = el + Vector((0.0, -sp.arm_len * 0.45, -sp.arm_len * 0.12))
        fused.append((kit.limb([sh, el, wr], [sp.arm_r * 1.4, sp.arm_r, sp.arm_r * 0.7], sides=8), (0.5,) * 3))
        tubes, cl = kit.hand(wr, sx, sp.fingers, sp.finger_len, sp.arm_r * 0.38)
        arm_parts += tubes
        crisp_claws += cl

    extra_crisp = []
    if sp.extras:
        ef, ec = sp.extras(ctx)
        fused += ef
        extra_crisp += ec

    body = kit.fuse_parts(fused, sp.voxel, sp.max_tris)
    if sp.pebble:
        kit.pebble(body, sp.pebble)

    jb = nh.MeshBuilder()
    jb.add(head_loft(sp, jrows, 2.4), (0.5,) * 3)
    jaw = jb.fuse(voxel=sp.voxel * 0.7, smooth=3, max_tris=1800)
    hinge = Vector((0, 0, 0))
    jaw_m = head_m @ Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(sp.jaw_open), 4, "X")
    nh.transform(jaw, jaw_m)

    mb = nh.MeshBuilder()
    mb.add(body, sp.paint)
    mb.add(jaw, sp.paint)
    for t in arm_parts:
        mb.add(t, sp.paint)
    # mouth lining
    lin = nh.uv_ellipsoid((0, -sp.head_len * 0.45, 0.0), (sp.head_w * 0.6, sp.head_len * 0.42, 0.012), segments=12, rings=6)
    mb.add(nh.transform(lin, jaw_m), sp.mouth)
    # teeth: upper row down from the mouth line, lower row up from the open jaw
    tl = []
    for i in range(sp.teeth):
        t = 0.3 + 0.66 * i / max(1, sp.teeth - 1)
        top, bot, w = ctx.head_row(t)
        ln = sp.tooth_len * (0.8 + 0.4 * math.sin(t * math.pi))
        for sx in (1, -1):
            b = head_m @ Vector((sx * w * 0.8, -t * sp.head_len, 0.01))
            tp = head_m @ Vector((sx * w * 0.8, -t * sp.head_len - ln * 0.15, -ln))
            tl.append((b, tp, ln * 0.28))
            if i % 2 == 0 and t < 0.9:
                b2 = jaw_m @ Vector((sx * w * 0.72, -t * sp.head_len, -0.01))
                t2 = jaw_m @ Vector((sx * w * 0.72, -t * sp.head_len, ln * 0.75))
                tl.append((b2, t2, ln * 0.24))
    kit.teeth(mb, tl, sp.tooth_color)
    # eyes and nostrils
    top, bot, w = ctx.head_row(0.24)
    e = ctx.head(0.24, x=w * 0.82, z=top * 0.68)
    kit.eyes(mb, e, sp.eye_r, iris=sp.eye_color)
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.9)
        mb.add(nh.ellipsoid(ctx.head(0.9, x=sx * w * 0.6, z=top * 0.7), (sp.eye_r * 0.4, sp.eye_r * 0.7, sp.eye_r * 0.35), subdivisions=1), kit.PUPIL)
    kit.claws(mb, crisp_claws, sp.claw_color)
    for bm, col in extra_crisp:
        mb.add(bm, col, smooth=False)
    if sp.detail:
        sp.detail(mb, ctx)
    return kit.finish(mb, sp.name)


PREVIEW = dict(ground=(0.33, 0.42, 0.24), views=((35, 22), (-90, 6), (25, 65)))
