"""
Procedural scarlet macaw (Ara macao) in flight, wings spread mid-glide.

Big parrot with a bright scarlet head, body and shoulders. The upper wing shows
the bold yellow band of the greater coverts tipped with green, then deep blue
flight feathers out to the pointed tips; the underwing is red with golden-red
flight feathers. Blue lower back and rump, and a very long graduated tail of
red central feathers with blue tips over shorter blue outer ones. The head has
the bare white face patch (lined with tiny red feathers), a pale yellow eye, a
huge hooked bill that is ivory above with a dark base and black below, and dark
feet tucked under the body.

Usage:
  blender --background --python tools/blender/ara_macao.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ScarletMacaw.fbx
Faces -Y, pivot at the body centre (flier). ~1.15 long incl. tail, wingspan ~1.2.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

RED = (0.86, 0.05, 0.04)
RED_DEEP = (0.62, 0.03, 0.03)
ORANGE_RED = (0.95, 0.22, 0.05)
YELLOW = (1.00, 0.80, 0.06)
GREEN = (0.20, 0.62, 0.18)
BLUE = (0.05, 0.26, 0.78)
BLUE_DARK = (0.03, 0.12, 0.42)
SKY = (0.25, 0.55, 0.92)          # pale blue of the rump and tail coverts
UNDER_FLIGHT = (0.70, 0.22, 0.08) # golden-red underside of the flight feathers
FACE = (0.97, 0.95, 0.92)
FACE_LINE = (0.80, 0.30, 0.28)
BILL_UPPER = (0.93, 0.88, 0.78)
BILL_BASE = (0.12, 0.10, 0.10)
BILL_LOWER = (0.06, 0.05, 0.05)
EYE_RING = (0.98, 0.92, 0.50)
EYE = (0.05, 0.04, 0.03)
FEET = (0.30, 0.28, 0.30)

HEAD = Vector((0.0, -0.245, 0.035))
HEAD_R = (0.062, 0.072, 0.064)

HALF_SPAN = 0.60
WING_ROOT = 0.045
WING_STATIONS = 22
CHORD = (0.0, 0.06, 0.16, 0.28, 0.40, 0.52, 0.64, 0.76, 0.88, 0.95, 1.0)


def interp(keys, t):
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            s = nh.smoothstep(t0, t1, t) if t1 > t0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


# Planform in span fraction t (0 = root, 1 = tip): broad inner wing, pointed swept-back hand
LEADING = [(0.0, -0.11), (0.42, -0.135), (0.75, -0.08), (1.0, 0.07)]
CHORD_LEN = [(0.0, 0.22), (0.42, 0.21), (0.75, 0.15), (1.0, 0.02)]
DIHEDRAL = [(0.0, 0.0), (0.42, 0.04), (0.8, 0.05), (1.0, 0.03)]
THICKNESS = [(0.0, 0.05), (0.42, 0.028), (1.0, 0.005)]


def airfoil(c):
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def wing_color(t, c, top):
    if not top:
        # red underwing coverts, golden-red flight feathers
        col = nh.lerp(RED, UNDER_FLIGHT, nh.smoothstep(0.38, 0.5, c + 0.25 * nh.smoothstep(0.4, 0.8, t)))
        return nh.lerp(col, BLUE_DARK, nh.smoothstep(0.85, 1.0, t) * 0.5)
    inner = 1.0 - nh.smoothstep(0.45, 0.6, t)   # coverts bands fade out toward the hand
    # chord bands of the inner wing: red lesser coverts, yellow greater coverts, green tips, blue remiges
    if c < 0.24:
        band = RED
    elif c < 0.46:
        band = YELLOW
    elif c < 0.56:
        band = GREEN
    else:
        band = BLUE
    col = nh.lerp(BLUE, band, inner)
    # red shoulder runs along the leading edge a little way into the hand
    col = nh.lerp(col, RED, (1.0 - nh.smoothstep(0.08, 0.14, c)) * (1.0 - nh.smoothstep(0.55, 0.7, t)))
    # darker blue tips to the flight feathers
    return nh.lerp(col, BLUE_DARK, nh.smoothstep(0.8, 1.0, max(c, t)) * 0.6)


def make_wing(side):
    bm = bmesh.new()
    colors = {}
    rings = []
    for i in range(WING_STATIONS + 1):
        t = i / WING_STATIONS
        x = WING_ROOT + t * (HALF_SPAN - WING_ROOT)
        le = interp(LEADING, t)
        ch = interp(CHORD_LEN, t)
        # feather-tip serration along the trailing edge
        ch -= 0.012 * (1 - abs(math.sin(math.pi * x / 0.05))) * (1 - t)
        z0 = interp(DIHEDRAL, t)
        th = interp(THICKNESS, t)
        if i == WING_STATIONS:
            v = bm.verts.new(Vector((side * x, le + ch * 0.5, z0)))
            colors[v] = wing_color(t, 0.9, True)
            rings.append([v])
            continue
        top = [(c, z0 + th * airfoil(c)) for c in CHORD]
        bottom = [(c, z0 - th * 0.35 * airfoil(c)) for c in reversed(CHORD[1:-1])]
        ring = []
        for k, (c, z) in enumerate(top + bottom):
            v = bm.verts.new(Vector((side * x, le + ch * c, z)))
            colors[v] = wing_color(t, c, k < len(top))
            ring.append(v)
        rings.append(ring)
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            if len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lookup = {tuple(round(c, 5) for c in v.co): col for v, col in colors.items()}
    return bm, (lambda co, nrm: lookup.get(tuple(round(c, 5) for c in co), RED))


# ---------------------------------------------------------------- body

def body_shells():
    s = []
    ys = [-0.20, -0.14, -0.06, 0.02, 0.10, 0.17]
    rs = [0.058, 0.075, 0.082, 0.075, 0.058, 0.035]
    zs = [0.02, 0.01, 0.0, 0.0, 0.004, 0.01]
    s.append(nh.tube([(0, y, z) for y, z in zip(ys, zs)], rs, sides=16, scale_xy=(1.0, 0.9)))
    s.append(nh.ellipsoid(HEAD, HEAD_R, subdivisions=3))
    # rounded cheeks behind the face patch
    s.append(nh.ellipsoid(HEAD + Vector((0, 0.03, -0.01)), (0.06, 0.05, 0.055), subdivisions=2))
    # feet tucked under the vent
    for sx in (-1, 1):
        s.append(nh.tube([(sx * 0.025, 0.04, -0.06), (sx * 0.028, 0.1, -0.06), (sx * 0.025, 0.14, -0.045)],
                         [0.014, 0.012, 0.008], sides=6))
    return s


def body_color(co, n):
    d = co - HEAD
    grain = noise.noise(co * 40.0)
    col = nh.lerp(RED, RED_DEEP, max(0.0, grain) * 0.4 + nh.smoothstep(0.0, -0.9, n.z) * 0.3)
    # blue lower back and rump
    rump = nh.smoothstep(0.05, 0.11, co.y) * nh.smoothstep(-0.1, 0.4, n.z)
    col = nh.lerp(col, SKY, rump)
    # dark grey feet
    if co.z < -0.045 and abs(co.x) > 0.012 and co.y > 0.03:
        return FEET
    # bare white face from the bill base back past the eye, with lines of tiny red feathers
    face = (nh.smoothstep(0.015, -0.01, d.y) * nh.smoothstep(0.035, 0.015, d.z)
            * nh.smoothstep(-0.05, -0.03, d.z) * nh.smoothstep(0.3, 0.55, abs(n.x)))
    if face > 0:
        lines = nh.smoothstep(0.75, 0.95, math.sin(d.z * 520.0 + d.y * 90.0))
        col = nh.lerp(col, nh.lerp(FACE, FACE_LINE, lines * 0.6), face)
    return col


def bill():
    """Huge hooked upper mandible (ivory with a dark base) over a black lower mandible."""
    base = HEAD + Vector((0, -0.055, 0.0))
    upper = [base + Vector(p) for p in ((0, 0.0, 0.012), (0, -0.035, 0.02), (0, -0.065, 0.006),
                                        (0, -0.08, -0.025), (0, -0.074, -0.055), (0, -0.064, -0.068))]
    up = nh.tube(upper, [0.036, 0.032, 0.026, 0.018, 0.009, 0.0], sides=10, scale_xy=(0.8, 1.0))

    def up_col(co, n):
        dark = nh.smoothstep(0.012, 0.0, co.y - base.y) * nh.smoothstep(base.z + 0.02, base.z - 0.01, co.z)
        return nh.lerp(BILL_UPPER, BILL_BASE, dark * 0.85)

    lower = [base + Vector(p) for p in ((0, 0.005, -0.028), (0, -0.03, -0.04), (0, -0.052, -0.05))]
    lo = nh.tube(lower, [0.03, 0.024, 0.0], sides=8, scale_xy=(0.9, 1.0))
    return [(up, up_col), (lo, BILL_LOWER)]


def tail():
    """Very long graduated tail: red central feathers with blue tips, shorter blue outer ones."""
    shells = []
    feathers = [  # (x offset, length, width, base colour)
        (0.0, 0.74, 0.042, RED),
        (0.022, 0.62, 0.04, RED),
        (0.042, 0.46, 0.038, BLUE),
        (0.058, 0.34, 0.036, BLUE),
    ]
    for k, (dx, L, w, base_col) in enumerate(feathers):
        for sx in ((1,) if dx == 0 else (-1, 1)):
            root = Vector((sx * dx * 0.4, 0.13, 0.008 - k * 0.003))
            tip = Vector((sx * dx * 0.9, 0.13 + L, -0.02 - k * 0.004))
            pts = [root.lerp(tip, s) + Vector((0, 0, -0.03 * math.sin(math.pi * s) * 0.5)) for s in (0, 0.3, 0.65, 0.92, 1.0)]
            ws = [w * 0.8, w, w * 0.85, w * 0.5, 0.0]
            bm = nh.tube(pts, ws, sides=6, scale_xy=(1.0, 0.18))

            def col(co, n, root=root, L=L, base_col=base_col):
                s = (co.y - root.y) / L
                tip_blue = nh.smoothstep(0.72, 0.85, s) if base_col == RED else 0.0
                c = nh.lerp(base_col, BLUE, tip_blue)
                c = nh.lerp(c, BLUE_DARK, nh.smoothstep(0.9, 1.0, s) * 0.5)
                # rump coverts blue at the root
                return nh.lerp(c, SKY, nh.smoothstep(0.12, 0.0, s))
            shells.append((bm, col))
    return shells


def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, RED)
    body = parts.fuse(voxel=0.008, smooth=6, smooth_factor=0.5, max_tris=4500)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    for bm, col in bill():
        mb.add(bm, col)
    for sx in (-1, 1):
        eye = HEAD + Vector((sx * 0.052, -0.022, 0.018))
        mb.add(nh.ellipsoid(eye, (0.011, 0.012, 0.011), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid(eye + Vector((sx * 0.006, -0.002, 0)), (0.0065, 0.007, 0.0065), subdivisions=1), EYE)
    for bm, col in tail():
        mb.add(bm, col, smooth=False)
    for side in (1, -1):
        mb.add(*make_wing(side))
    obj = mb.to_object("ScarletMacaw", roughness=0.5)
    return obj


if __name__ == "__main__":
    nh.run(build, "ScarletMacaw", background=(0.45, 0.58, 0.70),
           views=((35, 25), (20, 70), (-90, 8), (180, -35)))
