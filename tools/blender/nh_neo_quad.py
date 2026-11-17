"""
Shared parametric quadruped mammal for the Neogene / Pleistocene megafauna batch
(tag "neo"): proboscideans, rhinos, horses, camels, giraffids, entelodonts,
bear-dogs, bears, chalicotheres, litopterns, notoungulates, marsupials, deer...

One fused mesh caught mid-stride (left-front and right-hind forward), like
nh_sabretooth.py / lion.py, so the game's Ground walk swings only the legs:
the belly stays above the hip line printed by build() (use it as mapHip).

  * Spec: leg lengths front / hind (the back slope), trunk length and girth,
    hump, neck length / angle / thickness, head length / depth / pitch, muzzle
    taper, ears, tail, foot type (hoof, pillar, paw, plantigrade, knuckle),
    trunk (proboscis), tusks, horns, ossicones, antlers, mane, coat colours,
    shagginess and an optional pattern(co, n, c) -> rgb hook for stripes etc.
  * Head frame: h(t, s, u) - t runs from the back of the skull (0) to the
    snout tip (1) along the head axis, s is sideways, u is up from the axis
    (both in units of head length), so tusks, horns and eyes are placed
    relative to the skull whatever its pitch.
  * build(spec): parts fused into one surface, shaggy displacement, colours
    repainted with countershading (darker back, paler belly), then crisp
    details: eyes, horns, tusks, antlers, claws.
  * Faces -Y, pivot on the ground (z = 0 at the feet).
"""

import math
import sys
from dataclasses import dataclass, field

import bmesh
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

EYE = (0.10, 0.06, 0.03)
PUPIL = (0.02, 0.015, 0.01)
HOOF = (0.16, 0.13, 0.11)
IVORY = (0.90, 0.85, 0.70)
HORN = (0.32, 0.27, 0.22)
BONE = (0.80, 0.74, 0.62)
CLAW = (0.20, 0.17, 0.14)


@dataclass
class Spec:
    name: str
    leg_f: float = 0.80          # ground to the bottom of the chest at the shoulder
    leg_h: float = 0.80          # ground to the bottom of the flank at the hip
    length: float = 1.0          # shoulder-to-hip distance
    girth: tuple = (0.26, 0.30)  # trunk half-width, half-depth
    belly: float = 1.0           # >1 = deeper, rounder belly
    hump: float = 0.0            # extra height of a shoulder hump (in girth units)
    hump_y: float = -0.35        # hump position along the trunk (-0.5 = shoulders)
    leg_r: tuple = (0.07, 0.08)  # upper leg radius front, hind
    leg_taper: float = 0.55      # lower-leg radius / upper-leg radius
    foot: str = "hoof"           # hoof, pillar, paw, plantigrade, knuckle (front only; hind -> paw)
    foot_r: float = 1.0
    stride: float = 0.12
    neck_len: float = 0.35
    neck_angle: float = 35.0     # degrees above horizontal
    neck_r: tuple = (0.17, 0.11)
    head_len: float = 0.45
    head_r: tuple = (0.11, 0.13)  # cranium half-width, half-height
    snout_r: tuple = (0.06, 0.07)  # half-width, half-height at the snout tip
    head_pitch: float = 40.0     # degrees the head axis points down from horizontal
    jaw: float = 1.0             # lower jaw depth factor
    cranium: float = 1.0         # dome size
    eye_t: float = 0.36          # eye position along the head axis
    eye_u: float = 0.25          # eye height (cranium half-heights above the axis)
    ears: str = "point"          # point, round, flap, none
    ear_size: float = 0.08
    tail_len: float = 0.35
    tail_r: float = 0.035
    tail_tuft: float = 0.0       # radius of a hair tuft / brush on the tail end
    tail_droop: float = 0.85     # 1 = hangs straight down, 0 = straight back
    trunk_len: float = 0.0       # proboscis length
    trunk_r: float = 0.07
    trunk_curl: float = 0.15
    shovel: float = 0.0          # Platybelodon: length of the flat lower-jaw shovel
    shovel_teeth: str = "plate"  # plate (flat shovel incisors), tusks (two short forward tusks), none
    tusks: list = field(default_factory=list)   # dicts: t,s,u, dir (model), len, r, bend (model), color
    horns: list = field(default_factory=list)   # dicts: t,s,u, len, r, dir (model), bend (model), color
    antler: float = 0.0          # Megaloceros palm span (0 = none)
    mane: float = 0.0            # height of an upright mane / shaggy neck crest
    beard: float = 0.0           # throat hair / dewlap
    shag: float = 0.0            # fur displacement amplitude (0.004 = sleek, 0.02 = shaggy)
    lips: float = 0.0            # prehensile upper lip / short proboscis bulb (Macrauchenia, rhino)
    coat: tuple = (0.55, 0.42, 0.30)
    dark: tuple = (0.35, 0.26, 0.19)
    pale: tuple = (0.80, 0.72, 0.60)
    mane_col: tuple = None
    leg_col: tuple = None        # lower legs (stockings)
    skin: tuple = None           # trunk / muzzle colour
    hoof_col: tuple = HOOF
    countershade: float = 0.6
    pattern: object = None       # fn(co, n, c, spec) -> rgb
    voxel: float = 0.02
    max_tris: int = 11000
    extra: object = None         # fn(builder, L) to add more fused parts
    extra_details: object = None  # fn(mb, L, surf) for more crisp parts
    _claws: list = field(default_factory=list)


