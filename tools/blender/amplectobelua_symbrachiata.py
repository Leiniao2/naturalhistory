"""
Procedural low-poly Amplectobelua symbrachiata (Chengjiang radiodont).

Streamlined radiodont: a small head with a pair of large stalked eyes, an
oval sclerite on top; under it a pair of frontal appendages whose third
segment carries one enormous forward spine that closes against the rest of
the appendage like pincers (shown half open); eleven pairs of overlapping
swimming flaps tapering to the rear; a long tail of three pairs of narrow,
fringed blades and a pair of long streamer-like furcae. Dusky reddish brown
with pale flap margins. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Amplectobelua.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.56, 0.30, 0.24)
BODY_DARK = (0.36, 0.18, 0.15)
BELLY = (0.80, 0.60, 0.50)
FLAP = (0.66, 0.38, 0.30)
FLAP_EDGE = (0.88, 0.70, 0.56)
APP = (0.70, 0.42, 0.26)
SPINE = (0.92, 0.80, 0.60)
EYE = (0.04, 0.03, 0.04)

Y0, Y1, SEG = -0.36, 0.48, 11


def width(t):
    return 0.12 * (1 - 0.6 * t ** 1.3)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.55, sides=10, tip=0.02),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.6))
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.08, 0.01), (0.1, 0.12, 0.065), segments=14, rings=8),
           lambda co, n: nh.lerp(BELLY, BODY, nh.smoothstep(-0.5, 0.2, n.z)))
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.1, 0.06), (0.06, 0.08, 0.02), segments=10, rings=5), BODY_DARK)
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.5) * (Y1 - Y0) / SEG
        ln = 0.26 * (1 - 0.6 * t) + 0.03
        for s in (-1, 1):
            f = ec.paddle(ln, 0.06, n=12, taper=0.55, thickness=0.01)
            nh.transform(f, Matrix.Rotation(math.radians(-22), 4, "Z") @
                         Matrix.Rotation(math.radians(-6 + 10 * math.sin(i * 0.9)), 4, "Y"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * width(t) * 0.8, y, -0.01)))
            mb.add(f, lambda co, n: nh.lerp(FLAP, FLAP_EDGE, nh.smoothstep(0.18, 0.34, abs(co.x))), smooth=False)
    # tail fan: three pairs of narrow blades + two long furcae
    for s in (-1, 1):
        for k in range(3):
            b = ec.paddle(0.16 + 0.02 * k, 0.025, n=8, taper=0.5, thickness=0.008)
            nh.transform(b, Matrix.Rotation(math.radians(40 + 18 * k), 4, "Z") @
                         Matrix.Rotation(math.radians(-15), 4, "Y"))
            ec.mirror(b, s)
            nh.transform(b, Matrix.Translation((s * 0.02, Y1 - 0.02 + 0.02 * k, 0.01)))
            mb.add(b, FLAP_EDGE, smooth=False)
        f0 = Vector((s * 0.015, Y1 + 0.02, 0))
        mb.add(nh.tube([f0, f0 + Vector((s * 0.04, 0.2, 0.01)), f0 + Vector((s * 0.09, 0.42, 0.0))],
                       [0.012, 0.008, 0.0], sides=4), BODY_DARK)
    # frontal appendages with the big pincer spine
    for s in (-1, 1):
        b = Vector((s * 0.04, Y0 - 0.17, -0.03))
        k1 = b + Vector((s * 0.03, -0.1, -0.03))
        k2 = k1 + Vector((s * -0.01, -0.12, -0.02))
        tip = k2 + Vector((-s * 0.04, -0.06, 0.05))
        pts = [b, k1, k2, tip]
        mb.add(nh.tube(pts, [0.03, 0.026, 0.02, 0.012], sides=6), APP)
        for q in range(4):  # small ventral spines along the distal part
            p = k2.lerp(tip, q / 3)
            mb.add(ec.spike(p, p + Vector((0, 0.02, -0.035)), r=0.006, sides=3), SPINE, smooth=False)
        # the big spine on the third podomere, pointing forward and inward
        p = k1.lerp(k2, 0.3)
        mb.add(ec.spike(p, p + Vector((-s * 0.06, -0.2, 0.04)), r=0.02, sides=5), SPINE)
        # stalked eyes
        e0 = Vector((s * 0.07, Y0 - 0.12, 0.05))
        e1 = e0 + Vector((s * 0.07, -0.02, 0.03))
        mb.add(nh.tube([e0, e1], [0.02, 0.016], sides=6), BODY)
        mb.add(nh.ellipsoid(e1 + Vector((s * 0.02, 0, 0.0)), (0.035, 0.04, 0.032), subdivisions=2), EYE)
    return ec.centre(mb.to_object("Amplectobelua", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Amplectobelua")
