"""
Green sea turtle (Chelonia mydas) for the map, Swim style.

Swimming pose: long paddle front flippers mid-stroke (left raised, right lowered),
short rounded rear flippers. A smooth heart-shaped carapace built as its own
parametric shell, with the non-overlapping scutes (5 vertebrals, 4 pairs of
costals, a ring of marginals) as gently domed plates split by pale grooves, each
plate painted with radiating olive/brown/amber streaks; a pale yellow plastron.
Head, neck, flippers and tail are one fused seamless body painted with
cream-edged dark scales, then crisp details (eyes, beak sheath, serrations,
flipper claws) are added. Pivot at the body centre, faces -Y.

  blender --background --python tools/blender/green_sea_turtle.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SEED = 5

# ---- carapace outline (XY, faces -Y) ----
Y_FRONT, Y_BACK = -0.46, 0.60
HALF_W = 0.46
SHELL_H = 0.17
CENTER = Vector((0.0, 0.03, 0.0))
N_ANG, N_RING = 104, 22
INNER = 0.84            # radial fraction where the marginal ring starts
N_MARGINAL = 24         # marginal scutes around the rim

# ---- palette ----
SHELL_OLIVE = (0.28, 0.27, 0.12)
SHELL_BROWN = (0.27, 0.17, 0.08)
SHELL_AMBER = (0.62, 0.42, 0.14)
SHELL_DARK = (0.12, 0.08, 0.04)
SEAM = (0.78, 0.70, 0.46)
PLASTRON = (0.88, 0.80, 0.52)
SKIN_DARK = (0.20, 0.15, 0.09)
SKIN_MID = (0.34, 0.27, 0.15)
SKIN_EDGE = (0.86, 0.80, 0.62)
SKIN_UNDER = (0.80, 0.76, 0.62)
BEAK = (0.18, 0.15, 0.11)
EYE = (0.03, 0.03, 0.03)
CLAW = (0.62, 0.56, 0.42)


def half_width(y):
    t = (y - Y_FRONT) / (Y_BACK - Y_FRONT)
    if t <= 0.0 or t >= 1.0:
        return 0.0
    return HALF_W * math.sin(math.pi * t ** 0.72) ** 0.62 * (1.0 - 0.12 * t)


def inside(x, y):
    return Y_FRONT < y < Y_BACK and abs(x) < half_width(y)


_rim_cache = {}


def rim_radius(theta):
    key = round(theta, 5)
    if key in _rim_cache:
        return _rim_cache[key]
    d = Vector((math.cos(theta), math.sin(theta)))
    lo, hi = 0.0, 1.2
    for _ in range(36):
        mid = (lo + hi) * 0.5
        p = CENTER.xy + d * mid
        if inside(p.x, p.y):
            lo = mid
        else:
            hi = mid
    _rim_cache[key] = lo
    return lo


def polar(x, y):
    d = Vector((x, y)) - CENTER.xy
    theta = math.atan2(d.y, d.x)
    R = rim_radius(theta)
    return theta, (d.length / R if R > 1e-6 else 0.0), R


def vertebral_bounds():
    s0, s1 = 0.07, 0.86
    return [s0 + k * (s1 - s0) / 5 for k in range(6)]


def costal_bounds():
    s0, s1 = 0.10, 0.88
    return [s0 + k * (s1 - s0) / 4 for k in range(5)]


def scute_info(x, y):
    """-> (groove 0..1, dome offset, scute key, distance-to-centre, centre xy)."""
    theta, v, R = polar(x, y)
    s = (y - Y_FRONT) / (Y_BACK - Y_FRONT)
    hw = max(half_width(y), 1e-4)
    r = x / hw
    L = Y_BACK - Y_FRONT
    dists = []
    if v >= INNER:
        # marginal ring: radial dividers + the inner ring line
        a = (theta + math.pi) / math.tau * N_MARGINAL
        k = math.floor(a)
        frac = a - k
        dists.append(min(frac, 1 - frac) / N_MARGINAL * math.tau * R * v)
        dists.append((v - INNER) * R)
        ca = (k + 0.5) / N_MARGINAL * math.tau - math.pi
        cv = (INNER + 1.0) * 0.5
        rc = rim_radius(ca)
        centre = CENTER.xy + Vector((math.cos(ca), math.sin(ca))) * rc * cv
        key = ("m", k)
        size = 0.5 * math.tau * R / N_MARGINAL
    else:
        dists.append((INNER - v) * R)
        VW = 0.30
        dists.append(abs(abs(x) - VW * hw))
        if abs(r) < VW:
            b = vertebral_bounds()
            key_side = "v"
        else:
            b = costal_bounds()
            key_side = "c+" if x > 0 else "c-"
        k = max(0, min(len(b) - 2, sum(1 for bb in b[1:-1] if s > bb)))
        for bb in b[1:-1]:
            dists.append(abs(s - bb) * L)
        sc = (b[k] + b[k + 1]) * 0.5
        yc = Y_FRONT + sc * L
        if key_side == "v":
            xc = 0.0
        else:
            xc = (0.64 if x > 0 else -0.64) * half_width(yc)
        centre = Vector((xc, yc))
        key = (key_side, k)
        size = (b[k + 1] - b[k]) * L * 0.6
    d = min(dists)
    groove = math.exp(-(d / 0.010) ** 2)
    dc = (Vector((x, y)) - centre).length
    dome = 0.010 * max(0.0, 1.0 - (dc / max(size, 1e-3)) ** 2)
    return groove, dome, key, dc, centre


def scute_colour(x, y):
    groove, _dome, key, dc, centre = scute_info(x, y)
    rnd = random.Random(hash(key) & 0xFFFF)
    p = Vector((x, y, 0.0))
    # soft mottled base, varying a little from plate to plate
    mott = 0.5 + 0.5 * noise.noise(p * 7.0 + Vector((0, 0, rnd.random() * 20)))
    base = nh.lerp(SHELL_OLIVE, SHELL_BROWN, 0.35 * rnd.random() + 0.5 * mott)
    # warm amber streaks fanning out from the growth point at the plate's rear edge
    if key[0] == "m":
        grow = centre + (centre - CENTER.xy).normalized() * 0.03
    else:
        grow = centre + Vector((0.0, 0.07))
    rel = Vector((x, y)) - grow
    ang = math.atan2(rel.x, -rel.y)
    fan = noise.noise(Vector((ang * 2.4, rel.length * 3.0, rnd.random() * 30)))
    streak = nh.smoothstep(-0.05, 0.45, fan) * nh.smoothstep(0.0, 0.05, rel.length)
    c = nh.lerp(base, SHELL_AMBER, streak * 0.7)
    # dark speckles
    speck = noise.noise(p * 38.0 + Vector((0, 0, 3.0)))
    c = nh.lerp(c, SHELL_DARK, nh.smoothstep(0.32, 0.5, speck) * 0.8)
    return nh.lerp(c, SEAM, groove * 0.9)


def build_shell():
    bm = bmesh.new()
    top_rings = [j / N_RING for j in range(1, N_RING + 1)]
    bottom_rings = [(1.0, -0.018), (0.94, -0.045), (0.80, -0.065), (0.55, -0.078), (0.28, -0.083)]
    thetas = [-math.pi + (i + 0.5) / N_ANG * math.tau for i in range(N_ANG)]

    def top_z(v, x, y):
        z = SHELL_H * max(0.0, 1.0 - v ** 2.3) ** 0.55
        g, dome, *_ = scute_info(x, y)
        # a slight upturn of the marginal rim, grooves and domed plates
        z += 0.012 * nh.smoothstep(INNER, 1.0, v) * (1.0 - v) * 4.0
        return z + dome - g * 0.007

    centre_top = bm.verts.new((CENTER.x, CENTER.y, SHELL_H + scute_info(CENTER.x, CENTER.y)[1]))
    rings = []
    for v in top_rings:
        ring = []
        for th in thetas:
            R = rim_radius(th)
            x = CENTER.x + math.cos(th) * R * v
            y = CENTER.y + math.sin(th) * R * v
            ring.append(bm.verts.new((x, y, top_z(min(v, 0.999), x, y))))
        rings.append(ring)
    for v, z in bottom_rings:
        ring = []
        for th in thetas:
            R = rim_radius(th)
            ring.append(bm.verts.new((CENTER.x + math.cos(th) * R * v, CENTER.y + math.sin(th) * R * v, z)))
        rings.append(ring)
    centre_bot = bm.verts.new((CENTER.x, CENTER.y, -0.085))

    n = N_ANG
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([centre_top, rings[0][j], rings[0][i]])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([a[i], a[j], b[j], b[i]])
    last = rings[-1]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([centre_bot, last[i], last[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def colour(co, nrm):
        if co.z < -0.010:
            # plastron with faint scute lines
            line = math.exp(-((abs(co.x) % 0.11) - 0.055) ** 2 / 0.0002) * 0.0
            seam = 1.0 if abs(co.x) < 0.006 else 0.0
            ring = math.exp(-(((co.y + 0.5) % 0.16) - 0.08) ** 2 / 0.00004)
            c = nh.lerp(PLASTRON, (0.70, 0.62, 0.38), max(seam, ring * 0.5, line))
            return c
        return scute_colour(co.x, co.y)

    return bm, colour


# ---------------------------------------------------------------- fused body

def flipper(points, widths, flat=0.20, sides=10):
    return nh.tube(points, widths, sides=sides, scale_xy=(1.0, flat))


def build_body():
    body = nh.MeshBuilder()
    skin = SKIN_MID
    # core under the shell, joining neck, flippers and tail
    body.add(nh.uv_ellipsoid((0, 0.02, -0.035), (0.22, 0.34, 0.045), 20, 10), skin)
    # neck and head
    body.add(nh.tube([(0, -0.30, -0.02), (0, -0.42, 0.00), (0, -0.50, 0.02)], [0.098, 0.094, 0.088], sides=16), skin)
    body.add(nh.uv_ellipsoid((0, -0.585, 0.035), (0.102, 0.118, 0.095), 24, 16), skin)
    body.add(nh.uv_ellipsoid((0, -0.655, 0.018), (0.074, 0.064, 0.066), 20, 12), skin)   # blunt snout
    # front flippers: long swept paddles; left raised, right lowered (mid-stroke)
    for side, lift in ((-1, 0.13), (1, -0.07)):
        pts = [(side * 0.20, -0.24, -0.02),
               (side * 0.40, -0.31, -0.01 + lift * 0.25),
               (side * 0.60, -0.25, lift * 0.6),
               (side * 0.78, -0.10, lift * 0.9),
               (side * 0.90, 0.06, lift * 1.05),
               (side * 0.95, 0.15, lift * 1.1)]
        body.add(flipper(pts, [0.07, 0.085, 0.095, 0.080, 0.052, 0.016], flat=0.26), skin)
    # rear flippers: short, rounded
    for side in (-1, 1):
        pts = [(side * 0.18, 0.40, -0.04), (side * 0.30, 0.52, -0.04),
               (side * 0.38, 0.62, -0.045), (side * 0.40, 0.68, -0.045)]
        body.add(flipper(pts, [0.06, 0.075, 0.065, 0.018], flat=0.28), skin)
    # tail
    body.add(nh.tube([(0, 0.52, -0.04), (0, 0.64, -0.045), (0, 0.71, -0.05)], [0.040, 0.025, 0.0], sides=10), skin)
    fused = body.fuse(voxel=0.0198, smooth=6, smooth_factor=0.5, max_tris=None)

    paint_scales(fused)
    return fused


# ---------------------------------------------------------------- scale plates

FRONT_PATH_X = [0.20, 0.40, 0.60, 0.78, 0.90, 0.95]
FRONT_PATH_Y = [-0.24, -0.31, -0.25, -0.10, 0.06, 0.15]
SIDE_SEP = 0.06   # normals push the two faces of a thin flipper apart so plates don't wrap


def _interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for a in range(len(xs) - 1):
        if x <= xs[a + 1]:
            t = (x - xs[a]) / (xs[a + 1] - xs[a])
            return ys[a] + (ys[a + 1] - ys[a]) * t
    return ys[-1]


def plate_radius(co):
    """Half the spacing between scale centres at this point."""
    ax = abs(co.x)
    if co.y < -0.50:
        return 0.034                                   # head: large plates
    if ax > 0.26 and co.y < 0.25:                      # front flipper
        t = min(1.0, (ax - 0.26) / 0.69)
        lead = max(-1.0, min(1.0, (_interp(FRONT_PATH_X, FRONT_PATH_Y, ax) - co.y) / 0.08))
        return (0.019 + 0.024 * (lead + 1) * 0.5) * (1.0 - 0.35 * t)
    if co.y > 0.40:
        return 0.020 if ax > 0.12 else 0.015           # rear flippers / tail
    return 0.015                                       # neck and shoulders: small scales


HEAD_PLATES = [  # (x, y, z) targets; snapped to the nearest skin point
    (-0.024, -0.645, 0.10), (0.024, -0.645, 0.10),     # prefrontal pair
    (0.0, -0.600, 0.135),                              # frontal
    (-0.058, -0.615, 0.115), (0.058, -0.615, 0.115),   # supraoculars
    (-0.045, -0.555, 0.125), (0.045, -0.555, 0.125),   # parietals
    (-0.100, -0.592, 0.060), (0.100, -0.592, 0.060),   # post-oculars
    (-0.098, -0.560, 0.030), (0.098, -0.560, 0.030),
    (-0.090, -0.625, 0.010), (0.090, -0.625, 0.010),   # cheek (tympanic)
]


def _key(co, n):
    return co + n * SIDE_SEP


def paint_scales(bm):
    from mathutils.kdtree import KDTree
    rng = random.Random(SEED + 1)
    bm.normal_update()
    verts = list(bm.verts)

    # seeds: explicit head plates first, then a Poisson-style fill with region-dependent spacing
    vt = KDTree(len(verts))
    for i, v in enumerate(verts):
        vt.insert(v.co, i)
    vt.balance()
    seeds = []
    grid = {}
    cell = 0.05

    def gkey(q):
        return (int(math.floor(q.x / cell)), int(math.floor(q.y / cell)), int(math.floor(q.z / cell)))

    def free(q, r):
        gx, gy, gz = gkey(q)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for sq, sr in grid.get((gx + dx, gy + dy, gz + dz), ()):
                        if (sq - q).length < max(r, sr) * 2.0:
                            return False
        return True

    def add_seed(q, r):
        seeds.append(q)
        grid.setdefault(gkey(q), []).append((q, r))

    for t in HEAD_PLATES:
        _co, idx, _d = vt.find(Vector(t))
        v = verts[idx]
        add_seed(_key(v.co, v.normal), 0.040)
    order = verts[:]
    rng.shuffle(order)
    for v in order:
        q = _key(v.co, v.normal)
        r = plate_radius(v.co)
        if free(q, r):
            add_seed(q, r)

    st = KDTree(len(seeds))
    for i, q in enumerate(seeds):
        st.insert(q, i)
    st.balance()
    fills = [rng.random() for _ in seeds]
    BORDER = 0.0036

    def classify(co, n):
        (_, i1, d1), (_, i2, d2) = st.find_n(_key(co, n), 2)
        return i1, (d2 - d1) * 0.5 < BORDER

    # refine edges that cross a plate border so the borders come out crisp and even
    # (a second, head-only pass: the head plates are seen up close)
    for head_only in (False, True):
        cls = {v: classify(v.co, v.normal)[1] for v in bm.verts}
        cut = [e for e in bm.edges if cls[e.verts[0]] != cls[e.verts[1]]
               and (e.verts[0].co.y < -0.48 or (not head_only and abs(e.verts[0].co.x) > 0.26))]
        bmesh.ops.subdivide_edges(bm, edges=cut, cuts=1, use_grid_fill=True)
        bm.normal_update()

    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    for f in bm.faces:
        c0 = f.calc_center_median()
        for l in f.loops:
            p = l.vert.co * 0.65 + c0 * 0.35
            i, border = classify(p, f.normal)
            under = f.normal.z < -0.35
            if border:
                c = (0.72, 0.68, 0.54) if under else SKIN_EDGE
            else:
                fill = nh.lerp(SKIN_DARK, SKIN_MID, fills[i])
                if -0.50 <= p.y < -0.26 and abs(p.x) < 0.22:
                    fill = nh.lerp(fill, SKIN_UNDER, 0.40)   # paler neck skin
                if under:
                    fill = nh.lerp(fill, SKIN_UNDER, 0.80)
                c = fill
            l[col] = (c[0], c[1], c[2], 1.0)
        f.smooth = True


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    mb.add(build_body())  # keeps the per-corner scale colours

    shell, shell_colour = build_shell()
    mb.add(shell, shell_colour)

    # eyes, set on the sides of the head with a pale lid ring
    for side in (-1, 1):
        mb.add(nh.uv_ellipsoid((side * 0.080, -0.632, 0.052), (0.022, 0.026, 0.020), 12, 8), SKIN_DARK)
        mb.add(nh.uv_ellipsoid((side * 0.091, -0.634, 0.054), (0.016, 0.020, 0.017), 12, 8), EYE)
    # beak sheath: dark horny upper and lower rhamphotheca
    mb.add(nh.uv_ellipsoid((0, -0.690, 0.010), (0.050, 0.030, 0.028), 16, 10), BEAK)
    mb.add(nh.uv_ellipsoid((0, -0.684, -0.022), (0.046, 0.030, 0.016), 16, 8), BEAK)
    # serrated lower beak edge: tiny tooth-like points
    for k in range(-3, 4):
        x = k * 0.012
        y = -0.708 + abs(k) * 0.006
        mb.add(nh.tube([(x, y, -0.012), (x, y - 0.006, -0.004)], [0.005, 0.0], sides=3), (0.30, 0.26, 0.20))
    # a single claw on the leading edge of each front flipper
    for side, lift in ((-1, 0.13), (1, -0.07)):
        p = Vector((side * 0.56, -0.315, lift * 0.55 + 0.01))
        mb.add(nh.tube([p, p + Vector((side * 0.02, -0.035, 0.0))], [0.010, 0.0], sides=5), CLAW)

    obj = mb.to_object("GreenSeaTurtle", roughness=0.55)
    return obj


if __name__ == "__main__":
    nh.run(build, "GreenSeaTurtle", views=((35, 35), (-90, 8), (15, 75), (25, 18)))