class Layout:
    def __init__(self, s):
        self.s = s
        gy, gz = s.girth
        self.ys = -s.length / 2           # shoulder
        self.yh = s.length / 2            # hip
        self.zf = s.leg_f + gz            # trunk axis height at the shoulder
        self.zh = s.leg_h + gz
        a = math.radians(s.neck_angle)
        self.neck0 = Vector((0, self.ys - gy * 0.35, self.zf + gz * 0.35))
        self.neck_dir = Vector((0, -math.cos(a), math.sin(a)))
        self.head0 = self.neck0 + self.neck_dir * s.neck_len
        p = math.radians(s.head_pitch)
        self.F = Vector((0, -math.cos(p), -math.sin(p)))
        self.U = Vector((0, -math.sin(p), math.cos(p)))
        # start the head axis a little behind the end of the neck so the occiput covers it
        self.hb = self.head0 - self.F * s.head_r[1] * 0.4

    def axis_z(self, y):
        t = nh.smoothstep(self.ys, self.yh, y)
        return self.zf + (self.zh - self.zf) * t

    def h(self, t, sd=0.0, u=0.0):
        L = self.s.head_len
        return tuple(self.hb + self.F * (t * L) + Vector((sd * L, 0, 0)) + self.U * (u * L))


# ---------------------------------------------------------------- parts

COAT, MANE, SKIN, HOOFC, LEG = "coat", "mane", "skin", "hoof", "leg"


def colour_of(s, region):
    return {
        COAT: s.coat, MANE: s.mane_col or s.dark, SKIN: s.skin or s.coat, HOOFC: s.hoof_col,
        LEG: s.leg_col or s.coat,
    }[region]


def torso(b, L):
    s = L.s
    gy, gz = s.girth
    c = colour_of(s, COAT)
    ys, yh = L.ys, L.yh
    pts, rad = [], []
    n = 7
    for i in range(n + 1):
        t = i / n
        y = ys - gy * 0.55 + (yh - ys + gy * 1.1) * t
        pts.append((0, y, L.axis_z(y)))
        rad.append(gz * (0.80 + 0.25 * math.sin(math.pi * min(1, t * 1.15))) if 0 < i < n else gz * 0.55)
    b.add(nh.tube(pts, rad, sides=16, scale_xy=(gy / gz, 1.0)), c)
    b.add(nh.ellipsoid((0, ys - gy * 0.15, L.zf), (gy * 0.95, gy * 0.9, gz * 1.0), subdivisions=3), c)   # chest
    b.add(nh.ellipsoid((0, yh + gy * 0.05, L.zh + gz * 0.05), (gy * 0.92, gy * 0.85, gz * 0.95), subdivisions=3), c)
    if s.belly > 1.0:
        b.add(nh.ellipsoid((0, 0, L.axis_z(0) - gz * 0.15), (gy * s.belly * 0.95, s.length * 0.45, gz * s.belly * 0.85),
                           subdivisions=3), c)
    if s.hump > 0:
        y = s.hump_y * s.length
        b.add(nh.ellipsoid((0, y, L.axis_z(y) + gz * 0.55), (gy * 0.55, s.length * 0.32, gz * (0.35 + s.hump)),
                           subdivisions=3), colour_of(s, MANE if s.mane > 0 else COAT))


