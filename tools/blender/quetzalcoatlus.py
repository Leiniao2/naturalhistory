"""
Procedural Quetzalcoatlus northropi (giant azhdarchid pterosaur), gliding.

Body, shoulder girdle, muscular arms, the long vertebrate neck and the skull
with its tall crest are overlapping primitives fused into one seamless surface
(nh_model.MeshBuilder.fuse) and repainted procedurally with a mottled
pycnofibre coat. The wings are high-resolution lofted membranes running from
the bony leading edge (shoulder -> propatagium -> wrist -> wing finger) back to
the ankle; they billow between the bones, ripple slightly, carry fine
actinofibril streaks and curve up and back at the tips. The wing-finger bones
stand as a ridge along the leading edge.

Usage:
  blender --background --python tools/blender/quetzalcoatlus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Quetzalcoatlus.fbx (faces -Y, pivot at the body centre)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

# ---------------------------------------------------------------- palette
FUR = (0.50, 0.36, 0.24)          # pycnofibre coat
FUR_DARK = (0.30, 0.20, 0.13)
FUR_LIGHT = (0.74, 0.64, 0.50)    # belly / throat
ARM = (0.26, 0.17, 0.11)
HEAD = (0.62, 0.55, 0.46)
CREST = (0.86, 0.28, 0.10)
CREST_EDGE = (0.45, 0.10, 0.05)
BEAK_BASE = (0.92, 0.55, 0.18)
BEAK_TIP = (0.85, 0.80, 0.70)
EYE = (0.02, 0.02, 0.02)
EYE_RING = (0.95, 0.78, 0.30)
MEMBRANE_ROOT = (0.60, 0.30, 0.16)   # warm, near the body
MEMBRANE = (0.50, 0.36, 0.24)
MEMBRANE_EDGE = (0.78, 0.62, 0.45)   # thin pale trailing edge
LEADING = (0.16, 0.10, 0.06)         # dark bony leading edge
FIBRE = (0.32, 0.21, 0.13)

HALF_SPAN = 2.8
# (span x, y) along the leading edge (shoulder -> propatagium -> wrist -> wing finger tip)
LEADING_EDGE = [(0.10, -0.12), (0.45, -0.32), (0.95, -0.26), (1.45, -0.16), (1.95, -0.03), (2.40, 0.13), (2.80, 0.38)]
# trailing edge: body flank -> ankle -> concave sweep to the narrow tip
TRAILING_EDGE = [(0.10, 0.30), (0.22, 0.58), (0.55, 0.52), (1.00, 0.40), (1.50, 0.27), (2.00, 0.21), (2.40, 0.25), (2.80, 0.38)]
WRIST_X = 0.95


def interp(table, x):
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return table[-1][1]


def wing_z(x):
    """Wing height along the span: gentle dihedral, then the tips curl up."""
    ax = abs(x)
    return 0.10 * ax - 0.018 * ax * ax + 0.22 * nh.smoothstep(2.1, 2.8, ax) ** 2


# ---------------------------------------------------------------- wings

def wing_membrane(sx, nu=64, nv=14, thickness=0.014):
    """Closed lofted membrane for one side: billows between the leading-edge bones and the
    trailing edge, ripples a little, and carries actinofibril streaks in the vertex colours."""
    bm = bmesh.new()
    x0 = LEADING_EDGE[0][0]
    grid = {}
    for side, dz in (("top", 0.5), ("bot", -0.5)):
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (HALF_SPAN - x0) * (1 - (1 - u) ** 1.25)   # denser toward the tip
            yl, yt = interp(LEADING_EDGE, x), interp(TRAILING_EDGE, x)
            taper = 1.0 - u * 0.75
            for j in range(nv + 1):
                v = j / nv
                y = yl + (yt - yl) * v
                billow = -0.045 * math.sin(math.pi * min(1.0, v * 1.15)) * taper   # sags between the bones
                camber = 0.03 * math.sin(math.pi * v) * taper
                ripple = 0.006 * math.sin(x * 26.0 + v * 2.0) * v
                z = wing_z(x) + camber + billow + ripple + dz * thickness * taper
                grid[side, i, j] = bm.verts.new((sx * x, y, z))
    for i in range(nu):
        for j in range(nv):
            bm.faces.new([grid["top", i, j], grid["top", i + 1, j], grid["top", i + 1, j + 1], grid["top", i, j + 1]])
            bm.faces.new([grid["bot", i, j], grid["bot", i, j + 1], grid["bot", i + 1, j + 1], grid["bot", i + 1, j]])
    rim = ([(i, 0) for i in range(nu + 1)] + [(nu, j) for j in range(1, nv + 1)]
           + [(i, nv) for i in range(nu - 1, -1, -1)] + [(0, j) for j in range(nv - 1, 0, -1)])
    for a, b in zip(rim, rim[1:] + rim[:1]):
        try:
            bm.faces.new([grid["top", a[0], a[1]], grid["bot", a[0], a[1]], grid["bot", b[0], b[1]], grid["top", b[0], b[1]]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, normal):
        x = abs(co.x)
        yl, yt = interp(LEADING_EDGE, x), interp(TRAILING_EDGE, x)
        v = 0.0 if yt == yl else max(0.0, min(1.0, (co.y - yl) / (yt - yl)))
        base = nh.lerp(MEMBRANE_ROOT, MEMBRANE, nh.smoothstep(0.1, 1.3, x))
        c = nh.lerp(LEADING, base, nh.smoothstep(0.0, 0.22, v))
        c = nh.lerp(c, MEMBRANE_EDGE, nh.smoothstep(0.7, 1.0, v))
        # actinofibrils: fine streaks fanning from the wing finger back toward the trailing edge
        fibre = 0.5 + 0.5 * math.sin(x * 34.0 - v * 5.0)
        c = nh.lerp(c, FIBRE, fibre ** 3 * 0.35 * nh.smoothstep(0.12, 0.4, v) * (1 - nh.smoothstep(0.82, 1.0, v)))
        # soft mottling
        c = nh.lerp(c, FUR_DARK, max(0.0, noise.noise(Vector((x * 3.0, co.y * 3.0, 0.5)))) * 0.25)
        if normal.z < -0.5:
            c = nh.lerp(c, FUR_LIGHT, 0.3)   # paler underside
        return c
    return bm, color


def wing_finger(sx):
    """Bony ridge along the leading edge from the wrist to the tip, with phalanx joints."""
    pts, radii = [], []
    n = 14
    for k in range(n + 1):
        t = k / n
        x = WRIST_X + (HALF_SPAN - WRIST_X) * t
        pts.append(Vector((sx * x, interp(LEADING_EDGE, x) + 0.012, wing_z(x) + 0.018 * (1 - t))))
        radii.append(0.042 * (1 - t) + 0.006 if k < n else 0.0)
    shells = [(nh.tube(pts, radii, sides=7), LEADING)]
    for t in (0.0, 0.36, 0.64, 0.86):                    # wrist and three phalanx joints
        x = WRIST_X + (HALF_SPAN - WRIST_X) * t
        r = 0.05 * (1 - t) + 0.012
        c = (sx * x, interp(LEADING_EDGE, x) + 0.012, wing_z(x) + 0.02 * (1 - t))
        shells.append((nh.ellipsoid(c, (r * 1.2, r, r * 0.9), subdivisions=2), LEADING))
    return shells


# ---------------------------------------------------------------- body (fused)

def body_shells():
    """Overlapping primitives for the seamless torso, arms, neck, head and legs."""
    s = []
    # torso: deep chest, robust shoulder girdle, pectoral keel, short hips and tail
    s.append(nh.uv_ellipsoid((0, 0.04, 0.0), (0.15, 0.32, 0.125), segments=20, rings=12))
    s.append(nh.uv_ellipsoid((0, -0.13, -0.035), (0.09, 0.12, 0.085), segments=14, rings=10))   # keel
    for sx in (-1, 1):
        s.append(nh.uv_ellipsoid((sx * 0.12, -0.11, 0.04), (0.105, 0.12, 0.085), segments=14, rings=10))  # shoulder
    s.append(nh.tube([(0, 0.28, -0.01), (0, 0.40, -0.02), (0, 0.46, -0.03)], [0.06, 0.03, 0.012], sides=10))

    # neck: long and stiff, rising slightly, with vertebral swellings
    n = 16
    a, b = Vector((0, -0.18, 0.04)), Vector((0, -1.12, 0.19))
    pts = [a.lerp(b, k / n) for k in range(n + 1)]
    radii = [(0.070 - 0.025 * (k / n)) * (1.0 + 0.10 * math.cos(k * math.pi)) for k in range(n + 1)]
    s.append(nh.tube(pts, radii, sides=12))
    s.append(nh.uv_ellipsoid((0, -0.26, 0.03), (0.07, 0.12, 0.07), segments=12, rings=8))  # neck base

    # skull: rounded braincase, huge tapered beak, tall crest tilted back (partly visible from above)
    s.append(nh.uv_ellipsoid((0, -1.14, 0.21), (0.065, 0.11, 0.075), segments=14, rings=10))
    beak = [(0, -1.12, 0.20), (0, -1.30, 0.18), (0, -1.55, 0.12), (0, -1.80, 0.05), (0, -1.98, 0.00)]
    s.append(nh.tube(beak, [0.085, 0.072, 0.052, 0.034, 0.022], sides=12, scale_xy=(0.72, 1.0)))
    crest = nh.uv_ellipsoid((0, 0, 0), (0.05, 0.19, 0.13), segments=16, rings=10)
    nh.transform(crest, Matrix.Translation((0, -1.04, 0.32)) @ Matrix.Rotation(math.radians(-48), 4, "X"))
    s.append(crest)

    # arms: muscular humerus out to the elbow, forearm forward to the wrist, wrist knob
    for sx in (-1, 1):
        sh = Vector((sx * 0.14, -0.10, 0.05))
        el = Vector((sx * 0.46, -0.06, wing_z(0.46) + 0.03))
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X) + 0.012, wing_z(WRIST_X) + 0.02))
        s.append(nh.tube([sh, sh.lerp(el, 0.45) + Vector((0, 0, 0.012)), el], [0.085, 0.075, 0.05], sides=10))
        s.append(nh.tube([el, el.lerp(wr, 0.5), wr], [0.045, 0.036, 0.04], sides=10))
        # legs trailing back to the ankle under the membrane
        ankle = Vector((sx * 0.22, 0.58, wing_z(0.22) - 0.03))
        s.append(nh.tube([Vector((sx * 0.07, 0.20, -0.04)), Vector((sx * 0.14, 0.40, -0.03)), ankle],
                         [0.045, 0.03, 0.022], sides=8))
    return s


def body_color(co, normal):
    x, y, z = co
    mottle = noise.noise(co * 18.0)
    fuzz = noise.noise(co * 60.0)
    # beak and head
    if y < -1.0 and abs(x) < 0.12:
        if z > 0.25 or (z > 0.21 and y > -1.12):           # crest
            edge = nh.smoothstep(0.38, 0.46, z + (-y - 1.0) * 0.15)
            return nh.lerp(CREST, CREST_EDGE, edge * 0.7 + max(0.0, mottle) * 0.2)
        if y < -1.22:                                    # beak
            return nh.lerp(BEAK_BASE, BEAK_TIP, nh.smoothstep(-1.3, -1.9, y))
        return nh.lerp(HEAD, CREST, nh.smoothstep(0.22, 0.28, z) * 0.6)
    # arms and legs: dark, leathery
    if abs(x) > 0.2 or (y > 0.3 and z < -0.01 and abs(x) > 0.05):
        return nh.lerp(ARM, FUR_DARK, 0.4 + 0.3 * mottle)
    # pycnofibre coat: mottled brown, darker dorsal stripe, pale belly/throat
    up = normal.z
    c = nh.lerp(FUR_LIGHT, FUR, nh.smoothstep(-0.5, 0.2, up))
    c = nh.lerp(c, FUR_DARK, nh.smoothstep(0.7, 1.0, up) * 0.55)
    return nh.lerp(c, FUR_DARK, max(0.0, mottle) * 0.35 + max(0.0, fuzz) * 0.15)


def fuzz(bm, amount=0.004):
    """Pycnofibre 'fuzz': tiny normal displacement on the torso and neck only."""
    bm.normal_update()
    for v in bm.verts:
        if v.co.y > -1.0 and abs(v.co.x) < 0.2:
            v.co += v.normal * noise.noise(v.co * 70.0) * amount
    bm.normal_update()


# ---------------------------------------------------------------- assemble

def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, FUR)
    body = parts.fuse(voxel=0.011, smooth=5, smooth_factor=0.5, max_tris=7000)
    fuzz(body)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)

    # sharp beak tip (thinner than the fuse resolution keeps)
    mb.add(nh.tube([(0, -1.90, 0.02), (0, -2.06, -0.025), (0, -2.22, -0.05)], [0.026, 0.014, 0.0],
                   sides=8, scale_xy=(0.72, 1.0)), BEAK_TIP)
    # eyes with a pale ring
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.058, -1.18, 0.225), (0.02, 0.026, 0.02), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid((sx * 0.07, -1.18, 0.226), (0.013, 0.016, 0.013), subdivisions=2), EYE)

    for sx in (-1, 1):
        mb.add(*wing_membrane(sx))
        for shell, col in wing_finger(sx):
            mb.add(shell, col)
        # three small clawed fingers folded at the wrist
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X), wing_z(WRIST_X) + 0.03))
        for k, dx in enumerate((-0.035, 0.0, 0.035)):
            tip = wr + Vector((sx * dx, -0.13 - 0.015 * k, 0.0))
            mb.add(nh.tube([wr, wr.lerp(tip, 0.6), tip], [0.016, 0.011, 0.0], sides=5), FUR_DARK)
        # feet trailing past the ankle
        ankle = Vector((sx * 0.22, 0.58, wing_z(0.22) - 0.03))
        for dx in (-0.025, 0.0, 0.025):
            tip = ankle + Vector((sx * dx, 0.13, -0.02))
            mb.add(nh.tube([ankle, tip], [0.016, 0.0], sides=5), ARM)

    return mb.to_object("Quetzalcoatlus")


if __name__ == "__main__":
    nh.run(build, "Quetzalcoatlus", views=((35, 25), (20, 70), (0, 89), (180, -35)))
