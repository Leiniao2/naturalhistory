"""
Shared builder for the flea models: xenopsylla_cheopis.py, ctenocephalides_felis.py and
ctenocephalides_canis.py.

Fleas (Siphonaptera) are small wingless insects flattened from side to side, so they slip
between hairs or feathers. The model stands on its six legs, facing -Y:
  * a small helmet-like head whose side outline is set per species (Spec.head_len,
    head_h, frons, tip): a long, low, sloping forehead in Ctenocephalides felis, a short
    domed one in C. canis. Below it hang the piercing-sucking mouthparts (the stylet
    bundle between the segmented maxillary and labial palps); on its side sit a dark
    eye and, behind it, the short clubbed antenna folded back into its groove;
  * the thorax (pronotum, mesonotum, metanotum) and a deep, rounded abdomen of eight
    visible segments, each sclerotised plate overlapping the next like shingles, with
    a darker hind margin carrying a row of backward-pointing bristles;
  * optional combs (ctenidia) of flat, dark, backward-pointing spines: the genal comb
    along the lower margin of the head (Spec.genal: spine lengths front to back) and the
    pronotal comb along the hind margin of the pronotum (Spec.pronotal: spines per side);
  * three pairs of flattened, spiny legs on big plate-like coxae; the hind legs are much
    the largest (huge coxa and femur) for jumping, with five-segmented tarsi and paired
    claws on the ground.
The body, head and coxae are lofted, sculpted (the plate shingles are displaced into the
loft) and fused into one seamless shell, then repainted procedurally with a baked gloss
highlight (the map shader is diffuse only). Legs, combs, bristles, eye, antennae and
mouthparts are crisp separate shells. The flea is ~1.1 units long; pivot on the ground
under its feet (z = 0).

  * build(spec) -> (object, info) with info["hip_z"] / info["height"] for mapHip.
"""

import math
from pathlib import Path
from dataclasses import dataclass

import bmesh
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

LIGHT_DIR = Vector((-0.55, -0.45, 0.70)).normalized()


@dataclass
class Spec:
    name: str
    # head side outline
    head_len: float = 0.21          # along Y
    head_h: float = 0.16            # height at the back of the head
    head_w: float = 0.075           # half-width
    frons: float = 2.0              # forehead curve exponent: 2 = round dome, ~1.3 = long and sloping
    tip: float = 0.35               # height of the head's front point (fraction of head_h)
    eye_r: float = 0.022
    eye_color: tuple = (0.03, 0.02, 0.015)
    # combs
    genal: tuple = ()               # genal comb spine lengths, front to back; () = no comb
    pronotal: int = 0               # pronotal comb spines per side; 0 = no comb
    pronotal_len: float = 0.058
    comb_color: tuple = (0.06, 0.03, 0.02)
    # colours
    body_color: tuple = (0.5, 0.3, 0.15)
    dark_color: tuple = (0.25, 0.12, 0.05)     # plate margins, underside shading
    leg_color: tuple = (0.6, 0.4, 0.2)
    seta_color: tuple = (0.12, 0.07, 0.04)
    mouth_color: tuple = (0.55, 0.38, 0.20)
    gloss: float = 0.45
    seta_len: float = 0.068
    ocular: bool = True             # stout ocular bristle in front of the eye


# ---------------------------------------------------------------- profiles

Y_NECK = -0.33                       # front of the pronotum
HEAD_BOTTOM = 0.19                   # ventral margin of the head at its back

# thorax + abdomen side profile: dorsal line, ventral line, half-width
KEY_Y = [-0.36, -0.33, -0.26, -0.18, -0.10, -0.02, 0.06, 0.14, 0.22, 0.30, 0.37, 0.43, 0.48, 0.52]
KEY_T = [0.34, 0.355, 0.40, 0.45, 0.50, 0.55, 0.58, 0.60, 0.61, 0.60, 0.57, 0.52, 0.46, 0.39]
KEY_B = [0.21, 0.21, 0.205, 0.20, 0.19, 0.18, 0.17, 0.165, 0.165, 0.17, 0.19, 0.22, 0.27, 0.33]
KEY_W = [0.060, 0.064, 0.071, 0.076, 0.080, 0.084, 0.088, 0.090, 0.089, 0.085, 0.077, 0.064, 0.047, 0.026]
Y_END = 0.535

