"""
Procedural Pterodactylus antiquus (Late Jurassic pterodactyloid pterosaur, Solnhofen),
flying with the wings spread.

The first pterosaur ever described, here as a large adult with a wingspan of about
1-1.5 m. A long, low, narrow skull about as long as the neck, its jaws slightly
open over rows of many small, slender conical teeth along the front of the jaws; a
low soft-tissue crest running along the top of the skull and ending in a small
lappet behind the head (as preserved in Solnhofen specimens). A long neck, a
compact pycnofibre-covered body and only a short stub of a tail. The broad wing
membranes run from the bony leading edge (shoulder -> propatagium -> wrist ->
long fourth "wing" finger) back to the ankles.

Body, shoulders, arms, neck, skull, lower jaw and legs are overlapping primitives
fused into one seamless surface (nh_model.MeshBuilder.fuse) and repainted
procedurally with a mottled pycnofibre coat. The wings are lofted membranes that
billow between the bones and carry fine actinofibril streaks. Crisp details: the
crest, teeth, eyes, hand and foot claws.

Usage:
  blender --background --python tools/blender/pterodactylus_antiquus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pterodactylus.fbx
Faces -Y, pivot at the body centre (flier). Wingspan 1.7, snout to feet ~0.65.
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
FUR = (0.45, 0.40, 0.34)          # greyish pycnofibre coat
FUR_DARK = (0.20, 0.17, 0.14)
FUR_LIGHT = (0.80, 0.75, 0.66)    # belly / throat
HEAD = (0.52, 0.47, 0.40)
SNOUT = (0.66, 0.60, 0.50)
TEETH = (0.94, 0.91, 0.82)
EYE = (0.02, 0.02, 0.02)
EYE_RING = (0.70, 0.55, 0.30)
LIMB = (0.22, 0.18, 0.15)
CLAW = (0.10, 0.08, 0.06)
CREST = (0.62, 0.30, 0.18)
CREST_EDGE = (0.30, 0.12, 0.07)
MEMBRANE_ROOT = (0.36, 0.26, 0.20)
MEMBRANE = (0.30, 0.25, 0.21)
MEMBRANE_EDGE = (0.60, 0.52, 0.44)
LEADING = (0.13, 0.10, 0.08)
FIBRE = (0.21, 0.17, 0.14)

HALF_SPAN = 0.85
# (span x, y) along the leading edge (shoulder -> propatagium -> wrist -> wing finger tip)
LEADING_EDGE = [(0.04, -0.050), (0.14, -0.105), (0.29, -0.095), (0.45, -0.060), (0.60, -0.010),
                (0.74, 0.055), (0.85, 0.140)]
# trailing edge: body flank -> ankle -> concave sweep to the narrow tip
TRAILING_EDGE = [(0.04, 0.080), (0.13, 0.190), (0.24, 0.180), (0.38, 0.155), (0.53, 0.130),
                 (0.67, 0.120), (0.78, 0.128), (0.85, 0.140)]
WRIST_X = 0.29
ANKLE = (0.13, 0.185)

# skull: long and low; upper and lower jaw profiles (y, z centre, radius) as tubes
UPPER_JAW = [(-0.225, 0.096, 0.022), (-0.280, 0.088, 0.0165), (-0.340, 0.077, 0.0115),
             (-0.395, 0.066, 0.0075), (-0.440, 0.058, 0.0045)]
LOWER_JAW = [(-0.230, 0.066, 0.0135), (-0.300, 0.052, 0.0095), (-0.370, 0.040, 0.0065), (-0.428, 0.031, 0.004)]
UPPER_SY = 0.95
LOWER_SY = 0.75
JAW_SX = 0.70


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
                billow = -0.017 * math.sin(math.pi * min(1.0, v * 1.15)) * taper
                camber = 0.012 * math.sin(math.pi * v) * taper
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
        c = nh.lerp(c, MEMBRANE_EDGE, nh.smoothstep(0.75, 1.0, v))
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
        r = 0.012 * (1 - t) + 0.004
        c = (sx * x, interp(LEADING_EDGE, x) + 0.004, wing_z(x) + 0.007 * (1 - t))
        shells.append((nh.ellipsoid(c, (r * 1.2, r, r * 0.9), subdivisions=1), LEADING))
    return shells


# ---------------------------------------------------------------- body (fused)

def body_shells():
    s = []
    # torso: compact, deep chest with a small keel, shoulders, short hips
    s.append(nh.uv_ellipsoid((0, 0.0, 0.0), (0.046, 0.090, 0.040), segments=20, rings=12))
    s.append(nh.uv_ellipsoid((0, -0.04, -0.016), (0.03, 0.045, 0.034), segments=14, rings=10))
    for sx in (-1, 1):
        s.append(nh.uv_ellipsoid((sx * 0.036, -0.044, 0.014), (0.032, 0.036, 0.026), segments=14, rings=10))
    # very short tail stub
    s.append(nh.tube([(0, 0.07, -0.004), (0, 0.11, -0.008), (0, 0.135, -0.010)], [0.016, 0.008, 0.0], sides=10))
    # long neck rising forward to the head, with vertebral swellings
    n = 10
    a, b = Vector((0, -0.06, 0.016)), Vector((0, -0.215, 0.088))
    pts = [a.lerp(b, k / n) for k in range(n + 1)]
    radii = [(0.024 - 0.007 * (k / n)) * (1.0 + 0.07 * math.cos(k * math.pi)) for k in range(n + 1)]
    s.append(nh.tube(pts, radii, sides=12))
    # skull: rounded braincase, long low snout, lower jaw hanging slightly open
    s.append(nh.uv_ellipsoid((0, -0.222, 0.094), (0.022, 0.032, 0.025), segments=14, rings=10))
    s.append(nh.tube([(0, y, z) for y, z, r in UPPER_JAW], [r for _y, _z, r in UPPER_JAW], sides=12,
                     scale_xy=(JAW_SX, UPPER_SY)))
    s.append(nh.tube([(0, y, z) for y, z, r in LOWER_JAW], [r for _y, _z, r in LOWER_JAW], sides=12,
                     scale_xy=(JAW_SX, LOWER_SY)))
    # arms: humerus out to the elbow, forearm forward to the wrist
    for sx in (-1, 1):
        sh = Vector((sx * 0.04, -0.042, 0.016))
        el = Vector((sx * 0.14, -0.066, wing_z(0.14) + 0.008))
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X) + 0.004, wing_z(WRIST_X) + 0.006))
        s.append(nh.tube([sh, sh.lerp(el, 0.45) + Vector((0, 0, 0.004)), el], [0.024, 0.018, 0.012], sides=10))
        s.append(nh.tube([el, el.lerp(wr, 0.5), wr], [0.011, 0.009, 0.010], sides=8))
        # legs trailing back to the ankle under the membrane
        ankle = Vector((sx * ANKLE[0], ANKLE[1], wing_z(ANKLE[0]) - 0.012))
        s.append(nh.tube([Vector((sx * 0.025, 0.055, -0.020)), Vector((sx * 0.075, 0.12, -0.016)), ankle],
                         [0.016, 0.010, 0.007], sides=8))
    return s


def body_color(co, normal):
    x, y, z = co
    mottle = noise.noise(co * 40.0)
    fuzz = noise.noise(co * 140.0)
    if y < -0.21 and abs(x) < 0.04:                        # head
        if z < 0.073 and y < -0.235:                       # lower jaw
            c = nh.lerp(SNOUT, FUR_LIGHT, 0.45)
        else:
            c = nh.lerp(HEAD, SNOUT, nh.smoothstep(-0.26, -0.38, y))
            c = nh.lerp(c, FUR_DARK, nh.smoothstep(0.6, 1.0, normal.z) * 0.3 * nh.smoothstep(-0.3, -0.22, y))
        return nh.lerp(c, FUR_DARK, max(0.0, mottle) * 0.18)
    if abs(x) > 0.07 or (y > 0.05 and z < -0.012 and abs(x) > 0.02):   # arms and legs
        return nh.lerp(LIMB, FUR_DARK, 0.3 + 0.3 * mottle)
    up = normal.z
    c = nh.lerp(FUR_LIGHT, FUR, nh.smoothstep(-0.5, 0.2, up))
    c = nh.lerp(c, FUR_DARK, nh.smoothstep(0.7, 1.0, up) * 0.5)
    return nh.lerp(c, FUR_DARK, max(0.0, mottle) * 0.3 + max(0.0, fuzz) * 0.2)


def fuzz(bm, amount=0.0026):
    """Pycnofibre 'fuzz': tiny normal displacement on the torso, neck and back of the head."""
    bm.normal_update()
    for v in bm.verts:
        if -0.23 < v.co.y < 0.1 and abs(v.co.x) < 0.07:
            v.co += v.normal * noise.noise(v.co * 260.0) * amount
    bm.normal_update()


# ---------------------------------------------------------------- crisp details

def crest():
    """Low soft-tissue head crest along the midline of the skull, with a small rear lappet."""
    top = []
    n = 14
    for k in range(n + 1):
        y = -0.33 + (0.33 - 0.215) * k / n                   # from above the antorbital opening back over the braincase
        zc, r = profile(UPPER_JAW, y) if y < -0.235 else (0.096, 0.022)
        if y > -0.235:
            zc, r = 0.094, 0.025 * math.sqrt(max(0.0, 1 - ((y + 0.222) / 0.032) ** 2))
        surf = zc + r * UPPER_SY * 0.9
        t = k / n
        h = 0.010 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 + 0.003
        top.append((y, surf - 0.004, surf + h))
    yz = [(y, zt) for y, _zb, zt in top]
    yz += [(-0.196, 0.118), (-0.190, 0.111)]                  # rear lappet, pointing back
    yz += [(y, zb) for y, zb, _zt in reversed(top)]
    bm = bmesh.new()
    t = 0.0016
    left = [bm.verts.new((-t, y, z)) for y, z in yz]
    right = [bm.verts.new((t, y, z)) for y, z in yz]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    for i in range(len(yz)):
        j = (i + 1) % len(yz)
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        zc = 0.088 + (co.y + 0.33) * 0.12
        return nh.lerp(CREST_EDGE, CREST, nh.smoothstep(zc + 0.002, zc + 0.010, co.z))
    return bm, color


def cone(base, direction, length, radius, sides=5):
    d = Vector(direction).normalized()
    return nh.tube([base, base + d * length * 0.55, base + d * length], [radius, radius * 0.6, 0.0], sides=sides)


def add_teeth(mb):
    """Many small, slender conical teeth along the front half of both jaws."""
    for upper in (True, False):
        table, sy = (UPPER_JAW, UPPER_SY) if upper else (LOWER_JAW, LOWER_SY)
        y_front = table[-1][0] + 0.004
        y_back = -0.32
        n = 13
        for k in range(n):
            y = y_front + (y_back - y_front) * k / (n - 1)
            zc, r = profile(table, y)
            margin = zc - r * sy * 0.8 if upper else zc + r * sy * 0.8
            down = -1.0 if upper else 1.0
            length = (0.0085 - 0.004 * k / (n - 1)) * (1.0 if upper else 0.9)
            for sx in (-1, 1):
                base = Vector((sx * r * JAW_SX * 0.6, y, margin))
                mb.add(cone(base, (sx * 0.12, -0.25 + 0.15 * k / n, down), length, 0.0018), TEETH)


# ---------------------------------------------------------------- assemble

def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, FUR)
    body = parts.fuse(voxel=0.0042, smooth=5, smooth_factor=0.5, max_tris=4500)
    fuzz(body)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    mb.add(*crest(), smooth=False)
    add_teeth(mb)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.018, -0.232, 0.100), (0.006, 0.010, 0.009), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid((sx * 0.0215, -0.233, 0.101), (0.0045, 0.0075, 0.0065), subdivisions=2), EYE)

    for sx in (-1, 1):
        mb.add(*wing_membrane(sx))
        for shell, col in wing_finger(sx):
            mb.add(shell, col)
        # three small clawed fingers at the wrist
        wr = Vector((sx * WRIST_X, interp(LEADING_EDGE, WRIST_X), wing_z(WRIST_X) + 0.008))
        for k, dx in enumerate((-0.012, 0.0, 0.012)):
            tip = wr + Vector((sx * dx, -0.04 - 0.004 * k, 0.0))
            mb.add(nh.tube([wr, wr.lerp(tip, 0.6), tip], [0.0045, 0.003, 0.0], sides=5), CLAW)
        # feet trailing past the ankle
        ankle = Vector((sx * ANKLE[0], ANKLE[1], wing_z(ANKLE[0]) - 0.012))
        for dx in (-0.010, -0.003, 0.004, 0.011):
            tip = ankle + Vector((sx * dx, 0.04, -0.006))
            mb.add(nh.tube([ankle, tip], [0.004, 0.0], sides=5), LIMB)

    return mb.to_object("Pterodactylus")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "Pterodactylus")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, background=(0.45, 0.58, 0.70),
                          views=((35, 25), (20, 70), (0, 89), (180, -35)))
        # head close-up to check the jaws, teeth and crest
        cam = bpy.context.scene.camera
        cam.data.lens = 50
        cam.location = Vector((0.26, -0.56, 0.12))
        cam.rotation_euler = (Vector((0.0, -0.32, 0.075)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
