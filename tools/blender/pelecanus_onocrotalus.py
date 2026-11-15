"""
Procedural great white pelican (Pelecanus onocrotalus), swimming.

Huge, buoyant white bird with a rosy-pink flush to the plumage (breeding
colour), a short shaggy crest on the nape and a yellowish patch on the breast.
The neck rises in an S to a small head with bare pink facial skin around a dark
eye; the very long, flattened bill is grey-blue along the ridge with pink and
yellow edges and a red hooked nail, and the big naked throat pouch hanging
under it is yellow-orange. The folded wings show the black primaries crossing
over the short white tail and a black line of secondaries along their lower
edge.
Large animal: high-detail fused body, ~15k triangles.

Usage:
  blender --background --python tools/blender/pelecanus_onocrotalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WhitePelican.fbx
Faces -Y, pivot at the WATERLINE (z = 0); only the keel sits below it. ~1.75 long incl. bill.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

WHITE = (0.96, 0.95, 0.93)
PINK_FLUSH = (0.99, 0.80, 0.77)   # rosy wash over the plumage
SHADE = (0.80, 0.78, 0.78)
BREAST = (0.98, 0.88, 0.58)       # yellowish breast patch
BLACK = (0.05, 0.05, 0.06)
BLACK_SHEEN = (0.13, 0.13, 0.15)
FACE = (0.98, 0.60, 0.58)         # bare pink facial skin
FACE_YELLOW = (0.98, 0.78, 0.50)
EYE = (0.18, 0.05, 0.04)
BILL_RIDGE = (0.55, 0.62, 0.72)   # grey-blue culmen
BILL_PINK = (0.95, 0.62, 0.58)
BILL_EDGE = (0.98, 0.80, 0.40)
NAIL = (0.88, 0.18, 0.12)
POUCH = (1.00, 0.70, 0.16)
POUCH_DEEP = (0.95, 0.55, 0.12)

BODY_C = Vector((0.0, 0.14, 0.09))
BODY_R = (0.25, 0.50, 0.20)
HEAD = Vector((0.0, -0.37, 0.64))
HEAD_R = (0.078, 0.105, 0.085)
# bill: base just in front of the eye, running forward and gently down
BILL_BASE = HEAD + Vector((0.0, -0.06, -0.012))
BILL_TIP = HEAD + Vector((0.0, -0.62, -0.20))


def body_deform(v):
    """Flatter keel, fuller breast."""
    k = 1.0
    if v.z < 0:
        k *= 1.0 - 0.45 * (-v.z) ** 2
    if v.y < 0:
        k *= 1.0 + 0.06 * (-v.y)
    return k


def bill_point(t, dz=0.0):
    """Point a fraction t along the bill's top line, with a slight downward sag in the middle."""
    p = BILL_BASE.lerp(BILL_TIP, t)
    return p + Vector((0, 0, -0.025 * math.sin(math.pi * t) + dz))


def body_shells():
    s = []
    body = nh.uv_ellipsoid(BODY_C, BODY_R, segments=32, rings=20, deform=body_deform)
    for v in body.verts:  # stern sweeps up toward the tail
        if v.co.y > 0.3:
            v.co.z += (v.co.y - 0.3) ** 2 * 0.9
    s.append(body)
    # deep breast where the neck joins
    s.append(nh.ellipsoid((0, -0.20, 0.16), (0.17, 0.17, 0.16), subdivisions=3))
    # S-shaped neck rising into the head
    neck = [(0, -0.22, 0.18), (0, -0.31, 0.29), (0, -0.33, 0.40), (0, -0.30, 0.50), (0, -0.33, 0.58),
            (0, -0.36, 0.63)]
    s.append(nh.tube(neck, [0.13, 0.105, 0.09, 0.085, 0.08, 0.075], sides=16))
    s.append(nh.ellipsoid(HEAD, HEAD_R, subdivisions=3))
    # forehead feathering running forward onto the bill base
    s.append(nh.ellipsoid(HEAD + Vector((0, -0.065, 0.0)), (0.035, 0.05, 0.035), subdivisions=2))
    return s