# tergite boundaries (pronotum, meso-, metanotum, abdominal I-VIII)
SEGS = [-0.335, -0.255, -0.175, -0.095] + [-0.095 + 0.0745 * k for k in range(1, 9)]


def interp(ys, vs, y):
    if y <= ys[0]:
        return vs[0]
    if y >= ys[-1]:
        return vs[-1]
    for i in range(len(ys) - 1):
        if ys[i] <= y <= ys[i + 1]:
            t = (y - ys[i]) / (ys[i + 1] - ys[i])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5
            return vs[i] + (vs[i + 1] - vs[i]) * t
    return vs[-1]


def top(y):
    return interp(KEY_Y, KEY_T, y)


def bot(y):
    return interp(KEY_Y, KEY_B, y)


def hw(y):
    return interp(KEY_Y, KEY_W, y)


def local_v(co):
    """-1 at the ventral line .. +1 at the dorsal line."""
    t, b = top(co.y), bot(co.y)
    return (co.z - (t + b) * 0.5) / max((t - b) * 0.5, 1e-3)


def plate(y, v):
    """(segment index, phase 0..1 within the plate) or (-1, 0) outside the plated body."""
    ye = y - 0.035 * v                   # plate margins lean back toward the top
    if ye < SEGS[0] or ye >= SEGS[-1]:
        return -1, 0.0
    for i in range(len(SEGS) - 1):
        if SEGS[i] <= ye < SEGS[i + 1]:
            return i, (ye - SEGS[i]) / (SEGS[i + 1] - SEGS[i])
    return -1, 0.0


def shingle(t):
    """Height profile of one plate: rises toward its hind margin, then drops under the next."""
    return nh.smoothstep(0.0, 0.85, t) * (1.0 - nh.smoothstep(0.88, 1.0, t))


def q(u, a):
    """Superellipse quadrant 0 -> 1."""
    u = min(max(u, 0.0), 1.0)
    return (1.0 - (1.0 - u) ** a) ** (1.0 / a)


class Head:
    def __init__(self, s):
        self.s = s
        self.y0 = Y_NECK - s.head_len + 0.02
        self.zf = HEAD_BOTTOM + s.tip * s.head_h

    def y(self, u):
        return self.y0 + u * self.s.head_len

    def u(self, y):
        return (y - self.y0) / self.s.head_len

    def top(self, u):
        return self.zf + (HEAD_BOTTOM + self.s.head_h - self.zf) * q(u, self.s.frons)

    def bot(self, u):
        return self.zf - (self.zf - HEAD_BOTTOM) * q(u, 2.2)

    def w(self, u):
        return self.s.head_w * q(u, 2.0) ** 0.8


# ---------------------------------------------------------------- shells

def loft(rings_spec, sides, tip_front, tip_back):
    """rings_spec: list of (y, half-width, z_bottom, z_top, power, disp fn(y, a) or None)."""
    bm = bmesh.new()
    rings = []
    if tip_front is not None:
        rings.append([bm.verts.new(tip_front)])
    for y, w, zb, zt, p, disp in rings_spec:
        zc, h = (zt + zb) * 0.5, (zt - zb) * 0.5
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            cu, sv = math.cos(a), math.sin(a)
            ex = 2.0 / p
            pt = Vector((w * math.copysign(abs(cu) ** ex, cu), y, zc + h * math.copysign(abs(sv) ** ex, sv)))
            if disp:
                n = Vector((cu * h, 0.0, sv * w)).normalized()
                pt += n * disp(y, sv)
            ring.append(bm.verts.new(pt))
        rings.append(ring)
    if tip_back is not None:
        rings.append([bm.verts.new(tip_back)])
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
    # close open ends so the voxel remesh sees a solid
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def body_shell():
    def disp(y, v):
        i, t = plate(y, v)
        return 0.0075 * shingle(t) if i >= 0 else 0.0
    specs = []
    y = KEY_Y[0]
    while y < KEY_Y[-1]:
        specs.append((y, hw(y), bot(y), top(y), 2.5, disp))
        y += 0.006
    return loft(specs, 40, None, Vector((0, Y_END, 0.36)))