def leg_front(b, L, x, stride):
    s = L.s
    r = s.leg_r[0]
    lt = s.leg_taper
    zt = s.leg_f
    ys = L.ys
    col = colour_of(s, COAT)
    b.add(nh.ellipsoid((x * 0.9, ys + 0.02, zt + s.girth[1] * 0.4), (r * 1.15, r * 1.6, r * 2.2)), col)  # shoulder
    elbow = Vector((x, ys + r * 0.6, zt * 0.88))
    knee = Vector((x * 1.0, ys + stride * 0.55, zt * 0.36))
    foot = Vector((x, ys + stride, 0.0))
    if s.foot == "pillar":
        knee = Vector((x, ys + stride * 0.5, zt * 0.45))
        b.add(nh.tube([(x, ys, zt + s.girth[1] * 0.4), tuple(elbow), tuple(knee), tuple(foot + Vector((0, 0, r * 0.6)))],
                      [r * 1.2, r * 1.05, r * 0.85, r * 0.85], sides=12), col)
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -r * 0.1, r * 0.35))), (r * 0.95 * s.foot_r, r * 1.0 * s.foot_r, r * 0.4)),
              colour_of(s, LEG))
        return
    b.add(nh.tube([(x, ys, zt + s.girth[1] * 0.4), tuple(elbow), tuple(knee)], [r * 1.25, r, r * lt * 1.05], sides=12),
          col)
    b.add(nh.ellipsoid(tuple((elbow + knee) * 0.5 + Vector((0, -r * 0.1, 0))), (r * 0.85, r * 0.9, (elbow - knee).length * 0.35)),
          col)
    feet(b, L, knee, foot, r * lt, front=True)


def leg_hind(b, L, x, stride):
    s = L.s
    r = s.leg_r[1]
    lt = s.leg_taper
    zt = s.leg_h
    yh = L.yh
    col = colour_of(s, COAT)
    b.add(nh.ellipsoid((x * 0.85, yh - r * 0.3, zt + s.girth[1] * 0.3), (r * 1.15, r * 1.8, r * 2.3)), col)   # haunch / thigh
    stifle = Vector((x * 1.02, yh - r * 1.0, zt * 0.72))
    hock = Vector((x, yh + r * 0.9 + stride * 0.5, zt * 0.36))
    foot = Vector((x, yh + stride * 0.7, 0.0))
    if s.foot == "pillar":
        hock = Vector((x, yh + stride * 0.5, zt * 0.42))
        b.add(nh.tube([(x, yh, zt + s.girth[1] * 0.3), tuple(stifle), tuple(hock), tuple(foot + Vector((0, 0, r * 0.6)))],
                      [r * 1.3, r * 1.0, r * 0.8, r * 0.8], sides=12), col)
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -r * 0.1, r * 0.35))), (r * 0.9 * s.foot_r, r * 0.95 * s.foot_r, r * 0.4)),
              colour_of(s, LEG))
        return
    if s.foot == "plantigrade":
        hock = Vector((x, yh + r * 0.4 + stride * 0.5, zt * 0.22))
    b.add(nh.tube([(x, yh, zt + s.girth[1] * 0.3), tuple(stifle), tuple(hock)], [r * 1.3, r * 0.95, r * lt * 0.95],
                  sides=12), col)
    b.add(nh.ellipsoid(tuple(stifle + Vector((0, r * 0.2, r * 0.4))), (r * 0.95, r * 1.15, r * 1.5)), col)
    feet(b, L, hock, foot, r * lt * 0.9, front=False)


def feet(b, L, top, foot, r, front):
    s = L.s
    lc = colour_of(s, LEG)
    kind = s.foot
    if kind == "knuckle":
        kind = "knuckle" if front else "paw"
    if kind == "hoof":
        fet = foot + Vector((0, -r * 0.4, r * 1.6))
        b.add(nh.tube([tuple(top), tuple(fet)], [r, r * 0.8], sides=10), lc)
        b.add(nh.tube([tuple(fet), tuple(foot + Vector((0, -r * 0.7, r * 0.05)))], [r * 0.85, r * 0.95 * s.foot_r],
                      sides=10), colour_of(s, HOOFC))
    elif kind in ("paw", "plantigrade"):
        sole = foot + Vector((0, -r * (0.8 if kind == "paw" else 1.6), 0))
        b.add(nh.tube([tuple(top), tuple(foot + Vector((0, 0, r * 0.9)))], [r, r * 0.95], sides=10), lc)
        fr = r * 1.15 * s.foot_r
        b.add(nh.ellipsoid(tuple((foot + sole) * 0.5 + Vector((0, 0, fr * 0.5))),
                           (fr, fr * (1.2 if kind == "paw" else 1.9), fr * 0.55)), lc)
        for a in (-0.7, -0.23, 0.23, 0.7):
            tip = sole + Vector((math.sin(a) * fr * 0.9, -math.cos(a) * fr * 0.5 - fr * 0.3, fr * 0.25))
            s._claws.append((tip, Vector((math.sin(a) * 0.3, -1, -0.5)).normalized(), fr * 0.5))
    elif kind == "knuckle":
        # chalicothere / ape: weight on the backs of curled digits, claws turned inward
        wrist = foot + Vector((0, -r * 0.2, r * 1.3))
        b.add(nh.tube([tuple(top), tuple(wrist)], [r, r * 0.95], sides=10), lc)
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -r * 0.6, r * 0.65))), (r * 1.1, r * 1.3, r * 0.75)), lc)
        for a in (-0.5, 0.0, 0.5):
            tip = foot + Vector((math.sin(a) * r * 0.9, -r * 1.6, r * 0.8))
            s._claws.append((tip, Vector((0, 0.6, -1)).normalized(), r * 1.4))