def body_color(co, n):
    rel = co - BODY_C
    grain = noise.noise(co * 18.0)
    col = nh.lerp(WHITE, PINK_FLUSH, 0.8 + 0.2 * grain)
    # less pink on the upper back, rosier on flanks and neck
    col = nh.lerp(col, WHITE, nh.smoothstep(0.6, 0.95, n.z) * 0.3)
    col = nh.lerp(col, SHADE, nh.smoothstep(0.1, -0.8, n.z) * 0.45)
    # yellowish patch on the lower front of the neck / breast
    patch = nh.smoothstep(0.18, 0.02, abs(co.z - 0.30)) * nh.smoothstep(-0.18, -0.30, co.y) * nh.smoothstep(0.0, -0.6, n.y)
    col = nh.lerp(col, BREAST, patch * 0.75)
    # keel below the waterline: wet and darker
    col = nh.lerp(col, SHADE, nh.smoothstep(0.01, -0.03, co.z) * 0.6)
    # bare pink face around the eye, extending to the bill base
    d = co - HEAD
    if co.z > 0.5:
        face = (nh.smoothstep(0.06, 0.01, d.y) * nh.smoothstep(0.05, 0.02, abs(d.z + 0.005))
                * nh.smoothstep(0.25, 0.5, abs(n.x)))
        face = max(face, nh.smoothstep(-0.055, -0.08, d.y) * nh.smoothstep(0.02, -0.02, d.z))
        col = nh.lerp(col, nh.lerp(FACE, FACE_YELLOW, nh.smoothstep(-0.03, -0.09, d.y) * 0.6), face)
    return col


def bill():
    pts = [bill_point(t) for t in (0.0, 0.15, 0.35, 0.55, 0.75, 0.9, 1.0)]
    radii = [0.034, 0.030, 0.027, 0.025, 0.023, 0.02, 0.012]
    bm = nh.tube(pts, radii, sides=10, scale_xy=(1.15, 0.5))

    def color(co, n):
        t = (BILL_BASE - co).dot((BILL_BASE - BILL_TIP).normalized()) / (BILL_BASE - BILL_TIP).length
        side = abs(co.x)
        col = nh.lerp(BILL_PINK, BILL_RIDGE, nh.smoothstep(0.012, 0.0, side) * nh.smoothstep(0.2, 0.7, n.z))
        col = nh.lerp(col, BILL_EDGE, nh.smoothstep(0.022, 0.034, side) * 0.7)
        return nh.lerp(col, NAIL, nh.smoothstep(0.9, 0.96, t))
    return bm, color


def nail():
    p = bill_point(1.0)
    pts = [p + Vector((0, 0.03, 0.002)), p + Vector((0, -0.012, 0.0)), p + Vector((0, -0.024, -0.02)),
           p + Vector((0, -0.016, -0.035))]
    return nh.tube(pts, [0.014, 0.013, 0.009, 0.0], sides=6, scale_xy=(1.0, 0.8)), NAIL


def pouch():
    """Naked throat pouch hanging from the lower mandible, deepest a third of the way along."""
    ts = [0.0, 0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92]
    depth = [0.035, 0.06, 0.085, 0.09, 0.08, 0.06, 0.035, 0.0]
    pts = [bill_point(t, -0.012 - d * 0.75) + Vector((0, 0.02 if t == 0.0 else 0, 0)) for t, d in zip(ts, depth)]
    bm = nh.tube(pts, depth, sides=12, scale_xy=(0.6, 1.0))

    def color(co, n):
        wrinkles = 0.5 + 0.5 * math.sin(co.y * 160.0 + noise.noise(co * 40.0) * 3.0)
        col = nh.lerp(POUCH, POUCH_DEEP, nh.smoothstep(0.4, -0.8, n.z) * 0.7)
        return nh.lerp(col, POUCH_DEEP, wrinkles * 0.25)
    return bm, color