def head_shell(head):
    specs = []
    n = 26
    for i in range(1, n + 1):
        u = (i / n) ** 1.4 * 1.12          # crowd rings toward the rounded front
        specs.append((head.y(u), head.w(u), head.bot(u), head.top(u), 2.2, None))
    tip = Vector((0, head.y(0.0) - 0.004, head.zf))
    return loft(specs, 32, tip, None)


# coxae: centre (y, z), radii (x, y, z), forward tilt in degrees
COXAE = [((-0.335, 0.165), (0.030, 0.042, 0.075), 25),
         ((-0.195, 0.160), (0.030, 0.040, 0.065), 5),
         ((-0.030, 0.185), (0.036, 0.078, 0.105), -12)]
COXA_X = 0.058


def coxa_frames():
    for (y, z), r, tilt in COXAE:
        for s in (-1, 1):
            yield Vector((s * (COXA_X + r[0] * 0.3), y, z)), r, Matrix.Rotation(math.radians(tilt), 3, "X")


def in_coxa(co, margin=1.25):
    for c, r, rot in coxa_frames():
        d = rot.inverted() @ (co - c)
        if (d.x / r[0]) ** 2 + (d.y / r[1]) ** 2 + (d.z / r[2]) ** 2 < margin:
            return True
    return False


# ---------------------------------------------------------------- paint

def glossy(base, dark, n, gloss, sharp=14):
    c = nh.lerp(dark, base, nh.smoothstep(-0.7, 0.4, n.z))
    h = max(0.0, n.dot(LIGHT_DIR)) ** sharp
    return nh.lerp(c, (0.95, 0.88, 0.78), h * gloss)


def painter(s, head):
    def paint(co, n):
        if in_coxa(co, 1.1) and co.z < 0.26:
            c = glossy(s.leg_color, s.dark_color, n, s.gloss * 0.8)
        else:
            c = glossy(s.body_color, s.dark_color, n, s.gloss)
            v = local_v(co)
            i, t = plate(co.y, v)
            if i >= 0 and co.y > Y_NECK - 0.005:
                c = nh.lerp(c, s.dark_color, 0.75 * nh.smoothstep(0.78, 0.96, t))
                c = nh.lerp(c, nh.lerp(s.body_color, (1, 1, 1), 0.15), 0.4 * (1.0 - nh.smoothstep(0.0, 0.22, t)))
            elif co.y < Y_NECK:
                u = head.u(co.y)
                # darker oral margin and front of the head
                c = nh.lerp(c, s.dark_color, 0.45 * (1.0 - nh.smoothstep(0.0, 0.25, u)))
                c = nh.lerp(c, s.dark_color, 0.35 * nh.smoothstep(0.02, -0.03, co.z - head.bot(u) - 0.02))
        k = 0.93 + 0.12 * noise.noise(co * 35.0)
        return tuple(min(1.0, x * k) for x in c)
    return paint


# ---------------------------------------------------------------- details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, nrm, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, nrm


def bristle(mb, base, d, length, r, color, curl=None):
    d = d.normalized()
    curl = curl if curl is not None else Vector((0, 0, 0))
    tip = base + d * length + curl * length * 0.12      # straight cone, tip bent back toward the body
    mb.add(nh.tube([base, tip], [r, 0.0], sides=3), color, smooth=False)


def spine(mb, base, d, length, r, color, flat):
    """Flat comb spine: a tapering blade, flattened by `flat` (tube side / up scale)."""
    d = d.normalized()
    mb.add(nh.tube([base, base + d * length * 0.7, base + d * length], [r, r * 0.7, 0.0], sides=4,
                   scale_xy=flat), color, smooth=False)


