"""
Shared body for the sabre-toothed cats (Machairodontinae) in tools/blender/.

Same rig and layout as lion.py / panthera_onca.py, so the game's Ground walk and
Run gait animate them the same way: one fused quadruped mesh caught mid-stride
(left-front and right-hind forward), the belly kept above the hip line so that
only the four legs swing, front and hind legs well apart along the body, the
tail short or hanging in a loose curve.

  * Spec: withers and croup height (the back slope), body length, girth and limb
    robustness, head size and muzzle length, sabre length / depth / thickness,
    tail curve, coat colours and an optional faint spotting.
  * Head: broad, short-faced machairodont skull with wide cheekbones, a tall
    upper lip that sheathes the canine roots, a lowered mandible ending in a
    deep chin (the mandibular flange), small low ears.
  * build(spec): overlapping anatomy fused into one seamless surface with a faint
    fur texture, repainted procedurally (plain coat, darker back line, pale belly,
    throat and muzzle, dark lip line and ear backs), then crisp details: the
    laterally flattened, backward-curving upper sabres (ivory, darkening a
    little toward the root), the small lower canines, eyes, nose leather,
    whiskers and claws.
  * Faces -Y, pivot on the ground. Prints the hip fraction to use as mapHip.
"""

import math
import sys
from dataclasses import dataclass, field

import bmesh
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

NOSE = (0.30, 0.20, 0.17)
EYE = (0.74, 0.56, 0.20)
PUPIL = (0.02, 0.02, 0.01)
LIP = (0.10, 0.07, 0.05)
WHISKER = (0.93, 0.91, 0.86)
CLAW = (0.76, 0.72, 0.64)
TOOTH = (0.93, 0.89, 0.77)
TOOTH_ROOT = (0.78, 0.70, 0.55)


@dataclass
class Spec:
    name: str
    withers: float = 0.86        # top of the shoulders (jaguar layout: 0.80)
    croup: float = 0.74          # top of the croup (jaguar: 0.76); lower = sloping back
    length: float = 1.0          # stretches the trunk and leg spacing along y
    girth: float = 1.0           # trunk radii
    fore: float = 1.0            # forelimb thickness
    hind: float = 1.0            # hind limb thickness
    paw: float = 1.0
    neck: float = 1.0            # neck thickness
    head: float = 1.0            # head scale
    head_z: float = 0.0          # head carried this much above the withers line (jaguar layout)
    muzzle: float = 0.0          # extra muzzle length (head units)
    sabre: float = 0.19          # exposed upper canine length below the lip (head units)
    sabre_depth: float = 0.020   # fore-aft half-width of the blade at the root
    sabre_flat: float = 0.38     # thickness / depth of the blade cross-section
    tail: tuple = ((0, 0.0, 0.0), (0, 0.10, -0.05), (0, 0.17, -0.12))   # offsets from the tail root
    tail_r: tuple = (0.055, 0.045, 0.035)
    coat: tuple = (0.68, 0.50, 0.30)
    coat_dark: tuple = (0.52, 0.37, 0.21)
    pale: tuple = (0.88, 0.80, 0.66)
    spot: tuple = (0.45, 0.32, 0.19)
    spots: float = 0.0           # 0 = plain coat; ~0.3 = faint spots on the flanks and legs
    tail_tip: float = 0.3        # darkening of the tail tip
    voxel: float = 0.012
    max_tris: int = 19000
    _claws: list = field(default_factory=list)


# ---------------------------------------------------------------- layout

class Layout:
    """Maps jaguar-layout coordinates onto this Spec's proportions."""

    def __init__(self, s):
        self.s = s
        self.fz = s.withers / 0.80     # front legs lengthen with the withers
        self.hz = s.croup / 0.76       # hind legs with the croup

    def trunk(self, x, y, z):
        """Trunk point: y stretched, z lifted along the back slope."""
        s = self.s
        t = nh.smoothstep(-0.30, 0.42, y)
        dz = (s.withers - 0.80) * (1 - t) + (s.croup - 0.76) * t
        return (x, y * s.length, 0.55 + (z - 0.55) * s.girth + dz)

    def front(self, x, y, z):
        return (x, y * self.s.length, z * self.fz)

    def hindp(self, x, y, z):
        return (x, y * self.s.length, z * self.hz)

    @property
    def head_origin(self):
        s = self.s
        y0 = -0.40 * s.length - 0.37 - 0.05 * (s.head - 1.0)
        return Vector((0, y0, s.withers + s.head_z))

    def h(self, x, y, z):
        """Head-local point (origin = cranium centre) to model space."""
        return tuple(self.head_origin + Vector((x, y, z)) * self.s.head)


