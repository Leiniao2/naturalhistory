"""
Procedural low-poly red king crab (Paralithodes camtschaticus) for map colonies.

A broad, domed, slightly pear-shaped carapace (wider behind, with a forked
rostrum spike in front) studded with stout conical spines; three pairs of long,
spiny walking legs arched high to the sides with the knees above the shell;
a pair of claws folded in front, the right one (the crusher) clearly larger
than the left; a tiny fifth pair of legs tucked under the back of the shell
(kept for the gill-cleaning role, barely visible, as in life); small stalked
eyes and short antennae beside the rostrum. Dark burgundy red above shading to
cream-yellow below, spines tipped orange. Faces -Y, pivot at the body centre
(Swim style, like the other benthic marine animals on the opaque water tiles).

Usage:
  blender --background --python tools/blender/paralithodes_camtschaticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RedKingCrab.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.42, 0.05, 0.07)      # dark burgundy red
SHELL_LIGHT = (0.74, 0.18, 0.12)
SPINE = (0.62, 0.14, 0.10)
SPINE_TIP = (0.95, 0.55, 0.28)
UNDER = (0.94, 0.82, 0.60)      # cream-yellow underside
LEG = (0.52, 0.08, 0.08)
JOINT = (0.88, 0.50, 0.34)
CLAW_TIP = (0.16, 0.06, 0.05)
EYE = (0.04, 0.03, 0.03)

BODY_C = Vector((0.0, 0.0, 0.34))   # carapace centre


def shaded(top, bottom=UNDER):
    """Red above, cream below, blending on the normal."""
    return lambda co, n: nh.lerp(bottom, top, nh.smoothstep(-0.55, 0.15, n.z))


def carapace_point(u, v):
    """Surface point for unit-sphere direction (u = lon, v = lat): pear-shaped dome."""
    x, y, z = math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v)
    w = 0.36 * (1.0 + 0.22 * y - 0.08 * y * y)  # narrow front, broad shoulders behind
    ly = 0.34
    h = 0.17 if z > 0 else 0.09              # high dome, flatter belly
    z *= h * (1.0 - 0.15 * max(0.0, -y))     # front slopes down toward the rostrum
    return BODY_C + Vector((x * w, y * ly, z))


def carapace():
    bm = nh.uv_ellipsoid((0, 0, 0), (1, 1, 1), segments=22, rings=12)
    for v in bm.verts:
        n = v.co.normalized()
        lat = math.asin(max(-1.0, min(1.0, n.z)))
        lon = math.atan2(n.y, n.x)
        v.co = carapace_point(lon, lat)
    return bm


def cone(base, direction, length, radius, sides=4):
    d = Vector(direction).normalized()
    return nh.tube([Vector(base), Vector(base) + d * length], [radius, 0.0], sides=sides, cap_start=False)


def spine_color(base, direction, length, root=SPINE):
    b, d = Vector(base), Vector(direction).normalized()
    return lambda co, n: nh.lerp(root, SPINE_TIP, nh.smoothstep(0.3, 1.0, (co - b).dot(d) / length))


def carapace_spines(mb):
    """Stout conical spines scattered over the dome (golden-angle spiral), bigger near the middle."""
    count = 46
    for i in range(count):
        t = (i + 0.5) / count
        r = math.sqrt(t) * 0.92
        a = i * 2.39996
        x, y = r * math.cos(a), r * math.sin(a)
        lat = math.acos(min(1.0, r)) * 0.98
        lon = math.atan2(y, x)
        p = carapace_point(lon, lat)
        q = carapace_point(lon, lat + 0.02)
        nrm = (p - BODY_C)
        nrm = Vector((nrm.x / 0.36 ** 2, nrm.y / 0.34 ** 2, nrm.z / 0.17 ** 2)).normalized()
        length = 0.06 * (1.0 - 0.45 * r) + 0.02
        d = (nrm + Vector((0, 0, 0.3))).normalized()
        mb.add(cone(p - d * 0.01, d, length, 0.022 * (1.0 - 0.3 * r)), spine_color(p, d, length))
    # rostrum: a stout forked spike pointing forward
    base = carapace_point(-math.pi / 2, 0.15)
    for s in (-1, 1):
        d = Vector((s * 0.25, -1.0, 0.25))
        mb.add(cone(base + Vector((0, 0.02, 0)), d, 0.13, 0.024, sides=5), spine_color(base, d, 0.13))
    # marginal spines around the rim
    for k in range(14):
        lon = math.radians(-70 + 160 * (k % 7) / 6) if k < 7 else math.radians(250 - 160 * (k - 7) / 6)
        p = carapace_point(lon, 0.05)
        d = (p - BODY_C)
        d.z = 0.15
        mb.add(cone(p - d.normalized() * 0.01, d, 0.06, 0.018), spine_color(p, d, 0.06))


def densify(pts, radii, k):
    """Inserts k-1 evenly spaced rings between consecutive tube points."""
    out, out_r = [], []
    for i in range(len(pts) - 1):
        for j in range(k):
            t = j / k
            out.append(pts[i].lerp(pts[i + 1], t))
            out_r.append(radii[i] + (radii[i + 1] - radii[i]) * t)
    return out + [pts[-1]], out_r + [radii[-1]]


def leg(mb, base, angle, reach, knee_h, thick, spines=True):
    """Walking leg arching out from the body: up to a high knee, then down to the tip at z = 0."""
    out = Vector((math.cos(angle), math.sin(angle), 0.0))
    b = Vector(base)
    pts = [
        b,
        b + out * 0.08 + Vector((0, 0, 0.02)),             # coxa/basis
        b + out * reach * 0.42 + Vector((0, 0, knee_h)),   # merus up to the knee
        b + out * reach * 0.62 + Vector((0, 0, knee_h * 0.85)),  # carpus
        b + out * reach * 0.88 + Vector((0, 0, 0.10 - b.z + 0.04)),  # propodus down
        b + out * reach * 0.98 + Vector((0, 0, -b.z)),     # dactyl tip on the ground
    ]
    radii = [thick, thick * 0.95, thick * 0.85, thick * 0.75, thick * 0.55, 0.0]

    # densify so the joint bands and dark tip stay narrow instead of smearing along a segment
    dense, dense_r = densify(pts, radii, 4)

    def color(co, n):
        if (co - pts[5]).length < 0.05:
            return CLAW_TIP
        near_joint = min((pts[i] - co).length for i in (2, 3, 4)) < thick * 0.8
        top = JOINT if near_joint else LEG
        return nh.lerp(UNDER, top, nh.smoothstep(-0.85, -0.35, n.z))

    mb.add(nh.tube(dense, dense_r, sides=7), color)
    if not spines:
        return
    # spines along the top of the merus and propodus
    for a, b2, count in ((1, 2, 4), (2, 3, 2), (3, 4, 3)):
        for k in range(count):
            t = (k + 0.5) / count
            p = pts[a].lerp(pts[b2], t)
            r = radii[a] + (radii[b2] - radii[a]) * t
            seg = (pts[b2] - pts[a]).normalized()
            side = seg.cross(Vector((0, 0, 1))).normalized()
            for s in (-0.6, 0.6):
                d = (Vector((0, 0, 1)) + side * s + seg * 0.4).normalized()
                mb.add(cone(p + d * r * 0.6, d, r * 1.3, r * 0.38, sides=3),
                       spine_color(p, d, r * 1.3, LEG), smooth=False)


def cheliped(mb, side, scale):
    """Claw arm folded in front of the body; side -1 = the crab's right (larger crusher)."""
    s = side
    b = Vector((s * 0.22, -0.20, 0.27))
    elbow = Vector((s * 0.42, -0.36, 0.40)) * Vector((1, 1, 1))
    wrist = Vector((s * 0.30, -0.52, 0.30))
    th = 0.05 * scale
    pts = [b, b.lerp(elbow, 0.5) + Vector((0, 0, 0.03)), elbow, wrist]
    mb.add(nh.tube(pts, [th, th * 1.05, th * 0.95, th * 0.85], sides=8), shaded(LEG))
    # spines on the arm
    for i in range(3):
        p = elbow.lerp(b, 0.2 + 0.25 * i) + Vector((0, 0, th * 0.7))
        d = Vector((s * 0.3, -0.2, 1.0))
        mb.add(cone(p, d, th * 0.9, th * 0.3, sides=3), spine_color(p, d, th * 0.9, LEG), smooth=False)
    # chela: swollen palm pointing inward/forward, with a fixed finger and a movable dactyl
    fwd = Vector((-s * 0.75, -0.6, -0.12)).normalized()
    palm_len = 0.14 * scale
    palm_c = wrist + fwd * palm_len * 0.8
    rot = fwd.to_track_quat("Y", "Z").to_matrix()
    palm = nh.ellipsoid((0, 0, 0), (0.07 * scale, palm_len, 0.055 * scale), subdivisions=2)
    nh.transform(palm, rot.to_4x4())
    nh.transform(palm, Matrix.Translation(palm_c))
    mb.add(palm, shaded(SHELL_LIGHT))
    tip_base = palm_c + fwd * palm_len * 0.85
    up = Vector((0, 0, 1))
    for k, (dz, ln) in enumerate(((-0.025, 0.16), (0.03, 0.15))):
        root = tip_base + up * dz * scale
        mid = root + fwd * ln * 0.55 * scale + up * (-dz * 0.3) * scale
        end = root + fwd * ln * scale + up * (-dz * 0.9) * scale

        def fcolor(co, n, root=root, ln=ln):
            t = (co - root).length / (ln * scale)
            return nh.lerp(SHELL_LIGHT, CLAW_TIP, nh.smoothstep(0.45, 0.9, t))
        mb.add(nh.tube([root, mid, end], [0.032 * scale, 0.024 * scale, 0.0], sides=6), fcolor)
    # knobby spines on top of the palm
    for i in range(3):
        p = palm_c + fwd * palm_len * (0.5 - 0.45 * i) + up * 0.05 * scale
        mb.add(cone(p, up + fwd * 0.2, 0.035 * scale, 0.013 * scale, sides=3),
               spine_color(p, up, 0.035 * scale, SHELL_LIGHT), smooth=False)