def combs(mb, s, head, surf):
    comb_col = lambda co, n: glossy(s.comb_color, s.comb_color, n, 0.6, sharp=10)
    if s.genal:
        n = len(s.genal)
        for k, L in enumerate(s.genal):
            u = 0.24 + 0.56 * k / max(n - 1, 1)
            y = head.y(u)
            z = head.bot(u) + 0.022 + 0.10 * (head.top(u) - head.bot(u))
            for sx in (-1, 1):
                loc, nrm = surf.hit((sx * 0.5, y, z), (-sx, 0, 0))
                if loc is None:
                    continue
                d = Vector((sx * 0.22, 1.0, -0.58 + 0.22 * k / max(n - 1, 1)))
                spine(mb, loc + nrm * 0.002, d, L * 1.25, 0.0125, comb_col, (0.4, 1.0))
    if s.pronotal:
        y = SEGS[1] - 0.012
        zc = (top(y) + bot(y)) * 0.5
        for k in range(s.pronotal):
            phi = math.radians(6 + 112 * k / max(s.pronotal - 1, 1))
            for sx in (-1, 1):
                out = Vector((sx * math.sin(phi), 0, math.cos(phi)))
                ye = y + 0.035 * math.cos(phi)   # follow the leaning hind margin
                loc, nrm = surf.hit(Vector((0, ye, zc)) + out * 0.6, -out)
                if loc is None:
                    continue
                d = Vector((0, 1.0, 0)) + nrm * 0.75 - Vector((0, 0, 0.08))
                spine(mb, loc - nrm * 0.008, d, s.pronotal_len, 0.0125, comb_col, (0.75, 0.9))


def body_bristles(mb, s, surf):
    rows = []
    for i in range(len(SEGS) - 1):
        a, b = SEGS[i], SEGS[i + 1]
        heights = (0.88, 0.62, 0.34, 0.05) if i >= 3 else (0.85, 0.55, 0.25)
        if i == 0:
            continue                      # pronotum: comb or nothing
        for v in heights:
            rows.append((a + (b - a) * 0.80 + 0.035 * v, v, 1.0 if i >= 3 else 0.8))
        if i >= 4:
            rows.append((a + (b - a) * 0.75 - 0.03 * 0.45, -0.45, 0.8))   # sternite bristles
    for y, v, scale in rows:
        zc = (top(y) + bot(y)) * 0.5
        h = (top(y) - bot(y)) * 0.5
        z = zc + v * h
        for sx in (-1, 1):
            loc, nrm = surf.hit((sx * 0.6, y, z), (-sx, 0, 0))
            if loc is None or nrm.dot(Vector((sx, 0, 0))) < 0.1 and v < 0.8:
                continue
            d = Vector((0, 1.0, -0.10)) + nrm * 0.65
            bristle(mb, loc - nrm * 0.003, d, s.seta_len * scale, 0.0038, s.seta_color, curl=-nrm * 0.5)
    # long antesensilial bristle and a few at the tail end
    for sx in (-1, 1):
        loc, nrm = surf.hit((sx * 0.6, 0.47, 0.44), (-sx, 0, 0))
        if loc is not None:
            bristle(mb, loc, Vector((0, 1, 0.25)) + nrm * 0.3, s.seta_len * 1.5, 0.005, s.seta_color, curl=-nrm)


