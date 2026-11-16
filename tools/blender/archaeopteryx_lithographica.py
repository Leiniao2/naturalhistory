"""
Procedural Archaeopteryx lithographica (Late Jurassic avialan, Solnhofen) in flight,
wings spread.

A raven-sized feathered dinosaur. Broad, rounded wings: a lofted arm wing with
a gently serrated trailing edge of secondaries and a fan of long, asymmetric,
overlapping primaries closing into a rounded tip. Three free fingers stick out
of the leading edge at the hand, each with a big, hooked claw. A long bony tail
(about as long as the body) carries a pair of vaned feathers on each vertebra,
fanning out into a long, frond-like tail. A small feathered head with a short
snout whose jaws hang slightly open over small, conical teeth; feathered
"trousers" on the legs, which trail back under the tail with clawed toes.
The plumage is matte black, as melanosome studies of the isolated Solnhofen
feather suggest, with faint dark-grey edging on the coverts.

Body, neck, head, jaws, legs and the bony tail are overlapping primitives fused
into one seamless surface (nh_model.MeshBuilder.fuse) and repainted
procedurally; wings, primaries, tail feathers, claws, teeth and eyes are crisp
separate shells.

Usage:
  blender --background --python tools/blender/archaeopteryx_lithographica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archaeopteryx.fbx
Faces -Y, pivot at the body centre (flier). Wingspan ~1.9, snout to tail tip ~1.25.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BLACK = (0.035, 0.034, 0.034)
BLACK_MATT = (0.07, 0.065, 0.06)
EDGE_GREY = (0.17, 0.16, 0.15)      # faint pale edging of the covert rows
SHAFT = (0.11, 0.10, 0.09)
SKIN = (0.20, 0.18, 0.17)           # bare jaw margins
TEETH = (0.92, 0.89, 0.80)
CLAW = (0.30, 0.27, 0.24)
CLAW_TIP = (0.10, 0.09, 0.08)
EYE = (0.03, 0.02, 0.02)
IRIS = (0.45, 0.30, 0.12)

WING_ROOT = 0.06
HAND_END = 0.60
WING_STATIONS = 30
CHORD = (0.0, 0.03, 0.09, 0.17, 0.26, 0.35, 0.45, 0.55, 0.65, 0.75, 0.84, 0.91, 0.96, 1.0)

LEADING = [(WING_ROOT, -0.085), (0.22, -0.125), (0.42, -0.125), (0.52, -0.115), (HAND_END, -0.10)]
# over the hand the lofted part only covers the coverts; the primaries make the rest of the wing
TRAILING = [(WING_ROOT, 0.150), (0.22, 0.175), (0.36, 0.160), (0.44, 0.070), (0.52, 0.000), (HAND_END, -0.050)]
THICKNESS = [(WING_ROOT, 0.045), (0.3, 0.028), (0.5, 0.018), (HAND_END, 0.012)]

# upper and lower jaw profiles (y, z centre, radius); the snout is short and the mouth slightly open
UPPER_JAW = [(-0.300, 0.068, 0.030), (-0.335, 0.058, 0.020), (-0.370, 0.046, 0.0120), (-0.398, 0.036, 0.0065)]
LOWER_JAW = [(-0.300, 0.036, 0.020), (-0.340, 0.025, 0.0130), (-0.385, 0.016, 0.0065)]
UPPER_SY = 0.85
LOWER_SY = 0.7
JAW_SX = 0.8


def interp(keys, x):
    for (x0, v0), (x1, v1) in zip(keys, keys[1:]):
        if x <= x1:
            s = nh.smoothstep(x0, x1, x) if x1 > x0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


def profile(table, y):
    for (y0, z0, r0), (y1, z1, r1) in zip(table, table[1:]):
        if y >= y1:
            t = (y0 - y) / (y0 - y1)
            return z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
    return table[-1][1], table[-1][2]


def dihedral(x):
    """Wings held nearly flat with a slight lift toward the hand."""
    return 0.06 * x + 0.03 * nh.smoothstep(0.35, HAND_END, x)


def airfoil(c):
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def serration(x):
    """Rounded tips of the secondaries along the inner trailing edge."""
    period = 0.045
    s = (x - WING_ROOT) / period
    tooth = 1.0 - abs(math.sin(math.pi * s)) ** 0.6
    return -0.016 * tooth * (1 - nh.smoothstep(0.34, 0.42, x))


def loft(rings, cap_start=True, cap_end=True):
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


# ---------------------------------------------------------------- wings

def wing_color(co, n):
    ax = abs(co.x)
    yl, yt = interp(LEADING, ax), interp(TRAILING, ax)
    c = (co.y - yl) / (yt - yl) if yt != yl else 0.0
    grain = max(0.0, noise.noise(Vector((co.x * 30.0, co.y * 70.0, 0.7))))
    col = nh.lerp(BLACK, BLACK_MATT, grain * 0.7)
    feather = abs(math.sin(ax * math.pi / 0.045))
    if n.z >= 0:
        # rows of coverts: faint grey-edged scallops over the front half, then the secondaries
        rows = 0.5 + 0.5 * math.sin(c * 34.0 + math.sin(ax * 70.0) * 0.6)
        col = nh.lerp(col, EDGE_GREY, rows ** 6 * (1 - nh.smoothstep(0.35, 0.5, c)) * 0.55)
        col = nh.lerp(col, SHAFT, (1 - feather) ** 10 * nh.smoothstep(0.5, 0.6, c) * 0.6)
        return col
    return nh.lerp(col, EDGE_GREY, (1 - feather) ** 10 * nh.smoothstep(0.45, 0.6, c) * 0.4)


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


# primaries rooted along the hand bones (near the leading edge), outermost first:
# (base span x, angle back from +X in degrees, length); together they close into a rounded tip
PRIMARIES = [(0.62 - 0.22 * k / 10, -2.0 + 82.0 * (k / 10) ** 0.9, 0.36 - 0.10 * k / 10) for k in range(11)]


def primary(side, x0, angle, length, stations=8):
    """Long asymmetric flight feather: narrow leading vane, broad trailing vane, rounded tip."""
    base = Vector((x0, interp(LEADING, min(x0, HAND_END)) + 0.028, dihedral(min(x0, HAND_END)) + 0.002))
    a = math.radians(angle)
    fwd = Vector((math.cos(a), math.sin(a), 0.0))
    perp = Vector((-math.sin(a), math.cos(a), 0.0))
    rings = []
    for k in range(stations + 1):
        s = k / stations
        w = 0.090 * (0.85 + 0.15 * math.sin(math.pi * min(1.0, s * 1.3))) * (1 - max(0.0, (s - 0.72) / 0.28) ** 2 * 0.85)
        th = 0.008 * (1 - 0.6 * s)
        p = base + fwd * (length * s) + Vector((0, 0, 0.05 * length * s * s - 0.004 * s))
        ring = []
        for c, h in ((0.0, 0.0), (0.12, 0.7), (0.5, 1.0), (1.0, 0.0), (0.5, -0.6), (0.12, -0.5)):
            q = p + perp * (w * (c - 0.2)) + Vector((0, 0, th * h))
            ring.append(Vector((side * q.x, q.y, q.z)))
        if side < 0:
            ring.reverse()
        rings.append(ring)

    def color(co, n):
        d = (Vector((abs(co.x), co.y, 0)) - base).dot(perp)
        shaft = 1 - nh.smoothstep(0.0, 0.004, abs(d))
        s = (Vector((abs(co.x), co.y, 0)) - base).dot(fwd) / length
        col = nh.lerp(BLACK, BLACK_MATT, nh.smoothstep(0.2, 1.0, s) * 0.8)
        return nh.lerp(col, SHAFT, shaft * 0.7)
    return loft(rings), color


def finger_claws(side):
    """Three free fingers on the leading edge of the hand, each with a hooked claw."""
    shells = []
    for x, reach, r in ((0.40, 0.050, 0.0085), (0.47, 0.075, 0.0080), (0.53, 0.065, 0.0075)):
        y0 = interp(LEADING, x) + 0.02
        z0 = dihedral(x) + 0.006
        root = Vector((side * x, y0, z0))
        knuckle = Vector((side * (x + 0.012), y0 - reach, z0 + 0.004))
        shells.append((nh.tube([root, root.lerp(knuckle, 0.5), knuckle], [r, r * 0.85, r * 0.8], sides=6), SKIN))
        # hooked claw: forward then curling down
        c1 = knuckle + Vector((side * 0.004, -0.018, 0.004))
        c2 = knuckle + Vector((side * 0.006, -0.032, -0.006))
        c3 = knuckle + Vector((side * 0.006, -0.034, -0.020))
        claw = nh.tube([knuckle, c1, c2, c3], [r * 0.85, r * 0.65, r * 0.38, 0.0], sides=6, scale_xy=(0.6, 1.0))
        shells.append((claw, lambda co, n, k=knuckle: nh.lerp(CLAW, CLAW_TIP, nh.smoothstep(0.015, 0.04, (co - k).length))))
    return shells


# ---------------------------------------------------------------- tail

TAIL_PTS = [(0, 0.10, 0.004), (0, 0.20, 0.000), (0, 0.32, -0.004), (0, 0.44, -0.006), (0, 0.54, -0.006),
            (0, 0.62, -0.005)]
TAIL_R = [0.040, 0.020, 0.014, 0.011, 0.009, 0.0065]


def tail_point(t):
    """Point along the bony tail, t = 0 (base) .. 1 (tip)."""
    f = t * (len(TAIL_PTS) - 1)
    i = min(int(f), len(TAIL_PTS) - 2)
    return Vector(TAIL_PTS[i]).lerp(Vector(TAIL_PTS[i + 1]), f - i)


def tail_feather(base, direction, length, width=0.042, stations=6):
    d = direction.normalized()
    perp = Vector((-d.y, d.x, 0.0))
    rings = []
    for k in range(stations + 1):
        s = k / stations
        w = width * (0.55 + 0.45 * math.sin(math.pi * min(1.0, s * 1.4))) * (1 - max(0.0, (s - 0.75) / 0.25) ** 2 * 0.8)
        p = base + d * (length * s) + Vector((0, 0, 0.004 * s))
        th = 0.004 * (1 - 0.5 * s)
        ring = [p + perp * (w * (c - 0.35)) + Vector((0, 0, th * h))
                for c, h in ((0.0, 0.0), (0.35, 1.0), (1.0, 0.0), (0.35, -0.7))]
        if d.x < 0:
            ring.reverse()
        rings.append(ring)
    return loft(rings)


def tail_feathers():
    """A pair of feathers per caudal vertebra, longer toward the tip, forming a long frond."""
    shells = []
    n = 15
    for k in range(n):
        t = 0.18 + 0.82 * k / (n - 1)
        base = tail_point(t)
        length = 0.07 + 0.11 * nh.smoothstep(0.0, 0.85, t)
        spread = math.radians(62 - 40 * t)                    # fan back more steeply toward the tip
        for side in (-1, 1):
            d = Vector((side * math.sin(spread), math.cos(spread), 0.0))
            shells.append(tail_feather(base + Vector((side * 0.004, 0, 0.002 * k / n)), d, length))
    # the last pair runs straight back past the tip
    tip = tail_point(1.0)
    for side in (-1, 1):
        shells.append(tail_feather(tip + Vector((side * 0.006, -0.01, 0.001)),
                                   Vector((side * 0.12, 1.0, 0.0)), 0.17))
    return shells


def tail_color(co, n):
    grain = max(0.0, noise.noise(Vector((co.x * 40.0, co.y * 25.0, 1.3))))
    col = nh.lerp(BLACK, BLACK_MATT, grain * 0.8)
    return nh.lerp(col, EDGE_GREY, nh.smoothstep(0.08, 0.13, abs(co.x)) * 0.25)


# ---------------------------------------------------------------- body (fused)

def body_shells():
    s = []
    # slim torso with a shallow (keel-less) breast
    ys = [-0.17, -0.10, 0.0, 0.08, 0.13]
    rs = [0.060, 0.078, 0.080, 0.065, 0.045]
    s.append(nh.tube([(0, y, 0.0) for y in ys], rs, sides=18, scale_xy=(1.0, 0.85)))
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.055, -0.07, 0.015), (0.045, 0.09, 0.035), subdivisions=3))   # wing roots
    # S-curved feathered neck rising to the head
    s.append(nh.tube([(0, -0.15, 0.015), (0, -0.21, 0.035), (0, -0.255, 0.058), (0, -0.28, 0.068)],
                     [0.050, 0.040, 0.036, 0.036], sides=14))
    s.append(nh.uv_ellipsoid((0, -0.285, 0.072), (0.036, 0.042, 0.036), segments=16, rings=12))
    s.append(nh.tube([(0, y, z) for y, z, r in UPPER_JAW], [r for _y, _z, r in UPPER_JAW], sides=12,
                     scale_xy=(JAW_SX, UPPER_SY)))
    s.append(nh.tube([(0, y, z) for y, z, r in LOWER_JAW], [r for _y, _z, r in LOWER_JAW], sides=12,
                     scale_xy=(JAW_SX, LOWER_SY)))
    # feathered thighs ("trousers") and shanks trailing back under the tail
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.045, 0.06, -0.04), (0.035, 0.065, 0.035), subdivisions=3))
        s.append(nh.tube([(sx * 0.045, 0.09, -0.05), (sx * 0.05, 0.16, -0.055), (sx * 0.05, 0.22, -0.05)],
                         [0.026, 0.016, 0.010], sides=10))
    s.append(nh.tube(TAIL_PTS, TAIL_R, sides=10))
    return s


def body_color(co, n):
    x, y, z = co
    if y < -0.32 and abs(x) < 0.03:                     # bare jaw margins and snout
        zu, ru = profile(UPPER_JAW, y)
        zl, rl = profile(LOWER_JAW, y)
        lip = min(abs(z - (zu - ru * UPPER_SY)), abs(z - (zl + rl * LOWER_SY)))
        return nh.lerp(SKIN, BLACK_MATT, nh.smoothstep(0.002, 0.008, lip) * 0.6)
    grain = max(0.0, noise.noise(co * 60.0))
    col = nh.lerp(BLACK, BLACK_MATT, grain * 0.8)
    # faint scalloped contour-feather pattern
    sc = 0.5 + 0.5 * math.sin(y * 160.0 + math.sin(x * 120.0) * 1.5)
    return nh.lerp(col, EDGE_GREY, sc ** 8 * 0.25)


def plumage(bm, amount=0.003):
    """Soft, slightly ragged contour-feather surface on the body, neck and thighs."""
    bm.normal_update()
    for v in bm.verts:
        if -0.30 < v.co.y < 0.25:
            v.co += v.normal * noise.noise(v.co * 110.0) * amount
    bm.normal_update()


def add_teeth(mb):
    for upper in (True, False):
        table, sy = (UPPER_JAW, UPPER_SY) if upper else (LOWER_JAW, LOWER_SY)
        y_front = table[-1][0] + 0.004
        y_back = -0.335
        n = 6
        for k in range(n):
            y = y_front + (y_back - y_front) * k / (n - 1)
            zc, r = profile(table, y)
            margin = zc - r * sy * 0.8 if upper else zc + r * sy * 0.8
            down = -1.0 if upper else 1.0
            for sx in (-1, 1):
                base = Vector((sx * r * JAW_SX * 0.62, y, margin))
                d = Vector((sx * 0.1, 0.12, down)).normalized()     # slightly recurved, pointing back
                mb.add(nh.tube([base, base + d * 0.004, base + d * 0.007], [0.0022, 0.0014, 0.0], sides=5), TEETH)


# ---------------------------------------------------------------- assemble

def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, BLACK)
    body = parts.fuse(voxel=0.006, smooth=6, smooth_factor=0.5, max_tris=5000)
    plumage(body)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    add_teeth(mb)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.028, -0.300, 0.083), (0.009, 0.011, 0.010), subdivisions=2), IRIS)
        mb.add(nh.ellipsoid((sx * 0.033, -0.301, 0.084), (0.005, 0.006, 0.006), subdivisions=2), EYE)
    for shell in tail_feathers():
        mb.add(shell, tail_color)
    # feet: three forward toes and a hallux, with dark claws, trailing back
    for sx in (-1, 1):
        ankle = Vector((sx * 0.05, 0.22, -0.05))
        for dx, dz in ((-0.014, -0.004), (0.0, -0.006), (0.014, -0.004)):
            tip = ankle + Vector((sx * dx, 0.05, dz))
            mb.add(nh.tube([ankle, ankle.lerp(tip, 0.6), tip], [0.006, 0.005, 0.003], sides=5), SKIN)
            mb.add(nh.tube([tip, tip + Vector((0, 0.012, -0.008))], [0.003, 0.0], sides=5), CLAW_TIP)
        mb.add(nh.tube([ankle, ankle + Vector((sx * 0.004, -0.025, -0.008))], [0.005, 0.0], sides=5), SKIN)
    for side in (1, -1):
        mb.add(*make_wing(side))
        for x0, angle, length in PRIMARIES:
            mb.add(*primary(side, x0, angle, length))
        for shell, col in finger_claws(side):
            mb.add(shell, col)

    return mb.to_object("Archaeopteryx", roughness=0.85)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "Archaeopteryx")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, background=(0.62, 0.72, 0.80),
                          views=((35, 25), (20, 70), (0, 89), (180, -35)))
        # head and hand close-up: teeth and finger claws
        cam = bpy.context.scene.camera
        cam.data.lens = 50
        cam.location = Vector((0.40, -0.85, 0.22))
        cam.rotation_euler = (Vector((0.18, -0.25, 0.04)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
