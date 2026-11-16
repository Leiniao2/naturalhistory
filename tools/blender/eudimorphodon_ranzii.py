"""
Procedural Eudimorphodon ranzii (Late Triassic pterosaur, Norian of northern Italy),
flying with the wings spread.

A small, early, long-tailed pterosaur with a wingspan of about 1 m. The short,
deep skull has big orbits and its jaws hang slightly open over a mixed
dentition: a few large fangs at the front, then rows of small multi-cusped
cheek teeth (three to five cusps each), the feature that gives the genus its
name. A short neck, a compact pycnofibre-covered body and a long, stiffened
tail ending in a small diamond-shaped vane.

Body, shoulders, arms, neck, upper skull, lower jaw, legs and most of the tail
are overlapping primitives fused into one seamless surface
(nh_model.MeshBuilder.fuse) and repainted procedurally with a mottled
pycnofibre coat. The narrow wings are lofted membranes running from the bony
leading edge (shoulder -> propatagium -> wrist -> long fourth "wing" finger)
back to the ankle; they billow between the bones and carry fine actinofibril
streaks. A small uropatagium stretches between the legs and the long fifth
toes. Crisp details: the thin tail tip and its vertical vane, teeth, eyes, hand
and foot claws.

Usage:
  blender --background --python tools/blender/eudimorphodon_ranzii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eudimorphodon.fbx
Faces -Y, pivot at the body centre (flier). Wingspan 2.0, snout to tail vane ~0.8.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

# ---------------------------------------------------------------- palette
FUR = (0.42, 0.33, 0.24)          # pycnofibre coat
FUR_DARK = (0.20, 0.15, 0.11)
FUR_LIGHT = (0.78, 0.70, 0.56)    # belly / throat
HEAD = (0.46, 0.38, 0.30)
SNOUT = (0.58, 0.50, 0.40)
TEETH = (0.93, 0.89, 0.78)
EYE = (0.02, 0.02, 0.02)
EYE_RING = (0.80, 0.62, 0.25)
LIMB = (0.22, 0.16, 0.12)
CLAW = (0.10, 0.08, 0.06)
MEMBRANE_ROOT = (0.42, 0.24, 0.15)
MEMBRANE = (0.36, 0.25, 0.18)
MEMBRANE_EDGE = (0.62, 0.48, 0.36)
LEADING = (0.13, 0.09, 0.07)
FIBRE = (0.24, 0.16, 0.11)
VANE = (0.55, 0.20, 0.10)
VANE_EDGE = (0.16, 0.08, 0.05)

HALF_SPAN = 0.82
# (span x, y) along the leading edge (shoulder -> propatagium -> wrist -> wing finger tip)
LEADING_EDGE = [(0.04, -0.045), (0.13, -0.090), (0.26, -0.080), (0.42, -0.050), (0.58, 0.000),
                (0.71, 0.060), (0.82, 0.150)]
# trailing edge: body flank -> ankle -> gentle concave sweep to the pointed tip
TRAILING_EDGE = [(0.04, 0.070), (0.11, 0.165), (0.20, 0.162), (0.34, 0.145), (0.50, 0.128),
                 (0.64, 0.125), (0.75, 0.138), (0.82, 0.150)]
WRIST_X = 0.26
ANKLE = (0.11, 0.160)

# skull: upper jaw and lower jaw profiles (y, z centre, radius) as tubes
UPPER_JAW = [(-0.150, 0.052, 0.026), (-0.185, 0.046, 0.021), (-0.220, 0.038, 0.0145), (-0.252, 0.030, 0.0085)]
LOWER_JAW = [(-0.150, 0.026, 0.017), (-0.195, 0.016, 0.0125), (-0.245, 0.010, 0.0075)]
UPPER_SY = 0.95
LOWER_SY = 0.7
JAW_SX = 0.78


def interp(table, x):
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return table[-1][1]


def profile(table, y):
    """(z, r) of a jaw tube at y (tables run from the hinge forward, y decreasing)."""
    for (y0, z0, r0), (y1, z1, r1) in zip(table, table[1:]):
        if y >= y1:
            t = (y0 - y) / (y0 - y1)
            return z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
    return table[-1][1], table[-1][2]


def wing_z(x):
    """Wing height along the span: gentle dihedral, then the tips curl up."""
    u = abs(x) / HALF_SPAN
    return HALF_SPAN * (0.10 * u - 0.05 * u * u + 0.08 * nh.smoothstep(0.75, 1.0, u) ** 2)


# ---------------------------------------------------------------- wings

def wing_membrane(sx, nu=40, nv=10, thickness=0.0055):
    """Closed lofted membrane for one side, billowing between the bones, with fibre streaks."""
    bm = bmesh.new()
    x0 = LEADING_EDGE[0][0]
    grid = {}
    for side, dz in (("top", 0.5), ("bot", -0.5)):
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (HALF_SPAN - x0) * (1 - (1 - u) ** 1.25)
            yl, yt = interp(LEADING_EDGE, x), interp(TRAILING_EDGE, x)
            taper = 1.0 - u * 0.75
            for j in range(nv + 1):
                v = j / nv
                y = yl + (yt - yl) * v
                billow = -0.016 * math.sin(math.pi * min(1.0, v * 1.15)) * taper
                camber = 0.011 * math.sin(math.pi * v) * taper
                ripple = 0.002 * math.sin(x * 85.0 + v * 2.0) * v
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
        base = nh.lerp(MEMBRANE_ROOT, MEMBRANE, nh.smoothstep(0.05, 0.4, x))
        c = nh.lerp(LEADING, base, nh.smoothstep(0.0, 0.25, v))
        c = nh.lerp(c, MEMBRANE_EDGE, nh.smoothstep(0.72, 1.0, v))
        fibre = 0.5 + 0.5 * math.sin(x * 115.0 - v * 5.0)
        c = nh.lerp(c, FIBRE, fibre ** 3 * 0.35 * nh.smoothstep(0.12, 0.4, v) * (1 - nh.smoothstep(0.82, 1.0, v)))
        c = nh.lerp(c, FUR_DARK, max(0.0, noise.noise(Vector((x * 8.0, co.y * 8.0, 0.5)))) * 0.25)
        if normal.z < -0.5:
            c = nh.lerp(c, FUR_LIGHT, 0.25)
        return c
    return bm, color


def wing_finger(sx):
    """Bony ridge along the leading edge from the wrist to the tip, with phalanx joints."""
    pts, radii = [], []
    n = 12
    for k in range(n + 1):
        t = k / n
        x = WRIST_X + (HALF_SPAN - WRIST_X) * t
        pts.append(Vector((sx * x, interp(LEADING_EDGE, x) + 0.004, wing_z(x) + 0.006 * (1 - t))))
        radii.append(0.011 * (1 - t) + 0.002 if k < n else 0.0)
    shells = [(nh.tube(pts, radii, sides=6), LEADING)]
    for t in (0.0, 0.33, 0.62, 0.85):
        x = WRIST_X + (HALF_SPAN - WRIST_X) * t
        r = 0.014 * (1 - t) + 0.004
        c = (sx * x, interp(LEADING_EDGE, x) + 0.004, wing_z(x) + 0.007 * (1 - t))
        shells.append((nh.ellipsoid(c, (r * 1.2, r, r * 0.9), subdivisions=1), LEADING))
    return shells


def uropatagium():
    """Small membrane between the legs, spread by the long fifth toes."""
    ax, ay = ANKLE
    z = wing_z(ax) - 0.016
    outline = [(-ax, ay, z), (-0.03, 0.085, z + 0.006), (0.03, 0.085, z + 0.006), (ax, ay, z),
               (ax + 0.012, ay + 0.04, z - 0.004), (0.05, ay + 0.012, z), (0.0, ay + 0.0, z + 0.002),
               (-0.05, ay + 0.012, z), (-ax - 0.012, ay + 0.04, z - 0.004)]
    return nh.flat_panel(outline, thickness=0.004)


# ---------------------------------------------------------------- body (fused)

TAIL = [(0, 0.07, -0.002), (0, 0.16, -0.008), (0, 0.26, -0.012), (0, 0.36, -0.014), (0, 0.44, -0.015)]
TAIL_R = [0.022, 0.012, 0.009, 0.0075, 0.0065]


def body_shells():
    s = []
    # torso: compact, deep chest with a small keel, shoulders, hips
    s.append(nh.uv_ellipsoid((0, 0.0, 0.0), (0.048, 0.095, 0.042), segments=20, rings=12))
    s.append(nh.uv_ellipsoid((0, -0.04, -0.016), (0.03, 0.045, 0.034), segments=14, rings=10))
    for sx in (-1, 1):
        s.append(nh.uv_ellipsoid((sx * 0.036, -0.042, 0.014), (0.032, 0.036, 0.026), segments=14, rings=10))
    # short neck, curving up into the head
    s.append(nh.tube([(0, -0.06, 0.016), (0, -0.10, 0.028), (0, -0.14, 0.045)], [0.026, 0.022, 0.022], sides=12))
    # skull: rounded braincase, deep short snout, lower jaw hanging slightly open
    s.append(nh.uv_ellipsoid((0, -0.158, 0.056), (0.026, 0.034, 0.029), segments=14, rings=10))
    s.append(nh.tube([(0, y, z) for y, z, r in UPPER_JAW], [r for _y, _z, r in UPPER_JAW], sides=12,
                     scale_xy=(JAW_SX, UPPER_SY)))
    s.append(nh.tube([(0, y, z) for y, z, r in LOWER_JAW], [r for _y, _z, r in LOWER_JAW], sides=12,
                     scale_xy=(JAW_SX, LOWER_SY)))
    # arms: humerus out to the elbow, forearm forward to the wrist
    for sx in (-1, 1):
        sh = Vector((sx * 0.04, -0.04, 0.016))
        el = Vector((sx * 0.13, -0.058, wing_z(0.13) + 0.008))
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X) + 0.004, wing_z(WRIST_X) + 0.006))
        s.append(nh.tube([sh, sh.lerp(el, 0.45) + Vector((0, 0, 0.004)), el], [0.024, 0.018, 0.012], sides=10))
        s.append(nh.tube([el, el.lerp(wr, 0.5), wr], [0.011, 0.009, 0.010], sides=8))
        # legs trailing back to the ankle under the membrane
        ankle = Vector((sx * ANKLE[0], ANKLE[1], wing_z(ANKLE[0]) - 0.012))
        s.append(nh.tube([Vector((sx * 0.025, 0.06, -0.022)), Vector((sx * 0.065, 0.11, -0.018)), ankle],
                         [0.016, 0.010, 0.007], sides=8))
    # long stiff tail (the thin tip is added crisp after fusing)
    s.append(nh.tube(TAIL, TAIL_R, sides=10))
    return s


def body_color(co, normal):
    x, y, z = co
    mottle = noise.noise(co * 40.0)
    fuzz = noise.noise(co * 140.0)
    if y < -0.135 and abs(x) < 0.04:                       # head
        if z < 0.033 and y < -0.15:                        # lower jaw
            c = nh.lerp(SNOUT, FUR_LIGHT, 0.4)
        else:
            c = nh.lerp(HEAD, SNOUT, nh.smoothstep(-0.18, -0.24, y))
            c = nh.lerp(c, FUR_DARK, nh.smoothstep(0.6, 1.0, normal.z) * 0.35 * nh.smoothstep(-0.2, -0.15, y))
        return nh.lerp(c, FUR_DARK, max(0.0, mottle) * 0.2)
    if abs(x) > 0.07 or (y > 0.06 and z < -0.015 and abs(x) > 0.02):   # arms and legs
        return nh.lerp(LIMB, FUR_DARK, 0.3 + 0.3 * mottle)
    if y > 0.1:                                            # tail: faint dark rings
        ring = 0.5 + 0.5 * math.sin(y * 120.0)
        c = nh.lerp(FUR, FUR_DARK, 0.35 + 0.35 * ring ** 4)
        return nh.lerp(c, FUR_LIGHT, nh.smoothstep(-0.2, -0.8, normal.z) * 0.4)
    up = normal.z
    c = nh.lerp(FUR_LIGHT, FUR, nh.smoothstep(-0.5, 0.2, up))
    c = nh.lerp(c, FUR_DARK, nh.smoothstep(0.7, 1.0, up) * 0.5)
    return nh.lerp(c, FUR_DARK, max(0.0, mottle) * 0.3 + max(0.0, fuzz) * 0.2)


def fuzz(bm, amount=0.0026):
    """Pycnofibre 'fuzz': tiny normal displacement on the torso, neck and back of the head."""
    bm.normal_update()
    for v in bm.verts:
        if -0.17 < v.co.y < 0.1 and abs(v.co.x) < 0.07:
            v.co += v.normal * noise.noise(v.co * 260.0) * amount
    bm.normal_update()


# ---------------------------------------------------------------- crisp details

def tail_tip_and_vane():
    shells = []
    pts = [(0, 0.42, -0.015), (0, 0.48, -0.016), (0, 0.54, -0.016), (0, 0.585, -0.016)]
    shells.append((nh.tube(pts, [0.0068, 0.005, 0.0035, 0.0], sides=8), FUR_DARK))
    # vertical diamond-shaped vane around the tip
    bm = bmesh.new()
    yz = [(0.492, -0.016), (0.532, 0.016), (0.580, -0.007), (0.598, -0.016), (0.580, -0.028), (0.538, -0.048)]
    t = 0.0022
    left = [bm.verts.new((-t, y, z)) for y, z in yz]
    right = [bm.verts.new((t, y, z)) for y, z in yz]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    for i in range(len(yz)):
        j = (i + 1) % len(yz)
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def vane_color(co, n):
        d = abs((co.z + 0.016) / 0.032) + abs((co.y - 0.545) / 0.053)
        return nh.lerp(VANE, VANE_EDGE, nh.smoothstep(0.6, 0.95, d))
    shells.append((bm, vane_color))
    return shells


def cone(base, direction, length, radius, sides=6):
    d = Vector(direction).normalized()
    return nh.tube([base, base + d * length * 0.55, base + d * length], [radius, radius * 0.65, 0.0], sides=sides)


def cusped_tooth(base, down, height, width, cusps=3):
    """Flat multi-cusped cheek tooth in the jaw's side plane (y-z), points along `down` (+-Z)."""
    bm = bmesh.new()
    pts = [(base.y + width * 0.5, base.z)]
    for k in range(cusps):
        y0 = base.y + width * 0.5 - width * k / cusps
        y1 = y0 - width / cusps
        tip = height * (1.0 if k == cusps // 2 else 0.62)
        pts.append(((y0 + y1) * 0.5, base.z + down * tip))
        pts.append((y1, base.z + down * height * 0.35 if k < cusps - 1 else base.z))
    t = 0.0016
    left = [bm.verts.new((base.x - t, y, z)) for y, z in pts]
    right = [bm.verts.new((base.x + t, y, z)) for y, z in pts]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def add_teeth(mb):
    for upper in (True, False):
        table, sy = (UPPER_JAW, UPPER_SY) if upper else (LOWER_JAW, LOWER_SY)
        y_front = table[-1][0] + 0.004
        y_back = -0.172
        n = 11
        for k in range(n):
            y = y_front + (y_back - y_front) * k / (n - 1)
            zc, r = profile(table, y)
            margin = zc - r * sy * 0.82 if upper else zc + r * sy * 0.82
            down = -1.0 if upper else 1.0
            for sx in (-1, 1):
                base = Vector((sx * r * JAW_SX * 0.62, y, margin))
                if k < 2:   # big front fangs, raked forward
                    mb.add(cone(base, (sx * 0.15, -0.35, down), 0.014 if upper else 0.011, 0.0028), TEETH)
                else:       # small multi-cusped cheek teeth
                    mb.add(cusped_tooth(base, down, 0.0055, 0.0062, cusps=3 if k % 2 else 5), TEETH, smooth=False)


# ---------------------------------------------------------------- assemble

def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, FUR)
    body = parts.fuse(voxel=0.0042, smooth=5, smooth_factor=0.5, max_tris=4500)
    fuzz(body)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    for shell, col in tail_tip_and_vane():
        mb.add(shell, col, smooth=False)
    add_teeth(mb)
    # large eyes with a pale ring
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.021, -0.163, 0.062), (0.007, 0.011, 0.010), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid((sx * 0.025, -0.164, 0.063), (0.005, 0.008, 0.007), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.012, -0.243, 0.04), (0.003, 0.006, 0.003), subdivisions=1), FUR_DARK)  # nostril

    for sx in (-1, 1):
        mb.add(*wing_membrane(sx))
        for shell, col in wing_finger(sx):
            mb.add(shell, col)
        # three small clawed fingers at the wrist
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X), wing_z(WRIST_X) + 0.008))
        for k, dx in enumerate((-0.012, 0.0, 0.012)):
            tip = wr + Vector((sx * dx, -0.04 - 0.004 * k, 0.0))
            mb.add(nh.tube([wr, wr.lerp(tip, 0.6), tip], [0.0045, 0.003, 0.0], sides=5), CLAW)
        # feet: four toes and the long fifth toe spreading the uropatagium
        ankle = Vector((sx * ANKLE[0], ANKLE[1], wing_z(ANKLE[0]) - 0.012))
        for dx in (-0.010, -0.003, 0.004, 0.011):
            tip = ankle + Vector((sx * dx, 0.04, -0.006))
            mb.add(nh.tube([ankle, tip], [0.004, 0.0], sides=5), LIMB)
        mb.add(nh.tube([ankle, ankle + Vector((sx * 0.012, 0.04, -0.005))], [0.0035, 0.0012], sides=5), LIMB)
    mb.add(uropatagium(), lambda co, n: nh.lerp(MEMBRANE, MEMBRANE_EDGE, nh.smoothstep(0.15, 0.19, co.y)))

    return mb.to_object("Eudimorphodon")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "Eudimorphodon")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, background=(0.45, 0.58, 0.70),
                          views=((35, 25), (20, 70), (0, 89), (180, -35)))
        # head close-up to check the jaws and the multi-cusped teeth
        cam = bpy.context.scene.camera
        cam.data.lens = 50
        cam.location = Vector((0.16, -0.42, 0.06))
        cam.rotation_euler = (Vector((0.0, -0.2, 0.04)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