# ---------------------------------------------------------------- anatomy

def front_leg(b, L, x, stride):
    """Shoulder blade, heavy triceps, thick forearm and a broad paw; stride moves the paw along y."""
    f = L.s.fore
    F = L.front
    b.add(nh.ellipsoid(F(x * 0.92, -0.40, 0.64), (0.075 * f, 0.14, 0.17)), L.s.coat)    # shoulder (scapula) mass
    b.add(nh.ellipsoid(F(x * 1.10, -0.44, 0.46), (0.10 * f, 0.12 * f, 0.14 * f)), L.s.coat)  # triceps
    b.add(nh.tube([F(x * 1.08, -0.47, 0.52), F(x, -0.40, 0.31)], [0.11 * f, 0.09 * f], sides=12), L.s.coat)
    wrist = Vector(F(x, -0.44 + stride, 0.11))
    b.add(nh.tube([F(x, -0.40, 0.33), F(x, -0.42 + stride * 0.5, 0.22), tuple(wrist)],
                  [0.09 * f, 0.074 * f, 0.058 * f], sides=12), L.s.coat)               # forearm
    b.add(nh.ellipsoid(F(x * 1.04, -0.41 + stride * 0.3, 0.28), (0.078 * f, 0.085 * f, 0.10 * f)),
          L.s.coat)                                                                      # forearm muscle
    paw(b, L, Vector((wrist.x, wrist.y - 0.035, 0)), 0.098 * L.s.paw * (0.5 + 0.5 * f))


def hind_leg(b, L, x, stride):
    """Haunch, thigh, gaskin, hock and paw."""
    f = L.s.hind
    H = L.hindp
    b.add(nh.ellipsoid(H(x * 0.9, 0.40, 0.53), (0.13 * f, 0.20 * f, 0.21 * f)), L.s.coat)   # haunch
    b.add(nh.ellipsoid(H(x * 1.04, 0.33, 0.37), (0.105 * f, 0.13 * f, 0.14 * f)), L.s.coat)  # thigh muscle
    knee = Vector(H(x * 1.03, 0.28, 0.30))
    hock = Vector(H(x * 1.03, 0.50 + stride * 0.5, 0.18))
    ankle = Vector(H(x, 0.44 + stride, 0.09))
    b.add(nh.tube([tuple(knee), tuple(hock)], [0.09 * f, 0.055 * f], sides=12), L.s.coat)  # gaskin
    b.add(nh.ellipsoid(H(x * 1.03, 0.40 + stride * 0.2, 0.25), (0.065 * f, 0.09 * f, 0.08 * f)), L.s.coat)
    b.add(nh.tube([tuple(hock), tuple(ankle)], [0.05 * f, 0.047 * f], sides=10), L.s.coat)  # metatarsus
    paw(b, L, Vector((ankle.x, ankle.y - 0.05, 0)), 0.085 * L.s.paw * (0.5 + 0.5 * f))


def paw(b, L, center, r):
    b.add(nh.ellipsoid((center.x, center.y, 0.056), (r, r * 1.12, 0.06)), L.s.coat)
    # four toes in an arc across the front, slightly apart so the voxel surface keeps the gaps
    for a in (-0.78, -0.26, 0.26, 0.78):
        tx = center.x + math.sin(a) * r * 1.05
        ty = center.y - math.cos(a) * r * 1.0 - 0.035
        b.add(nh.ellipsoid((tx, ty, 0.036), (r * 0.34, r * 0.40, 0.038)), L.s.coat)
        d = Vector((math.sin(a) * 0.4, -1.0, 0.0)).normalized()
        L.s._claws.append((Vector((tx, ty, 0.03)) + d * r * 0.37, d))