def head_details(mb, s, head, surf):
    for sx in (-1, 1):
        # eye, mid-height on the side of the head
        u = 0.50
        z = (head.top(u) + head.bot(u)) * 0.5 + 0.004
        loc, nrm = surf.hit((sx * 0.5, head.y(u), z), (-sx, 0, 0))
        if loc is not None:
            c = loc - nrm * (s.eye_r * 0.45)
            look = nrm

            def eye_col(co, n, c=c, look=look):
                k = max(0.0, n.dot(LIGHT_DIR)) ** 20
                return nh.lerp(s.eye_color, (0.85, 0.8, 0.7), k * 0.8)
            mb.add(nh.uv_ellipsoid(c, (s.eye_r * 0.7, s.eye_r, s.eye_r), 10, 6), eye_col)
            if s.ocular:
                bristle(mb, loc + Vector((0, -s.eye_r * 1.3, s.eye_r * 0.4)),
                        Vector((0, 0.6, 0.5)) + nrm * 0.4, s.seta_len * 0.8, 0.0045, s.seta_color, curl=-nrm)
        # short clubbed antenna folded back in its groove behind the eye
        u = 0.82
        z = (head.top(u) + head.bot(u)) * 0.5 - 0.005
        loc, nrm = surf.hit((sx * 0.5, head.y(u), z), (-sx, 0, 0))
        if loc is not None:
            c = loc + nrm * 0.004
            rot = Matrix.Rotation(math.radians(32), 4, "X")
            club = nh.uv_ellipsoid((0, 0, 0), (0.010, 0.017, 0.034), 8, 6)
            nh.transform(club, Matrix.Translation(c) @ rot)
            ac = nh.lerp(s.leg_color, s.dark_color, 0.25)

            def ant_col(co, n, c=c, ac=ac):
                ring = 0.5 + 0.5 * math.sin((co.z - c.z) / 0.011 * math.pi)
                return glossy(nh.lerp(ac, s.dark_color, 0.35 * ring), s.dark_color, n, s.gloss * 0.6)
            mb.add(club, ant_col)
        # occipital bristles at the back of the head
        for v in (0.7, 0.3):
            u = 0.93
            z = head.bot(u) + (head.top(u) - head.bot(u)) * (0.5 + 0.5 * v)
            loc, nrm = surf.hit((sx * 0.5, head.y(u), z), (-sx, 0, 0))
            if loc is not None:
                bristle(mb, loc, Vector((0, 1, 0.05)) + nrm * 0.4, s.seta_len * 0.8, 0.0045, s.seta_color, curl=-nrm)
    # mouthparts: stylet bundle between the labial palps, maxillary palps either side
    u = 0.16
    p0 = Vector((0, head.y(u) + 0.01, head.bot(u) + 0.012))
    mc = s.mouth_color
    mb.add(nh.tube([p0, p0 + Vector((0, 0.025, -0.07)), p0 + Vector((0, 0.05, -0.125))],
                   [0.0075, 0.006, 0.002], sides=5), nh.lerp(mc, s.dark_color, 0.3))
    for sx in (-1, 1):
        lp = [p0 + Vector((sx * 0.010, 0.004, 0)), p0 + Vector((sx * 0.012, 0.03, -0.065)),
              p0 + Vector((sx * 0.012, 0.052, -0.118))]
        mb.add(nh.tube(lp, [0.0065, 0.0058, 0.004], sides=5), mc)
        mp = [p0 + Vector((sx * 0.028, -0.005, 0.005)), p0 + Vector((sx * 0.034, -0.02, -0.03)),
              p0 + Vector((sx * 0.036, -0.025, -0.058)), p0 + Vector((sx * 0.036, -0.018, -0.085))]
        mb.add(nh.tube(mp, [0.0075, 0.0068, 0.006, 0.004], sides=5), mc)


# legs: hip (y, z) on the coxa, knee (y, z), ankle (y, z), tarsus tip (y), x at the hip/knee/ankle/foot,
# femur radius, tibia radius
LEGS = [
    ((-0.375, 0.105), (-0.440, 0.150), (-0.470, 0.035), -0.560, (0.062, 0.080, 0.095, 0.105), 0.023, 0.016),
    ((-0.205, 0.100), (-0.285, 0.150), (-0.245, 0.032), -0.150, (0.065, 0.098, 0.122, 0.135), 0.024, 0.016),
    ((0.000, 0.090), (-0.120, 0.120), (0.110, 0.030), 0.320, (0.078, 0.108, 0.140, 0.150), 0.038, 0.020),
]


