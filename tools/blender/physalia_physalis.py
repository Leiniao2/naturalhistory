"""
Procedural low-poly Portuguese man o' war (Physalia physalis) for the map.

An elongated, lopsided gas float (pale blue blushing to violet) with a crinkled
pink-magenta crest along its top, a cluster of short blue polyps underneath,
and a few wavy, tapering blue tentacles hanging below the waterline.
All colour lives in vertex colours (see nh_model.py).

Usage:
  blender --background --python tools/blender/physalia_physalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PortugueseManOWar.fbx
Pivot: the waterline (z = 0 at the float's underside); tentacles hang below.
Faces -Y (the blunt end of the float).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

SEED = 11
FLOAT_LENGTH = 1.0       # along Y
FLOAT_RADII = (0.17, 0.15)  # x (width), z (height) at the fattest point
TENTACLES = 9
TENTACLE_LENGTH = (0.45, 0.85)

FLOAT_LOW = (0.60, 0.72, 1.00)   # pale glassy blue near the water
FLOAT_HIGH = (0.64, 0.40, 0.96)  # violet toward the crest
FLOAT_SHINE = (0.90, 0.96, 1.00) # fake specular band along the upper flank
CREST_BASE = (0.70, 0.55, 0.92)
CREST_EDGE = (1.00, 0.38, 0.70)  # pink-magenta rim
POLYP = (0.36, 0.42, 0.90)
POLYP_TIP = (0.62, 0.45, 0.88)
POLYP_TIPS = ((0.62, 0.45, 0.88), (0.86, 0.45, 0.80), (0.45, 0.62, 0.98))
TENTACLE_ROOT = (0.25, 0.38, 0.90)
TENTACLE_TIP = (0.55, 0.72, 0.98)


# ---------------------------------------------------------------- float shape

def _profile(t):
    """Cross-section scale, x drift and z lift along the float, t in [-1 (front), 1 (back)]."""
    body = math.sqrt(max(0.0, 1.0 - t * t))
    # bulbous front, narrowing toward the raised, pointed back
    scale = body * (1.1 - 0.5 * nh.smoothstep(-0.3, 1.0, t))
    drift = 0.035 * t + 0.02 * math.sin(t * 2.4)       # lopsided curve
    lift = 0.24 * nh.smoothstep(0.0, 1.0, t) ** 2      # back end curls upward
    return scale, drift, lift


def float_top(y):
    """Approximate z of the float's top surface at y (before the waterline shift)."""
    t = max(-1.0, min(1.0, y / (FLOAT_LENGTH * 0.5)))
    scale, _, lift = _profile(t)
    return FLOAT_RADII[1] * scale + lift


