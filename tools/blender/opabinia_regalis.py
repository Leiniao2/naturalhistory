"""
Procedural low-poly Opabinia regalis (Burgess Shale stem arthropod) for map colonies.

A slender, flattened, segmented trunk with a row of overlapping lateral flaps
down each side, each flap carrying a frilly gill blade on its upper surface; a
tail fan of three pairs of upturned blades; a small rounded head crowned with
five mushroom-shaped stalked eyes (two pairs plus one in the middle); and the
long, flexible, banded frontal proboscis curling down from under the head and
ending in a grasping claw of two spiny jaws. Muted pinkish grey-brown with
darker segment bands and redder gills. Faces -Y, pivot at the body centre
(Swim style).

Usage:
  blender --background --python tools/blender/opabinia_regalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Opabinia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.74, 0.52, 0.42)       # pinkish grey-brown
BODY_DARK = (0.46, 0.28, 0.22)  # segment bands
BELLY = (0.90, 0.74, 0.62)
FLAP = (0.80, 0.58, 0.44)
FLAP_EDGE = (0.52, 0.30, 0.22)
GILL = (0.86, 0.36, 0.30)       # gill lamellae, blood-red
TAIL = (0.88, 0.50, 0.30)
TAIL_EDGE = (0.56, 0.24, 0.14)
PROBOSCIS = (0.80, 0.56, 0.44)
PROBOSCIS_DARK = (0.56, 0.34, 0.26)
CLAW = (0.40, 0.18, 0.12)
SPINE = (0.98, 0.86, 0.66)
EYE = (0.05, 0.04, 0.05)
EYE_STALK = (0.80, 0.58, 0.46)

SEGMENTS = 15
BODY_FRONT = -0.42   # y where the trunk starts (head in front of it)
BODY_BACK = 0.60     # y where the tail fan starts
SEG_LEN = (BODY_BACK - BODY_FRONT) / SEGMENTS
HEAD_Y = -0.47


def body_width(y):
    """Half-width of the trunk: narrow neck, widest a third of the way back, tapering to the tail."""
    t = (y - BODY_FRONT) / (BODY_BACK - BODY_FRONT)
    return 0.045 + 0.065 * math.sin(math.pi * min(1.0, t * 0.85 + 0.12)) ** 0.8


def wave(y):
    """Gentle vertical ripple travelling down the body (frozen swim pose)."""
    return 0.02 * math.sin(y * 6.0 + 0.6)


def banded(light, dark, sharp=0.3):
    def color(co, n):
        t = ((co.y - BODY_FRONT) / SEG_LEN) % 1.0
        band = 1.0 - nh.smoothstep(0.0, sharp, min(t, 1.0 - t))
        c = nh.lerp(light, dark, band * 0.8)
        return nh.lerp(BELLY, c, nh.smoothstep(-0.6, 0.1, n.z))
    return color


def trunk():
    """Flattened tube along Y, two rings per segment with a pinch at each seam."""
    pts, radii = [], []
    n = SEGMENTS * 2
    for i in range(n + 1):
        y = BODY_FRONT - 0.03 + (BODY_BACK + 0.05 - BODY_FRONT) * i / n
        r = body_width(min(max(y, BODY_FRONT), BODY_BACK)) * (0.88 if i % 2 == 0 else 1.0)
        if i == n:
            r = 0.0
        pts.append((0, y, wave(y)))
        radii.append(r)
    return nh.tube(pts, radii, sides=10, scale_xy=(1.0, 0.5))


def mirror(bm, side):
    if side < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def flap(y, side, length, width):
    """Lateral swimming flap: rounded paddle, tips trailing back and drooping a little."""
    pts = []
    n = 9
    for i in range(n):
        a = i / n * math.tau
        u = math.cos(a) * 0.5 + 0.5
        pts.append((u * length, math.sin(a) * width * (0.4 + 0.6 * u), 0.0))
    bm = nh.flat_panel(pts, thickness=0.008)
    nh.transform(bm, Matrix.Rotation(math.radians(-20), 4, "Z") @
                 Matrix.Rotation(math.radians(-8 + 8 * math.sin(y * 7.0)), 4, "Y"))
    mirror(bm, side)
    nh.transform(bm, Matrix.Translation((body_width(y) * 0.75 * side, y, wave(y) - 0.005)))
    return bm


def gill(y, side, length, width):
    """Gill blade riding on top of a flap: a comb-edged panel along its rear margin."""
    pts = [(0.0, 0.0, 0)]
    teeth = 5
    for k in range(teeth + 1):
        x = length * (0.15 + 0.8 * k / teeth)
        pts.append((x, width * (0.55 if k % 2 == 0 else 0.95), 0))
    pts.append((length * 0.9, width * 0.1, 0))
    pts.append((length * 0.2, -width * 0.15, 0))
    bm = nh.flat_panel(pts, thickness=0.006)
    nh.transform(bm, Matrix.Rotation(math.radians(-20), 4, "Z") @
                 Matrix.Rotation(math.radians(-8 + 8 * math.sin(y * 7.0) - 6), 4, "Y"))
    mirror(bm, side)
    nh.transform(bm, Matrix.Translation((body_width(y) * 0.6 * side, y, wave(y) + 0.008)))
    return bm


def flap_color(co, n):
    return nh.lerp(FLAP, FLAP_EDGE, nh.smoothstep(0.12, 0.26, abs(co.x)) * 0.8)


def tail_blade(side, k):
    """Upturned tail-fan blade; k = 0..2 from front to rear pair, the rear pair the longest."""
    length = 0.17 + 0.025 * k
    pts = [(0, -0.02, 0), (length * 0.55, -0.04, 0), (length, -0.008, 0),
           (length * 0.6, 0.036, 0), (0, 0.02, 0)]
    bm = nh.flat_panel(pts, thickness=0.01)
    yaw = math.radians(12 + 27 * k)       # front pair spread sideways, rear pair point back
    up = math.radians(22 + 12 * k)         # blades tilt steeply upward
    nh.transform(bm, Matrix.Rotation(-up, 4, "Y"))
    nh.transform(bm, Matrix.Rotation(yaw, 4, "Z"))
    mirror(bm, side)
    y = BODY_BACK - 0.02 + 0.04 * k
    nh.transform(bm, Matrix.Translation((0.025 * side, y, wave(y) + 0.02)))
    return bm


def proboscis_path():
    """Proboscis: leaves the underside of the head, reaches forward, then curls down."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = HEAD_Y - 0.05 - 0.42 * t
        z = -0.035 - 0.06 * t - 0.16 * t ** 3 + 0.03 * math.sin(t * math.pi)
        pts.append(Vector((0.0, y, z)))
    return pts


