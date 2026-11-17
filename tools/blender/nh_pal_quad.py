"""
Parametric four-legged (or hopping two-legged) mammal for the Paleogene species in
tools/blender/ (pakicetus_attocki.py, uintatherium_anceps.py, mesohippus_bairdi.py ...).

One Spec describes the proportions in model units (the body is ~1.5-2.2 long):
trunk length / heights / girth, leg thickness and foot type, neck, head and snout,
ears, tail, plus a list of horns / tusks / knobs (Horn) and colours. The parts are
overlapping primitives fused into one seamless surface, repainted procedurally
(coat, darker back line, pale belly, optional stripes / dapples / face mask), then
crisp details (eyes, nose, hooves, claws, tusks) are added on top.

Layout (like lion.py / nh_sabretooth.py): faces -Y, pivot on the ground, shoulders
at y = -length/2, hips at y = +length/2, the four legs caught mid-stride
(left-front and right-hind forward) and the belly kept above the hip line so that
only the legs swing on the map. build() prints the belly / height fraction to use
as mapHip.

Species scripts may pass `extra(b, L)` (more shells before fusing) and
`details(mb, L, surf)` (crisp parts after fusing) for anatomy the Spec can't express.
"""

import math
import sys
from dataclasses import dataclass, field

import bmesh
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

EYE = (0.05, 0.035, 0.025)
EYE_SHINE = (0.30, 0.22, 0.14)
HOOF = (0.16, 0.13, 0.10)
CLAW = (0.20, 0.17, 0.14)
NOSE = (0.12, 0.09, 0.08)
TOOTH = (0.92, 0.88, 0.76)


@dataclass
class Horn:
    """A cone on the head (head-local coordinates: origin = cranium centre, x right, -y forward, z up;
    in head units, i.e. multiplied by Spec.head_len). bend bends the tip toward bend_dir."""
    base: tuple
    direction: tuple
    length: float
    radius: float
    color: tuple = (0.55, 0.48, 0.40)
    fuse: bool = False          # skin-covered bony horn (fused into the head) or crisp tusk / horn
    bend: float = 0.0
    bend_dir: tuple = (0, 0, 1)
    flat: float = 1.0           # cross-section aspect (blade-like sabres < 1)
    mirror: bool = True         # also add the mirrored one at -x
    tip: float = 0.0            # tip radius fraction (blunt knobs > 0)