def neck_head(b, L):
    s = L.s
    c = colour_of(s, COAT)
    n0, n1 = L.neck0, L.head0
    mid = (n0 + n1) * 0.5 + Vector((0, 0, s.neck_r[1] * 0.25))
    b.add(nh.tube([tuple(n0 - L.neck_dir * s.neck_r[0] * 0.5), tuple(mid), tuple(n1)],
                  [s.neck_r[0], (s.neck_r[0] + s.neck_r[1]) * 0.5, s.neck_r[1]], sides=14,
                  scale_xy=(0.85, 1.0)), c)
    if s.mane > 0:
        mc = colour_of(s, MANE)
        for i in range(6):
            t = i / 5
            p = n0.lerp(n1, 0.05 + t * 0.8) + Vector((0, 0, 1)) * (s.neck_r[0] * (1 - t) + s.neck_r[1] * t) * 0.75
            b.add(nh.ellipsoid(tuple(p + Vector((0, 0, s.mane * 0.4))), (0.025 + s.mane * 0.15, s.neck_len * 0.13 + 0.03,
                                                                         s.mane * 0.7)), mc)
    if s.beard > 0:
        p = n0.lerp(n1, 0.6) - Vector((0, 0, s.neck_r[1] * 0.9))
        b.add(nh.ellipsoid(tuple(p), (s.neck_r[1] * 0.6, s.neck_len * 0.3 + 0.04, s.beard)), colour_of(s, MANE))
    hr, sr = s.head_r, s.snout_r
    HL = s.head_len
    h = L.h
    # cranium + snout + jaw
    b.add(nh.ellipsoid(h(0.22), (hr[0] * s.cranium, HL * 0.26, hr[1] * s.cranium), subdivisions=3), c)
    sk = colour_of(s, SKIN) if (s.trunk_len > 0 or s.lips > 0) else c
    b.add(_snout(L), c)
    b.add(nh.ellipsoid(h(0.97, 0, -0.03), (sr[0] * 1.05, sr[1] * 0.9, sr[1] * 1.0)), sk)        # muzzle end
    if s.jaw > 0:
        b.add(nh.tube([h(0.25, 0, -hr[1] / HL * 0.45), h(0.88, 0, -(sr[1] / HL) * 0.75)],
                      [hr[1] * 0.55 * s.jaw, sr[1] * 0.55 * s.jaw], sides=12, scale_xy=(1.1, 1.0)), c)
    for sx in (-1, 1):
        b.add(nh.ellipsoid(h(0.38, sx * hr[0] / HL * 0.62, -hr[1] / HL * 0.25), (hr[0] * 0.4, HL * 0.12, hr[1] * 0.45)),
              c)   # cheeks
    if s.lips > 0:
        b.add(nh.ellipsoid(h(1.02, 0, 0.0), (sr[0] * 1.1, s.lips, sr[1] * 0.8)), sk)
    if s.trunk_len > 0:
        tip0 = Vector(h(1.0, 0, -0.02))
        pts = [tip0]
        d = (L.F * 0.6 + Vector((0, 0, -1))).normalized()
        n = 6
        seg = s.trunk_len / n
        for i in range(n):
            t = (i + 1) / n
            d = (d + Vector((0, -s.trunk_curl * t * 0.9, 0))).normalized()
            pts.append(pts[-1] + d * seg)
        radii = [s.trunk_r * (1.0 - 0.55 * i / n) for i in range(n + 1)]
        b.add(nh.tube([tuple(p) for p in pts], radii, sides=12), colour_of(s, SKIN))
    if s.shovel > 0:
        # long, flat-bottomed lower jaw ending in a broad scoop
        base, tip = shovel_ends(L)
        b.add(nh.tube([tuple(base), tuple(base.lerp(tip, 0.5)), tuple(tip)], [sr[1] * 0.9, sr[1] * 0.75, sr[1] * 0.6],
                      sides=12, scale_xy=(2.0, 0.55)), c)
    # ears
    if s.ears != "none":
        e = s.ear_size
        for sx in (-1, 1):
            base = Vector(h(0.12, sx * hr[0] / HL * 0.75, hr[1] / HL * 0.7))
            if s.ears == "point":
                tip = base + Vector((sx * e * 0.35, e * 0.25, e * 1.0))
                b.add(nh.tube([tuple(base), tuple(base.lerp(tip, 0.5)), tuple(tip)],
                              [e * 0.32, e * 0.26, max(e * 0.08, s.voxel * 0.9)],
                              sides=8, scale_xy=(1.0, 0.45)), c)
            elif s.ears == "round":
                b.add(nh.ellipsoid(tuple(base + Vector((sx * e * 0.2, e * 0.1, e * 0.35))), (e * 0.45, e * 0.25, e * 0.5)), c)
            elif s.ears == "flap":
                b.add(nh.ellipsoid(tuple(base + Vector((sx * e * 0.35, e * 0.25, -e * 0.25))), (e * 0.1, e * 0.6, e * 0.75)),
                      colour_of(s, SKIN))


