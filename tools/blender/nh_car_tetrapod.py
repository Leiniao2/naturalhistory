"""
Parametric sprawling tetrapod for the Carboniferous batch (petrolacosaurus_kansensis.py,
archaeothyris_florensis.py, westlothiana_lizziae.py, crassigyrinus_scoticus.py,
pederpes_finneyae.py, proterogyrinus_scheelei.py, amphibamus_grandiceps.py).

One seamless fused body lofted along a spine (snout at -Y): head, neck, trunk and a
tapering tail (optionally deepened into a swimming fin), with four sprawling legs whose
upper segments stick out sideways and lower segments reach down to the ground. Painted
procedurally from the spine parameters (countershading plus stripes / bands / blotches),
then crisp eyes, teeth and toes are added on top.

Ground animals pivot on the ground; with Spec.swim the legs are folded back along the
flanks and the model is centred on its bounding box (Swim style).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh


@dataclass
class Spec:
    name: str
    # lengths along the spine (model units; whole animal ~1.2)
    head_len: float = 0.16
    head_w: float = 0.045        # half-width at the widest point
    head_h: float = 0.028        # half-height
    snout: float = 0.35          # snout tip half-width as a fraction of head_w
    neck_len: float = 0.05
    neck_r: float = 0.032
    trunk_len: float = 0.40
    trunk_r: float = 0.06
    trunk_h: float = 0.80        # trunk z-radius as a fraction of trunk_r
    tail_len: float = 0.55
    tail_r: float = 0.035        # radius at the tail root
    tail_fin: float = 1.0        # tail z / x radius ratio (>1 = deep paddle tail)
    tail_curve: float = 0.12     # sideways swing of the tail tip
    # legs
    leg_r: float = 0.016
    front: tuple = (0.07, 0.07)  # upper, lower segment lengths
    hind: tuple = (0.08, 0.08)
    foot: float = 0.04           # longest toe
    toes: int = 5
    body_z: float = 0.0          # spine height; 0 = from the legs
    swim: bool = False
    # colours
    back: tuple = (0.30, 0.26, 0.16)
    flank: tuple = (0.46, 0.40, 0.26)
    belly: tuple = (0.78, 0.72, 0.54)
    pattern: str = "stripes"     # stripes, bands, blotches, spots, none
    pattern_col: tuple = (0.14, 0.11, 0.07)
    pattern_scale: float = 1.0
    head_col: tuple = None
    iris: tuple = (0.75, 0.55, 0.15)
    eye_r: float = 0.011
    eye_at: float = 0.55         # eye position along the head (0 snout tip .. 1 back)
    eye_up: float = 0.55         # eye height on the head (fraction of head_h above centre)
    teeth: int = 0               # teeth per side along the upper jaw (0 = none)
    tooth_len: float = 0.008
    lateral_line: bool = False
    voxel: float = 0.006
    max_tris: int = 6000
    extra: list = field(default_factory=list)  # callables(spec, spine) -> [(bm, colour)]


PUPIL = (0.02, 0.02, 0.02)
CLAW = (0.10, 0.08, 0.06)
TOOTH = (0.94, 0.92, 0.84)
LIP = (0.12, 0.09, 0.07)


class Spine:
    def __init__(self, sp):
        self.sp = sp
        h, n, t, l = sp.head_len, sp.neck_len, sp.trunk_len, sp.tail_len
        self.s_head, self.s_neck, self.s_trunk, self.s_end = h, h + n, h + n + t, h + n + t + l
        legs_front = sp.front[1]
        self.z = sp.body_z or (legs_front * 0.92 + 0.004)
        if sp.swim:
            self.z = 0.0
        self.n = 120
        self.pts, self.s = [], []
        for i in range(self.n + 1):
            s = self.s_end * i / self.n
            x = 0.0
            if s > self.s_trunk:
                u = (s - self.s_trunk) / l
                x = -sp.tail_curve * u * u
            z = self.z
            if s < self.s_head:  # head held a touch above the body line
                z += 0.15 * sp.head_h * (1 - s / self.s_head)
            if s > self.s_trunk and not sp.swim:  # tail droops toward the ground
                u = (s - self.s_trunk) / l
                z = self.z - (self.z - max(self.rz(s), 0.003)) * nh.smoothstep(0.0, 0.8, u) * 0.9
            self.pts.append(Vector((x, s - self.s_end * 0.45, z)))
            self.s.append(s)

    def rx(self, s):
        sp = self
        p = self.sp
        key = [(0.0, p.head_w * p.snout), (p.head_len * 0.25, p.head_w * (0.55 + 0.45 * p.snout)),
               (p.head_len * 0.75, p.head_w), (p.head_len, p.head_w * 0.85),
               (sp.s_head + p.neck_len * 0.5, p.neck_r),
               (sp.s_neck + p.trunk_len * 0.2, p.trunk_r), (sp.s_neck + p.trunk_len * 0.65, p.trunk_r),
               (sp.s_trunk, (p.trunk_r + p.tail_r) * 0.5), (sp.s_trunk + p.tail_len * 0.1, p.tail_r),
               (sp.s_end * 0.999, 0.003), (sp.s_end, 0.001)]
        return _interp(key, s)

    def rz(self, s):
        p = self.sp
        hz = p.head_h / max(p.head_w, 1e-6)
        key = [(0.0, hz * 0.8), (p.head_len * 0.8, hz), (self.s_head + p.neck_len * 0.5, 0.95),
               (self.s_neck + p.trunk_len * 0.2, p.trunk_h), (self.s_trunk - p.trunk_len * 0.1, p.trunk_h),
               (self.s_trunk + p.tail_len * 0.25, p.tail_fin), (self.s_end, p.tail_fin)]
        return self.rx(s) * _interp(key, s)

    def at(self, s):
        i = max(0, min(self.n, int(round(s / self.s_end * self.n))))
        return self.pts[i]

    def nearest(self, co):
        best, bi = 1e9, 0
        for i, p in enumerate(self.pts):
            d = (p - co).length_squared
            if d < best:
                best, bi = d, i
        return self.s[bi], self.pts[bi], math.sqrt(best)


def _interp(key, s):
    for (s0, r0), (s1, r1) in zip(key, key[1:]):
        if s <= s1:
            t = (s - s0) / max(s1 - s0, 1e-6)
            t = t * t * (3 - 2 * t)
            return r0 + (r1 - r0) * t
    return key[-1][1]


def loft(sp_, sides=20):
    """Elliptical rings along the spine, perpendicular to it in plan view."""
    bm = bmesh.new()
    rings = []
    for i, (p, s) in enumerate(zip(sp_.pts, sp_.s)):
        a = sp_.pts[max(i - 1, 0)]
        b = sp_.pts[min(i + 1, sp_.n)]
        fwd = (b - a)
        fwd.z = 0
        fwd.normalize()
        side = Vector((-fwd.y, fwd.x, 0.0))
        rx, rz = sp_.rx(s), sp_.rz(s)
        if i == 0 or i == sp_.n:
            rings.append([bm.verts.new(p)])
            continue
        ring = []
        for k in range(sides):
            ang = k / sides * math.tau
            c, si = math.cos(ang), math.sin(ang)
            z = rz * si
            if s < sp_.s_head and si < 0:  # flatter jaw underside
                z *= 0.8
            ring.append(bm.verts.new(p + side * rx * c + Vector((0, 0, z))))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def legs(sp, spine):
    """(root, knee, foot, toe direction, radius, hind) for each leg."""
    out = []
    for hind in (False, True):
        s = spine.s_neck + sp.trunk_len * (0.1 if not hind else 0.92)
        root = spine.at(s).copy()
        r = spine.rx(s)
        up_len, lo_len = sp.hind if hind else sp.front
        lr = sp.leg_r * (1.1 if hind else 1.0)
        for sx in (-1, 1):
            phase = sx * (1 if hind else -1) * 0.35
            if sp.swim:
                rt = root + Vector((sx * r * 0.7, 0, -spine.rz(s) * 0.4))
                kn = rt + Vector((sx * up_len * 0.75, up_len * 0.55, -0.004))
                ft = kn + Vector((sx * lo_len * 0.35, lo_len * 0.9, -0.002))
                fwd = Vector((sx * 0.25, 1.0, 0)).normalized()
            else:
                rt = root + Vector((sx * r * 0.6, 0, -spine.rz(s) * 0.35))
                kn = rt + Vector((sx * up_len * 0.95, -phase * up_len * 0.6, up_len * 0.12))
                ft = Vector((kn.x + sx * lo_len * 0.25, kn.y - phase * lo_len * 0.4, lr * 0.5))
                fwd = Vector((sx * (0.55 if hind else 0.35), -1.0, 0)).normalized()
            out.append((rt, kn, ft, fwd, lr, hind))
    return out


def parts(sp, spine):
    ps = [loft(spine)]
    for rt, kn, ft, _fwd, r, hind in legs(sp, spine):
        ps.append(nh.tube([rt, (rt + kn) / 2 + Vector((0, 0, r * 0.3)), kn], [r * 1.5, r * 1.2, r], sides=10))
        ps.append(nh.tube([kn, (kn + ft) / 2, ft], [r * 0.95, r * 0.8, r * 0.7], sides=10))
        ps.append(nh.ellipsoid(ft, (r * 1.2, r * 1.4, r * 0.6), subdivisions=2))
        if hind:
            ps.append(nh.ellipsoid(rt * 0.6 + kn * 0.4, (r * 2.0, r * 1.7, r * 1.5), subdivisions=2))
    return ps


def make_paint(sp, spine):
    head_col = sp.head_col or sp.back

    def paint(co, n):
        s, p, d = spine.nearest(co)
        rx, rz = max(spine.rx(s), 1e-3), max(spine.rz(s), 1e-3)
        up = (co.z - p.z) / rz
        side = (co.x - p.x) / rx
        coarse = noise.noise(co * 18.0 / sp.pattern_scale)
        fine = noise.noise(co * 140.0)
        if d > max(rx, rz) * 1.35 and spine.s_head < s < spine.s_trunk + 0.05:   # legs
            c = nh.lerp(sp.flank, sp.back, nh.smoothstep(-0.3, 0.6, n.z))
            c = nh.lerp(c, sp.belly, 0.25 * nh.smoothstep(0.0, -0.8, n.z))
        else:
            c = nh.lerp(sp.flank, sp.back, nh.smoothstep(-0.25, 0.55, up + 0.15 * coarse))
            if s < spine.s_head:
                c = nh.lerp(c, head_col, 0.6 * nh.smoothstep(-0.1, 0.5, up))
            pat = 0.0
            ps = sp.pattern_scale
            if sp.pattern == "stripes" and s > spine.s_head * 0.6:
                pat = math.exp(-((abs(side) - 0.5) / 0.17) ** 2) * nh.smoothstep(0.1, 0.5, up)
                pat *= 0.65 + 0.35 * math.sin(s * 60.0 / ps + coarse * 2.0)
            elif sp.pattern == "bands" and s > spine.s_head:
                ring = ((s - spine.s_head) / (0.07 * ps)) % 1.0
                pat = (1.0 if ring < 0.38 else 0.0) * nh.smoothstep(-0.5, 0.2, up)
            elif sp.pattern == "blotches" and s > spine.s_head * 0.5:
                pat = nh.smoothstep(0.15, 0.35, coarse) * nh.smoothstep(-0.4, 0.2, up)
            elif sp.pattern == "spots":
                pat = nh.smoothstep(0.42, 0.5, noise.noise(co * 45.0 / ps)) * nh.smoothstep(-0.3, 0.2, up)
            c = nh.lerp(c, sp.pattern_col, max(0.0, min(1.0, pat)))
            if sp.lateral_line and abs(up) < 0.06 and spine.s_head < s < spine.s_trunk:
                c = nh.lerp(c, sp.belly, 0.4)
            c = nh.lerp(c, sp.belly, nh.smoothstep(-0.15, -0.7, up))
            if s < spine.s_head * 0.95 and abs(up + 0.3) < 0.07 and abs(side) > 0.5:
                c = LIP
        if fine > 0.55 and n.z > 0.1:
            c = nh.lerp(c, sp.belly, 0.25)
        k = 0.92 + 0.16 * (0.5 + 0.5 * coarse)
        return (c[0] * k, c[1] * k, c[2] * k)
    return paint


def details(sp, spine, tree):
    out = []
    toe_col = sp.flank
    for rt, kn, ft, fwd, r, hind in legs(sp, spine):
        side = Vector((-fwd.y, fwd.x, 0.0))
        n = sp.toes
        base = Vector((ft.x, ft.y, 0.0 if not sp.swim else ft.z)) + fwd * r * 0.5
        for k in range(n):
            a = (k / max(n - 1, 1) - 0.5) * 1.9
            d = (fwd * math.cos(a) + side * math.sin(a)).normalized()
            L = sp.foot * (0.6 + 0.4 * math.sin(math.pi * (k + 1) / (n + 1))) * (1.1 if hind else 0.9)
            p0 = base + Vector((0, 0, r * 0.45))
            p2 = base + d * L
            p2.z = (r * 0.2) if not sp.swim else base.z
            tr = r * 0.32
            out.append((nh.tube([p0, (p0 + p2) / 2 + Vector((0, 0, r * 0.1)), p2], [tr, tr * 0.85, tr * 0.7], sides=5),
                        toe_col))
            out.append((nh.tube([p2, p2 + d * tr * 2.2], [tr * 0.6, 0.0], sides=4), CLAW))
    # eyes
    s_eye = sp.head_len * sp.eye_at
    p = spine.at(s_eye)
    z = p.z + spine.rz(s_eye) * sp.eye_up
    for sx in (-1, 1):
        loc, nrm, _i, _d = tree.ray_cast(Vector((p.x + sx * 0.5, p.y, z)), Vector((-sx, 0, 0)))
        if loc is None:
            continue
        look = Vector((sx * 0.85, -0.35, 0.45)).normalized()
        c = loc - look * sp.eye_r * 0.35

        def eye_col(co, n, c=c, lk=look):
            k = (co - c).normalized().dot(lk)
            return PUPIL if k > 0.82 else (sp.iris if k > 0.45 else (0.10, 0.08, 0.06))
        out.append((nh.ellipsoid(c, (sp.eye_r, sp.eye_r * 1.1, sp.eye_r), subdivisions=2), eye_col))
        # teeth along the upper jaw
        for t in range(sp.teeth):
            s = sp.head_len * (0.04 + 0.8 * t / max(sp.teeth - 1, 1))
            q = spine.at(s)
            zl = q.z - spine.rz(s) * 0.3
            loc, nrm, _i, _d = tree.ray_cast(Vector((q.x + sx * 0.5, q.y, zl)), Vector((-sx, 0, 0)))
            if loc is None:
                continue
            L = sp.tooth_len * (1.6 if t in (1, 2) else 1.0)
            b = loc + Vector((-sx * L * 0.25, 0, 0))
            out.append((nh.tube([b + Vector((0, 0, L * 0.2)), b + Vector((sx * L * 0.1, 0, -L))],
                                [L * 0.3, 0.0], sides=4), TOOTH))
    for fn in sp.extra:
        out += fn(sp, spine)
    return out


def drop_islands(bm, min_verts=60):
    seen = set()
    for start in list(bm.verts):
        if start in seen or not start.is_valid:
            continue
        part, stack = [], [start]
        seen.add(start)
        while stack:
            v = stack.pop()
            part.append(v)
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in seen:
                    seen.add(o)
                    stack.append(o)
        if len(part) < min_verts:
            bmesh.ops.delete(bm, geom=part, context="VERTS")


def build(sp):
    spine = Spine(sp)
    body = nh.MeshBuilder()
    for p in parts(sp, spine):
        body.add(p, sp.flank)
    fused = body.fuse(voxel=sp.voxel, smooth=4, smooth_factor=0.5, max_tris=sp.max_tris)
    drop_islands(fused)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * sp.voxel * 0.12 * noise.noise(v.co * 90.0)
    fused.normal_update()
    tree = BVHTree.FromBMesh(fused)
    extra = details(sp, spine, tree)
    mb = nh.MeshBuilder()
    mb.add(fused, color=make_paint(sp, spine))
    for bm, col in extra:
        mb.add(bm, col, smooth=False)
    obj = mb.to_object(sp.name, roughness=0.5)
    if sp.swim:
        centre(obj)
    else:
        nh.ground_to_zero(obj)
    return obj


def centre(obj):
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c


def run(sp, ground=(0.30, 0.27, 0.18), background=(0.20, 0.28, 0.18)):
    views = ((35, 25), (-90, 8), (160, 60))
    if sp.swim:
        nh.run(lambda: build(sp), sp.name, background=(0.06, 0.18, 0.22), views=views)
    else:
        nh.run(lambda: build(sp), sp.name, ground=ground, background=background, views=views)