def torso(b, L):
    s, T, g = L.s, L.trunk, L.s.girth
    b.add(nh.ellipsoid(T(0, -0.22, 0.55), (0.235 * g, 0.36 * s.length, 0.26 * g), subdivisions=4), s.coat)  # chest
    b.add(nh.ellipsoid(T(0, 0.12, 0.55), (0.20 * g, 0.32 * s.length, 0.20 * g), subdivisions=4), s.coat)    # loin
    b.add(nh.ellipsoid(T(0, 0.04, 0.63), (0.19 * g, 0.55 * s.length, 0.16 * g), subdivisions=4), s.coat)    # back
    b.add(nh.ellipsoid(T(0, 0.04, 0.42), (0.16 * g, 0.28 * s.length, 0.09 * g)), s.coat)                    # belly
    b.add(nh.ellipsoid(T(0, 0.40, 0.57), (0.20 * g, 0.21, 0.19 * g), subdivisions=4), s.coat)               # croup
    b.add(nh.ellipsoid(T(0, -0.40, 0.66), (0.17 * g, 0.16, 0.13 * g)), s.coat)                              # withers hump
    b.add(nh.ellipsoid(T(0, -0.50, 0.50), (0.14 * g, 0.14, 0.14 * g)), s.coat)                              # chest / dewlap
    # thick neck from the withers up to the back of the head
    n = s.neck
    base = Vector(T(0, -0.36, 0.63))
    top = Vector(L.h(0, 0.05, -0.01))
    mid = (base + top) * 0.5 + Vector((0, 0, 0.03))
    b.add(nh.tube([tuple(base), tuple(mid), tuple(top)], [0.20 * n, 0.175 * n, 0.14 * n * s.head ** 0.5], sides=14),
          s.coat)
    b.add(nh.ellipsoid(tuple((base + top) * 0.5 + Vector((0, 0, -0.08))), (0.13 * n, 0.15, 0.12 * n)), s.coat)  # throat


def head(b, L):
    s, h, m = L.s, L.h, L.s.muzzle
    c = s.coat
    b.add(nh.ellipsoid(h(0, 0, 0), (0.15, 0.155, 0.14), subdivisions=4), c)          # cranium
    b.add(nh.ellipsoid(h(0, 0.05, 0.05), (0.09, 0.11, 0.10)), c)                      # temporal muscles / crest
    b.add(nh.tube([h(-0.085, -0.115, 0.045), h(0, -0.14, 0.06), h(0.085, -0.115, 0.045)], [0.03, 0.034, 0.03],
                  sides=10), c)                                                       # brow
    for sx in (-1, 1):
        b.add(nh.ellipsoid(h(sx * 0.11, -0.06, -0.05), (0.075, 0.085, 0.06)), c)     # wide cheekbones
        b.add(nh.ellipsoid(h(sx * 0.048, -0.205 - m, -0.09), (0.052, 0.05, 0.062)), c)  # tall upper lip / pads
    b.add(nh.tube([h(0, -0.09, 0.06), h(0, -0.19 - m * 0.6, 0.02), h(0, -0.25 - m, -0.03)], [0.07, 0.064, 0.052],
                  sides=12, scale_xy=(1.3, 0.8)), c)                                  # short broad muzzle
    b.add(nh.tube([h(0, -0.03, -0.11), h(0, -0.20 - m, -0.145)], [0.08, 0.05], sides=12), c)   # mandible
    b.add(nh.ellipsoid(h(0, -0.215 - m, -0.165), (0.052, 0.04, 0.045)), c)            # deep chin flange
    for sx in (-1, 1):
        b.add(nh.ellipsoid(h(sx * 0.112, 0.03, 0.10), (0.042, 0.03, 0.036)), c)      # small low rounded ears


def tail(b, L):
    s = L.s
    root = Vector(L.trunk(0, 0.54, 0.62))
    pts = [tuple(root + Vector(p)) for p in s.tail]
    b.add(nh.tube(pts, list(s.tail_r), sides=12), s.coat)
    b.add(nh.ellipsoid(pts[-1], (s.tail_r[-1],) * 3), s.coat)
    return [Vector(p) for p in pts]


# ---------------------------------------------------------------- paint

