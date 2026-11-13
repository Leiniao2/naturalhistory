"""
Procedural low-poly mosquito (Culicidae, Aedes-style) in flight, for swarms over wetland tiles.

Round head with big dark compound eyes, long straight proboscis, bushy antennae,
humped thorax, slender banded abdomen, two narrow glassy wings in a shallow V,
tiny halteres and six long jointed legs (hind pair raised). Faces -Y, pivot at
the body centre.

Usage:
  blender --background --python tools/blender/mosquito.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mosquito.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

# Palette
BODY_DARK = (0.10, 0.09, 0.10)
BODY_MID = (0.22, 0.19, 0.18)
THORAX = (0.30, 0.25, 0.20)
SCALE_WHITE = (0.85, 0.85, 0.82)  # Aedes-style pale bands
EYE = (0.05, 0.05, 0.07)
EYE_SHEEN = (0.18, 0.16, 0.22)
WING_EDGE = (0.45, 0.50, 0.58)
WING = (0.78, 0.84, 0.92)
LEG = (0.14, 0.12, 0.12)
LEG_BAND = (0.80, 0.80, 0.78)
HALTERE = (0.70, 0.62, 0.45)

# Key positions (Y is the body axis, head toward -Y)
HEAD = Vector((0.0, -0.36, 0.06))
THORAX_C = Vector((0.0, -0.13, 0.08))
ABDOMEN_START = Vector((0.0, 0.04, 0.04))


def build_head(mb):
    mb.add(nh.uv_ellipsoid(HEAD, (0.075, 0.07, 0.07), segments=12, rings=8), BODY_MID)
    # compound eyes wrap the front/sides of the head
    for sx in (-1, 1):
        c = HEAD + Vector((sx * 0.045, -0.025, 0.01))

        def eye_col(co, n, c=c):
            return nh.lerp(EYE, EYE_SHEEN, max(0.0, n.z) * 0.8)

        mb.add(nh.uv_ellipsoid(c, (0.05, 0.05, 0.06), segments=10, rings=7), eye_col)

    # proboscis: long, straight, angled slightly down
    tip = HEAD + Vector((0.0, -0.46, -0.10))
    mb.add(nh.tube([HEAD + Vector((0, -0.06, -0.02)), HEAD.lerp(tip, 0.5) + Vector((0, -0.03, -0.01)), tip],
                   [0.012, 0.008, 0.0], sides=4), BODY_DARK)
    # palps either side of the proboscis, short
    for sx in (-1, 1):
        mb.add(nh.tube([HEAD + Vector((sx * 0.015, -0.06, -0.02)),
                        HEAD + Vector((sx * 0.022, -0.17, -0.05))],
                       [0.008, 0.0], sides=3), nh.lerp(BODY_DARK, SCALE_WHITE, 0.35))

    # antennae: thin shafts with whorls of short bristles (plumose look)
    for sx in (-1, 1):
        base = HEAD + Vector((sx * 0.02, -0.06, 0.04))
        tip = HEAD + Vector((sx * 0.11, -0.27, 0.13))
        mb.add(nh.tube([base, base.lerp(tip, 0.5), tip], [0.006, 0.005, 0.0], sides=3), BODY_MID)
        axis = (tip - base).normalized()
        side = axis.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(axis).normalized()
        for i in range(1, 6):
            t = i / 6.0
            p = base.lerp(tip, t)
            length = 0.055 * (1.0 - t * 0.6)
            for k in range(4):
                a = k / 4 * math.tau + i * 0.4
                d = (side * math.cos(a) + up * math.sin(a) + axis * 0.5).normalized()
                mb.add(nh.tube([p, p + d * length], [0.003, 0.0], sides=3, cap_start=False),
                       nh.lerp(BODY_MID, (0.55, 0.5, 0.45), 0.5))


def build_thorax(mb):
    # humped thorax: taller toward the front
    def hump(n):
        return 1.0 + 0.18 * max(0.0, n.z) * max(0.0, 1.0 - abs(n.y + 0.2))

    def col(co, n):
        c = nh.lerp(THORAX, BODY_DARK, max(0.0, -n.z))
        # lyre-like pale stripes on top (Aedes)
        if n.z > 0.55 and abs(co.x) < 0.025:
            c = nh.lerp(c, SCALE_WHITE, 0.8)
        return c

    mb.add(nh.uv_ellipsoid(THORAX_C, (0.10, 0.15, 0.11), segments=14, rings=10, deform=hump), col)
    # scutellum / neck joint
    mb.add(nh.uv_ellipsoid(HEAD.lerp(THORAX_C, 0.55), (0.04, 0.05, 0.04), segments=8, rings=6), BODY_MID)


def build_abdomen(mb):
    # One continuous tapering tube, curving gently down; 8 segments painted as dark
    # tergites with pale basal bands, and a faint pinch at each segment boundary.
    n_seg = 8
    length = 0.68
    steps = n_seg * 3
    pts, radii = [], []
    for i in range(steps + 1):
        t = i / steps
        pts.append(ABDOMEN_START + Vector((0.0, t * length, -0.07 * t * t)))
        seg_phase = (t * n_seg) % 1.0
        pinch = 1.0 - 0.12 * (1.0 - min(seg_phase, 1.0 - seg_phase) * 2.0) ** 4
        radii.append(0.056 * (1.0 - 0.5 * t) * pinch)
    radii[0] *= 0.7
    radii[-1] = 0.0

    def col(co, n):
        t = max(0.0, min(0.999, (co.y - ABDOMEN_START.y) / length))
        phase = (t * n_seg) % 1.0
        c = BODY_DARK if n.z > -0.2 else BODY_MID
        if phase < 0.25 and t > 0.05:
            c = nh.lerp(c, SCALE_WHITE, 0.9 if n.z > -0.2 else 0.6)
        return c

    mb.add(nh.tube(pts, radii, sides=10, scale_xy=(1.0, 0.85)), col)
    # cerci at the tip
    end = pts[-1]
    for sx in (-1, 1):
        mb.add(nh.tube([end + Vector((0, -0.02, 0)), end + Vector((sx * 0.018, 0.05, -0.012))],
                       [0.007, 0.0], sides=3), BODY_MID)


def wing_outline(sx):
    """Narrow, rounded wing in the XY plane; root at origin, pointing outward and back."""
    pts = []
    length, width = 0.70, 0.10
    n = 14
    for i in range(n + 1):  # leading edge root -> tip
        t = i / n
        x = t * length
        y = -width * 0.35 * math.sin(math.pi * min(1.0, t * 1.05)) * (1.0 - 0.3 * t)
        pts.append((x, y, 0.0))
    for i in range(n, -1, -1):  # trailing edge tip -> root
        t = i / n
        x = t * length
        y = width * 0.65 * math.sin(math.pi * min(1.0, t)) ** 0.8 * (0.6 + 0.4 * t)
        pts.append((x, y, 0.0))
    # drop duplicate tip/root points
    clean = []
    for p in pts:
        if not clean or (Vector(p) - Vector(clean[-1])).length > 1e-5:
            clean.append(p)
    if (Vector(clean[0]) - Vector(clean[-1])).length < 1e-5:
        clean.pop()
    return [(x * sx, y, z) for x, y, z in clean]


def build_wings(mb):
    root_y = THORAX_C.y - 0.02
    for sx in (-1, 1):
        bm = nh.flat_panel(wing_outline(sx), thickness=0.006)
        # sweep back ~48°, lift into a shallow V (~18°)
        sweep = Matrix.Rotation(math.radians(48 * sx), 4, "Z")
        dihedral = Matrix.Rotation(math.radians(18 * sx), 4, "Y")
        nh.transform(bm, sweep @ dihedral)
        root = Vector((sx * 0.06, root_y, THORAX_C.z + 0.09))
        nh.transform(bm, Matrix.Translation(root))

        def col(co, n, root=root):
            d = (co - root).length / 0.72
            # darker veins near the leading edge / root, glassy pale toward the edge
            return nh.lerp(WING_EDGE, WING, nh.smoothstep(0.0, 0.5, d))

        mb.add(bm, col, smooth=False)

    # halteres: tiny knobbed stalks behind the wings
    for sx in (-1, 1):
        base = Vector((sx * 0.07, THORAX_C.y + 0.10, THORAX_C.z + 0.03))
        tip = base + Vector((sx * 0.07, 0.03, 0.03))
        mb.add(nh.tube([base, tip], [0.006, 0.004], sides=3), HALTERE)
        mb.add(nh.uv_ellipsoid(tip, (0.014, 0.014, 0.014), segments=6, rings=4), HALTERE)


def leg_path(sx, pair):
    """Coxa at the thorax underside -> femur up/out -> knee -> tibia down -> long tarsus.
    pair: 0 front, 1 middle, 2 hind (hind legs raised behind, typical in flight)."""
    hip = Vector((sx * 0.05, THORAX_C.y - 0.06 + pair * 0.07, THORAX_C.z - 0.08))
    if pair == 0:    # forward and down
        knee = hip + Vector((sx * 0.20, -0.22, -0.02))
        ankle = knee + Vector((sx * 0.10, -0.25, -0.30))
        toe = ankle + Vector((sx * 0.05, -0.12, -0.28))
    elif pair == 1:  # straight out and down
        knee = hip + Vector((sx * 0.30, -0.02, 0.02))
        ankle = knee + Vector((sx * 0.20, 0.02, -0.36))
        toe = ankle + Vector((sx * 0.08, 0.05, -0.32))
    else:            # backward, tarsi curving up
        knee = hip + Vector((sx * 0.24, 0.28, 0.02))
        ankle = knee + Vector((sx * 0.16, 0.32, -0.18))
        toe = ankle + Vector((sx * 0.04, 0.30, 0.10))
    return hip, knee, ankle, toe


def build_legs(mb):
    for pair in range(3):
        for sx in (-1, 1):
            hip, knee, ankle, toe = leg_path(sx, pair)
            # femur, tibia, tarsus as separate thin tubes so the joints read
            mb.add(nh.tube([hip, knee], [0.014, 0.011], sides=4), LEG)
            mb.add(nh.tube([knee, ankle], [0.011, 0.008], sides=4), LEG)
            mid = ankle.lerp(toe, 0.5)
            mb.add(nh.tube([ankle, mid, toe], [0.007, 0.005, 0.0], sides=3), LEG)
            # pale "knee" and tarsal bands (Aedes white socks)
            for p, r in ((knee, 0.016), (ankle, 0.012), (mid, 0.009)):
                mb.add(nh.uv_ellipsoid(p, (r, r, r), segments=6, rings=4), LEG_BAND)


def build():
    mb = nh.MeshBuilder()
    build_head(mb)
    build_thorax(mb)
    build_abdomen(mb)
    build_wings(mb)
    build_legs(mb)
    obj = mb.to_object("Mosquito", roughness=0.45)
    # pivot at the body centre (between thorax and abdomen)
    centre = THORAX_C.lerp(ABDOMEN_START, 0.5)
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Mosquito", views=((35, 25), (-90, 8), (150, 55)))
