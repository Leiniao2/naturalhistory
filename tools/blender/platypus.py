"""
Procedural low-poly platypus (Ornithorhynchus anatinus) for map colonies.

A low, streamlined, otter-like body in dark-brown fur with a tan belly, a broad
flat grey-black duck bill, small eyes, a flat beaver-like paddle tail and short
sprawling legs with webbed feet. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/platypus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Platypus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

FUR = (0.26, 0.15, 0.08)        # dark brown back
FUR_LIGHT = (0.40, 0.25, 0.13)  # flanks
BELLY = (0.68, 0.50, 0.30)      # tan underside
BILL = (0.16, 0.16, 0.18)       # grey-black, leathery
BILL_TOP = (0.26, 0.26, 0.28)
FEET = (0.22, 0.20, 0.20)
EYE = (0.02, 0.02, 0.02)
TAIL = (0.22, 0.13, 0.07)

BODY_Z = 0.115  # body centre height: belly almost on the ground


def fur(belly_line):
    """Back dark, flanks lighter, belly tan below belly_line (local z)."""
    def color(co, n):
        top = nh.smoothstep(-0.2, 0.7, n.z)
        c = nh.lerp(FUR_LIGHT, FUR, top)
        c = nh.lerp(c, FUR_LIGHT, 0.35 * max(0.0, noise.noise(co * 9.0)))  # patchy, sleek fur sheen
        return nh.lerp(BELLY, c, nh.smoothstep(belly_line - 0.03, belly_line + 0.03, co.z))
    return color


def body():
    # Streamlined: wider at the hips, tapering a little toward the neck, flat underneath
    def deform(n):
        k = 1.0 + 0.08 * max(0.0, n.y)       # fuller rear
        if n.z < 0:
            k *= 1.0 - 0.25 * (-n.z) ** 2    # flatter belly
        return k
    return nh.uv_ellipsoid((0, 0.02, BODY_Z), (0.19, 0.40, 0.11), segments=20, rings=12, deform=deform)


def head():
    # long and low so it flows out of the shoulders instead of sitting on them like a ball
    return nh.uv_ellipsoid((0, -0.36, BODY_Z + 0.005), (0.13, 0.19, 0.085), segments=16, rings=10)


def bill():
    """Broad, flat, duck-like bill that widens toward a rounded tip."""
    bm = nh.uv_ellipsoid((0, 0, 0), (0.12, 0.19, 0.028), segments=18, rings=8)
    for v in bm.verts:
        t = nh.smoothstep(0.14, -0.19, v.co.y)  # 0 at base, 1 at tip
        v.co.x *= 0.85 + 0.4 * t
        v.co.z *= 1.0 - 0.25 * t
        v.co.z += 0.012 * t                       # tip turns up slightly
    nh.transform(bm, Matrix.Rotation(math.radians(6), 4, "X"))  # nose dips a touch
    nh.transform(bm, Matrix.Translation(Vector((0, -0.66, BODY_Z - 0.01))))

    def color(co, n):
        return nh.lerp(BILL, BILL_TOP, nh.smoothstep(0.0, 0.8, n.z))
    return bm, color


def tail():
    """Flat, broad paddle, slightly narrower at the root."""
    bm = nh.uv_ellipsoid((0, 0, 0), (0.16, 0.23, 0.032), segments=16, rings=8)
    for v in bm.verts:
        t = nh.smoothstep(0.22, -0.22, v.co.y)  # 1 at the root, 0 at the tip
        v.co.x *= 1.0 - 0.3 * t
        v.co.z *= 1.0 + 0.6 * t
    nh.transform(bm, Matrix.Rotation(math.radians(-8), 4, "X"))  # tip dips toward the ground
    nh.transform(bm, Matrix.Translation(Vector((0, 0.56, BODY_Z - 0.035))))
    return bm, (lambda co, n: nh.lerp(nh.lerp(TAIL, BELLY, 0.3), TAIL, nh.smoothstep(-0.5, 0.5, n.z)))


def leg(side, front):
    """Short sprawling leg: upper limb out sideways from the body, down to a webbed foot."""
    sx = 1 if side > 0 else -1
    y = -0.22 if front else 0.24
    # reptile-like sprawl: the elbow sticks out sideways at body height, the foot plants beside it
    hip = Vector((sx * 0.12, y, BODY_Z - 0.02))
    knee = Vector((sx * 0.22, y - 0.01, BODY_Z - 0.01))
    ankle = Vector((sx * 0.26, y - 0.03, 0.02))
    limb = nh.tube([hip, knee, ankle], [0.05, 0.042, 0.03], sides=7)

    # webbed foot: flat fan of toes; front feet broader (they paddle)
    spread = 0.13 if front else 0.09
    reach = 0.11 if front else 0.09
    fx = sx * 0.28
    fy = y - 0.05
    outline = []
    toes = 5
    for i in range(toes):
        a = math.radians(-55 + 110 * i / (toes - 1))
        tip = Vector((fx + math.sin(a) * spread * 0.9 * sx, fy - math.cos(a) * reach, 0.012))
        outline.append(tip)
        if i < toes - 1:
            a2 = math.radians(-55 + 110 * (i + 0.5) / (toes - 1))
            web = 0.78 if front else 0.6  # webbing reaches the toe tips on the front feet
            outline.append(Vector((fx + math.sin(a2) * spread * 0.9 * web * sx, fy - math.cos(a2) * reach * web, 0.012)))
    outline.append(Vector((fx + 0.03 * sx, fy + 0.04, 0.012)))
    outline.append(Vector((fx - 0.03 * sx, fy + 0.04, 0.012)))
    if sx < 0:
        outline.reverse()
    foot = nh.flat_panel([tuple(p) for p in outline], thickness=0.018)
    return limb, foot


def eye(side):
    return nh.ellipsoid((side * 0.085, -0.44, BODY_Z + 0.04), (0.022, 0.022, 0.022), subdivisions=1)


def build():
    mb = nh.MeshBuilder()
    mb.add(body(), fur(BODY_Z - 0.05))
    mb.add(head(), fur(BODY_Z - 0.04))
    mb.add(*bill())
    mb.add(*tail())
    for side in (1, -1):
        for front in (True, False):
            limb, foot = leg(side, front)
            mb.add(limb, nh.lerp(FUR, FUR_LIGHT, 0.35))
            mb.add(foot, FEET, smooth=False)
        mb.add(eye(side), EYE)
    obj = mb.to_object("Platypus", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Platypus", ground=(0.25, 0.38, 0.22), views=((35, 35), (-90, 10), (180, 60)))
