"""
Procedural low-poly superb lyrebird (Menura novaehollandiae), male in display.

A pheasant-sized brown ground bird on strong grey legs with its tail raised in
the classic lyre: two broad S-curved outer feathers banded chestnut with pale
notches, framing a fan of fine silvery filamentous plumes that arch outward.
The tail leans back a little so it still reads from a high map camera.

Usage:
  blender --background --python tools/blender/superb_lyrebird.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SuperbLyrebird.fbx (faces -Y, pivot at the feet)
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

SEED = 11

BROWN = (0.30, 0.19, 0.11)
BROWN_DARK = (0.20, 0.12, 0.07)
BELLY = (0.48, 0.38, 0.28)
THROAT = (0.55, 0.30, 0.17)    # rufous throat
LEG = (0.38, 0.38, 0.40)
BEAK = (0.12, 0.11, 0.10)
EYE = (0.03, 0.03, 0.03)
CHESTNUT = (0.42, 0.20, 0.08)
NOTCH = (0.86, 0.78, 0.62)     # pale translucent notches in the lyrate feathers
FEATHER_EDGE = (0.16, 0.08, 0.04)
SILVER = (0.86, 0.88, 0.92)
SILVER_DARK = (0.48, 0.50, 0.56)

TAIL_TILT = math.radians(-22)  # lean the tail back (+Y) so it shows from above
TAIL_BASE = Vector((0.0, 0.24, 0.50))


def ribbon(points, widths, thickness=0.012, plane_normal=Vector((0, 1, 0))):
    """Closed flat slab along points; the broad side faces plane_normal (feather vanes)."""
    import bmesh
    bm = bmesh.new()
    pts = [Vector(p) for p in points]
    rings = []
    for i, (p, w) in enumerate(zip(pts, widths)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        d = t.cross(plane_normal).normalized()   # width direction, in the vane plane
        n = d.cross(t).normalized()               # thickness direction
        hw, ht = w * 0.5, thickness * 0.5
        rings.append([bm.verts.new(p + d * hw + n * ht), bm.verts.new(p - d * hw + n * ht),
                      bm.verts.new(p - d * hw - n * ht), bm.verts.new(p + d * hw - n * ht)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        t = i / (n - 1)
        u = 1 - t
        out.append(Vector(p0) * u ** 3 + Vector(p1) * 3 * u * u * t + Vector(p2) * 3 * u * t * t + Vector(p3) * t ** 3)
    return out


def tail_xf(points):
    """Tilt tail geometry back around the tail base."""
    rot = Matrix.Rotation(TAIL_TILT, 3, "X")
    return [TAIL_BASE + rot @ (Vector(p) - TAIL_BASE) for p in points]


def param_color(path, fn):
    """Colour fn(s, co) where s in 0..1 is the nearest position along `path`."""
    n = len(path) - 1

    def color(co, normal):
        best = min(range(len(path)), key=lambda i: (path[i] - co).length_squared)
        return fn(best / n, co)
    return color


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # ---- body: plump, slightly tilted forward, fur-ish lumpy silhouette
    def body_deform(n):
        return 1.0 + noise.noise(n * 2.5 + Vector((1.3, 4.1, 0.7))) * 0.04

    def body_color(co, n):
        t = nh.smoothstep(0.30, 0.55, co.z)
        c = nh.lerp(BELLY, BROWN, t)
        return nh.lerp(c, BROWN_DARK, max(0.0, n.z) * 0.25)

    body = nh.uv_ellipsoid((0, 0.02, 0.52), (0.15, 0.25, 0.16), segments=16, rings=10, deform=body_deform)
    nh.transform(body, Matrix.Translation((0, 0.02, 0.52)) @ Matrix.Rotation(math.radians(-12), 4, "X")
                 @ Matrix.Translation((0, -0.02, -0.52)))
    mb.add(body, body_color)

    # ---- neck + head
    neck = [(0, -0.16, 0.58), (0, -0.23, 0.68), (0, -0.27, 0.78)]
    mb.add(nh.tube(neck, [0.085, 0.07, 0.06], sides=10), lambda co, n: nh.lerp(THROAT, BROWN, nh.smoothstep(0.62, 0.8, co.z) * 0.5 + max(0.0, n.z) * 0.5))
    head_c = Vector((0, -0.30, 0.82))
    mb.add(nh.uv_ellipsoid(head_c, (0.062, 0.075, 0.062), segments=12, rings=8),
           lambda co, n: nh.lerp(BROWN, BROWN_DARK, max(0.0, n.z) * 0.6))
    # beak: short, slightly downcurved
    mb.add(nh.tube([(0, -0.36, 0.82), (0, -0.41, 0.815), (0, -0.445, 0.80)], [0.022, 0.013, 0.0], sides=6), BEAK)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.05, -0.325, 0.835), (0.014, 0.014, 0.014), subdivisions=1), EYE)

    # ---- folded wings on the flanks
    for sx in (-1, 1):
        wing = nh.uv_ellipsoid((sx * 0.115, 0.06, 0.56), (0.04, 0.19, 0.10), segments=10, rings=8)
        nh.transform(wing, Matrix.Translation((sx * 0.115, 0.06, 0.56)) @ Matrix.Rotation(math.radians(-14), 4, "X")
                     @ Matrix.Translation((-sx * 0.115, -0.06, -0.56)))
        mb.add(wing, lambda co, n: nh.lerp(BROWN_DARK, BROWN, nh.smoothstep(0.46, 0.62, co.z)))

    # ---- strong grey legs with long toes
    for sx in (-1, 1):
        x = sx * 0.065
        leg = [(x, 0.03, 0.42), (x * 1.1, 0.07, 0.26), (x * 1.15, 0.0, 0.10), (x * 1.15, -0.02, 0.02)]
        mb.add(nh.tube(leg, [0.05, 0.032, 0.026, 0.022], sides=6), lambda co, n: nh.lerp(LEG, BROWN, nh.smoothstep(0.3, 0.42, co.z)))
        foot = Vector((x * 1.15, -0.02, 0.015))
        for ang in (-28, 0, 28):
            a = math.radians(ang + sx * 6)
            tip = foot + Vector((math.sin(a) * 0.11, -math.cos(a) * 0.11, -0.01))
            mb.add(nh.tube([foot, (foot + tip) / 2 + Vector((0, 0, 0.01)), tip], [0.016, 0.012, 0.0], sides=4), LEG)
        mb.add(nh.tube([foot, foot + Vector((0, 0.07, -0.005))], [0.012, 0.0], sides=4), LEG)  # hind toe

    # ---- tail: two lyrate outer feathers
    for sx in (-1, 1):
        ctrl = [(sx * 0.03, 0.24, 0.50), (sx * 0.30, 0.30, 0.75), (sx * 0.06, 0.34, 1.15), (sx * 0.24, 0.30, 1.42)]
        path = bezier(*ctrl, 20)
        # tip curls outward and down in a smooth arc
        end, rad = path[-1], 0.055
        center = end + Vector((sx * rad * 0.2, 0, -rad))
        tip_curl = [center + Vector((sx * math.sin(a) * rad, -0.01 * k, math.cos(a) * rad))
                    for k, a in enumerate([0.5, 1.0, 1.5, 2.0, 2.5], 1)]
        path = tail_xf(path + tip_curl)
        widths = [0.03 + 0.07 * math.sin(min(1.0, i / (len(path) - 3)) * math.pi * 0.9) for i in range(len(path))]
        for k in range(1, 6):
            widths[-k] = min(widths[-k], 0.015 + 0.006 * k)

        def lyre_color(s, co):
            band = (s * 18.0) % 1.0
            c = NOTCH if 0.5 < band < 0.8 and 0.1 < s < 0.82 else CHESTNUT
            if s > 0.84:
                c = FEATHER_EDGE
            return c
        mb.add(ribbon(path, widths, thickness=0.014, plane_normal=Vector((0, 1, 0.25)).normalized()),
               param_color(path, lyre_color), smooth=False)

    # ---- fan of silvery filamentous plumes arching outward between the lyrates
    count = 26
    for i in range(count):
        u = (i + 0.5) / count * 2 - 1          # -1..1 across the fan
        spread = u * 0.42
        height = 1.05 + 0.25 * (1 - abs(u)) + rng.uniform(-0.05, 0.05)
        droop = abs(u) * 0.22
        ctrl = [(u * 0.02, 0.25, 0.52),
                (spread * 0.5, 0.30 + rng.uniform(-0.03, 0.03), 0.85),
                (spread * 1.05, 0.33, height),
                (spread * 1.35, 0.30 - droop * 0.2, height - droop)]
        path = tail_xf(bezier(*ctrl, 9))
        radii = [0.011 * (1 - k / 8) + 0.003 for k in range(9)]
        radii[-1] = 0.0
        mb.add(nh.tube(path, radii, sides=3),
               param_color(path, lambda s, co: nh.lerp(SILVER, SILVER_DARK, s ** 1.5 * 0.6)))
        # a few fine side barbs for the shimmering fuzz
        for k in (2, 3, 4, 5, 6, 7):
            p = path[k]
            sgn = 1.0 if k % 2 else -1.0
            side = Vector((sgn, rng.uniform(-0.3, 0.3), rng.uniform(0.0, 0.6))).normalized()
            mb.add(nh.tube([p, p + side * rng.uniform(0.06, 0.1)], [0.005, 0.0], sides=3), SILVER)

    # two wiry median plumes standing straight up in the middle
    for sx in (-1, 1):
        path = tail_xf(bezier((sx * 0.01, 0.25, 0.52), (sx * 0.04, 0.32, 0.9), (sx * 0.02, 0.35, 1.3), (sx * 0.08, 0.32, 1.5), 10))
        mb.add(nh.tube(path, [0.012 * (1 - k / 9) + 0.002 if k < 9 else 0 for k in range(10)], sides=4), SILVER_DARK)

    obj = mb.to_object("SuperbLyrebird")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "SuperbLyrebird", ground=(0.25, 0.38, 0.22),
           views=((35, 25), (-90, 8), (20, 65)))