@dataclass
class Spec:
    name: str
    length: float = 0.9          # shoulder to hip along y
    shoulder: float = 0.8        # top of the back over the shoulders
    hip: float = 0.78            # top of the back over the hips
    width: float = 0.17          # trunk half-width
    depth: float = 0.2           # trunk half-depth at the chest
    belly: float = 1.0           # >1 = barrel / pot belly
    hump: float = 0.0            # withers hump height
    arch: float = 0.0            # raises the middle of the back
    fore_r: float = 0.07         # upper forelimb radius
    hind_r: float = 0.08         # thigh radius
    shin: float = 0.55           # lower-leg radius as a fraction of the upper
    foot: str = "paw"            # paw, hoof, pad (columnar), web (big splayed feet), hand
    foot_r: float = 0.06
    toes: int = 4
    hock: float = 0.6            # how far the hock sits behind the foot (digitigrade / unguligrade); 0 = columnar
    stride: float = 0.1
    neck_len: float = 0.3
    neck_angle: float = 35.0     # degrees above horizontal
    neck_r: float = 0.11
    head_len: float = 0.3        # cranium + snout length scale; head-local units are multiplied by this
    head_w: float = 0.42         # cranium half-width (head units)
    head_h: float = 0.42         # cranium half-height (head units)
    snout: float = 0.6           # snout length beyond the cranium (head units)
    snout_r: tuple = (0.28, 0.18)  # snout radius at root / tip (head units)
    snout_flat: float = 1.0      # snout width / height ratio
    snout_tilt: float = 15.0     # degrees the snout points down
    head_tilt: float = 0.0       # extra pitch of the whole head (degrees, + = nose down)
    jaw: float = 0.8             # lower jaw length as a fraction of the snout
    jaw_r: float = 0.17
    ear: float = 0.18            # ear length (head units); 0 = none
    ear_shape: str = "point"     # point, round
    ear_angle: float = 20.0      # tilt outward (degrees)
    eye: float = 0.07            # eye radius (head units)
    eye_pos: tuple = (0.32, -0.30, 0.16)  # head-local eye centre (x magnitude), pushed onto the surface
    eye_up: bool = False         # eyes looking upward (Pakicetus)
    nose_col: tuple = None       # nose leather colour (None = no nose pad)
    tail_len: float = 0.5
    tail_r: float = 0.05
    tail_angle: float = -30.0    # degrees from horizontal (negative = hanging)
    tail_curl: float = 0.0       # extra bend toward the tip (degrees)
    tail_tuft: float = 0.0       # tuft / brush radius at the tip
    tail_bush: float = 0.0       # bushy tail: radius stays thick to the tip (0-1)
    horns: list = field(default_factory=list)
    coat: tuple = (0.5, 0.4, 0.3)
    back: tuple = None           # dorsal colour (None = darker coat)
    pale: tuple = (0.8, 0.72, 0.6)
    pale_amt: float = 0.8
    dark_legs: float = 0.0       # darken the lower legs (0-1)
    stripes: int = 0             # vertical stripe count on the trunk / haunches
    stripe_col: tuple = (0.25, 0.2, 0.15)
    stripe_amt: float = 0.6
    dapple: float = 0.0          # light spots on the flanks (0-1)
    dapple_col: tuple = (0.85, 0.8, 0.7)
    mask: tuple = None           # face mask colour (dark eye band / face)
    muzzle_col: tuple = None     # colour of the snout tip
    mane: float = 0.0            # short upright mane along the neck (radius)
    mane_col: tuple = (0.2, 0.15, 0.1)
    skin: float = 0.0            # wrinkly / hairless skin texture strength
    fur: float = 1.0             # fur noise strength
    biped: bool = False          # hops / runs on long hind legs, short forelimbs off the ground
    voxel: float = 0.016
    max_tris: int = 14000
    ground: tuple = (0.45, 0.45, 0.32)


# ---------------------------------------------------------------- layout

class Layout:
    def __init__(self, s):
        self.s = s
        L2 = s.length / 2
        self.sh = Vector((0, -L2, s.shoulder - s.depth))     # chest centre
        self.hp = Vector((0, L2, s.hip - s.depth * 0.85))    # rump centre
        a = math.radians(s.neck_angle)
        self.neck0 = self.sh + Vector((0, -s.depth * 0.45, s.depth * 0.45))
        self.head_c = self.neck0 + Vector((0, -math.cos(a), math.sin(a))) * s.neck_len
        self.pitch = math.radians(s.head_tilt)

    def h(self, x, y, z):
        """Head-local (head units) -> model space."""
        s = self.s
        c, sn = math.cos(self.pitch), math.sin(self.pitch)
        y2, z2 = y * c + z * sn, -y * sn + z * c
        return tuple(self.head_c + Vector((x, y2, z2)) * s.head_len)

    def hv(self, x, y, z):
        """Head-local direction -> model space (unit)."""
        c, sn = math.cos(self.pitch), math.sin(self.pitch)
        return Vector((x, y * c + z * sn, -y * sn + z * c)).normalized()

    def snout_dir(self):
        t = math.radians(self.s.snout_tilt)
        return (0, -math.cos(t), -math.sin(t))

    def snout_pt(self, f):
        """Point along the snout axis, f = 0 at the cranium front, 1 at the tip (head-local)."""
        s = self.s
        d = self.snout_dir()
        start = Vector((0, -0.25, -0.05))
        return start + Vector(d) * s.snout * f