def legs(mb, s):
    lc = lambda co, n: glossy(s.leg_color, s.dark_color, n, s.gloss * 0.8)
    for (hy, hz), (ky, kz), (ay, az), ty, xs, fr, tr in LEGS:
        for sx in (-1, 1):
            hip = Vector((sx * xs[0], hy, hz))
            knee = Vector((sx * xs[1], ky, kz))
            ankle = Vector((sx * xs[2], ay, az))
            foot = Vector((sx * xs[3], ty, 0.0))
            flat = (0.55, 1.0)
            # trochanter + femur (broad, flattened), tibia, five-segmented tarsus
            mid = hip.lerp(knee, 0.45) + Vector((0, 0, fr * 0.25))
            mb.add(nh.tube([hip, mid, knee], [fr * 0.8, fr, fr * 0.6], sides=6, scale_xy=flat), lc)
            mb.add(nh.uv_ellipsoid(knee, (fr * 0.45, fr * 0.6, fr * 0.6), 6, 4), lc)
            mb.add(nh.tube([knee, knee.lerp(ankle, 0.5), ankle], [tr, tr * 1.1, tr * 0.85], sides=5, scale_xy=flat),
                   lc)
            # tarsus: segments shorten toward the claws
            fr_ = [0.0, 0.36, 0.58, 0.74, 0.87, 1.0]
            pts = [ankle.lerp(foot, f) for f in fr_]
            for k in range(1, len(pts) - 1):
                pts[k].z = max(pts[k].z, 0.004 + 0.02 * (1 - fr_[k]) * az / 0.035)
            radii = [tr * 0.8, tr * 0.6, tr * 0.55, tr * 0.5, tr * 0.45, tr * 0.38]
            tpts, trad = [], []
            for k, (p, r) in enumerate(zip(pts, radii)):   # pinch at each joint
                if k:
                    tpts.append(pts[k - 1].lerp(p, 0.75))
                    trad.append(r * 1.15)
                tpts.append(p)
                trad.append(r * 0.8)
            mb.add(nh.tube(tpts, trad, sides=4), lc)
            # paired claws
            d = (foot - pts[-2]).normalized()
            for k in (-1, 1):
                c1 = foot + d * 0.012 + Vector((k * 0.004, 0, 0))
                c2 = c1 + d * 0.008 + Vector((0, 0, -0.008))
                mb.add(nh.tube([foot, c1, c2], [0.004, 0.003, 0.0], sides=3), s.seta_color, smooth=False)
            # spines along the back edge of the tibia and the femur
            td = (ankle - knee)
            for k in range(3):
                p = knee + td * (0.3 + 0.25 * k)
                bristle(mb, p + Vector((sx * 0.002, 0, 0)), td.normalized() * 0.9 + Vector((sx * 0.3, 0.45, 0.2)),
                        0.03, 0.0038, s.seta_color)
            for k in range(1):
                p = hip.lerp(knee, 0.55) + Vector((0, 0, fr * 0.7))
                bristle(mb, p, (knee - hip).normalized() + Vector((sx * 0.3, 0, 0.5)), 0.03, 0.0038, s.seta_color)


# ---------------------------------------------------------------- build

def build(spec):
    s = spec
    head = Head(s)
    body = nh.MeshBuilder()
    body.add(body_shell(), s.body_color)
    body.add(head_shell(head), s.body_color)
    for c, r, rot in coxa_frames():
        body.add(nh.ellipsoid(c, r, subdivisions=3, rotation=rot), s.leg_color)
    fused = body.fuse(voxel=0.0095, smooth=4, smooth_factor=0.5, max_tris=2100)

    surf = Surface(fused)
    mb = nh.MeshBuilder()
    combs(mb, s, head, surf)
    body_bristles(mb, s, surf)
    head_details(mb, s, head, surf)
    legs(mb, s)
    mb.add(fused, color=painter(s, head))
    obj = mb.to_object(s.name, roughness=0.35)
    zmin = min(v.co.z for v in obj.data.vertices)
    nh.ground_to_zero(obj)
    height = max(v.co.z for v in obj.data.vertices)
    hip_z = 0.11 - zmin
    print(f"height {height:.3f}, hip {hip_z:.3f} -> mapHip {hip_z / height:.2f}")
    return obj, {"hip_z": hip_z, "height": height}


def render_extra(path):
    """Head and comb close-ups, using the camera and light set up by nh.render_preview."""
    import bpy
    scene = bpy.context.scene
    cam = scene.camera
    target = Vector((0, -0.40, 0.25))
    for i, (az, el, dist) in enumerate(((-90, 5, 0.75), (-40, 20, 0.8))):
        a, e = math.radians(az), math.radians(el)
        cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        out = Path(path)
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


def run(spec, ground=(0.55, 0.50, 0.42)):
    """Factory-reset, build, export and optionally render (--render out.png) plus head close-ups."""
    import sys
    import bpy
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj, _info = build(spec)
    nh.export_fbx(obj, spec.name)
    if "--render" in argv:
        path = argv[argv.index("--render") + 1]
        nh.render_preview(obj, path, ground=ground, views=((35, 22), (-90, 4), (0, 82), (-150, 25)))
        render_extra(path)
