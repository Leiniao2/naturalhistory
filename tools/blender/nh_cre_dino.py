"""
High-level body-plan generator for the Cretaceous batch: dinosaurs (bipedal or on all
fours), crocodyliforms and small mammals. A DinoSpec holds proportions in model units
(the animal is roughly 2 units long, facing -Y, standing on z = 0); to_spec() turns it into
an nh_cre_tetrapod.Spec. Species scripts fill a DinoSpec, add their own crests, horns,
frills or feathers through the hooks, and call run().

Layout along Y: snout (most -Y) ... head ... neck ... chest ... hips at hip_y ... tail tip.
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

from mathutils import Vector

import nh_model as nh
import nh_cre_core as cc
import nh_cre_tetrapod as tp


@dataclass
class DinoSpec:
    name: str
    paint: Callable
    # trunk
    hip_y: float = 0.2
    hip_z: float = 0.55
    body_len: float = 0.5
    torso_w: float = 0.12
    torso_h: float = 0.14
    belly: float = 0.02          # how far the mid-torso sags below the hip line
    chest_dz: float = 0.0        # chest centre height relative to the hips
    # tail
    tail_len: float = 1.0
    tail_r: float = 0.7          # tail base radius as a fraction of torso_h
    tail_droop: float = 0.0      # tail tip z relative to the hips (negative = down)
    tail_flat: float = 1.0       # half width / half height of the tail (crocs < 1)
    # neck and head
    neck_len: float = 0.3
    neck_rise: float = 0.2       # head-base height above the chest
    neck_r: float = 0.05
    neck_s: float = 0.04         # S-curve sag in the middle of the neck
    head_len: float = 0.35
    head_h: float = 0.07         # half height at the back of the skull
    head_w: float = 0.06
    snout_h: float = 0.45        # tip half height as a fraction of head_h
    snout_w: float = 0.5
    snout_drop: float = 0.0      # z drop of the snout tip
    head_power: float = 2.4
    head_rows: Optional[list] = None   # override: rows relative to the head base (dy<0, dz, hw, hh)
    # jaw
    jaw: bool = False
    jaw_open: float = 12.0
    jaw_h: float = 0.4           # lower jaw half height as a fraction of head_h
    teeth: int = 0
    tooth_len: float = 0.02
    # hind legs
    leg_r: float = 0.06
    knee_fwd: float = 0.12       # knee ahead of the hip (bird-like legs)
    ankle_back: float = 0.06
    leg_type: str = "bird"       # bird | column | sprawl
    leg_x: float = 0.0           # extra lateral offset of the feet
    toes: int = 3
    toe_len: float = 0.1
    toe_r: float = 0.018
    claw: float = 0.03
    sickle: float = 0.0
    stride: float = 0.05
    # fore limbs
    fore: str = "arm"            # arm | leg | none
    arm_len: float = 0.25
    arm_r: float = 0.025
    fingers: int = 3
    finger_len: float = 0.06
    hand_claw: float = 0.03
    arm_lift: float = 0.0
    arm_x: float = 0.0
    finger_r: float = 0.0
    hand_dir: tuple = (0, -0.5, -1.0)
    shoulder_dy: float = 0.03    # shoulder position behind the chest end
    fore_len_ratio: float = 1.0  # fore-leg reach relative to the hip height (leg)
    fore_type: str = "column"    # for fore == "leg": column | bent | sprawl
    fore_toes: int = 3
    # extras
    blobs: list = field(default_factory=list)
    tubes: list = field(default_factory=list)
    lofts: list = field(default_factory=list)
    crisp: Optional[Callable] = None
    eye_r: float = 0.018
    eye_pos: Optional[tuple] = None   # (dy from head base, dz, x frac of head width)
    eye_col: tuple = (0.85, 0.55, 0.12)
    eye_ring: Optional[tuple] = None
    fuzz: float = 0.0
    scales: float = 0.0015
    voxel: float = 0.011
    max_tris: int = 12000
    sides: int = 22
    power: float = 2.1
    claw_col: tuple = cc.CLAW
    pivot: str = "ground"

    # ------------------------------------------------------------- derived
    @property
    def chest_y(self):
        return self.hip_y - self.body_len

    @property
    def chest_z(self):
        return self.hip_z + self.chest_dz

    @property
    def head_base(self):
        """Back of the skull (centre)."""
        return Vector((0.0, self.chest_y - 0.04 - self.neck_len, self.chest_z + self.neck_rise))

    def head_profile(self):
        if self.head_rows:
            return self.head_rows
        L, H, W = self.head_len, self.head_h, self.head_w
        d = self.snout_drop
        return [
            (0.00, 0.0, W, H),
            (-0.25 * L, -0.05 * d, W * 1.0, H * 0.98),
            (-0.50 * L, -0.25 * d, W * (0.55 + 0.45 * self.snout_w), H * (0.62 + 0.36 * self.snout_h)),
            (-0.78 * L, -0.6 * d, W * self.snout_w * 1.05, H * self.snout_h * 1.1),
            (-0.95 * L, -0.9 * d, W * self.snout_w * 0.75, H * self.snout_h * 0.8),
            (-1.00 * L, -d, 0.0, 0.0),
        ]

    def head_at(self, f):
        """(centre, hw, hh) of the skull at fraction f (0 = back, 1 = tip)."""
        rows = self.head_profile()
        L = -rows[-1][0]
        y = -f * L
        for a, b in zip(rows, rows[1:]):
            if b[0] <= y <= a[0]:
                t = (a[0] - y) / max(1e-6, a[0] - b[0])
                dz = a[1] + (b[1] - a[1]) * t
                hw = a[2] + (b[2] - a[2]) * t
                hh = a[3] + (b[3] - a[3]) * t
                hb = self.head_base
                return Vector((0, hb.y + y, hb.z + dz)), hw, hh
        hb = self.head_base
        return Vector((0, hb.y - L, hb.z + rows[-1][1])), 0.0, 0.0


def _axis_rows(s: DinoSpec):
    rows = []
    th, tw = s.torso_h, s.torso_w
    # tail: tip -> base
    rb = th * s.tail_r
    n = 7
    for i in range(n - 1):
        u = i / (n - 1)           # 0 at the tip (the base row is the hip row below)
        y = s.hip_y + s.tail_len * (1 - u) + 0.0
        z = s.hip_z + s.tail_droop * (1 - u) ** 1.6
        r = rb * (0.04 + 0.96 * u ** 1.15) if i > 0 else 0.0
        rows.append((y, z, r * s.tail_flat, r))
    # torso
    rows.append((s.hip_y, s.hip_z, tw * 0.85, th * 0.85))
    rows.append((s.hip_y - s.body_len * 0.5, s.hip_z - s.belly + s.chest_dz * 0.5, tw, th))
    rows.append((s.chest_y, s.chest_z - s.belly * 0.5, tw * 0.9, th * 0.92))
    # neck
    hb = s.head_base
    c0 = Vector((0, s.chest_y - 0.02, s.chest_z + th * 0.25))
    m = 4
    for i in range(1, m + 1):
        u = i / (m + 1)
        p = c0.lerp(hb, u)
        p.z -= s.neck_s * math.sin(math.pi * u)
        r0 = min(th * 0.8, s.neck_r * 1.8)
        r = r0 + (s.neck_r - r0) * u ** 0.7
        rows.append((p.y, p.z, r * (tw / th) ** 0.3, r))
    # head
    for dy, dz, hw, hh in s.head_profile():
        rows.append((hb.y + dy, hb.z + dz, hw, hh))
    return rows


def _hind(s: DinoSpec):
    hz, hy = s.hip_z, s.hip_y - 0.02
    x = s.torso_w * 0.75
    r = s.leg_r
    if s.leg_type == "bird":
        hip = (x, hy, hz)
        knee = (x + 0.01, hy - s.knee_fwd, hz * 0.58)
        ankle = (x + s.leg_x * 0.6, hy - s.knee_fwd + s.ankle_back + 0.05, hz * 0.22)
        ball = (x + s.leg_x, ankle[1] - 0.05, s.toe_r * 1.1)
        return tp.Limb([(x * 0.6, hy + 0.02, hz + r * 0.6), hip, knee, ankle, ball],
                       [r * 0.6, r, r * 0.55, r * 0.32, r * 0.26], toes=s.toes, toe_len=s.toe_len,
                       toe_r=s.toe_r, claw=s.claw, sickle=s.sickle, stride=s.stride, hallux=s.toes >= 3)
    if s.leg_type == "column":
        hip = (x, hy, hz)
        knee = (x + s.leg_x * 0.5, hy - 0.03, hz * 0.5)
        ankle = (x + s.leg_x, hy, hz * 0.12)
        ball = (x + s.leg_x, hy - 0.03, r * 0.3)
        return tp.Limb([(x * 0.6, hy + 0.02, hz + r * 0.4), hip, knee, ankle, ball],
                       [r * 0.7, r, r * 0.75, r * 0.6, r * 0.65], toes=s.toes, toe_len=s.toe_len,
                       toe_r=s.toe_r, claw=s.claw, stride=s.stride, spread=0.6)
    # sprawl
    hip = (x, hy, hz)
    knee = (x + hz * 0.9, hy - 0.04, hz * 0.75)
    ankle = (x + hz * 1.0, hy + 0.04, hz * 0.18)
    ball = (x + hz * 1.05, hy - 0.02, s.toe_r)
    return tp.Limb([(x * 0.5, hy, hz), hip, knee, ankle, ball], [r, r, r * 0.65, r * 0.45, r * 0.4],
                   toes=s.toes, toe_len=s.toe_len, toe_r=s.toe_r, claw=s.claw, stride=s.stride, spread=0.7)


def _fore(s: DinoSpec):
    if s.fore == "none":
        return None
    x = s.torso_w * 0.7
    sy = s.chest_y + s.shoulder_dy
    sz = s.chest_z - s.torso_h * 0.15
    r = s.arm_r
    if s.fore == "arm":
        sh, el, wr, _tip = arm_points(s, 1)
        return tp.Limb([(x * 0.5, sy, sz + r), tuple(sh), tuple(el), tuple(wr)], [r * 1.3, r * 1.1, r * 0.8, r * 0.55],
                       toes=s.fingers, toe_len=s.finger_len, toe_r=s.finger_r or r * 0.35, spread=0.25,
                       claw=s.hand_claw, toe_dir=s.hand_dir, free=True, stride=0.0)
    reach = sz * s.fore_len_ratio
    if s.fore_type == "sprawl":
        sh = (x, sy, sz)
        el = (x + sz * 0.8, sy + 0.04, sz * 0.75)
        wr = (x + sz * 0.95, sy - 0.02, sz * 0.15)
        ball = (x + sz * 1.0, sy - 0.05, s.toe_r)
        return tp.Limb([(x * 0.5, sy, sz), sh, el, wr, ball], [r, r, r * 0.65, r * 0.45, r * 0.4],
                       toes=s.fore_toes, toe_len=s.toe_len * 0.8, toe_r=s.toe_r * 0.85, claw=s.claw * 0.8,
                       stride=-s.stride, spread=0.7)
    bend = 0.05 if s.fore_type == "bent" else 0.015
    sh = (x, sy, sz)
    el = (x + s.leg_x * 0.4, sy + bend, sz - reach * 0.5)
    wr = (x + s.leg_x * 0.8, sy - bend * 0.4, sz - reach * 0.88)
    ball = (x + s.leg_x, sy - bend * 0.6 - 0.01, s.toe_r * 1.1)
    return tp.Limb([(x * 0.5, sy, sz + r * 0.5), sh, el, wr, ball], [r * 1.2, r, r * 0.72, r * 0.55, r * 0.55],
                   toes=s.fore_toes, toe_len=s.toe_len * 0.7, toe_r=s.toe_r * 0.85, claw=s.claw * 0.6,
                   stride=-s.stride, spread=0.5)


def to_spec(s: DinoSpec) -> tp.Spec:
    limbs = [_hind(s)]
    f = _fore(s)
    if f is not None:
        limbs.append(f)
    hb = s.head_base
    if s.eye_pos:
        dy, dz, xf = s.eye_pos
        c, hw, hh = s.head_at(-dy / s.head_len)
        eye = (hw * xf, hb.y + dy, c.z + dz, s.eye_r)
    else:
        c, hw, hh = s.head_at(0.22)
        eye = (hw * 0.82, c.y, c.z + hh * 0.35, s.eye_r)
    disp = None
    if s.fuzz or s.scales:
        fz, sc = cc.fuzz_disp(s.fuzz, 70.0), cc.scales_disp(s.scales, 45.0)
        disp = lambda co, n: (fz(co, n) if s.fuzz else 0.0) + (sc(co, n) if s.scales else 0.0)
    spec = tp.Spec(name=s.name, axis=_axis_rows(s), paint=s.paint, limbs=limbs, power=s.power,
                   sides=s.sides, blobs=list(s.blobs), tubes=list(s.tubes), lofts=list(s.lofts),
                   eye=eye, eye_col=s.eye_col, eye_ring=s.eye_ring, voxel=s.voxel, max_tris=s.max_tris,
                   disp=disp, pivot=s.pivot, claw_col=s.claw_col)
    # thigh muscle
    spec.blobs.append(((s.torso_w * 0.7, s.hip_y - 0.03, s.hip_z - s.leg_r * 0.3),
                       (s.leg_r * 0.9, s.leg_r * 1.6, s.leg_r * 1.5), True))
    if s.jaw:
        rows = s.head_profile()
        jrows = []
        for dy, dz, hw, hh in rows[:-1]:
            jh = max(0.004, hh * s.jaw_h)
            jrows.append((hb.y + dy, hb.z + dz - hh * 0.75 - jh * 0.4, hw * 0.85, jh))
        tipy = hb.y + rows[-1][0] + s.head_len * 0.06
        jrows.append((tipy, hb.z + rows[-1][1] - s.head_h * s.snout_h * 0.6, 0.0, 0.0))
        spec.jaw = jrows
        spec.hinge = (hb.y + 0.01, hb.z - s.head_h * 0.6)
        spec.jaw_open = s.jaw_open
    user = s.crisp

    def crisp(mb, sp):
        if s.teeth:
            up, lo = [], []
            for i in range(s.teeth):
                f = 0.3 + 0.62 * i / max(1, s.teeth - 1)
                c, hw, hh = s.head_at(f)
                for sx in (1, -1):
                    up.append((sx * hw * 0.78, c.y, c.z - hh * 0.62))
                    lo.append((sx * hw * 0.62, c.y, c.z - hh * 0.80))
            cc.teeth_row(mb, up, s.tooth_len, s.tooth_len * 0.32, down=True)
            if sp._jaw_rot is not None:
                cc.teeth_row(mb, lo, s.tooth_len * 0.8, s.tooth_len * 0.28, down=False, rot=sp._jaw_rot)
            if sp._jaw_rot is not None:
                tongue = nh.ellipsoid((0, hb.y - s.head_len * 0.4, hb.z - s.head_h * 0.62),
                                      (s.head_w * 0.5, s.head_len * 0.33, s.head_h * 0.12))
                mb.add(nh.transform(tongue, sp._jaw_rot), cc.MOUTH)
        if user:
            user(mb, s)
    spec.crisp = crisp
    return spec


def run(make, name, preview=None):
    nh.run(lambda: tp.build(to_spec(make())), name, **(preview or tp.GROUND_VIEWS))


# ---------------------------------------------------------------- common paint

def make_paint(back, flank, belly, stripe=None, freq=0.0, stripe_amt=0.7, spot=None, spot_scale=0.0,
               head=None, head_y=None, mottle=0.12, legs=None, leg_z=None, extra=None, y_range=(-9, 9)):
    """Countershaded paint with optional transverse back stripes, spots and a head tint
    (applied where co.y < head_y). extra(co, n, c) -> c for species specifics."""
    def paint(co, n):
        c = cc.countershade(n, belly, flank, back)
        top = nh.smoothstep(-0.2, 0.6, n.z)
        if stripe is not None and freq and y_range[0] < co.y < y_range[1]:
            c = nh.lerp(c, stripe, stripe_amt * cc.stripes(co, freq, warp=1.2) * top)
        if spot is not None and spot_scale:
            c = nh.lerp(c, spot, 0.8 * cc.spots(co, spot_scale) * nh.smoothstep(-0.4, 0.3, n.z))
        if head is not None and head_y is not None and co.y < head_y:
            c = nh.lerp(c, head, nh.smoothstep(head_y, head_y - 0.06, co.y) * 0.85)
        if legs is not None and leg_z is not None and co.z < leg_z:
            c = nh.lerp(c, legs, nh.smoothstep(leg_z, leg_z * 0.5, co.z))
        if extra is not None:
            c = extra(co, n, c)
        return cc.mottle(c, co, mottle)
    return paint


# ---------------------------------------------------------------- feather helpers

def arm_points(s: DinoSpec, sx=1):
    x = s.torso_w * 0.7 + s.arm_x
    sy = s.chest_y + s.shoulder_dy
    sz = s.chest_z - s.torso_h * 0.15
    L = s.arm_len
    sh = Vector((sx * x, sy, sz))
    el = Vector((sx * (x + 0.025), sy + L * 0.38, sz - L * 0.38))
    wr = Vector((sx * (x + 0.015), sy - L * 0.12, sz - L * 0.5 + s.arm_lift))
    tip = wr + Vector(s.hand_dir).normalized() * s.finger_len
    return sh, el, wr, tip


def tail_point(s: DinoSpec, u):
    """Centre and radius of the tail at u (0 = base at the hips, 1 = tip)."""
    y = s.hip_y + s.tail_len * u
    z = s.hip_z + s.tail_droop * u ** 1.6
    r = s.torso_h * s.tail_r * (0.04 + 0.96 * (1 - u) ** 1.15)
    return Vector((0, y, z)), r


def arm_vanes(mb, s: DinoSpec, color, length=0.12, n=6, droop=0.15):
    """Wing-like fans of pennaceous feathers trailing back from forearm and hand."""
    for sx in (1, -1):
        sh, el, wr, tip = arm_points(s, sx)
        pts = cc.polyline([el, wr, tip], n)
        pairs = []
        for i, p in enumerate(pts):
            k = 0.55 + 0.45 * i / (n - 1)
            off = Vector((sx * 0.01, length * k, -length * k * droop))
            pairs.append((p + Vector((sx * 0.004, 0, 0)), p + off))
        mb.add(cc.ribbon(pairs, 0.006, normal_hint=Vector((sx, 0, 0))), color)


def tail_fan(mb, s: DinoSpec, color, u0=0.55, width=0.07, n=8, flare=1.0):
    """Horizontal frond of tail feathers along the distal tail (both sides)."""
    for sx in (1, -1):
        pairs = []
        for i in range(n):
            u = u0 + (1 - u0) * i / (n - 1)
            c, r = tail_point(s, u)
            w = width * (0.5 + 0.5 * math.sin(math.pi * min(1.0, (i + 1) / n * 0.9 + 0.1))) * flare
            pairs.append((c + Vector((sx * r * 0.5, 0, 0)), c + Vector((sx * (r + w), w * 0.3, -0.003))))
        mb.add(cc.ribbon(pairs, 0.005, normal_hint=Vector((0, 0, 1))), color)