# ---------------------------------------------------------------- anatomy

def torso(b, L):
    s, c = L.s, L.s.coat
    w, d = s.width, s.depth
    sh, hp = L.sh, L.hp
    mid = (sh + hp) * 0.5 + Vector((0, 0, -d * 0.08 * (s.belly - 1)))
    b.add(nh.ellipsoid(tuple(sh), (w, d * 1.25, d), subdivisions=4), c)                         # chest
    b.add(nh.ellipsoid(tuple(mid), (w * s.belly, s.length * 0.42, d * 0.95 * s.belly), subdivisions=4), c)
    b.add(nh.ellipsoid(tuple(hp), (w * 0.9, d * 1.1, d * 0.9), subdivisions=4), c)             # rump
    b.add(nh.tube([tuple(sh + Vector((0, 0, d * 0.3))), tuple(mid + Vector((0, 0, d * 0.35 + s.arch))),
                   tuple(hp + Vector((0, 0, d * 0.3)))], [d * 0.75, d * 0.75, d * 0.65], sides=14,
                  scale_xy=(w / d * 1.05, 1.0)), c)                                              # back
    if s.hump > 0:
        b.add(nh.ellipsoid(tuple(sh + Vector((0, d * 0.1, d * 0.55))), (w * 0.7, d * 0.9, d * 0.4 + s.hump)), c)
    # neck from the chest to the back of the head
    base = L.neck0
    top = Vector(L.h(0, 0.15, -0.05))
    m = (base + top) * 0.5 + Vector((0, 0, s.neck_r * 0.2))
    b.add(nh.tube([tuple(base - Vector((0, -d * 0.2, 0))), tuple(m), tuple(top)],
                  [s.neck_r * 1.25, s.neck_r, s.neck_r * 0.85], sides=14), c)
    if s.mane > 0:
        b.add(nh.tube([tuple(base + Vector((0, 0.02, s.neck_r * 1.1))), tuple(m + Vector((0, 0, s.neck_r * 0.95))),
                       tuple(top + Vector((0, 0.02, s.neck_r * 0.8)))], [s.mane * 0.6, s.mane, s.mane * 0.7],
                      sides=8, scale_xy=(0.35, 1.0)), s.mane_col)