def shovel_ends(L):
    s = L.s
    base = Vector(L.h(0.75, 0, -(s.snout_r[1] / s.head_len) * 1.1))
    return base, base + Vector((0, -s.shovel, -s.shovel * 0.35))


def _snout(L):
    s = L.s
    hr, sr = s.head_r, s.snout_r
    pts = [L.h(t, 0, -0.012 * t) for t in (0.18, 0.45, 0.72, 0.97)]
    # interpolate widths/heights; tube() radius * scale_xy -> use radius = height, sx = width/height per ring is
    # not supported, so build rings manually
    bm = bmesh.new()
    rings = []
    sides = 14
    wh = [(hr[0], hr[1] * 0.92), ((hr[0] * 0.55 + sr[0] * 0.45), (hr[1] * 0.5 + sr[1] * 0.5)),
          ((hr[0] * 0.2 + sr[0] * 0.8), (hr[1] * 0.2 + sr[1] * 0.8)), (sr[0], sr[1])]
    for p, (w, hh) in zip(pts, wh):
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ring.append(bm.verts.new(Vector(p) + Vector((math.cos(a) * w, 0, 0)) + L.U * (math.sin(a) * hh)))
        rings.append(ring)
    for a, c in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], c[j], c[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def tail(b, L):
    s = L.s
    if s.tail_len <= 0:
        return
    root = Vector((0, L.yh + s.girth[0] * 0.75, L.zh + s.girth[1] * 0.35))
    d = s.tail_droop
    pts = [root]
    n = 4
    for i in range(n):
        t = (i + 1) / n
        ang = (0.25 + d * 1.2 * t) * (math.pi / 2) * min(1.0, d * 1.3 + 0.2)
        pts.append(pts[-1] + Vector((0, math.cos(ang), -math.sin(ang))) * (s.tail_len / n))
    b.add(nh.tube([tuple(p) for p in pts], [s.tail_r * (1 - 0.6 * i / n) for i in range(n + 1)], sides=10),
          colour_of(s, COAT))
    if s.tail_tuft > 0:
        e = pts[-1]
        dirn = (pts[-1] - pts[-2]).normalized()
        b.add(nh.ellipsoid(tuple(e - dirn * s.tail_tuft * 0.8), (s.tail_tuft * 0.6, s.tail_tuft * 0.6, s.tail_tuft * 1.6)),
              colour_of(s, MANE))


# ---------------------------------------------------------------- crisp details

def bent_tube(root, dirn, length, r, bend=(0, 0, 0), steps=7, tip_r=0.0, flat=1.0):
    root, d0 = Vector(root), Vector(dirn).normalized()
    bend = Vector(bend)
    pts, radii = [], []
    p = root.copy()
    d = d0.copy()
    seg = length / steps
    for i in range(steps + 1):
        pts.append(tuple(p))
        t = i / steps
        radii.append(r * (1 - t) + tip_r * t if i < steps else tip_r)
        d = (d + bend / steps).normalized()
        p = p + d * seg
    return nh.tube(pts, radii, sides=10, scale_xy=(1.0, flat))


class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal

    def near(self, p):
        loc, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return loc, normal


def details(mb, L, surf):
    s = L.s
    HL = s.head_len
    for sx in (-1, 1):
        o = Vector(L.h(s.eye_t, 0, s.head_r[1] / HL * s.eye_u))
        p, n = surf.hit(o, (sx, 0, 0.0))  # from inside the skull: skips ears, horns, tusks
        er = max(0.012, s.head_r[1] * 0.16)
        mb.add(nh.ellipsoid(tuple(p - n * er * 0.35), (er, er, er * 0.85), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(tuple(p + n * er * 0.45), (er * 0.4, er * 0.45, er * 0.4), subdivisions=1), PUPIL)
    for t in s.tusks:
        root = Vector(L.h(t["t"], t.get("s", 0), t.get("u", 0)))
        mb.add(bent_tube(root, t["dir"], t["len"], t["r"], t.get("bend", (0, 0, 0)), tip_r=t.get("tip", t["r"] * 0.2),
                         flat=t.get("flat", 1.0)), t.get("color", IVORY))
    for hn in s.horns:
        o = Vector(L.h(hn["t"], hn.get("s", 0), hn.get("u", 0.5)))
        if hn.get("surface", True):
            p, n = surf.near(o)
            o = p - n * hn["r"] * 0.4
        mb.add(bent_tube(o, hn.get("dir", (0, 0, 1)), hn["len"], hn["r"], hn.get("bend", (0, 0, 0)),
                         tip_r=hn.get("tip", 0.0), flat=hn.get("flat", 1.0)), hn.get("color", HORN))
        if hn.get("knob"):
            d = Vector(hn.get("dir", (0, 0, 1))).normalized()
            tip = o + (d + Vector(hn.get("bend", (0, 0, 0))) * 0.5).normalized() * hn["len"]
            mb.add(nh.ellipsoid(tuple(tip), (hn["knob"],) * 3, subdivisions=2), hn.get("color", HORN))
    if s.shovel > 0 and s.shovel_teeth != "none":
        base, tip = shovel_ends(L)
        d = (tip - base).normalized()
        w = s.snout_r[1] * 0.9 * 2.0
        if s.shovel_teeth == "plate":
            for sx in (-1, 1):
                r0 = tip - d * 0.02 + Vector((sx * w * 0.42, 0, 0.01))
                mb.add(bent_tube(r0, d, s.shovel * 0.32, w * 0.42, tip_r=w * 0.32, flat=0.22), IVORY)
        else:
            for sx in (-1, 1):
                r0 = tip - d * 0.03 + Vector((sx * w * 0.35, 0, 0))
                mb.add(bent_tube(r0, d + Vector((sx * 0.1, 0, 0.05)), s.shovel * 0.5, 0.022, tip_r=0.008), IVORY)
    if s.antler > 0:
        antlers(mb, L)
    for tip, d, r in s._claws:
        mb.add(nh.tube([tuple(tip - d * r * 0.2), tuple(tip + d * r * 0.7)], [r * 0.32, 0.0], sides=6), CLAW)
    if s.extra_details:
        s.extra_details(mb, L, surf)


def antlers(mb, L):
    """Megaloceros: short beam out to the side, then a vast palm with tines along its rim."""
    s = L.s
    A = s.antler
    for sx in (-1, 1):
        root = Vector(L.h(0.12, sx * 0.13, 0.30))
        beam_end = root + Vector((sx * A * 0.30, A * 0.05, A * 0.10))
        mb.add(nh.tube([tuple(root), tuple(beam_end)], [A * 0.028, A * 0.024], sides=8), BONE)
        # brow tine forward
        mb.add(bent_tube(root + Vector((sx * A * 0.06, 0, A * 0.02)), (sx * 0.3, -1, 0.3), A * 0.18, A * 0.025,
                         bend=(0, 0, 0.6)), BONE)
        # palm: flat panel in a plane tilted up from horizontal
        out = Vector((sx, 0, 0))
        fwd = -Vector((0, 0.45, 0.9)).normalized()   # palm spreads up and back, facing forward-up
        up = Vector((0, 0, 1))
        pts = []
        prof = [(0.0, -0.08), (0.25, -0.22), (0.55, -0.25), (0.85, -0.12), (1.0, 0.05), (0.95, 0.25), (0.7, 0.35),
                (0.4, 0.3), (0.15, 0.15), (0.0, 0.06)]
        tilt = math.radians(28)
        for u, v in prof:
            q = beam_end + out * (u * A * 0.62 * math.cos(tilt)) + up * (u * A * 0.62 * math.sin(tilt)) + fwd * (-v * A * 0.6)
            pts.append(tuple(q))
        bm = _panel(pts, A * 0.018)
        mb.add(bm, BONE)
        # tines along the outer rim
        for u, v in prof[2:8]:
            q = beam_end + out * (u * A * 0.62 * math.cos(tilt)) + up * (u * A * 0.62 * math.sin(tilt)) + fwd * (-v * A * 0.6)
            d = (out * 0.4 + fwd * (-1.0 if v > 0 else 0.3) + up * 0.3).normalized()
            mb.add(nh.tube([tuple(q - d * A * 0.02), tuple(q + d * A * 0.13)], [A * 0.02, 0.0], sides=6), BONE)


def _panel(outline, th):
    """Thin slab from a closed 3D outline (fan-triangulated around its centroid)."""
    bm = bmesh.new()
    pts = [Vector(p) for p in outline]
    c = sum(pts, Vector()) / len(pts)
    nrm = Vector()
    for a, b in zip(pts, pts[1:] + pts[:1]):
        nrm += (a - c).cross(b - c)
    nrm.normalize()
    top = [bm.verts.new(p + nrm * th * 0.5) for p in pts]
    bot = [bm.verts.new(p - nrm * th * 0.5) for p in pts]
    ct, cb = bm.verts.new(c + nrm * th), bm.verts.new(c - nrm * th)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ct, top[i], top[j]])
        bm.faces.new([cb, bot[j], bot[i]])
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- paint / build

