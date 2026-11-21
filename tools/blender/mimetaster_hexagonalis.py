"""
Procedural Mimetaster hexagonalis (Early Devonian marrellomorph, Hunsrueck Slate, Germany)
for map colonies (Swim style).

A Devonian cousin of Marrella about 5 cm across: a small, raised, star-shaped head shield
with six long rays radiating out like a snowflake, each ray studded with small spines; a
short segmented trunk under and behind the shield with a fringe of many small legs; a pair
of long, thin antennae and a pair of long, bristled swimming limbs; small eyes on short
stalks. Bluish-grey with rusty, paler-tipped rays. Reuses nh_edicam.py helpers. Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/mimetaster_hexagonalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mimetaster.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.56, 0.60, 0.66)
BODY_DARK = (0.34, 0.38, 0.46)
BELLY = (0.80, 0.80, 0.80)
SHIELD = (0.50, 0.40, 0.36)
RAY = (0.56, 0.32, 0.20)
RAY_TIP = (0.90, 0.80, 0.62)
LEG = (0.80, 0.70, 0.64)
GILL = (0.78, 0.52, 0.48)
EYE = (0.06, 0.05, 0.06)

Y0, Y1, SEG = -0.12, 0.42, 18


def width(t):
    return 0.06 * (1 - 0.7 * t ** 1.3)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.55, sides=8),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.5))
    for i in range(SEG):
        t = (i + 0.5) / SEG
        y = Y0 + (Y1 - Y0) * t
        w = width(t)
        ln = 0.05 + 0.04 * (1 - t)
        for s in (-1, 1):
            root = Vector((s * w * 0.8, y, -0.01))
            foot = root + Vector((s * ln * 0.8, -0.01, -ln * 0.6))
            mb.add(ec.jointed_leg([root, root.lerp(foot, 0.5) + Vector((s * 0.01, 0, 0.01)), foot],
                                  0.007, 0.003, sides=4), LEG, smooth=False)
    # star-shaped head shield: a raised hexagonal plate over the head
    cy, cz = -0.12, 0.07
    outline = []
    for k in range(12):
        a = math.radians(90 + k * 30)
        r = 0.15 if k % 2 == 0 else 0.075
        outline.append((math.cos(a) * r, cy + math.sin(a) * r, cz))
    mb.add(nh.flat_panel(outline, thickness=0.02), SHIELD, smooth=False)
    mb.add(nh.uv_ellipsoid((0, cy, cz + 0.01), (0.07, 0.07, 0.03), 12, 6), SHIELD)
    mb.add(nh.tube([(0, cy, cz - 0.01), (0, cy, -0.0)], [0.04, 0.05], sides=8), BODY_DARK)

    # six long rays from the star points, each with small spines
    for k in range(6):
        a = math.radians(-90 + k * 60)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        base = Vector((0, cy, cz)) + d * 0.12
        ln = 0.42
        pts = [base, base + d * ln * 0.35 + Vector((0, 0, 0.03)), base + d * ln * 0.7 + Vector((0, 0, 0.03)), base + d * ln]

        def col(co, n, base=base, d=d):
            t = max(0.0, min(1.0, (co - base).dot(d) / ln))
            return nh.lerp(RAY, RAY_TIP, nh.smoothstep(0.65, 1.0, t))
        mb.add(nh.tube(pts, [0.016, 0.012, 0.008, 0.0], sides=6), col)
        side = Vector((-d.y, d.x, 0))
        for j in range(5):
            p = base + d * ln * (0.15 + 0.15 * j) + Vector((0, 0, 0.03 if j else 0.015))
            for sgn in (1, -1):
                mb.add(ec.spike(p, p + side * sgn * 0.035 + d * 0.02, r=0.004, sides=3), RAY, smooth=False)
    for s in (-1, 1):
        a0 = Vector((s * 0.02, Y0 - 0.06, 0.0))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.04, -0.15, 0.01)), a0 + Vector((s * 0.12, -0.30, -0.01)),
                        a0 + Vector((s * 0.22, -0.40, -0.03))], [0.007, 0.005, 0.003, 0.0], sides=4), LEG)
        b0 = Vector((s * 0.04, Y0 - 0.02, -0.02))
        b1 = b0 + Vector((s * 0.16, -0.06, -0.02))
        b2 = b1 + Vector((s * 0.10, 0.08, -0.01))
        mb.add(nh.tube([b0, b1, b2], [0.012, 0.009, 0.005], sides=5), LEG)
        for k in range(6):
            p = b1.lerp(b2, k / 5) if k else b0.lerp(b1, 0.6)
            mb.add(ec.spike(p, p + Vector((s * 0.02, 0.045, 0)), r=0.004, sides=3), GILL, smooth=False)
        e = Vector((s * 0.035, Y0 - 0.07, 0.01))
        mb.add(nh.tube([e - Vector((s * 0.02, 0, 0)), e], [0.006, 0.006], sides=5), BODY_DARK)
        mb.add(nh.ellipsoid(e, (0.012, 0.012, 0.01), subdivisions=1), EYE)
    obj = mb.to_object("Mimetaster", roughness=0.4)
    return ec.centre(obj)


if __name__ == "__main__":
    ec.export(build, "Mimetaster")