class Painter:
    def __init__(self, L, tail_pts, eyes):
        self.L, self.s = L, L.s
        self.tail_pts = tail_pts
        self.eyes = eyes
        self.ho = L.head_origin
        self.hs = L.s.head

    def tail_param(self, p):
        best, best_t, acc = 1e9, 0.0, 0.0
        pts = self.tail_pts
        lens = [(b - a).length for a, b in zip(pts, pts[1:])]
        total = sum(lens)
        for (a, b), ln in zip(zip(pts, pts[1:]), lens):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            d = (p - (a + ab * t)).length
            if d < best:
                best, best_t = d, (acc + t * ln) / total
            acc += ln
        return best, best_t

    def __call__(self, co, n):
        s, p = self.s, co
        q = (p - self.ho) / self.hs        # head-local
        m = s.muzzle
        on_head = q.y < 0.13 and q.z > -0.25 and abs(q.x) < 0.25
        under = nh.smoothstep(-0.25, -0.7, n.z) * (1.0 - nh.smoothstep(0.40, 0.55, p.z / max(s.croup, 0.1) * 0.76))
        inner = 0.0
        if p.z < 0.5 * s.withers / 0.8:
            inner = nh.smoothstep(0.15, 0.55, -n.x * math.copysign(1, p.x)) * nh.smoothstep(0.1, 0.16, abs(p.x))
        throat = 0.0
        if not on_head and p.y < self.ho.y + 0.4:
            throat = nh.smoothstep(-0.1, -0.6, n.z) * nh.smoothstep(self.ho.y + 0.40, self.ho.y + 0.15, p.y)

        c = nh.lerp(nh.lerp(s.pale, s.coat, 0.55), s.coat, nh.smoothstep(-0.3, 0.3, n.z))
        c = nh.lerp(c, s.coat_dark, 0.6 * nh.smoothstep(0.6, 0.95, n.z) * nh.smoothstep(s.croup - 0.1, s.croup, p.z))
        c = nh.lerp(c, s.coat_dark, 0.14 * max(0.0, noise.noise(p * 6.0)))
        white = min(1.0, under * 0.85 + inner * 0.6 + throat * 0.8)
        if p.z < 0.1:
            white *= 0.3
        c = nh.lerp(c, s.pale, white)

        td, tt = self.tail_param(p)
        if td < max(s.tail_r) * 1.4 and p.y > self.tail_pts[0].y - 0.02:
            c = nh.lerp(c, s.coat_dark, s.tail_tip * nh.smoothstep(0.7, 0.95, tt) * 1.6)
        elif on_head:
            muzzle = nh.smoothstep(-0.17 - m, -0.21 - m, q.y) * nh.smoothstep(-0.02, -0.05, q.z)
            chin = nh.smoothstep(-0.125, -0.15, q.z) * nh.smoothstep(-0.12, -0.17, q.y)
            c = nh.lerp(c, s.pale, max(muzzle, chin) * 0.85)
            # dark lip line along the bottom of the upper lip
            if q.y < -0.12 and -0.165 < q.z < -0.135 and abs(q.x) < 0.11 and n.z < 0.3:
                c = nh.lerp(c, LIP, 0.8)
            # dark tear-line and pale fur under the eyes
            for e in self.eyes:
                d = (p - e) / self.hs
                r = Vector((d.x, d.y, d.z * 1.35)).length
                if r < 0.05:
                    c = nh.lerp(c, s.pale, 0.6 * nh.smoothstep(-0.01, -0.03, d.z) * (1 - nh.smoothstep(0.035, 0.05, r)))
                    c = nh.lerp(c, LIP, 0.8 * (1.0 - nh.smoothstep(0.032, 0.040, r)))
            # ear backs dark
            if q.z > 0.08 and abs(q.x) > 0.075 and n.y > 0.1 and q.y > -0.02:
                c = nh.lerp(c, LIP, 0.55)
        elif s.spots > 0 and p.z > 0.12:
            # faint, small solid spots on flanks and legs (a reconstruction choice)
            sp = spots(p, 15.0, 0.30)
            c = nh.lerp(c, s.spot, s.spots * sp * (1.0 - white))
        return c


def spots(p, freq, size):
    q = p * freq + Vector((5.0, 2.5, 1.25))
    dist, pts = noise.voronoi(q, distance_metric="DISTANCE")
    h = noise.noise(pts[0] * 2.7) * 0.5 + 0.5
    r = size * (0.6 + 0.6 * h)
    wob = 0.08 * noise.noise(q * 2.0)
    return 1.0 - nh.smoothstep(r - 0.08, r + 0.06, dist[0] + wob)


def fur_displace(co):
    if co.z < 0.04:
        return 0.0
    return 0.0018 * noise.noise(co * 40.0) + 0.001 * noise.noise(Vector((co.x * 80.0, co.y * 25.0, co.z * 80.0)))


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        """First surface point along a ray (falls back to the nearest point)."""
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal


def find_eyes(L, surf):
    eyes, normals = [], []
    for sx in (-1, 1):
        p, n = surf.hit(L.h(sx * 0.068, 0.0, 0.025), (sx * 0.12, -1, 0))
        eyes.append(p)
        normals.append(n)
    return eyes, normals


def sabre(mb, L, sx, length, depth, flat, inset=0.0):
    """Laterally flattened canine: root hidden in the upper lip, curving down and back."""
    h, m = L.h, L.s.muzzle
    k = L.s.head
    root = Vector(h(sx * 0.046, -0.215 - m, -0.07 - inset))
    pts, radii = [], []
    steps = 7
    for i in range(steps + 1):
        t = i / steps
        # anterior edge convex: the blade bows forward a little then the tip curves back
        y = -0.012 * math.sin(t * math.pi) + 0.05 * t * t
        pts.append(tuple(root + Vector((sx * 0.004 * t, y, -length * t)) * k))
        radii.append(depth * k * (1.0 - t ** 1.6) ** 0.8 if i < steps else 0.0)
    col = lambda co, n: nh.lerp(TOOTH, TOOTH_ROOT, nh.smoothstep(root.z - 0.08 * k, root.z, co.z))
    mb.add(nh.tube(pts, radii, sides=10, scale_xy=(1.0, flat)), col)