def leg(b, L, x, front, stride):
    s, c = L.s, L.s.coat
    if s.biped and front:
        # short arms held under the chest
        r = s.fore_r
        sh = L.sh + Vector((x * 0.7, -s.depth * 0.3, -s.depth * 0.2))
        el = sh + Vector((0, 0.02, -s.depth * 0.9))
        wr = el + Vector((0, -s.depth * 0.6, -s.depth * 0.1))
        b.add(nh.tube([tuple(sh), tuple(el), tuple(wr)], [r, r * 0.8, r * 0.6], sides=10), c)
        b.add(nh.ellipsoid(tuple(wr + Vector((0, -r * 0.5, 0))), (r * 0.8, r * 1.1, r * 0.6)), c)
        return
    if front:
        r = s.fore_r
        top = L.sh + Vector((x * 0.75, -s.depth * 0.15, s.depth * 0.1))
        elbow = Vector((x, L.sh.y + s.depth * 0.15, L.sh.z - s.depth * 0.85))
        foot = Vector((x * 1.02, L.sh.y - 0.02 + stride, 0))
        wrist = Vector((foot.x, foot.y + 0.005, s.foot_r * 1.6 + (elbow.z - s.foot_r) * 0.18))
        b.add(nh.ellipsoid(tuple(top), (r * 1.15, r * 2.0, r * 2.4)), c)                        # shoulder mass
        b.add(nh.tube([tuple(top), tuple(elbow)], [r * 1.25, r * 1.05], sides=12), c)            # upper arm
        b.add(nh.tube([tuple(elbow), tuple((elbow + wrist) * 0.5), tuple(wrist)],
                      [r * 0.95, r * (0.6 + s.shin * 0.4), r * s.shin], sides=12), c)            # forearm
        b.add(nh.tube([tuple(wrist), tuple(foot + Vector((0, 0, s.foot_r)))], [r * s.shin, r * s.shin * 0.9],
                      sides=10), c)
    else:
        r = s.hind_r
        top = L.hp + Vector((x * 0.8, 0.0, s.depth * 0.15))
        knee = Vector((x * 1.04, L.hp.y - s.depth * 0.35, L.hp.z - s.depth * 0.95))
        foot = Vector((x * 1.02, L.hp.y + 0.03 + stride, 0))
        hz = s.foot_r * 1.6 + (knee.z - s.foot_r) * (0.15 + 0.35 * s.hock)
        hock = Vector((foot.x, foot.y + s.hock * (knee.z * 0.35) + 0.01, hz))
        b.add(nh.ellipsoid(tuple(top + Vector((0, 0, -s.depth * 0.25))), (r * 1.3, r * 2.4, r * 2.6)), c)  # haunch
        b.add(nh.tube([tuple(top), tuple(knee)], [r * 1.3, r * 1.0], sides=12), c)               # thigh
        b.add(nh.tube([tuple(knee), tuple((knee + hock) * 0.5), tuple(hock)],
                      [r * 0.95, r * (0.55 + s.shin * 0.4), r * s.shin * 0.95], sides=12), c)     # shank
        b.add(nh.tube([tuple(hock), tuple(foot + Vector((0, 0, s.foot_r)))], [r * s.shin * 0.85, r * s.shin * 0.8],
                      sides=10), c)
    foot_shell(b, L, foot, front)


def foot_shell(b, L, foot, front):
    s, c = L.s, L.s.coat
    fr = s.foot_r * (1.0 if front else 1.05)
    if s.foot == "hoof":
        b.add(nh.tube([tuple(foot + Vector((0, 0, fr * 1.8))), tuple(foot + Vector((0, -fr * 0.15, 0.002)))],
                      [fr * 0.85, fr], sides=12), HOOF)
    elif s.foot == "pad":
        b.add(nh.tube([tuple(foot + Vector((0, 0, fr * 1.6))), tuple(foot + Vector((0, 0, 0.002)))],
                      [fr * 0.95, fr * 1.05], sides=14), c)
    elif s.foot == "web":
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -fr * 0.9, fr * 0.35))), (fr * 1.1, fr * 2.0, fr * 0.35)), c)
    else:  # paw / hand
        long = 1.4 if s.foot == "hand" else 1.15
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -fr * 0.4, fr * 0.55))), (fr, fr * long, fr * 0.6)), c)
        n = max(1, s.toes)
        for i in range(n):
            a = (i / max(1, n - 1) - 0.5) * 1.5 if n > 1 else 0.0
            t = foot + Vector((math.sin(a) * fr * 0.85, -fr * long * 0.95 - math.cos(a) * fr * 0.25, fr * 0.3))
            b.add(nh.ellipsoid(tuple(t), (fr * 0.28, fr * 0.38, fr * 0.3)), c)


