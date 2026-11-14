"""
Procedural reef manta ray (Mobula alfredi) for map colonies (Swim style).

A broad diamond of wing-like pectoral fins (wingspan ~2.4x body length) with
swept, upturned tips and a gentle wave running out along each wing, a rounded
ridge down the back, a small dorsal fin and a short whip tail. The disc, ridge,
tail root and dorsal fin are fused into one seamless surface and repainted
analytically: charcoal back with the crisp pale shoulder patches that mark
reef mantas, white belly with dark wing margins, gill slits and a few dark
spots. Crisp extras on top: domed eyes on the sides of the head, rolled
cephalic fins, and an open mouth with a hint of gill rakers.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/mobula_alfredi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MantaRay.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BACK = (0.07, 0.075, 0.09)       # charcoal
BACK_EDGE = (0.035, 0.035, 0.045)
RIDGE = (0.10, 0.105, 0.12)
PATCH = (0.84, 0.86, 0.88)       # pale shoulder patches
BELLY = (0.95, 0.95, 0.93)
BELLY_MARGIN = (0.20, 0.21, 0.24)
SPOT = (0.25, 0.26, 0.29)
GILL = (0.36, 0.36, 0.40)
MOUTH = (0.05, 0.045, 0.05)
RAKER = (0.62, 0.55, 0.56)
EYE = (0.015, 0.015, 0.02)
EYE_SOCKET = (0.20, 0.21, 0.24)
FIN_INNER = (0.70, 0.72, 0.74)

# Half outline (x >= 0), front (-Y) to back (+Y); mirrored for the left side.
HALF_OUTLINE = [
    (0.00, -0.38), (0.15, -0.39), (0.32, -0.34), (0.52, -0.26), (0.72, -0.13),
    (0.89, 0.00), (1.02, 0.11), (0.95, 0.14), (0.78, 0.13), (0.56, 0.15),
    (0.36, 0.22), (0.22, 0.32), (0.10, 0.40), (0.00, 0.42),
]

RINGS = 30
SAMPLES = 160
# No decimation: an even voxel grid keeps the painted patch and spot edges clean
# (decimated slivers smear vertex colours into saw-teeth). The rim stays a couple of
# voxels thick so the remesh can't fray the wing edge.
VOXEL = 0.0195
RIM = 0.032


def catmull(points, n):
    """Closed Catmull-Rom resample of a 2D polygon to n points."""
    out = []
    m = len(points)
    for i in range(n):
        t = i / n * m
        k = int(t)
        u = t - k
        p0, p1, p2, p3 = (Vector(points[(k + j) % m]) for j in (-1, 0, 1, 2))
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u))
    return out


def outline():
    right = HALF_OUTLINE
    left = [(-x, y) for x, y in reversed(HALF_OUTLINE[1:-1])]
    return catmull(right + left, SAMPLES)


def thickness(x, y):
    """Thick central disc, a rounded ridge down the back, thin wings."""
    body = math.exp(-(x / 0.26) ** 2 - ((y + 0.02) / 0.34) ** 2)
    ridge = math.exp(-(x / 0.075) ** 2) * nh.smoothstep(-0.36, -0.22, y) * (1.0 - nh.smoothstep(0.22, 0.42, y))
    return 0.10 * body + 0.035 * ridge + 0.016


def flap(x, y):
    """Wings on the upstroke: tips curl up, with a gentle wave travelling out along the wing."""
    ax = abs(x)
    wave = 0.05 * math.sin(ax * 5.5 - 1.2 + y * 2.0) * nh.smoothstep(0.15, 0.5, ax)
    return 0.15 * ax ** 2.2 + 0.03 * ax * y + wave


def body_shell():
    bm = bmesh.new()
    rim = outline()
    top_c = bm.verts.new((0, 0, flap(0, 0) + thickness(0, 0) * 0.62))
    bot_c = bm.verts.new((0, 0, flap(0, 0) - thickness(0, 0) * 0.38))
    tops, bots = [], []
    for k in range(1, RINGS):
        s = k / RINGS
        tr, br = [], []
        for p in rim:
            x, y = p.x * s, p.y * s
            t = max(thickness(x, y) * (1.0 - s ** 8), RIM)
            z0 = flap(x, y)
            tr.append(bm.verts.new((x, y, z0 + t * 0.62)))
            br.append(bm.verts.new((x, y, z0 - t * 0.38)))
        tops.append(tr)
        bots.append(br)
    edge_ring = [bm.verts.new((p.x, p.y, flap(p.x, p.y))) for p in rim]

    n = SAMPLES
    for ring_list, centre, flip in ((tops, top_c, False), (bots, bot_c, True)):
        rings = ring_list + [edge_ring]
        for j in range(n):
            a, b = rings[0][j], rings[0][(j + 1) % n]
            bm.faces.new([centre, b, a] if flip else [centre, a, b])
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(n):
                q = [r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]]
                bm.faces.new(list(reversed(q)) if flip else q)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def dorsal_fin():
    bm = nh.flat_panel([(0.0, -0.01, 0), (0.075, 0.0, 0), (0.0, 0.10, 0)], thickness=0.022)
    # drawn in XY; stand it up in the YZ plane with the tip leaning back
    nh.transform(bm, Matrix.Rotation(math.radians(-90), 4, "Y"))
    nh.transform(bm, Matrix.Rotation(math.radians(90), 4, "X"))
    nh.transform(bm, Matrix.Translation((0, 0.28, flap(0, 0.28) + thickness(0, 0.28) * 0.5)))
    return bm


# ---------------------------------------------------------------- analytic markings

def sd_segment(p, a, b):
    pa, ba = p - a, b - a
    h = max(0.0, min(1.0, pa.dot(ba) / ba.dot(ba)))
    return (pa - ba * h).length


def sd_triangle(p, a, b, c):
    """Signed distance to a 2D triangle (negative inside)."""
    d = min(sd_segment(p, a, b), sd_segment(p, b, c), sd_segment(p, c, a))
    def cross(o, u, v):
        return (u.x - o.x) * (v.y - o.y) - (u.y - o.y) * (v.x - o.x)
    s1, s2, s3 = cross(a, b, p), cross(b, c, p), cross(c, a, p)
    inside = (s1 >= 0 and s2 >= 0 and s3 >= 0) or (s1 <= 0 and s2 <= 0 and s3 <= 0)
    return -d if inside else d


# Shoulder patch: a rounded triangle behind the head - straight front edge running out
# toward the wing, inner edge parallel to the dark midline, tapering back toward the ridge.
PATCH_A = Vector((0.075, -0.255))
PATCH_B = Vector((0.47, -0.165))
PATCH_C = Vector((0.10, 0.03))
PATCH_ROUND = 0.035
EDGE = 0.008  # half-width of the anti-aliased boundary


def patch_mask(x, y):
    p = Vector((abs(x), y))
    d = sd_triangle(p, PATCH_A, PATCH_B, PATCH_C) - PATCH_ROUND
    # soft concave bite out of the back edge, like the real crescent shape
    bite = (p - Vector((0.30, 0.07))).length - 0.16
    d = max(d, -bite)
    return 1.0 - nh.smoothstep(-EDGE, EDGE, d)


rng = random.Random(11)
BELLY_SPOTS = []
while len(BELLY_SPOTS) < 9:
    sx, sy = rng.uniform(-0.17, 0.17), rng.uniform(-0.02, 0.28)
    if all((Vector((sx, sy)) - Vector(s[:2])).length > 0.07 for s in BELLY_SPOTS):
        BELLY_SPOTS.append((sx, sy, rng.uniform(0.012, 0.026)))


def gill_slit(x, y):
    """Five slightly curved slits each side of the belly; returns 0..1 coverage."""
    ax = abs(x)
    if not (0.09 < ax < 0.24 and -0.32 < y < -0.06):
        return 0.0
    best = 1.0
    for i in range(5):
        cy = -0.29 + i * 0.05
        # arc bowing toward the midline
        yy = cy + 0.25 * (ax - 0.165) ** 2 * 4.0
        dx = max(0.0, abs(ax - 0.165) - 0.05 + 0.006 * i)
        best = min(best, math.hypot(dx, y - yy))
    return 1.0 - nh.smoothstep(0.004, 0.009, best)


def disc_color(co, n):
    x, y = co.x, co.y
    r_out = abs(x) / 1.02
    if -0.45 < n.z < 0.25 and r_out > 0.3:
        return BACK_EDGE
    if n.z >= -0.05:
        c = nh.lerp(BACK, RIDGE, math.exp(-(x / 0.06) ** 2) * 0.8)
        c = nh.lerp(c, PATCH, patch_mask(x, y))
        return nh.lerp(c, BACK_EDGE, nh.smoothstep(0.8, 1.0, r_out) * 0.6)
    c = BELLY
    # dark trailing margin and wingtips on the underside
    trailing = nh.smoothstep(0.0, 0.05, y - 0.05 - 0.06 * abs(x)) * nh.smoothstep(0.3, 0.55, abs(x))
    c = nh.lerp(c, BELLY_MARGIN, max(trailing * 0.85, nh.smoothstep(0.82, 0.97, r_out)))
    for sx, sy, sr in BELLY_SPOTS:
        d = math.hypot(x - sx, y - sy) - sr
        c = nh.lerp(c, SPOT, (1.0 - nh.smoothstep(-0.004, 0.004, d)) * 0.85)
    return nh.lerp(c, GILL, gill_slit(x, y))


# ---------------------------------------------------------------- crisp details

def rolled_sheet(surface, nu, nv, thick):
    """Closed thin slab around a parametric surface(u, v) -> Vector, u, v in [0, 1]."""
    bm = bmesh.new()
    eps = 1e-3

    def normal(u, v):
        du = surface(min(1, u + eps), v) - surface(max(0, u - eps), v)
        dv = surface(u, min(1, v + eps)) - surface(u, max(0, v - eps))
        return du.cross(dv).normalized()

    grid_a, grid_b = [], []
    for i in range(nu + 1):
        u = i / nu
        ra, rb = [], []
        for j in range(nv + 1):
            v = j / nv
            p, nrm = surface(u, v), normal(u, v)
            taper = 1.0 - 0.6 * u
            ra.append(bm.verts.new(p + nrm * thick * 0.5 * taper))
            rb.append(bm.verts.new(p - nrm * thick * 0.5 * taper))
        grid_a.append(ra)
        grid_b.append(rb)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new([grid_a[i][j], grid_a[i + 1][j], grid_a[i + 1][j + 1], grid_a[i][j + 1]])
            bm.faces.new([grid_b[i][j + 1], grid_b[i + 1][j + 1], grid_b[i + 1][j], grid_b[i][j]])
    # stitch the four borders
    for i in range(nu):
        for j in (0, nv):
            bm.faces.new([grid_a[i][j], grid_b[i][j], grid_b[i + 1][j], grid_a[i + 1][j]])
    for j in range(nv):
        for i in (0, nu):
            bm.faces.new([grid_a[i][j], grid_a[i][j + 1], grid_b[i][j + 1], grid_b[i][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def cephalic_fin(side):
    """Paddle unfurled forward from beside the mouth, its cross-section rolled into a
    C that opens toward the mouth (the two fins form a funnel)."""
    root = Vector((side * 0.135, -0.335, flap(0.135, -0.335) + 0.002))
    tip = Vector((side * 0.165, -0.59, flap(0.13, -0.33) - 0.015))

    def surface(u, v):
        p = root.lerp(tip, u) + Vector((0, 0, -0.025 * math.sin(math.pi * u)))
        # height of the paddle: grows out of the root, rounded tip
        h = 0.105 * math.sin(math.pi * (0.25 + 0.75 * u)) ** 0.6 + 0.01
        roll = math.radians(60 + 45 * u)               # rolls tighter toward the tip
        phi = (v * 2.0 - 1.0) * roll
        R = h / (2.0 * math.sin(roll))
        lateral = -side * R * (1.0 - math.cos(phi))      # curls inward at the top and bottom
        return p + Vector((lateral, 0, R * math.sin(phi)))

    return rolled_sheet(surface, 12, 10, 0.012)


def cephalic_color(side):
    def color(co, n):
        inward = n.x * -side
        return nh.lerp(BACK, FIN_INNER, nh.smoothstep(0.0, 0.7, inward) * 0.85)
    return color


def mouth():
    """Open, wide terminal mouth: a dark gape set into the front edge, with pale gill rakers
    showing as vertical stripes inside."""
    z = flap(0, -0.39)
    bm = nh.uv_ellipsoid((0, -0.375, z), (0.105, 0.045, 0.026), segments=32, rings=12)

    def color(co, n):
        if n.y < -0.35 and abs(co.x) < 0.085:
            f = (co.x / 0.011) % 1.0
            if f < 0.4:
                return RAKER
        return MOUTH
    return bm, color


def eye(mb, side):
    centre = Vector((side * 0.175, -0.325, flap(0.175, -0.325) + 0.012))
    mb.add(nh.uv_ellipsoid(centre, (0.026, 0.03, 0.022), segments=12, rings=8), EYE_SOCKET)
    mb.add(nh.uv_ellipsoid(centre + Vector((side * 0.013, -0.004, 0.003)), (0.017, 0.019, 0.017),
                           segments=12, rings=8), EYE)


def build():
    parts = nh.MeshBuilder()
    parts.add(body_shell(), BACK)
    parts.add(dorsal_fin(), BACK)
    parts.add(nh.tube([(0, 0.36, flap(0, 0.36)), (0, 0.48, flap(0, 0.48) + 0.008)], [0.028, 0.02], sides=10), BACK)
    fused = parts.fuse(voxel=VOXEL, smooth=4, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(fused, disc_color)
    for side in (-1, 1):
        mb.add(cephalic_fin(side), cephalic_color(side))
        eye(mb, side)
    mb.add(*mouth())
    tail = nh.tube([(0, 0.46, flap(0, 0.46) + 0.008), (0, 0.6, 0.03), (0, 0.74, 0.045), (0, 0.88, 0.06)],
                   [0.02, 0.011, 0.006, 0.0], sides=6)
    mb.add(tail, BACK)

    obj = mb.to_object("MantaRay", roughness=0.45)
    # pivot at the body centre
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "MantaRay", background=(0.05, 0.22, 0.30), views=((35, 30), (-90, 6), (0, 80), (20, -40)))