def details(mb, L, surf, eyes, normals):
    s, h, m = L.s, L.h, L.s.muzzle
    k = s.head
    for i, sx in enumerate((-1, 1)):
        e = eyes[i]
        look = (normals[i] * 0.4 + Vector((sx * 0.15, -1, 0.05))).normalized()
        mb.add(nh.ellipsoid(tuple(e - look * 0.013 * k), (0.025 * k, 0.025 * k, 0.019 * k), subdivisions=3), EYE)
        mb.add(nh.ellipsoid(tuple(e + look * 0.0075 * k), (0.010 * k, 0.010 * k, 0.011 * k), subdivisions=2), PUPIL)
        # whiskers fanning out from the pads
        for j in range(4):
            a = math.radians(-16 + j * 10)
            start, n = surf.hit(h(sx * 0.07, -0.10 - m, -0.075 + j * 0.011), (0, -1, 0))
            end = start + Vector((sx * math.cos(a) * 0.17, 0.06, math.sin(a) * 0.05)) * k
            mb.add(nh.tube([tuple(start - n * 0.004), tuple(end)], [0.0025, 0.0], sides=3), WHISKER)
        # the sabres, and small lower canines just behind them
        sabre(mb, L, sx, s.sabre, s.sabre_depth, s.sabre_flat)
        lc, _n = surf.hit(h(sx * 0.03, -0.10 - m, -0.15), (0, -1, 0.0))
        mb.add(nh.tube([tuple(lc + Vector((0, 0.006, -0.004))), tuple(lc + Vector((0, 0.0, 0.026 * k)))],
                       [0.008 * k, 0.0], sides=6), TOOTH)
    # nose leather on the end of the short muzzle
    p, n = surf.hit(h(0, -0.60, 0.15), Vector(h(0, -0.20 - m, -0.03)) - Vector(h(0, -0.60, 0.15)))
    mb.add(nh.ellipsoid(tuple(p + Vector((0, 0.004, 0))), (0.032 * k, 0.012 * k, 0.018 * k), subdivisions=2,
                        deform=lambda v: 1.0 - 0.35 * max(0.0, -v.z)), NOSE)
    # claws peeking out of the toe fur
    for tip, d in s._claws:
        base = tip - d * 0.01
        mb.add(nh.tube([base, tip + d * 0.012 + Vector((0, 0, -0.016))], [0.007, 0.0], sides=6), CLAW)


def build(s):
    s._claws.clear()
    L = Layout(s)
    b = nh.MeshBuilder()
    torso(b, L)
    # walking: left-front and right-hind forward
    front_leg(b, L, -0.15 * s.girth, -0.12)
    front_leg(b, L, 0.15 * s.girth, 0.10)
    hind_leg(b, L, -0.16 * s.girth, 0.08)
    hind_leg(b, L, 0.16 * s.girth, -0.10)
    head(b, L)
    tail_pts = tail(b, L)
    fused = b.fuse(voxel=s.voxel, smooth=5, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * fur_displace(v.co)
    fused.normal_update()

    surf = Surface(fused)
    eyes, normals = find_eyes(L, surf)
    # belly height (just behind the forelegs) for mapHip
    belly, _n = surf.hit((0, 0.0, 0.0), (0, 0, 1))
    mb = nh.MeshBuilder()
    mb.add(fused, color=Painter(L, tail_pts, eyes))
    details(mb, L, surf, eyes, normals)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"{s.name}: belly at {belly.z:.3f}, height {top:.3f}, mapHip ~ {belly.z / top:.2f}")
    return obj


def closeup(path, target, dist, az, el, lens=60):
    """Extra render aimed at `target` (after nh.run set up the scene and camera)."""
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    target = Vector(target)
    cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main(spec, ground):
    """nh.run() plus a head close-up (out_head.png) when rendering."""
    from pathlib import Path
    nh.run(lambda: build(spec), spec.name, ground=ground, views=((35, 25), (-90, 8), (20, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        target = Layout(spec).h(0, -0.12, -0.12)
        closeup(out.with_name(out.stem + "_head.png"), target, 1.0 * spec.head, 50, 8)