def shade(s, co, n, c):
    """Countershading: darker along the back, paler on the belly and inner legs."""
    pale = nh.smoothstep(0.0, -0.7, n.z)
    back = nh.smoothstep(0.3, 0.9, n.z)
    k = s.countershade
    c = nh.lerp(c, s.dark, back * k * 0.8)
    c = nh.lerp(c, s.pale, pale * k)
    c = nh.lerp(c, nh.lerp(c, s.dark, 0.5), 0.25 * max(0.0, noise.noise(co * 7.0)))
    if s.pattern:
        c = s.pattern(co, n, c, s)
    return c


def build(s):
    s._claws.clear()
    L = Layout(s)
    b = nh.MeshBuilder()
    torso(b, L)
    gy = s.girth[0]
    leg_front(b, L, -gy * 0.62, -s.stride)
    leg_front(b, L, gy * 0.62, s.stride * 0.8)
    leg_hind(b, L, -gy * 0.62, s.stride * 0.7)
    leg_hind(b, L, gy * 0.62, -s.stride)
    neck_head(b, L)
    tail(b, L)
    if s.extra:
        s.extra(b, L)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    if s.shag > 0:
        for v in fused.verts:
            if v.co.z < 0.03:
                continue
            a = s.shag * (0.6 + 0.4 * noise.noise(v.co * 9.0)) * max(0.0, noise.noise(Vector((v.co.x * 30, v.co.y * 30, v.co.z * 8))))
            v.co += v.normal * a + Vector((0, 0, -a * 0.6))
        fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            nc = shade(s, l.vert.co, l.vert.normal, (c[0], c[1], c[2]))
            l[col] = (nc[0], nc[1], nc[2], 1.0)
    surf = Surface(fused)
    belly, _n = surf.hit((0, 0.0, 0.0), (0, 0, 1))
    mb = nh.MeshBuilder()
    mb.add(fused)
    details(mb, L, surf)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    zmin = 0.0
    print(f"{s.name}: belly at {belly.z:.3f}, height {top:.3f}, mapHip ~ {belly.z / top:.2f}")
    return obj


