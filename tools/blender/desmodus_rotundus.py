"""
Procedural common vampire bat (Desmodus rotundus) in flight, wings spread.

Short grey-brown fur with a paler belly, a pug face with a flat horseshoe
nose-leaf, pointed ears, and big dark eyes. The wings are thin membranes
stretched between the arm and the four finger bones, billowing between them
and scalloped along the trailing edge. The thumb is long (vampire bats walk
on it) and the tail membrane is reduced to a narrow strip between the legs.
Shown in swarms above the tile, so the top view is the one that matters.

Usage:
  blender --background --python tools/blender/desmodus_rotundus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/VampireBat.fbx
Faces -Y, pivot at the body centre (flier). Body ~0.65 long, wingspan ~2.1.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

FUR = (0.36, 0.29, 0.23)
FUR_DARK = (0.22, 0.17, 0.14)
FUR_BELLY = (0.56, 0.49, 0.42)
SKIN = (0.40, 0.30, 0.28)      # bare snout, ears
NOSE = (0.48, 0.33, 0.31)
MEMBRANE = (0.20, 0.15, 0.14)
MEMBRANE_ROOT = (0.27, 0.20, 0.17)
MEMBRANE_EDGE = (0.34, 0.26, 0.22)
BONE = (0.13, 0.10, 0.09)
EYE = (0.02, 0.02, 0.02)
TOOTH = (0.92, 0.90, 0.85)

# Plan view (x, y) of the right wing skeleton; the left wing mirrors it.
SHOULDER = (0.06, -0.07)
ELBOW = (0.28, 0.06)
WRIST = (0.50, -0.10)
TIP_D3 = (1.05, 0.04)        # wingtip (digits 2 + 3 along the leading edge)
TIP_D4 = (0.84, 0.36)
TIP_D5 = (0.50, 0.43)
ANKLE = (0.15, 0.31)
HIP = (0.045, 0.17)
FLANK = (0.05, 0.10)          # where the membrane leaves the body

# Leading edge: shoulder -> propatagium (a little ahead of the arm) -> wrist -> tip
LEADING = [SHOULDER, (0.28, -0.115), WRIST, (0.78, -0.06), TIP_D3]
# Trailing-edge corner points; the membrane scallops inward between them
TRAIL_PTS = [FLANK, ANKLE, TIP_D5, TIP_D4, TIP_D3]
SCALLOP = [0.10, 0.22, 0.20, 0.16]   # inward sag of each scallop, as a fraction of its length
BONES = [(SHOULDER, ELBOW), (ELBOW, WRIST), (WRIST, TIP_D3), (WRIST, TIP_D4), (WRIST, TIP_D5), (HIP, ANKLE)]


def interp(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0) if x1 > x0 else 1.0
            return y0 + (y1 - y0) * t
    return pts[-1][1]


def trailing(x):
    for k, ((x0, y0), (x1, y1)) in enumerate(zip(TRAIL_PTS, TRAIL_PTS[1:])):
        if x <= x1:
            s = (x - x0) / (x1 - x0)
            y = y0 + (y1 - y0) * s
            seg = math.hypot(x1 - x0, y1 - y0)
            return y - SCALLOP[k] * seg * math.sin(math.pi * s) ** 0.8
    return TRAIL_PTS[-1][1]


def wing_z(x):
    """Gentle downward arch of the spread wing (mid-downstroke glide), tip lifting slightly."""
    return -0.10 * x * x + 0.05 * x + 0.04 * nh.smoothstep(0.85, 1.05, x)


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def bone_dist(x, y):
    return min(seg_dist((x, y), a, b) for a, b in BONES)


def bone_z(x, y):
    return wing_z(x) + 0.012


def membrane(sx, nu=30, nv=9, thickness=0.007):
    """Closed lofted membrane: billows up between the bones (air pressure in flight)."""
    bm = bmesh.new()
    x0, x1 = FLANK[0], TIP_D3[0]
    grid = {}
    for side, dz in (("top", 0.5), ("bot", -0.5)):
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (x1 - x0) * u
            yl = interp(LEADING, x) if i < nu else TIP_D3[1]
            yt = trailing(x) if i < nu else TIP_D3[1]
            for j in range(nv + 1):
                v = j / nv
                y = yl + (yt - yl) * v
                d = bone_dist(x, y)
                billow = 0.035 * nh.smoothstep(0.0, 0.12, d) * (1.0 - 0.6 * u)
                z = wing_z(x) + billow + dz * thickness
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
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        x, y = abs(co.x), co.y
        c = nh.lerp(MEMBRANE_ROOT, MEMBRANE, nh.smoothstep(0.05, 0.35, x))
        d = bone_dist(x, y)
        c = nh.lerp(BONE, c, nh.smoothstep(0.0, 0.03, d))
        yt = trailing(min(x, TIP_D3[0] - 1e-4))
        c = nh.lerp(c, MEMBRANE_EDGE, nh.smoothstep(-0.05, 0.0, y - yt) * 0.6)
        # faint wrinkles running parallel to the fingers
        c = nh.lerp(c, FUR_DARK, max(0.0, noise.noise(Vector((x * 9.0, y * 30.0, 0.3)))) * 0.25)
        if n.z < -0.3:
            c = nh.lerp(c, MEMBRANE_EDGE, 0.25)
        return c
    return bm, color


def bones(sx):
    shells = []

    def p3(xy, lift=0.0):
        return Vector((sx * xy[0], xy[1], bone_z(*xy) + lift))

    def limb(a, b, r0, r1, n=3):
        pts = [p3(nh.lerp(a, b, k / n)) for k in range(n + 1)]
        radii = [r0 + (r1 - r0) * k / n for k in range(n + 1)]
        shells.append(nh.tube(pts, radii, sides=5))

    limb(SHOULDER, ELBOW, 0.026, 0.017)
    limb(ELBOW, WRIST, 0.018, 0.014, n=4)
    shells.append(nh.ellipsoid(p3(ELBOW), (0.02, 0.02, 0.018), subdivisions=1))
    shells.append(nh.ellipsoid(p3(WRIST), (0.022, 0.02, 0.018), subdivisions=1))
    # digits: 3 to the tip, 4 and 5 to the trailing edge
    for tip, r in ((TIP_D3, 0.011), (TIP_D4, 0.010), (TIP_D5, 0.010)):
        mid = nh.lerp(WRIST, tip, 0.48)
        limb(WRIST, mid, r, r * 0.8)
        limb(mid, tip, r * 0.8, 0.003)
    # digit 2 runs just ahead of digit 3 to mid-wing
    limb(WRIST, (0.76, -0.075), 0.008, 0.003)
    # the long walking thumb with a claw, angled forward
    th0, th1 = p3(WRIST, 0.01), p3((0.53, -0.20), 0.025)
    shells.append(nh.tube([th0, th0.lerp(th1, 0.6), th1], [0.014, 0.011, 0.007], sides=6))
    claw_tip = th1 + Vector((sx * 0.012, -0.03, -0.02))
    shells.append(nh.tube([th1, claw_tip], [0.007, 0.0], sides=5))
    return shells


def legs(sx):
    shells = []
    hip = Vector((sx * HIP[0], HIP[1], -0.02))
    ankle = Vector((sx * ANKLE[0], ANKLE[1], wing_z(ANKLE[0]) - 0.005))
    knee = hip.lerp(ankle, 0.5) + Vector((0, 0, 0.01))
    shells.append(nh.tube([hip, knee, ankle], [0.024, 0.016, 0.012], sides=6))
    # small clawed foot with five toes pointing back
    for k in range(5):
        dx = (k - 2) * 0.008
        tip = ankle + Vector((sx * dx, 0.055, -0.012))
        shells.append(nh.tube([ankle, ankle.lerp(tip, 0.7), tip], [0.006, 0.005, 0.0], sides=4))
    return shells


def body_shells():
    s = []
    # torso: deep chest tapering to the hips
    s.append(nh.tube([(0, -0.13, 0.0), (0, -0.05, 0.006), (0, 0.05, 0.0), (0, 0.15, -0.012), (0, 0.24, -0.022), (0, 0.30, -0.028)],
                     [0.064, 0.095, 0.100, 0.086, 0.058, 0.0], sides=14, scale_xy=(1.0, 0.8)))
    # shoulders bulging into the wings
    for sx in (-1, 1):
        s.append(nh.ellipsoid((sx * 0.07, -0.07, 0.01), (0.055, 0.06, 0.042), subdivisions=2))
    # head: rounded skull, short pug snout
    s.append(nh.ellipsoid((0, -0.21, 0.025), (0.075, 0.075, 0.066), subdivisions=3))
    s.append(nh.ellipsoid((0, -0.28, 0.01), (0.042, 0.036, 0.036), subdivisions=2))
    # chin / lower lip with the grooved vampire lip
    s.append(nh.ellipsoid((0, -0.27, -0.022), (0.032, 0.028, 0.02), subdivisions=2))
    return s


def body_color(co, n):
    # bare snout and chin, fur elsewhere; paler belly, darker crown and back
    snout = nh.smoothstep(-0.255, -0.29, co.y)
    c = nh.lerp(FUR, FUR_DARK, nh.smoothstep(0.2, 0.9, n.z) * 0.5)
    c = nh.lerp(c, FUR_BELLY, nh.smoothstep(-0.1, -0.8, n.z))
    c = nh.lerp(c, FUR_DARK, max(0.0, noise.noise(co * 60.0)) * 0.35)
    return nh.lerp(c, SKIN, snout)


def ear(sx):
    """Pointed, slightly cupped ear: a flattened cone leaning out and back."""
    base = Vector((sx * 0.048, -0.195, 0.07))
    tip = base + Vector((sx * 0.04, 0.035, 0.085))
    pts = [base, base.lerp(tip, 0.35), base.lerp(tip, 0.7), tip]
    return nh.tube(pts, [0.032, 0.029, 0.019, 0.0], sides=8, scale_xy=(1.0, 0.45))


def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, FUR)
    body = parts.fuse(voxel=0.011, smooth=5, smooth_factor=0.5, max_tris=1800)

    mb = nh.MeshBuilder()
    mb.add(body, body_color)
    for sx in (-1, 1):
        mb.add(ear(sx), SKIN)
        mb.add(nh.ellipsoid((sx * 0.047, -0.265, 0.05), (0.014, 0.014, 0.014), subdivisions=1), EYE)
        # razor upper incisors peeking below the lip
        mb.add(nh.tube([(sx * 0.01, -0.296, -0.01), (sx * 0.01, -0.298, -0.034)], [0.006, 0.0], sides=4), TOOTH)
        mem, col = membrane(sx)
        mb.add(mem, col)
        for shell in bones(sx) + legs(sx):
            mb.add(shell, BONE)
    # flat horseshoe nose-leaf on the snout tip
    mb.add(nh.ellipsoid((0, -0.316, 0.016), (0.03, 0.01, 0.02), subdivisions=2), NOSE)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.01, -0.325, 0.018), (0.005, 0.004, 0.005), subdivisions=1), EYE)
    # vestigial tail membrane: a narrow strip between the ankles
    strip = [(-ANKLE[0], ANKLE[1] - 0.02, wing_z(ANKLE[0])), (-0.02, 0.22, -0.025), (0.02, 0.22, -0.025),
             (ANKLE[0], ANKLE[1] - 0.02, wing_z(ANKLE[0])), (0.0, 0.28, -0.02)]
    mb.add(nh.flat_panel([strip[0], strip[1], strip[2], strip[3], strip[4]], thickness=0.006), MEMBRANE, smooth=False)

    return mb.to_object("VampireBat", roughness=0.75)


if __name__ == "__main__":
    nh.run(build, "VampireBat", background=(0.10, 0.12, 0.10),
           views=((35, 25), (20, 70), (0, 89), (160, 10)))