def proboscis(mb):
    pts = proboscis_path()
    n = len(pts) - 1
    radii = [0.028 * (1.0 - 0.45 * i / n) for i in range(n + 1)]

    def color(co, nrm):
        best = min(range(len(pts)), key=lambda i: (pts[i] - co).length_squared)
        return PROBOSCIS if best % 2 == 0 else PROBOSCIS_DARK  # annulated, flexible hose

    mb.add(nh.tube(pts, radii, sides=8, cap_start=True, cap_end=True), color)
    # terminal claw: two opposed, slightly gaping jaws lined with inward spines
    tip = pts[-1]
    fwd = (pts[-1] - pts[-2]).normalized()
    side = Vector((1, 0, 0))
    up = side.cross(fwd).normalized()
    for s in (-1, 1):
        base = tip - fwd * 0.005
        mid = tip + fwd * 0.055 + side * s * 0.04
        end = tip + fwd * 0.11 + side * s * 0.008
        jaw = [base, mid, end]
        mb.add(nh.tube(jaw, [0.02, 0.016, 0.0], sides=6, scale_xy=(0.7, 1.0)), CLAW)
        for k in range(3):
            t = 0.3 + 0.25 * k
            p = (mid - base) * t * 2 + base if t < 0.5 else mid.lerp(end, (t - 0.5) * 2)
            inward = -side * s
            mb.add(nh.tube([p, p + inward * 0.032 + fwd * 0.008 + up * 0.004 * (k - 1)],
                           [0.005, 0.0], sides=3, cap_start=False), SPINE, smooth=False)


def eye(mb, base, tip):
    """Short stalk topped with a dark mushroom-cap eye."""
    base, tip = Vector(base), Vector(tip)
    mb.add(nh.tube([base, tip], [0.014, 0.011], sides=6), EYE_STALK)
    d = (tip - base).normalized()
    mb.add(nh.ellipsoid(tip + d * 0.015, (0.026, 0.026, 0.022), subdivisions=2), EYE)


def build():
    mb = nh.MeshBuilder()
    mb.add(trunk(), banded(BODY, BODY_DARK))
    head = nh.uv_ellipsoid((0, HEAD_Y, 0.0), (0.075, 0.085, 0.055), segments=14, rings=8)
    mb.add(head, lambda co, n: nh.lerp(BELLY, BODY, nh.smoothstep(-0.6, 0.2, n.z)))

    for i in range(SEGMENTS):
        y = BODY_FRONT + (i + 0.5) * SEG_LEN
        t = i / (SEGMENTS - 1)
        length = 0.10 + 0.07 * math.sin(math.pi * min(1.0, t * 0.9 + 0.1))
        length *= 1.0 - 0.45 * nh.smoothstep(0.7, 1.0, t)  # rear flaps shrink ahead of the tail fan
        width = SEG_LEN * 1.3
        for side in (-1, 1):
            mb.add(flap(y, side, length, width), flap_color, smooth=False)
            mb.add(gill(y, side, length * 0.85, width * 0.7), GILL, smooth=False)

    for side in (-1, 1):
        for k in range(3):
            mb.add(tail_blade(side, k),
                   lambda co, n: nh.lerp(TAIL, TAIL_EDGE, nh.smoothstep(0.80, 0.92, co.y)), smooth=False)

    proboscis(mb)

    # five eyes: a pair at each side of the head's front, a pair behind, one in the middle
    hz = 0.035
    eye(mb, (0, HEAD_Y - 0.01, hz), (0, HEAD_Y - 0.02, hz + 0.07))
    for s in (-1, 1):
        eye(mb, (s * 0.03, HEAD_Y - 0.03, hz), (s * 0.075, HEAD_Y - 0.06, hz + 0.055))
        eye(mb, (s * 0.035, HEAD_Y + 0.025, hz), (s * 0.085, HEAD_Y + 0.04, hz + 0.065))

    obj = mb.to_object("Opabinia", roughness=0.5)
    # pivot at the body centre
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "Opabinia", background=(0.05, 0.22, 0.30), views=((35, 30), (-90, 8), (0, 80)))