def build():
    mb = nh.MeshBuilder()
    mb.add(carapace(), lambda co, n: nh.lerp(UNDER, nh.lerp(SHELL, SHELL_LIGHT, 0.25 * (1 - n.z)),
                                             nh.smoothstep(-0.45, 0.05, n.z)))
    carapace_spines(mb)

    # three pairs of walking legs: front pair angled forward, rear pair back
    for side in (-1, 1):
        for k, (deg, reach, knee) in enumerate(((-28, 0.86, 0.28), (2, 0.9, 0.30), (32, 0.84, 0.26))):
            a = math.radians(deg)
            ang = a if side > 0 else math.pi - a
            base = BODY_C + Vector((side * 0.26, -0.10 + 0.13 * k, -0.06))
            leg(mb, base, ang, reach, knee, 0.06)
        # tiny fifth pair tucked under the back of the shell
        base = BODY_C + Vector((side * 0.12, 0.26, -0.08))
        leg(mb, base, math.radians(70) if side > 0 else math.radians(110), 0.14, 0.02, 0.012, spines=False)
        # claws: the crab's right (-X) is the big crusher
        cheliped(mb, side, 1.3 if side < 0 else 0.95)
        # stalked eyes and short antennae beside the rostrum
        eb = BODY_C + Vector((side * 0.06, -0.30, 0.02))
        et = eb + Vector((side * 0.025, -0.05, 0.03))
        mb.add(nh.tube([eb, et], [0.014, 0.012], sides=5), SHELL_LIGHT)
        mb.add(nh.ellipsoid(et + Vector((0, -0.01, 0.005)), (0.02, 0.02, 0.02), subdivisions=1), EYE)
        ab = BODY_C + Vector((side * 0.10, -0.30, -0.01))
        mb.add(nh.tube([ab, ab + Vector((side * 0.06, -0.10, 0.04)), ab + Vector((side * 0.1, -0.2, 0.03))],
                       [0.008, 0.005, 0.0], sides=3), SHELL_LIGHT)

    # tucked abdomen flap on the belly
    abd = nh.ellipsoid(BODY_C + Vector((0, 0.05, -0.08)), (0.22, 0.24, 0.03), subdivisions=2)
    mb.add(abd, UNDER)

    obj = mb.to_object("RedKingCrab", roughness=0.45)
    # pivot at the body centre
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "RedKingCrab", background=(0.05, 0.22, 0.30), views=((30, 35), (-90, 8), (0, 80)))