def main(spec, ground=(0.45, 0.42, 0.30), views=((35, 20), (-90, 5), (0, 10))):
    nh.run(lambda: build(spec), spec.name, ground=ground, views=views)


# ---------------------------------------------------------------- coat patterns (Spec.pattern)

def back_stripes(color, freq=14.0, amount=0.8, y0=-0.2, y1=1.0, zmin=0.0):
    """Vertical bands across the back and rump (thylacine / Thylacoleo style)."""
    def f(co, n, c, s):
        L = Layout(s)
        if not (L.ys + (L.yh - L.ys) * y0 <= co.y <= L.yh + s.girth[0] * y1):
            return c
        if co.z < max(zmin, s.leg_h * 0.8) or n.z < -0.2:
            return c
        band = 0.5 + 0.5 * math.sin(co.y * freq * math.tau / 2 + 0.6 * noise.noise(co * 4.0))
        return nh.lerp(c, color, amount * nh.smoothstep(0.65, 0.85, band))
    return f


def spots(color, freq=10.0, size=0.28, amount=0.85, zmin=0.1):
    def f(co, n, c, s):
        if co.z < zmin:
            return c
        dist, pts = noise.voronoi(co * freq + Vector((3.1, 1.7, 0.4)), distance_metric="DISTANCE")
        k = 1.0 - nh.smoothstep(size - 0.06, size + 0.06, dist[0] + 0.06 * noise.noise(co * freq * 2.0))
        return nh.lerp(c, color, amount * k * (1 - nh.smoothstep(-0.3, -0.7, n.z)))
    return f