def wing(side):
    """Folded wing on the flank: white coverts, black secondary line below, black primaries at the rear."""
    c = Vector((side * 0.13, 0.25, 0.20))
    bm = nh.ellipsoid((0, 0, 0), (0.12, 0.42, 0.06), subdivisions=4,
                      deform=lambda v: 1.0 - 0.25 * max(0.0, v.y) ** 2)
    nh.transform(bm, Matrix.Rotation(math.radians(side * 22), 4, "Y"))
    nh.transform(bm, Matrix.Rotation(math.radians(side * -4), 4, "Z"))
    nh.transform(bm, Matrix.Translation(c))

    def color(co, n):
        rel = co - c
        grain = noise.noise(co * 25.0)
        col = nh.lerp(WHITE, PINK_FLUSH, 0.6 + 0.2 * grain)
        # scalloped covert rows
        rows = 0.5 + 0.5 * math.sin(rel.y * 55.0 + abs(rel.x) * 30.0)
        col = nh.lerp(col, SHADE, rows * 0.12)
        # black secondaries along the lower edge, black primaries toward the back
        low = nh.smoothstep(-0.015, -0.05, rel.z) * nh.smoothstep(-0.2, 0.0, rel.y)
        back = nh.smoothstep(0.16, 0.24, rel.y)
        return nh.lerp(col, BLACK, max(low, back))
    return bm, color


def primaries(side):
    """Long black primary tips crossing over the tail."""
    shells = []
    for k, (dx, dz, L) in enumerate(((0.0, 0.0, 0.38), (0.03, -0.02, 0.35), (0.06, -0.04, 0.31))):
        base = Vector((side * (0.13 - dx), 0.42, 0.25 + dz))
        tip = Vector((side * (0.04 + dx * 0.6), 0.44 + L, 0.27 + dz * 0.6))
        mid = base.lerp(tip, 0.5) + Vector((side * 0.02, 0, 0.012))
        shells.append(nh.tube([base, mid, tip], [0.065, 0.045, 0.0], sides=8, scale_xy=(1.0, 0.3)))
    return shells


def tail():
    outline = [(-0.09, 0.56, 0.0), (0.09, 0.56, 0.0), (0.11, 0.74, 0.0), (0.0, 0.79, 0.0), (-0.11, 0.74, 0.0)]
    bm = nh.flat_panel(outline, thickness=0.025)
    nh.transform(bm, Matrix.Translation((0, 0, 0.24)))
    return bm


def crest(rng):
    """Short shaggy tuft on the back of the head."""
    shells = []
    for k in range(9):
        a = (k - 4) * 0.22
        base = HEAD + Vector((math.sin(a) * 0.035, 0.05, 0.03 - abs(k - 4) * 0.005))
        tip = base + Vector((math.sin(a) * 0.03, 0.07 * rng.uniform(0.8, 1.2), -0.02 * rng.uniform(0.5, 1.5)))
        shells.append(nh.tube([base, base.lerp(tip, 0.5), tip], [0.018, 0.012, 0.0], sides=5))
    return shells


def build():
    rng = random.Random(11)
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, WHITE)
    body = parts.fuse(voxel=0.012, smooth=6, smooth_factor=0.5, max_tris=11000)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    for shell in crest(rng):
        mb.add(shell, PINK_FLUSH)
    mb.add(*bill())
    mb.add(*nail())
    mb.add(*pouch())
    for sx in (-1, 1):
        mb.add(*wing(sx))
        for shell in primaries(sx):
            mb.add(shell, lambda co, n: nh.lerp(BLACK, BLACK_SHEEN, max(0.0, n.z) * 0.6))
    mb.add(tail(), lambda co, n: nh.lerp(WHITE, SHADE, nh.smoothstep(0.65, 0.79, co.y) * 0.4), smooth=False)

    # dark eyes set in a patch of bare pink facial skin, with a pale yellow ring
    for sx in (-1, 1):
        eye = HEAD + Vector((sx * 0.058, -0.02, 0.012))
        mb.add(nh.ellipsoid(eye + Vector((-sx * 0.004, -0.008, -0.002)), (0.02, 0.036, 0.022), subdivisions=2), FACE)
        mb.add(nh.ellipsoid(eye, (0.016, 0.02, 0.016), subdivisions=2), FACE_YELLOW)
        mb.add(nh.ellipsoid(eye + Vector((sx * 0.007, 0, 0)), (0.012, 0.013, 0.012), subdivisions=2), EYE)

    return mb.to_object("WhitePelican", roughness=0.6)


if __name__ == "__main__":
    nh.run(build, "WhitePelican", ground=(0.22, 0.42, 0.50), views=((40, 22), (-90, 5), (25, 65)))
