"""
Procedural California condor (Gymnogyps californianus) soaring, wings spread flat.

Broad, plank-like wings (span ~2.6x body length) with seven long primaries
splayed into upturned "fingers" at each tip and a finely serrated trailing
edge of secondaries. All-black plumage, a pale silvery panel on the upper
secondaries and the bright white triangle on the underwing coverts. The bare
head and neck are orange-pink, wrinkled, with an ivory hooked bill, framed by a
spiky black ruff. Short square tail, pale legs tucked under it.
Large animal: high-detail fused body, ~20k triangles.

Usage:
  blender --background --python tools/blender/california_condor.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CaliforniaCondor.fbx
Faces -Y, pivot at the body centre (flier). Body ~1.2 long, wingspan ~3.1.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BLACK = (0.045, 0.045, 0.05)
BLACK_SHEEN = (0.10, 0.10, 0.12)
BROWN_BLACK = (0.09, 0.075, 0.07)
SILVER = (0.60, 0.60, 0.60)
WHITE = (0.90, 0.90, 0.88)
SKIN = (0.90, 0.50, 0.34)
SKIN_RED = (0.78, 0.32, 0.26)
SKIN_DUSK = (0.48, 0.34, 0.36)   # greyish-purple at the neck base
BILL = (0.88, 0.84, 0.72)
EYE = (0.35, 0.04, 0.03)
LEG = (0.66, 0.58, 0.55)

WING_ROOT = 0.10
HAND_END = 1.16
WING_STATIONS = 56
# chord positions (0 = leading edge, 1 = trailing edge) for the top surface; bottom reuses the inner ones
CHORD = (0.0, 0.03, 0.09, 0.17, 0.26, 0.35, 0.45, 0.55, 0.65, 0.75, 0.84, 0.91, 0.96, 1.0)

LEADING = [(WING_ROOT, -0.24), (0.45, -0.31), (0.80, -0.31), (1.0, -0.27), (HAND_END, -0.21)]
TRAILING = [(WING_ROOT, 0.30), (0.45, 0.29), (0.80, 0.25), (1.0, 0.19), (HAND_END, 0.10)]
THICKNESS = [(WING_ROOT, 0.085), (0.5, 0.05), (0.85, 0.032), (HAND_END, 0.02)]


def interp(keys, x):
    for (x0, v0), (x1, v1) in zip(keys, keys[1:]):
        if x <= x1:
            s = nh.smoothstep(x0, x1, x) if x1 > x0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


def dihedral(x):
    """Flat soaring wing with a slight lift toward the hand."""
    return 0.035 * x + 0.03 * nh.smoothstep(0.7, HAND_END, x)


def airfoil(c):
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def serration(x):
    """Secondary feather tips: rounded teeth along the inner trailing edge."""
    period = 0.075
    s = (x - WING_ROOT) / period
    tooth = 1.0 - abs(math.sin(math.pi * s)) ** 0.6
    return -0.028 * tooth * (1 - nh.smoothstep(0.85, 1.02, x))


def loft(rings, cap_start=True, cap_end=True):
    """Bridges a list of equal-length closed vertex rings (lists of Vectors)."""
    bm = bmesh.new()
    vrings = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(vrings[0])
    for a, b in zip(vrings, vrings[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    if cap_start:
        bm.faces.new(list(reversed(vrings[0])))
    if cap_end:
        bm.faces.new(vrings[-1])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def wing_frac(x, y):
    """(span fraction, chord fraction) of a point on the inner wing, for colouring."""
    ax = abs(x)
    yl, yt = interp(LEADING, ax), interp(TRAILING, ax)
    c = (y - yl) / (yt - yl) if yt != yl else 0.0
    return (ax - WING_ROOT) / (HAND_END - WING_ROOT), c


def wing_color(co, n):
    t, c = wing_frac(co.x, co.y)
    feather = abs(math.sin(abs(co.x) * math.pi / 0.075))      # one stripe per secondary
    grain = max(0.0, noise.noise(Vector((co.x * 14.0, co.y * 40.0, 0.7))))
    if n.z >= 0:
        col = nh.lerp(BLACK, BLACK_SHEEN, grain * 0.6)
        # silvery panel on the secondaries, fading out toward the hand, with dark shafts between feathers
        panel = nh.smoothstep(0.50, 0.62, c) * (1 - nh.smoothstep(0.93, 1.0, c)) * (1 - nh.smoothstep(0.62, 0.8, t))
        silver = nh.lerp(SILVER, BLACK_SHEEN, (1 - feather) ** 10 * 0.45)
        col = nh.lerp(col, silver, panel * 0.7)
        # rows of coverts: faint scalloped bands across the front half
        rows = 0.5 + 0.5 * math.sin(c * 38.0 + math.sin(abs(co.x) * 40.0) * 0.6)
        return nh.lerp(col, BROWN_BLACK, rows * (1 - nh.smoothstep(0.3, 0.45, c)) * 0.5)
    # underside: white triangle on the coverts, widest at the body and pointed at the wrist
    tri = nh.smoothstep(-0.03, 0.06, 0.48 * (1 - t / 0.68) - abs(c - 0.30 * (1 - t / 0.68) - 0.12))
    tri *= nh.smoothstep(0.03, 0.1, c)
    col = nh.lerp(BLACK, BLACK_SHEEN, grain * 0.5)
    return nh.lerp(col, nh.lerp(WHITE, SILVER, grain * 0.4), tri)


def make_wing(side):
    rings = []
    for i in range(WING_STATIONS + 1):
        u = i / WING_STATIONS
        x = WING_ROOT + (HAND_END - WING_ROOT) * u
        yl = interp(LEADING, x)
        yt = interp(TRAILING, x) + serration(x)
        th = interp(THICKNESS, x)
        z0 = dihedral(x)
        top = [(c, z0 + th * airfoil(c)) for c in CHORD]
        bottom = [(c, z0 - th * 0.3 * airfoil(c)) for c in reversed(CHORD[1:-1])]
        rings.append([Vector((side * x, yl + (yt - yl) * c, z)) for c, z in top + bottom])
    return loft(rings), wing_color


# ---------------------------------------------------------------- primaries

PRIMARIES = [
    # (base chord fraction on the hand, angle back from +X in degrees, length)
    (0.05, -14.0, 0.36),
    (0.20, -6.0, 0.44),
    (0.34, 2.0, 0.47),
    (0.48, 10.0, 0.46),
    (0.62, 19.0, 0.43),
    (0.76, 29.0, 0.37),
    (0.92, 42.0, 0.33),
]


def primary(side, chord_frac, angle, length, stations=10):
    x0 = HAND_END - 0.12
    yl, yt = interp(LEADING, x0), interp(TRAILING, x0)
    base = Vector((x0, yl + (yt - yl) * chord_frac, dihedral(x0) + 0.006))
    a = math.radians(angle)
    fwd = Vector((math.cos(a), math.sin(a), 0.0))
    perp = Vector((-math.sin(a), math.cos(a), 0.0))   # toward the trailing side of the feather
    rings = []
    for k in range(stations + 1):
        s = k / stations
        # emarginated feather: narrow near the base, broad in the middle, rounded tip
        w = 0.088 * (0.78 + 0.3 * math.sin(math.pi * min(1.0, s * 1.2))) * (1 - max(0.0, (s - 0.78) / 0.22) ** 2 * 0.8)
        th = 0.012 * (1 - 0.7 * s)
        p = base + fwd * (length * s) + Vector((0, 0, 0.18 * length * s * s))   # tips curl upward
        twist = 0.25 * s      # leading vane lifts a little
        ring = []
        for c, h in ((0.0, 0.0), (0.2, 0.7), (0.55, 1.0), (1.0, 0.0), (0.55, -0.6), (0.2, -0.5)):
            q = p + perp * (w * (c - 0.3)) + Vector((0, 0, th * h + twist * w * (0.3 - c) * 0.5))
            ring.append(Vector((side * q.x, q.y, q.z)))
        if side < 0:
            ring.reverse()
        rings.append(ring)

    def color(co, n):
        s = (abs(co.x) - x0) / (length * math.cos(a) + 1e-6)
        shaft = 1 - nh.smoothstep(0.0, 0.006, abs((Vector((abs(co.x), co.y, 0)) - base).dot(perp) + 0.3 * 0.088 * 0.2))
        col = nh.lerp(BLACK, BROWN_BLACK, nh.smoothstep(0.3, 1.0, s) * 0.8)
        return nh.lerp(col, BLACK_SHEEN, shaft * 0.5)
    return loft(rings), color


# ---------------------------------------------------------------- body

def body_shells():
    s = []
    # deep keel-chested torso tapering into the tail base
    ys = [-0.30, -0.22, -0.10, 0.04, 0.18, 0.30, 0.40]
    rs = [0.10, 0.15, 0.175, 0.175, 0.15, 0.105, 0.06]
    zs = [0.0, 0.0, -0.01, -0.01, 0.0, 0.01, 0.015]
    s.append(nh.tube([(0, y, z) for y, z in zip(ys, zs)], rs, sides=20, scale_xy=(1.0, 0.82)))
    # breast and wing roots
    s.append(nh.ellipsoid((0, -0.14, -0.05), (0.14, 0.16, 0.12), subdivisions=3))
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.12, -0.02, 0.02), (0.08, 0.20, 0.06), subdivisions=3))
    # bare neck, slightly lowered, into the head
    neck = [(0, -0.26, 0.02), (0, -0.34, 0.02), (0, -0.42, 0.01), (0, -0.48, 0.005)]
    s.append(nh.tube(neck, [0.075, 0.055, 0.048, 0.05], sides=14))
    s.append(nh.ellipsoid((0, -0.515, 0.012), (0.06, 0.08, 0.062), subdivisions=3))
    # cere / base of the bill
    s.append(nh.ellipsoid((0, -0.575, 0.012), (0.035, 0.04, 0.038), subdivisions=2))
    # legs tucked back under the tail coverts
    for sx in (-1, 1):
        s.append(nh.tube([(sx * 0.07, 0.12, -0.10), (sx * 0.075, 0.26, -0.12), (sx * 0.07, 0.36, -0.10)],
                         [0.04, 0.03, 0.025], sides=10))
    return s


HEAD_Y = -0.30   # where the bare skin starts (hidden by the ruff)


def body_color(co, n):
    if co.y < HEAD_Y and co.z > -0.09:
        h = nh.smoothstep(HEAD_Y, -0.45, co.y)
        col = nh.lerp(SKIN_DUSK, SKIN_RED, h)
        col = nh.lerp(col, SKIN, nh.smoothstep(-0.44, -0.55, co.y))
        wrinkles = 0.5 + 0.5 * math.sin(co.y * 220.0 + noise.noise(co * 30.0) * 4.0)
        col = nh.lerp(col, SKIN_RED, wrinkles * 0.25 * nh.smoothstep(-0.36, -0.46, co.y))
        return nh.lerp(col, SKIN_DUSK, max(0.0, noise.noise(co * 45.0)) * 0.3)
    if co.z < -0.095 and abs(co.x) > 0.04 and co.y > 0.31:
        return LEG
    grain = max(0.0, noise.noise(co * 35.0))
    col = nh.lerp(BLACK, BLACK_SHEEN, grain * 0.7)
    return nh.lerp(col, BROWN_BLACK, nh.smoothstep(0.2, -0.8, n.z) * 0.5)


def ruff(rng):
    """Spiky collar of black lanceolate feathers around the neck base."""
    shells = []
    centre = Vector((0, -0.26, 0.01))
    for row, (dy, rad, length, count) in enumerate(((0.0, 0.085, 0.13, 36), (0.035, 0.115, 0.11, 32))):
        for k in range(count):
            a = (k + 0.5 * row) / count * math.tau
            radial = Vector((math.cos(a), 0.0, math.sin(a) * 0.9))
            if radial.z < -0.6:
                continue  # leave the throat open
            base = centre + Vector((0, dy, 0)) + radial * rad
            d = (radial * 0.75 + Vector((0, 0.65, 0))).normalized()
            L = length * rng.uniform(0.75, 1.15)
            tip = base + d * L + Vector((rng.uniform(-0.01, 0.01), 0, rng.uniform(-0.01, 0.01)))
            shells.append(nh.tube([base - d * 0.02, base.lerp(tip, 0.45), tip], [0.026, 0.021, 0.0], sides=5,
                                  scale_xy=(1.0, 0.5)))
    return shells


def bill():
    """Ivory hooked bill: deep at the base, curving down to a sharp hook."""
    pts = [(0, -0.585, 0.02), (0, -0.625, 0.022), (0, -0.66, 0.016), (0, -0.682, 0.0), (0, -0.688, -0.022),
           (0, -0.680, -0.035)]
    return nh.tube(pts, [0.03, 0.025, 0.02, 0.015, 0.008, 0.0], sides=10, scale_xy=(0.72, 1.0))


def tail():
    """Short square tail: a fanned panel with rounded feather tips."""
    outline = [(-0.09, 0.36, 0.015), (0.09, 0.36, 0.015), (0.15, 0.56, 0.012)]
    n = 30
    for k in range(n + 1):
        x = 0.15 - 0.30 * k / n
        y = 0.585 - 0.02 * (x / 0.15) ** 2 + 0.014 * abs(math.sin(math.pi * (x + 0.15) / 0.05)) ** 0.5
        outline.append((x, y, 0.01))
    outline.append((-0.15, 0.56, 0.012))
    return nh.flat_panel(outline, thickness=0.022)


def tail_color(co, n):
    feather = abs(math.sin(co.x * math.pi / 0.05))
    col = nh.lerp(BLACK, BROWN_BLACK, nh.smoothstep(0.45, 0.62, co.y) * 0.7)
    return nh.lerp(col, BLACK_SHEEN, (1 - feather) ** 8 * 0.6)


def build():
    rng = random.Random(7)
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, BLACK)
    body = parts.fuse(voxel=0.0125, smooth=6, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    mb.add(bill(), lambda co, n: nh.lerp(BILL, (0.7, 0.62, 0.5), nh.smoothstep(-0.60, -0.58, co.y)))
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.05, -0.54, 0.035), (0.012, 0.014, 0.012), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.016, -0.598, 0.033), (0.006, 0.01, 0.005), subdivisions=1), (0.15, 0.1, 0.08))
    for shell in ruff(rng):
        mb.add(shell, lambda co, n: nh.lerp(BLACK, BLACK_SHEEN, max(0.0, noise.noise(co * 50.0))))
    mb.add(tail(), tail_color, smooth=False)
    # feet with dark talons, drawn up under the tail
    for sx in (-1, 1):
        ankle = Vector((sx * 0.07, 0.37, -0.10))
        for k, dx in enumerate((-0.025, 0.0, 0.025)):
            tip = ankle + Vector((sx * dx, 0.09, -0.015))
            mb.add(nh.tube([ankle, ankle.lerp(tip, 0.7), tip], [0.014, 0.011, 0.004], sides=6), LEG)
            mb.add(nh.tube([tip, tip + Vector((0, 0.022, -0.012))], [0.006, 0.0], sides=5), BLACK)
    for side in (1, -1):
        mb.add(*make_wing(side))
        for chord_frac, angle, length in PRIMARIES:
            mb.add(*primary(side, chord_frac, angle, length))

    return mb.to_object("CaliforniaCondor", roughness=0.75)


if __name__ == "__main__":
    nh.run(build, "CaliforniaCondor", background=(0.45, 0.58, 0.70),
           views=((35, 25), (20, 70), (0, 89), (180, -35)))
