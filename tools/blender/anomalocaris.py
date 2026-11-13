"""
Procedural low-poly Anomalocaris canadensis for map colonies (Swim style).

A long, flattened, segmented body with a row of overlapping swimming lobes down
each side (rippling in a gentle wave), a tail fan of three pairs of upturned
blades, a head with large stalked compound eyes, and a pair of big segmented,
spiny frontal appendages curling down in front of the head. Reddish pink /
orange with darker segment bands. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/anomalocaris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anomalocaris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.86, 0.38, 0.26)       # reddish pink-orange
BODY_DARK = (0.55, 0.18, 0.13)  # segment bands
BELLY = (0.95, 0.66, 0.48)
LOBE = (0.93, 0.50, 0.30)
LOBE_EDGE = (0.62, 0.22, 0.14)
APPENDAGE = (0.90, 0.48, 0.24)
APPENDAGE_DARK = (0.58, 0.22, 0.10)
SPINE = (1.0, 0.86, 0.62)
EYE = (0.05, 0.04, 0.05)
EYE_STALK = (0.78, 0.36, 0.24)

SEGMENTS = 11
BODY_FRONT = -0.55   # y where the trunk starts (head in front of it)
BODY_BACK = 0.62     # y where the tail fan starts
SEG_LEN = (BODY_BACK - BODY_FRONT) / SEGMENTS


def body_width(y):
    """Half-width of the trunk at y: widest just behind the head, tapering to the tail."""
    t = (y - BODY_FRONT) / (BODY_BACK - BODY_FRONT)
    return 0.14 * (1.0 - 0.6 * t ** 1.3) + 0.02


def wave(y):
    """Small vertical ripple travelling down the body (frozen swim pose)."""
    return 0.03 * math.sin(y * 7.0)


def banded(light, dark, sharp=0.35):
    def color(co, n):
        t = ((co.y - BODY_FRONT) / SEG_LEN) % 1.0
        band = 1.0 - nh.smoothstep(0.0, sharp, min(t, 1.0 - t))  # dark seam between segments
        c = nh.lerp(light, dark, band * 0.85)
        return nh.lerp(BELLY, c, nh.smoothstep(-0.6, 0.1, n.z))
    return color


def trunk():
    """Flattened tube along Y, three rings per segment with a pinch at each seam."""
    pts, radii = [], []
    n = SEGMENTS * 3
    for i in range(n + 1):
        y = BODY_FRONT - 0.04 + (BODY_BACK + 0.06 - BODY_FRONT) * i / n
        seam = (i % 3 == 0)
        r = body_width(min(max(y, BODY_FRONT), BODY_BACK)) * (0.9 if seam else 1.0)
        if i == n:
            r = 0.0
        pts.append((0, y, wave(y)))
        radii.append(r)
    return nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.36))


def lobe(y, side, length, width):
    """One swimming flap: a rounded paddle sticking out sideways, angled slightly down."""
    pts = []
    n = 10
    for i in range(n):
        a = i / n * math.tau
        # teardrop: narrower where it joins the body
        u = math.cos(a) * 0.5 + 0.5
        x = u * length
        yy = math.sin(a) * width * (0.35 + 0.65 * u)
        pts.append((x, yy, 0.0))
    bm = nh.flat_panel(pts, thickness=0.01)
    droop = Matrix.Rotation(math.radians(-10 + 12 * math.sin(y * 6.0 + 1.0)), 4, "Y")
    sweep = Matrix.Rotation(math.radians(-12), 4, "Z")  # tips trail backwards
    nh.transform(bm, sweep @ droop)
    if side < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
        bmesh_flip(bm)
    x0 = body_width(y) * 0.8 * side
    nh.transform(bm, Matrix.Translation((x0, y, wave(y) - 0.01)))
    return bm


def bmesh_flip(bm):
    import bmesh
    bmesh.ops.reverse_faces(bm, faces=bm.faces)


def lobe_color(co, n):
    d = abs(co.x)
    edge = nh.smoothstep(0.2, 0.4, d)
    return nh.lerp(LOBE, LOBE_EDGE, edge * 0.75)


def tail_blade(side, k):
    """Upturned tail-fan blade; k = 0..2 from inner to outer pair."""
    length = 0.30 - 0.04 * k
    pts = [(0, -0.025, 0), (length * 0.6, -0.04, 0), (length, 0.0, 0), (length * 0.6, 0.04, 0), (0, 0.025, 0)]
    bm = nh.flat_panel(pts, thickness=0.014)
    yaw = math.radians(90 - 22 - 24 * k)       # fan out from straight back
    up = math.radians(28 + 6 * k)               # blades tilt upward
    nh.transform(bm, Matrix.Rotation(-up, 4, "Y"))
    nh.transform(bm, Matrix.Rotation(yaw, 4, "Z"))
    if side < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
        bmesh_flip(bm)
    nh.transform(bm, Matrix.Translation((0.015 * side, BODY_BACK + 0.04, wave(BODY_BACK) + 0.01)))
    return bm


def appendage_path(side):
    """Frontal appendage: reaches forward from under the head, then curls down and back."""
    pts = []
    n = 12
    for i in range(n + 1):
        t = i / n
        a = t * math.radians(230)
        r = 0.24 * (1.0 - 0.45 * t)
        y = -0.80 - math.sin(a) * r - 0.06 * t
        z = -0.02 + (math.cos(a) - 1.0) * r * 0.85 + 0.06
        x = side * (0.09 - 0.05 * t)
        pts.append(Vector((x, y, z)))
    return pts


def appendage(mb, side):
    pts = appendage_path(side)
    n = len(pts) - 1
    radii = [0.042 * (1.0 - 0.7 * i / n) + 0.006 for i in range(n + 1)]
    radii[-1] = 0.0

    def color(co, nrm):
        # alternate light/dark per podomere along the arm
        best = min(range(len(pts)), key=lambda i: (pts[i] - co).length)
        return APPENDAGE if best % 2 == 0 else APPENDAGE_DARK

    mb.add(nh.tube(pts, radii, sides=7, cap_start=True, cap_end=False), color)
    # paired spines on the inner (concave) side of each segment
    for i in range(1, n - 1):
        p = pts[i]
        fwd = (pts[i + 1] - pts[i - 1]).normalized()
        centre = Vector((side * 0.09, -0.86, -0.08))
        inward = (centre - p)
        inward = (inward - fwd * inward.dot(fwd)).normalized()
        for s in (-1, 1):
            off = Vector((s * 0.015, 0, 0))
            base = p + inward * radii[i] * 0.8 + off
            tip = base + inward * (0.07 * (1.0 - 0.5 * i / n)) + fwd * 0.012
            mb.add(nh.tube([base, tip], [radii[i] * 0.28, 0.0], sides=3, cap_start=False), SPINE, smooth=False)


def eye(mb, side):
    base = Vector((side * 0.08, -0.62, 0.05))
    tip = Vector((side * 0.22, -0.70, 0.12))
    mb.add(nh.tube([base, (base + tip) / 2 + Vector((0, 0, 0.02)), tip], [0.025, 0.02, 0.018], sides=6), EYE_STALK)
    mb.add(nh.ellipsoid(tip + Vector((side * 0.03, -0.01, 0.01)), (0.055, 0.045, 0.045), subdivisions=2), EYE)


def build():
    mb = nh.MeshBuilder()
    mb.add(trunk(), banded(BODY, BODY_DARK))
    # head: rounded shield in front of the trunk
    head = nh.uv_ellipsoid((0, -0.64, 0.0), (0.16, 0.15, 0.075), segments=16, rings=10)
    mb.add(head, lambda co, n: nh.lerp(BELLY, BODY, nh.smoothstep(-0.6, 0.2, n.z)))

    for i in range(SEGMENTS):
        y = BODY_FRONT + (i + 0.5) * SEG_LEN
        t = i / (SEGMENTS - 1)
        length = 0.30 * (1.0 - 0.5 * t) + 0.08 if i > 0 else 0.24
        width = SEG_LEN * 1.25  # overlap the next lobe back
        for side in (-1, 1):
            mb.add(lobe(y, side, length, width), lobe_color, smooth=False)

    for side in (-1, 1):
        for k in range(3):
            mb.add(tail_blade(side, k), lambda co, n: nh.lerp(LOBE, LOBE_EDGE, nh.smoothstep(0.75, 0.95, co.y)), smooth=False)
        appendage(mb, side)
        eye(mb, side)

    obj = mb.to_object("Anomalocaris", roughness=0.5)
    # pivot at the body centre
    zs = [v.co.z for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in obj.data.vertices:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "Anomalocaris", background=(0.05, 0.22, 0.30), views=((35, 30), (-90, 8), (0, 80)))