def leg_bands(color, freq=18.0, amount=0.7, z0=0.05, z1=0.6):
    """Horizontal bars on the legs (okapi / zebra-like stockings)."""
    def f(co, n, c, s):
        if not (z0 < co.z < z1 * min(s.leg_f, s.leg_h)):
            return c
        band = 0.5 + 0.5 * math.sin(co.z * freq * math.tau / 2 + co.y * 3.0)
        return nh.lerp(c, color, amount * nh.smoothstep(0.55, 0.8, band))
    return f


def collar(color, y0, y1, amount=0.85):
    """A darker (or paler) band around the neck / shoulders between y0 and y1 (model space)."""
    def f(co, n, c, s):
        k = nh.smoothstep(y1, y1 - 0.06, co.y) * nh.smoothstep(y0, y0 + 0.06, co.y)
        if co.z < s.leg_f * 0.85:
            k = 0.0
        return nh.lerp(c, color, amount * k)
    return f


def combine(*fs):
    def f(co, n, c, s):
        for g in fs:
            c = g(co, n, c, s)
        return c
    return f


def lower_legs(color, z1=0.45, amount=0.9):
    def f(co, n, c, s):
        k = 1.0 - nh.smoothstep(z1 * 0.8, z1, co.z / max(min(s.leg_f, s.leg_h), 0.05))
        return nh.lerp(c, color, amount * k)
    return f


def pink_tail(color, amount=0.9):
    """Bare tail (and toes) in skin colour."""
    def f(co, n, c, s):
        L = Layout(s)
        if co.y > L.yh + s.girth[0] * 0.95 and co.z < L.zh + s.girth[1] * 0.6:
            return nh.lerp(c, color, amount)
        return c
    return f


def face(color, t0=0.5, amount=0.9):
    """Bare face skin in front of head-axis position t0."""
    def f(co, n, c, s):
        L = Layout(s)
        d = Vector(co) - L.hb
        t = d.dot(L.F) / s.head_len
        if t > t0 and (d - L.F * d.dot(L.F)).length < s.head_r[1] * 1.6:
            return nh.lerp(c, color, amount * nh.smoothstep(t0, t0 + 0.12, t))
        return c
    return f


# ---------------------------------------------------------------- species extras

def jowl_flanges(b, L, t, size, drop):
    """Entelodont cheek flanges below the eyes and knobs under the chin (fused parts)."""
    s = L.s
    HL = s.head_len
    for sx in (-1, 1):
        b.add(nh.ellipsoid(L.h(t, sx * s.head_r[0] / HL * 0.85, -s.head_r[1] / HL * 0.6 - drop),
                           (size * 0.45, size * 0.9, size * 0.8)), s.coat)
        b.add(nh.ellipsoid(L.h(0.82, sx * s.snout_r[0] / HL * 0.6, -s.snout_r[1] / HL * 1.6),
                           (size * 0.35, size * 0.45, size * 0.5)), s.coat)


def palmate_ossicones(mb, L, color=(0.42, 0.33, 0.24)):
    """Flat, branching palms on the tips of the rear ossicone pair (Sivatherium)."""
    s = L.s
    for hn in s.horns[:2]:
        o = Vector(L.h(hn["t"], hn.get("s", 0), hn.get("u", 0.5)))
        d = Vector(hn["dir"]).normalized()
        tip = o + (d + Vector(hn.get("bend", (0, 0, 0))) * 0.5).normalized() * hn["len"]
        side = d.cross(Vector((0, 1, 0))).normalized()
        k = hn["len"]
        outline = [tip + side * (k * 0.45 * math.cos(a)) + d * (k * 0.25 * math.sin(a)) for a in
                   [i / 10 * math.tau for i in range(10)]]
        mb.add(_panel([tuple(p) for p in outline], k * 0.12), color)
        for j in (-1, 0, 1):
            p = tip + side * (k * 0.32 * j) + d * k * 0.15
            mb.add(nh.tube([tuple(p), tuple(p + (d * 1.0 + side * j * 0.4).normalized() * k * 0.32)],
                           [k * 0.09, k * 0.04], sides=6), color)