def head(b, L):
    s, c, h = L.s, L.s.coat, L.h
    k = s.head_len
    b.add(nh.ellipsoid(h(0, 0, 0), (s.head_w * k, 0.42 * k, s.head_h * k), subdivisions=4), c)   # cranium
    sr0, sr1 = s.snout_r
    pts = [tuple(Vector(h(*L.snout_pt(f)))) for f in (0.0, 0.5, 1.0)]
    rr = [sr0 * k, (sr0 + sr1) * 0.5 * k, sr1 * k]
    b.add(nh.tube(pts, rr, sides=14, scale_xy=(s.snout_flat, 1.0)), c)
    b.add(nh.ellipsoid(pts[-1], (sr1 * k * s.snout_flat, sr1 * k * 0.9, sr1 * k)), c)            # rounded tip
    # face: bridges the cranium into the snout so the head reads as one deep wedge
    fc = Vector(L.snout_pt(0.22)) + Vector((0, 0, 0.02))
    b.add(nh.ellipsoid(h(*fc), (s.head_w * 0.82 * k, (0.3 + s.snout * 0.22) * k, s.head_h * 0.85 * k)), c)
    if s.snout > 0.5:
        fm = Vector(L.snout_pt(0.5))
        b.add(nh.ellipsoid(h(*fm), (sr0 * 0.95 * s.snout_flat * k, s.snout * 0.3 * k, sr0 * 0.95 * k)), c)
    if s.jaw > 0:
        j0 = Vector(L.snout_pt(0.0)) + Vector((0, 0.15, -s.snout_r[0] * 0.55))
        j1 = Vector(L.snout_pt(s.jaw)) + Vector((0, 0, -s.snout_r[1] * 0.75))
        b.add(nh.tube([h(*j0), h(*j1)], [s.jaw_r * k, s.jaw_r * 0.65 * k], sides=12,
                      scale_xy=(s.snout_flat * 0.9, 1.0)), c)
    if s.ear > 0:
        for sx in (-1, 1):
            base = Vector((sx * s.head_w * 0.6, 0.18, s.head_h * 0.75))
            a = math.radians(s.ear_angle)
            tipd = Vector((sx * math.sin(a), 0.25, math.cos(a))).normalized()
            if s.ear_shape == "round":
                cen = base + tipd * s.ear * 0.5
                b.add(nh.ellipsoid(h(*cen), (s.ear * 0.5 * k, s.ear * 0.18 * k, s.ear * 0.55 * k)), c)
            else:
                tip = base + tipd * s.ear
                b.add(nh.tube([h(*base), h(*(base + tipd * s.ear * 0.45)), h(*tip)],
                              [s.ear * 0.32 * k, s.ear * 0.26 * k, 0.0], sides=8, scale_xy=(1.0, 0.6)), c)
    for hn in s.horns:
        if hn.fuse:
            for shell, col in horn_shells(L, hn):
                b.add(shell, col)


def horn_shells(L, hn):
    out = []
    k = L.s.head_len
    for sx in ((1, -1) if hn.mirror else (1,)):
        base = Vector((hn.base[0] * sx, hn.base[1], hn.base[2]))
        d = Vector((hn.direction[0] * sx, hn.direction[1], hn.direction[2])).normalized()
        bd = Vector((hn.bend_dir[0] * sx, hn.bend_dir[1], hn.bend_dir[2])).normalized()
        pts, rr = [], []
        n = 6
        p = base.copy()
        for i in range(n + 1):
            t = i / n
            pts.append(L.h(*p))
            rr.append(hn.radius * k * ((1 - t) + hn.tip * t) if i < n or hn.tip > 0 else 0.0)
            step = (d + bd * hn.bend * t).normalized() * hn.length / n
            p = p + step
        out.append((nh.tube(pts, rr, sides=10, scale_xy=(hn.flat, 1.0)), hn.color))
        if hn.tip > 0:
            out.append((nh.ellipsoid(pts[-1], (rr[-1] * hn.flat,) * 1 + (rr[-1], rr[-1])), hn.color))
    return out


