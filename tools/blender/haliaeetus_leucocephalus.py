"""
Procedural bald eagle (Haliaeetus leucocephalus) soaring, wings spread flat.

Long, broad, plank-like wings (span ~2.3x body length) held almost flat with a
slight upward lift at the hand, six slotted primaries splayed into short
fingers at each tip and a gently bulging, serrated trailing edge of
secondaries. Dark chocolate-brown body and wings with paler-edged coverts on
top; the adult's snow-white head and neck and white, slightly wedge-shaped
tail. Big, deep, hooked yellow bill with a yellow cere, pale yellow eyes under
a heavy brow, and yellow feet with black talons drawn up under the tail.
Large animal: high-detail fused body, ~22k triangles.

Usage:
  blender --background --python tools/blender/haliaeetus_leucocephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BaldEagle.fbx
Faces -Y, pivot at the body centre (flier). Body ~1.15 long, wingspan ~2.7.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BROWN = (0.12, 0.075, 0.045)
BROWN_DARK = (0.065, 0.045, 0.03)
BROWN_EDGE = (0.26, 0.17, 0.10)    # pale fringes on the upper coverts
WHITE = (0.94, 0.93, 0.89)
WHITE_SHADE = (0.76, 0.75, 0.72)
YELLOW = (0.98, 0.76, 0.14)
YELLOW_DEEP = (0.90, 0.62, 0.08)
IRIS = (0.96, 0.88, 0.50)
PUPIL = (0.03, 0.03, 0.03)
TALON = (0.05, 0.05, 0.05)

WING_ROOT = 0.09
HAND_END = 1.0
WING_STATIONS = 48
CHORD = (0.0, 0.03, 0.09, 0.17, 0.26, 0.35, 0.45, 0.55, 0.65, 0.75, 0.84, 0.91, 0.96, 1.0)

LEADING = [(WING_ROOT, -0.20), (0.40, -0.265), (0.75, -0.26), (0.92, -0.22), (HAND_END, -0.18)]
TRAILING = [(WING_ROOT, 0.25), (0.30, 0.27), (0.55, 0.245), (0.80, 0.19), (0.92, 0.14), (HAND_END, 0.09)]
THICKNESS = [(WING_ROOT, 0.08), (0.5, 0.045), (0.85, 0.03), (HAND_END, 0.02)]


def interp(keys, x):
    for (x0, v0), (x1, v1) in zip(keys, keys[1:]):
        if x <= x1:
            s = nh.smoothstep(x0, x1, x) if x1 > x0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


def dihedral(x):
    """Flat soaring wing, the hand lifted a touch."""
    return 0.02 * x + 0.04 * nh.smoothstep(0.65, HAND_END, x)


def airfoil(c):
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def serration(x):
    """Rounded secondary tips along the inner trailing edge."""
    period = 0.068
    s = (x - WING_ROOT) / period
    tooth = 1.0 - abs(math.sin(math.pi * s)) ** 0.6
    return -0.022 * tooth * (1 - nh.smoothstep(0.82, 0.98, x))


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
    grain = max(0.0, noise.noise(Vector((co.x * 14.0, co.y * 40.0, 0.3))))
    feather = abs(math.sin(abs(co.x) * math.pi / 0.068))   # one stripe per secondary
    if n.z >= 0:
        col = nh.lerp(BROWN, BROWN_EDGE, grain * 0.35)
        # scalloped rows of coverts with pale fringes over the front half
        rows = 0.5 + 0.5 * math.sin(c * 34.0 + math.sin(abs(co.x) * 38.0) * 0.7)
        col = nh.lerp(col, BROWN_EDGE, rows ** 6 * (1 - nh.smoothstep(0.35, 0.5, c)) * 0.6)
        # flight feathers darker, with faint shafts
        col = nh.lerp(col, BROWN_DARK, nh.smoothstep(0.5, 0.65, c) * 0.8)
        return nh.lerp(col, BROWN, (1 - feather) ** 10 * nh.smoothstep(0.55, 0.65, c) * 0.5)
    # underside: dark coverts, slightly greyer flight feathers
    col = nh.lerp(BROWN_DARK, BROWN, grain * 0.6)
    return nh.lerp(col, (0.17, 0.13, 0.10), nh.smoothstep(0.5, 0.7, c) * 0.6)


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
    (0.06, -10.0, 0.30),
    (0.24, -3.0, 0.36),
    (0.42, 5.0, 0.37),
    (0.60, 14.0, 0.34),
    (0.78, 25.0, 0.29),
    (0.94, 38.0, 0.24),
]


def primary(side, chord_frac, angle, length, stations=10):
    x0 = HAND_END - 0.10
    yl, yt = interp(LEADING, x0), interp(TRAILING, x0)
    base = Vector((x0, yl + (yt - yl) * chord_frac, dihedral(x0) + 0.006))
    a = math.radians(angle)
    fwd = Vector((math.cos(a), math.sin(a), 0.0))
    perp = Vector((-math.sin(a), math.cos(a), 0.0))
    rings = []
    for k in range(stations + 1):
        s = k / stations
        # broad feather, narrowing a little toward the rounded tip
        w = 0.082 * (0.85 + 0.2 * math.sin(math.pi * min(1.0, s * 1.2))) * (1 - max(0.0, (s - 0.75) / 0.25) ** 2 * 0.8)
        th = 0.011 * (1 - 0.7 * s)
        p = base + fwd * (length * s) + Vector((0, 0, 0.12 * length * s * s))   # tips curl up a little
        twist = 0.2 * s
        ring = []
        for c, h in ((0.0, 0.0), (0.2, 0.7), (0.55, 1.0), (1.0, 0.0), (0.55, -0.6), (0.2, -0.5)):
            q = p + perp * (w * (c - 0.3)) + Vector((0, 0, th * h + twist * w * (0.3 - c) * 0.5))
            ring.append(Vector((side * q.x, q.y, q.z)))
        if side < 0:
            ring.reverse()
        rings.append(ring)

    def color(co, n):
        s = (abs(co.x) - x0) / (length * math.cos(a) + 1e-6)
        return nh.lerp(BROWN_DARK, (0.04, 0.035, 0.03), nh.smoothstep(0.4, 1.0, s))
    return loft(rings), color


# ---------------------------------------------------------------- body

HEAD_Y = -0.25   # where the white hood begins


def body_shells():
    s = []
    # deep-chested torso tapering into the tail base
    ys = [-0.28, -0.20, -0.08, 0.05, 0.18, 0.29, 0.38]
    rs = [0.095, 0.14, 0.16, 0.16, 0.135, 0.095, 0.055]
    zs = [0.0, 0.0, -0.01, -0.01, 0.0, 0.01, 0.015]
    s.append(nh.tube([(0, y, z) for y, z in zip(ys, zs)], rs, sides=20, scale_xy=(1.0, 0.82)))
    s.append(nh.ellipsoid((0, -0.12, -0.05), (0.13, 0.15, 0.11), subdivisions=3))
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.11, -0.02, 0.02), (0.075, 0.19, 0.055), subdivisions=3))
    # thick feathered neck into a big, flat-crowned head
    neck = [(0, -0.22, 0.02), (0, -0.30, 0.03), (0, -0.37, 0.035)]
    s.append(nh.tube(neck, [0.09, 0.075, 0.068], sides=14))
    s.append(nh.ellipsoid((0, -0.415, 0.04), (0.066, 0.085, 0.06), subdivisions=3))
    # heavy brow ridges over the eyes
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.038, -0.45, 0.07), (0.03, 0.04, 0.018), subdivisions=2))
    # feathered legs ("trousers") tucked back under the tail
    for sx in (-1, 1):
        s.append(nh.tube([(sx * 0.065, 0.10, -0.09), (sx * 0.07, 0.22, -0.11), (sx * 0.065, 0.30, -0.10)],
                         [0.045, 0.035, 0.026], sides=10))
    return s


def body_color(co, n):
    grain = max(0.0, noise.noise(co * 32.0))
    # white hood: head and upper neck, a soft ragged edge on the nape and throat
    hood = nh.smoothstep(HEAD_Y + 0.02, HEAD_Y - 0.03, co.y + noise.noise(co * 18.0) * 0.02 - 0.03 * n.z)
    brown = nh.lerp(BROWN, BROWN_EDGE, grain * 0.4)
    brown = nh.lerp(brown, BROWN_DARK, nh.smoothstep(0.2, -0.8, n.z) * 0.5)
    white = nh.lerp(WHITE, WHITE_SHADE, nh.smoothstep(0.0, -0.9, n.z) * 0.5 + grain * 0.2)
    return nh.lerp(brown, white, hood)


def bill():
    """Deep, laterally compressed yellow bill curving down to a sharp hook."""
    pts = [(0, -0.475, 0.035), (0, -0.505, 0.036), (0, -0.535, 0.03), (0, -0.56, 0.015), (0, -0.572, -0.005),
           (0, -0.570, -0.025), (0, -0.562, -0.036)]
    return nh.tube(pts, [0.036, 0.033, 0.028, 0.021, 0.014, 0.008, 0.0], sides=12, scale_xy=(0.62, 1.0))


def lower_bill():
    pts = [(0, -0.47, 0.0), (0, -0.51, 0.002), (0, -0.54, 0.004)]
    return nh.tube(pts, [0.026, 0.02, 0.0], sides=10, scale_xy=(0.7, 0.6))


def bill_color(co, n):
    return nh.lerp(YELLOW, YELLOW_DEEP, nh.smoothstep(-0.53, -0.57, co.y) * 0.6)


def tail():
    """White tail, a fan with a slightly wedge-shaped, feather-tipped end."""
    outline = [(-0.08, 0.34, 0.015), (0.08, 0.34, 0.015), (0.13, 0.55, 0.012)]
    n = 30
    for k in range(n + 1):
        x = 0.13 - 0.26 * k / n
        y = 0.60 - 0.045 * (x / 0.13) ** 2 + 0.010 * abs(math.sin(math.pi * (x + 0.13) / 0.043)) ** 0.5
        outline.append((x, y, 0.01))
    outline.append((-0.13, 0.55, 0.012))
    return nh.flat_panel(outline, thickness=0.02)


def tail_color(co, n):
    feather = abs(math.sin(co.x * math.pi / 0.043))
    col = nh.lerp(WHITE, WHITE_SHADE, (1 - feather) ** 8 * 0.5)
    # brown undertail coverts cover the base from below
    return nh.lerp(col, BROWN, nh.smoothstep(0.42, 0.38, co.y) * (1.0 if n.z < 0 else 0.6))


def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, BROWN)
    body = parts.fuse(voxel=0.0115, smooth=6, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    # cere and bill
    mb.add(nh.ellipsoid((0, -0.468, 0.038), (0.034, 0.03, 0.03), subdivisions=2), YELLOW_DEEP)
    mb.add(bill(), bill_color)
    mb.add(lower_bill(), YELLOW_DEEP)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.047, -0.448, 0.052), (0.012, 0.016, 0.014), subdivisions=2), IRIS)
        mb.add(nh.ellipsoid((sx * 0.055, -0.452, 0.052), (0.006, 0.008, 0.008), subdivisions=1), PUPIL)
        mb.add(nh.ellipsoid((sx * 0.016, -0.49, 0.05), (0.005, 0.008, 0.004), subdivisions=1), (0.3, 0.2, 0.05))
    mb.add(tail(), tail_color, smooth=False)
    # yellow feet with black talons, drawn up under the tail
    for sx in (-1, 1):
        ankle = Vector((sx * 0.065, 0.31, -0.10))
        mb.add(nh.tube([ankle - Vector((0, 0.04, -0.01)), ankle], [0.017, 0.016], sides=8), YELLOW)
        for dx in (-0.024, 0.0, 0.024):
            tip = ankle + Vector((sx * dx, 0.085, -0.012))
            mb.add(nh.tube([ankle, ankle.lerp(tip, 0.7), tip], [0.014, 0.011, 0.006], sides=6), YELLOW)
            mb.add(nh.tube([tip, tip + Vector((0, 0.018, -0.016)), tip + Vector((0, 0.022, -0.03))],
                           [0.007, 0.004, 0.0], sides=5), TALON)
    for side in (1, -1):
        mb.add(*make_wing(side))
        for chord_frac, angle, length in PRIMARIES:
            mb.add(*primary(side, chord_frac, angle, length))

    return mb.to_object("BaldEagle", roughness=0.75)


if __name__ == "__main__":
    nh.run(build, "BaldEagle", background=(0.45, 0.58, 0.70),
           views=((35, 25), (20, 70), (0, 89), (180, -35), (-60, 10)))