def make_float(rings=16, segments=16):
    bm = bmesh.new()
    half = FLOAT_LENGTH * 0.5
    grid = []
    for i in range(1, rings):
        u = i / rings
        t = -math.cos(math.pi * u)
        scale, drift, lift = _profile(t)
        ring = []
        for j in range(segments):
            a = j / segments * math.tau
            # slightly flatter belly where it rests on the water
            zr = FLOAT_RADII[1] * (0.75 if math.sin(a) < 0 else 1.0)
            ring.append(bm.verts.new((drift + FLOAT_RADII[0] * scale * math.cos(a),
                                      t * half,
                                      zr * scale * math.sin(a) + lift)))
        grid.append(ring)
    _, d0, l0 = _profile(-1.0)
    _, d1, l1 = _profile(1.0)
    front = bm.verts.new((d0, -half, l0))
    back = bm.verts.new((d1, half, l1 + 0.01))
    for a, b in zip(grid, grid[1:]):
        for j in range(segments):
            k = (j + 1) % segments
            bm.faces.new([a[j], a[k], b[k], b[j]])
    for j in range(segments):
        k = (j + 1) % segments
        bm.faces.new([front, grid[0][k], grid[0][j]])
        bm.faces.new([back, grid[-1][j], grid[-1][k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    zmax = max(v.co.z for v in bm.verts)

    def color(co, n):
        h = nh.smoothstep(-0.05, zmax, co.z)
        c = nh.lerp(FLOAT_LOW, FLOAT_HIGH, h ** 1.1)
        # pink blush toward the raised back tip
        c = nh.lerp(c, CREST_EDGE, 0.6 * nh.smoothstep(0.12, 0.5, co.y))
        # glossy band on the upper flanks facing outwards
        shine = max(0.0, n.z) * (1.0 - abs(n.z)) * 2.2
        return nh.lerp(c, FLOAT_SHINE, min(1.0, shine) * 0.4)

    return bm, color


def make_crest(steps=34, thickness=0.012):
    """Crinkled sail along the top of the float: a thin, wavy, scalloped slab."""
    bm = bmesh.new()
    y0, y1 = -0.30, 0.46
    left, right = [], []
    for i in range(steps + 1):
        s = i / steps
        y = y0 + (y1 - y0) * s
        base = float_top(y) - 0.03
        height = 0.17 * math.sin(math.pi * s) ** 0.8 * (1.0 + 0.25 * math.sin(s * 3.1))
        scallop = 0.018 * abs(math.sin(s * math.pi * 9))
        top = base + 0.03 + height + scallop
        zig = 0.022 * math.sin(s * math.pi * 13) * math.sin(math.pi * s)  # crinkles
        _, drift, _ = _profile(y / (FLOAT_LENGTH * 0.5))
        for side, out in ((-1, left), (1, right)):
            x = drift + side * thickness * 0.5
            out.append((bm.verts.new((x, y, base)), bm.verts.new((x + zig, y, top))))
    for strip, flip in ((left, True), (right, False)):
        for (b0, t0), (b1, t1) in zip(strip, strip[1:]):
            q = [b0, b1, t1, t0]
            bm.faces.new(list(reversed(q)) if flip else q)
    for (lb0, lt0), (lb1, lt1), (rb0, rt0), (rb1, rt1) in zip(left, left[1:], right, right[1:]):
        bm.faces.new([lt0, lt1, rt1, rt0])  # rim
    bm.faces.new([left[0][0], left[0][1], right[0][1], right[0][0]])
    bm.faces.new([left[-1][0], right[-1][0], right[-1][1], left[-1][1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        rel = (co.z - (float_top(co.y) - 0.03)) / 0.2
        return nh.lerp(CREST_BASE, CREST_EDGE, nh.smoothstep(0.1, 0.8, rel))

    return bm, color


# ---------------------------------------------------------------- underside

def make_polyp(rng, root):
    """Short drooping polyp: a little tapered tube ending in a bulb."""
    length = rng.uniform(0.06, 0.13)
    lean = Vector((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), 0))
    pts = [root, root + lean * 0.4 + Vector((0, 0, -length * 0.5)), root + lean + Vector((0, 0, -length))]
    r = rng.uniform(0.014, 0.022)
    bm = nh.tube(pts, [r, r * 0.8, r * 0.6], sides=5)
    tip = nh.ellipsoid(pts[-1], (r * 1.3, r * 1.3, r * 1.5), subdivisions=1)
    bm2 = bmesh.new()
    for src in (bm, tip):
        vmap = {v: bm2.verts.new(v.co) for v in src.verts}
        for f in src.faces:
            bm2.faces.new([vmap[v] for v in f.verts])
        src.free()
    top = root.z
    tip_col = rng.choice(POLYP_TIPS)

    def color(co, n):
        return nh.lerp(POLYP, tip_col, nh.smoothstep(top, top - length, co.z))

    return bm2, color


def make_tentacle(rng, root):
    length = rng.uniform(*TENTACLE_LENGTH)
    n = 10
    phase = rng.uniform(0, math.tau)
    sway = rng.uniform(0.03, 0.06)
    drift = Vector((rng.uniform(-0.12, 0.12), rng.uniform(0.0, 0.25), 0))  # trail back with the wind
    pts, radii = [], []
    for i in range(n + 1):
        s = i / n
        wave = math.sin(s * math.tau * 1.6 + phase) * sway * s
        p = root + drift * s * s + Vector((wave, wave * 0.5, -length * s))
        pts.append(p)
        radii.append(0.017 * (1.0 - s) ** 0.9 + 0.002 if i < n else 0.0)
    bm = nh.tube(pts, radii, sides=5, cap_end=False)
    top = root.z

    def color(co, n_):
        return nh.lerp(TENTACLE_ROOT, TENTACLE_TIP, nh.smoothstep(top, top - length, co.z) ** 0.7)

    return bm, color


def build():
    rng = random.Random(SEED)
    parts = [make_float(), make_crest()]

    # underside: polyps clustered under the front two-thirds, tentacles from the same zone
    belly = []
    for _ in range(32):
        y = rng.uniform(-0.38, 0.18)
        t = y / (FLOAT_LENGTH * 0.5)
        scale, drift, lift = _profile(t)
        x = drift + rng.uniform(-0.6, 0.6) * FLOAT_RADII[0] * scale
        belly.append(Vector((x, y, lift - FLOAT_RADII[1] * 0.75 * scale * 0.85)))
    for root in belly[:24]:
        parts.append(make_polyp(rng, root))
    for i in range(TENTACLES):
        parts.append(make_tentacle(rng, belly[24 + i % 8]))

    # waterline: the float's underside sits at z = 0
    float_bm = parts[0][0]
    dz = -min(v.co.z for v in float_bm.verts)
    shift = Matrix.Translation((0, 0, dz))
    mb = nh.MeshBuilder()
    for bm, color in parts:
        nh.transform(bm, shift)
        mb.add(bm, (lambda c: lambda co, n: c(co - Vector((0, 0, dz)), n))(color))
    return mb.to_object("PortugueseManOWar", roughness=0.25)


if __name__ == "__main__":
    nh.run(build, "PortugueseManOWar",
           background=(0.04, 0.20, 0.30),
           views=((40, 22), (-90, 5), (150, 35)))

