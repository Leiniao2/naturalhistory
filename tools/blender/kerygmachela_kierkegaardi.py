"""
Procedural low-poly Kerygmachela kierkegaardi (Sirius Passet gilled lobopodian).

A broad, soft trunk fringed with eleven pairs of wide, rounded swimming flaps
(gills on their upper side), small stubby lobopod legs beneath, a pair of very
long, slender tail spines streaming behind, a small head with a pair of big
frontal appendages each ending in long forward-curving spines like a rake.
Greyish ochre with darker flap bases. A cousin of the radiodonts and Opabinia.
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Kerygmachela.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.70, 0.60, 0.44)
BODY_DARK = (0.48, 0.40, 0.28)
BELLY = (0.86, 0.78, 0.64)
FLAP = (0.76, 0.66, 0.48)
FLAP_EDGE = (0.56, 0.44, 0.30)
GILL = (0.80, 0.44, 0.36)
APP = (0.66, 0.50, 0.34)
SPINE = (0.92, 0.84, 0.66)
EYE = (0.06, 0.05, 0.05)

Y0, Y1, SEG = -0.32, 0.36, 11


def width(t):
    return 0.09 * (1 - 0.55 * t ** 1.6)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.55, sides=10, tip=0.015),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.5))
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.06, 0.0), (0.07, 0.08, 0.05), segments=12, rings=7), BODY)
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.5) * (Y1 - Y0) / SEG
        ln = 0.18 * (1 - 0.45 * t) + 0.02
        for s in (-1, 1):
            f = ec.paddle(ln, 0.045, n=12, taper=0.6, thickness=0.009)
            nh.transform(f, Matrix.Rotation(math.radians(-12), 4, "Z") @ Matrix.Rotation(math.radians(-4), 4, "Y"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * width(t) * 0.8, y, -0.005)))
            mb.add(f, lambda co, n: nh.lerp(FLAP_EDGE, FLAP, nh.smoothstep(0.08, 0.18, abs(co.x))), smooth=False)
            g = ec.paddle(ln * 0.6, 0.02, n=8, thickness=0.006)
            nh.transform(g, Matrix.Rotation(math.radians(-10), 4, "Z"))
            ec.mirror(g, s)
            nh.transform(g, Matrix.Translation((s * width(t) * 0.8, y + 0.008, 0.006)))
            mb.add(g, GILL, smooth=False)
            # stubby lobopod
            r = Vector((s * width(t) * 0.5, y, -0.02))
            mb.add(nh.tube([r, r + Vector((s * 0.015, 0, -0.04))], [0.012, 0.007], sides=5), BELLY)
    # tail spines
    for s in (-1, 1):
        b = Vector((s * 0.012, Y1 - 0.005, 0.0))
        mb.add(nh.tube([b, b + Vector((s * 0.04, 0.2, 0.0)), b + Vector((s * 0.1, 0.45, -0.01)),
                        b + Vector((s * 0.15, 0.66, -0.02))], [0.012, 0.009, 0.005, 0.0], sides=5), BODY_DARK)
    # frontal appendages with long spines
    for s in (-1, 1):
        b = Vector((s * 0.04, Y0 - 0.12, -0.01))
        pts = [b, b + Vector((s * 0.04, -0.08, 0.0)), b + Vector((s * 0.05, -0.17, 0.0)),
               b + Vector((s * 0.03, -0.25, -0.01))]
        mb.add(nh.tube(pts, [0.026, 0.022, 0.016, 0.01], sides=6), APP)
        for q in range(4):
            p = pts[q] if q < 3 else pts[3]
            mb.add(ec.spike(p, p + Vector((-s * 0.04, -0.13 - 0.03 * q, -0.01)), r=0.008, sides=4), SPINE,
                   smooth=False)
        mb.add(nh.ellipsoid((s * 0.035, Y0 - 0.1, 0.035), (0.014, 0.014, 0.012), subdivisions=1), EYE)
    return ec.centre(mb.to_object("Kerygmachela", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Kerygmachela")
