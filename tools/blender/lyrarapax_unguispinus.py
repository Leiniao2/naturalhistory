"""
Procedural Lyrarapax unguispinus (early Cambrian amplectobeluid radiodont, Chengjiang, ~6 cm).

A small, streamlined radiodont: a rounded head with a pair of big stalked eyes, a pair of
frontal appendages whose long, curved, claw-like spines close inward like grasping hooks
("unguispinus"), eleven pairs of swimming flaps tapering back, and a lyre-shaped tail of two
long, outward-curving blades ("lyra"). Dark reddish brown with paler flap edges and ivory
claws. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/lyrarapax_unguispinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lyrarapax.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.50, 0.24, 0.20)
DARK = (0.30, 0.13, 0.11)
BELLY = (0.78, 0.56, 0.46)
FLAP = (0.60, 0.32, 0.26)
FLAP_EDGE = (0.90, 0.68, 0.54)
CLAW = (0.95, 0.88, 0.72)
EYE = (0.03, 0.03, 0.04)
Y0, Y1, SEG = -0.32, 0.42, 11


def width(t):
    return 0.1 * (1 - 0.55 * t ** 1.2)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.55, sides=10, tip=0.02),
           ec.banded(BODY, DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.6))
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.07, 0.01), (0.085, 0.1, 0.06), segments=14, rings=8),
           lambda co, n: nh.lerp(BELLY, BODY, nh.smoothstep(-0.5, 0.2, n.z)))
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.5) * (Y1 - Y0) / SEG
        ln = 0.22 * (1 - 0.6 * t) + 0.03
        for s in (-1, 1):
            f = ec.paddle(ln, 0.05, n=12, taper=0.55, thickness=0.01)
            nh.transform(f, Matrix.Rotation(math.radians(-25), 4, "Z") @
                         Matrix.Rotation(math.radians(-4 + 8 * math.sin(i)), 4, "Y"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * width(t) * 0.8, y, -0.01)))
            mb.add(f, lambda co, n: nh.lerp(FLAP, FLAP_EDGE, nh.smoothstep(0.15, 0.28, abs(co.x))), smooth=False)
    # lyre tail: two long blades curving out then back in
    for s in (-1, 1):
        pts = kit.curve((s * 0.01, Y1, 0.0), (s * 0.16, Y1 + 0.16, 0.01), (s * 0.08, Y1 + 0.36, 0.0), 8)
        mb.add(nh.tube(pts, [0.03, 0.035, 0.035, 0.032, 0.028, 0.022, 0.016, 0.01, 0.0], sides=6, scale_xy=(1.0, 0.3)),
               FLAP_EDGE)
    # grasping appendages with long, curved, inward claw-spines
    for s in (-1, 1):
        b = Vector((s * 0.035, Y0 - 0.14, -0.02))
        pts = kit.curve(b, b + Vector((s * 0.05, -0.12, -0.02)), b + Vector((-s * 0.01, -0.2, -0.07)), 6)
        mb.add(nh.tube(pts, [0.026, 0.024, 0.021, 0.018, 0.015, 0.012, 0.008], sides=6), kit.ringed(BODY, DARK, 0.03, axis=1))
        for k in range(1, 6):
            p = pts[k]
            ln = 0.09 - 0.01 * k
            tip = p + Vector((-s * ln * 0.8, ln * 0.2, -ln * 0.6))
            mid = p.lerp(tip, 0.5) + Vector((0, -0.02, -0.01))
            mb.add(ec.spike(p, tip, r=0.008, sides=4, mid=mid), CLAW, smooth=False)
        e0 = Vector((s * 0.06, Y0 - 0.1, 0.05))
        e1 = e0 + Vector((s * 0.06, -0.02, 0.03))
        mb.add(nh.tube([e0, e1], [0.016, 0.013], sides=6), BODY)
        mb.add(nh.ellipsoid(e1 + Vector((s * 0.015, 0, 0)), (0.032, 0.036, 0.03), subdivisions=2), EYE)
    return ec.centre(mb.to_object("Lyrarapax", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Lyrarapax")
