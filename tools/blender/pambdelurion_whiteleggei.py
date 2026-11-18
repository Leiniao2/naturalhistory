"""
Procedural Pambdelurion whiteleggei (early Cambrian gilled lobopodian, Sirius Passet, Greenland).

A big (up to ~50 cm), soft, annulated, slightly flattened body; eleven pairs of broad lateral
swimming flaps overlapping along the sides, eleven pairs of short, stubby lobopod legs below
them, a small head with a ventral ring-shaped mouth of plates, and a pair of large, curved,
spiny frontal appendages held down and forward for grabbing prey. Pinkish brown with darker
annulations and paler flap edges. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/pambdelurion_whiteleggei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pambdelurion.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.66, 0.40, 0.34)
DARK = (0.42, 0.22, 0.20)
BELLY = (0.84, 0.66, 0.58)
FLAP = (0.72, 0.46, 0.38)
FLAP_EDGE = (0.92, 0.76, 0.64)
APP = (0.60, 0.32, 0.26)
SPINE = (0.95, 0.86, 0.70)
MOUTH = (0.30, 0.16, 0.12)
Y0, Y1, SEG = -0.5, 0.6, 11


def width(t):
    return 0.13 * (1 - 0.55 * t ** 1.6) + 0.01


def build():
    mb = nh.MeshBuilder()
    trunk = ec.segmented_trunk(Y0, Y1, SEG * 2, width, flat=0.6, sides=12, tip=0.03, pinch=0.9)
    mb.add(trunk, ec.banded(BODY, DARK, BELLY, Y0, (Y1 - Y0) / (SEG * 2), amount=0.5))
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.05, -0.005), (0.09, 0.1, 0.065), segments=14, rings=8),
           lambda co, n: nh.lerp(BELLY, BODY, nh.smoothstep(-0.5, 0.2, n.z)))
    mb.add(nh.ellipsoid((0, Y0 - 0.09, -0.06), (0.04, 0.035, 0.012), subdivisions=2), MOUTH)
    seg = (Y1 - Y0) / SEG
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.5) * seg
        w = width(t)
        ln = 0.2 * (1 - 0.5 * t) + 0.04
        for s in (-1, 1):
            f = ec.paddle(ln, 0.06, n=12, taper=0.6, thickness=0.012)
            nh.transform(f, Matrix.Rotation(math.radians(-15), 4, "Z") @ Matrix.Rotation(math.radians(-10), 4, "Y"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * w * 0.85, y, 0.0)))
            mb.add(f, lambda co, n: nh.lerp(FLAP, FLAP_EDGE, nh.smoothstep(0.17, 0.3, abs(co.x))), smooth=False)
            kit.lobopod(mb, (s * w * 0.55, y, -w * 0.45), (s * 0.35, -0.1, -1), 0.08, 0.025, BELLY, claw=DARK, rings=3)
    for s in (-1, 1):
        b = Vector((s * 0.05, Y0 - 0.1, -0.01))
        pts = kit.curve(b, b + Vector((s * 0.06, -0.2, -0.02)), b + Vector((s * 0.02, -0.26, -0.2)), 8)
        mb.add(nh.tube(pts, [0.04 - 0.004 * k for k in range(9)], sides=8), kit.ringed(APP, DARK, period=0.035, axis=1))
        for k in range(1, 8):
            p = pts[k]
            mb.add(ec.spike(p, p + Vector((-s * 0.04, 0.02, -0.05)), r=0.008, sides=4), SPINE, smooth=False)
            mb.add(ec.spike(p, p + Vector((s * 0.03, 0.03, -0.05)), r=0.006, sides=4), SPINE, smooth=False)
        e = Vector((s * 0.06, Y0 - 0.08, 0.05))
        mb.add(nh.ellipsoid(e, (0.014, 0.014, 0.014), subdivisions=2), (0.05, 0.04, 0.04))
    return ec.centre(mb.to_object("Pambdelurion", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Pambdelurion")