def tail(b, L):
    s = L.s
    if s.tail_len <= 0:
        return []
    root = L.hp + Vector((0, s.depth * 0.85, s.depth * 0.35))
    pts = [root]
    n = 6
    a = math.radians(s.tail_angle)
    for i in range(1, n + 1):
        t = i / n
        ang = a + math.radians(s.tail_curl) * t * t
        pts.append(pts[-1] + Vector((0, math.cos(ang), math.sin(ang))) * s.tail_len / n)
    rr = []
    for i in range(n + 1):
        t = i / n
        thin = 1.0 - 0.75 * t
        bush = 1.0 + 0.5 * math.sin(t * math.pi * 0.8)
        rr.append(max(s.voxel * 1.3, s.tail_r * (thin * (1 - s.tail_bush) + bush * s.tail_bush)))
    b.add(nh.tube([tuple(p) for p in pts], rr, sides=10), s.coat)
    b.add(nh.ellipsoid(tuple(pts[-1]), (rr[-1],) * 3), s.coat)
    if s.tail_tuft > 0:
        b.add(nh.ellipsoid(tuple(pts[-1]), (s.tail_tuft * 0.8, s.tail_tuft * 1.3, s.tail_tuft)), s.back or s.coat)
    return pts


# ---------------------------------------------------------------- paint

class Painter:
    def __init__(self, L, tail_pts):
        self.L, self.s = L, L.s
        self.tail_pts = tail_pts
        s = L.s
        self.back = s.back or tuple(c * 0.72 for c in s.coat)

    def __call__(self, co, n):
        s, L, p = self.s, self.L, co
        c = s.coat
        top = max(s.shoulder, s.hip)
        # dorsal darkening
        c = nh.lerp(c, self.back, nh.smoothstep(0.3, 0.9, n.z) * nh.smoothstep(top * 0.6, top * 0.95, p.z))
        # pale underside (belly, throat, inner legs)
        under = nh.smoothstep(-0.15, -0.65, n.z)
        if p.z < 0.1 * top:
            under *= 0.2
        c = nh.lerp(c, s.pale, under * s.pale_amt)
        # stripes across the back and haunches
        if s.stripes and L.sh.y - s.depth < p.y < L.hp.y + s.depth * 1.2 and p.z > top * 0.35:
            u = (p.y - (L.sh.y - s.depth * 0.5)) / (s.length + s.depth * 1.5)
            band = 0.5 + 0.5 * math.cos(u * s.stripes * math.tau + 0.4 * noise.noise(p * 4))
            c = nh.lerp(c, s.stripe_col, s.stripe_amt * nh.smoothstep(0.55, 0.85, band) * nh.smoothstep(-0.3, 0.3, n.z + 0.2))
        if s.dapple > 0 and p.z > top * 0.3 and L.sh.y - s.depth < p.y < L.hp.y + s.depth:
            v = noise.noise(p * 14.0)
            c = nh.lerp(c, s.dapple_col, s.dapple * nh.smoothstep(0.25, 0.4, v) * nh.smoothstep(-0.5, 0.2, n.z))
        # lower legs
        if s.dark_legs > 0 and p.z < top * 0.35:
            c = nh.lerp(c, self.back, s.dark_legs * nh.smoothstep(top * 0.35, top * 0.15, p.z))
        # face
        q = Vector(p) - L.head_c
        if s.mask is not None and q.length < s.head_len * 0.9:
            ey = Vector(L.h(s.eye_pos[0], s.eye_pos[1], s.eye_pos[2]))
            dz = abs(p.z - ey.z) / s.head_len
            if dz < 0.12 and p.y < L.head_c.y + 0.1 * s.head_len:
                c = nh.lerp(c, s.mask, 0.75 * (1 - nh.smoothstep(0.06, 0.12, dz)))
        if s.muzzle_col is not None:
            tip = Vector(L.h(*L.snout_pt(1.0)))
            dd = (Vector(p) - tip).length / s.head_len
            c = nh.lerp(c, s.muzzle_col, 1 - nh.smoothstep(0.15, 0.35, dd))
        # mottling
        c = nh.lerp(c, self.back, 0.12 * max(0.0, noise.noise(p * 7.0)))
        return c


def displace(bm, s):
    bm.normal_update()
    for v in bm.verts:
        if v.co.z < 0.03:
            continue
        p = v.co
        d = 0.0012 * s.fur * noise.noise(p * 45.0)
        if s.skin > 0:
            d += 0.004 * s.skin * noise.noise(Vector((p.x * 30, p.y * 12, p.z * 40)))
        v.co += v.normal * d
    bm.normal_update()


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal


def details(mb, L, surf):
    s, k = L.s, L.s.head_len
    for sx in (-1, 1):
        ex, ey, ez = s.eye_pos
        target = Vector(L.h(sx * ex * 0.3, ey, ez))
        origin = target + Vector((sx * 2.0, 0, 0.6 if s.eye_up else 0.0))
        p, n = surf.hit(origin, target - origin)
        r = s.eye * k
        mb.add(nh.ellipsoid(tuple(p - n * r * 0.5), (r, r, r * 0.85), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(tuple(p + n * r * 0.45 + Vector((0, -r * 0.2, r * 0.25))), (r * 0.25,) * 3,
                            subdivisions=1), EYE_SHINE)
    if s.nose_col is not None:
        tip = Vector(L.h(*(L.snout_pt(1.0) + Vector(L.snout_dir()) * 1.0)))
        p, n = surf.hit(tip, Vector(L.h(*L.snout_pt(0.6))) - tip)
        r = s.snout_r[1] * k
        mb.add(nh.ellipsoid(tuple(p + n * r * 0.05), (r * 0.75 * s.snout_flat, r * 0.25, r * 0.5), subdivisions=2),
               s.nose_col)
    for hn in s.horns:
        if not hn.fuse:
            for shell, col in horn_shells(L, hn):
                mb.add(shell, col)


def build(s, extra=None, more=None):
    L = Layout(s)
    b = nh.MeshBuilder()
    torso(b, L)
    w = s.width * 0.78
    leg(b, L, -w, True, -s.stride)
    leg(b, L, w, True, s.stride)
    leg(b, L, -w * 1.05, False, s.stride)
    leg(b, L, w * 1.05, False, -s.stride)
    head(b, L)
    tail_pts = tail(b, L)
    if extra:
        extra(b, L)
    fused = b.fuse(voxel=s.voxel, smooth=5, smooth_factor=0.5, max_tris=s.max_tris)
    displace(fused, s)
    surf = Surface(fused)
    belly, _n = surf.hit((0, 0.0, -0.5), (0, 0, 1))
    mb = nh.MeshBuilder()
    paint = Painter(L, tail_pts)
    # keep hoof colour (painted on the parts) where the fused surface came from hooves
    col = fused.loops.layers.color["Col"]
    for f in fused.faces:
        for l in f.loops:
            c0 = l[col]
            if s.foot == "hoof" and l.vert.co.z < s.foot_r * 1.9 and abs(c0[0] - HOOF[0]) < 0.12 and c0[0] < 0.3:
                continue
            pc = paint(l.vert.co, l.vert.normal)
            # fused horns keep their own colour
            if any(abs(c0[i] - hn.color[i]) < 0.03 for hn in s.horns if hn.fuse for i in range(3)) and \
                    any(all(abs(c0[i] - hn.color[i]) < 0.05 for i in range(3)) for hn in s.horns if hn.fuse):
                pc = (c0[0], c0[1], c0[2])
            if s.mane > 0 and all(abs(c0[i] - s.mane_col[i]) < 0.05 for i in range(3)):
                pc = s.mane_col
            l[col] = (pc[0], pc[1], pc[2], 1.0)
    mb.add(fused)
    details(mb, L, surf)
    if more:
        more(mb, L, surf)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    zmin_shift = 0.0
    print(f"{s.name}: belly at {belly.z:.3f}, height {top:.3f}, mapHip ~ {belly.z / top:.2f}")
    return obj


def main(spec, extra=None, more=None):
    nh.run(lambda: build(spec, extra, more), spec.name, ground=spec.ground,
           views=((35, 20), (-90, 5), (150, 35)))
