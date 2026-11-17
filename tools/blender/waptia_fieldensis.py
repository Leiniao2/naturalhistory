"""
Procedural low-poly Waptia fieldensis (Burgess Shale bivalved arthropod).

A shrimp-like animal: a large two-valved carapace covering the front half, with
a dorsal hinge line; a pair of stalked eyes and long antennae poking out in
front; slender walking legs under the carapace; a long, slim, five-segment
abdomen tapering to a forked tail of two flat, paddle-shaped caudal rami.
Translucent amber carapace, darker abdomen bands. Also shown: a small cluster
of eggs under the carapace (Waptia brooded its eggs).
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Waptia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

CARAPACE = (0.82, 0.62, 0.36)
CARAPACE_EDGE = (0.58, 0.38, 0.20)
BODY = (0.76, 0.52, 0.34)
BODY_DARK = (0.50, 0.30, 0.18)
BELLY = (0.90, 0.76, 0.58)
LEG = (0.80, 0.60, 0.44)
EYE = (0.05, 0.04, 0.04)
EGG = (0.92, 0.80, 0.40)


def build():
    mb = nh.MeshBuilder()
    # body under the carapace and abdomen
    mb.add(ec.segmented_trunk(-0.45, 0.62, 11, lambda t: 0.065 * (1 - 0.5 * t), flat=0.75, sides=10),
           ec.banded(BODY, BODY_DARK, BELLY, -0.40, 0.1, amount=0.7))
    # carapace: two valves meeting in a raised dorsal hinge, open below
    def valve_deform(n):
        return 1.0

    car = nh.uv_ellipsoid((0, -0.27, 0.02), (0.13, 0.22, 0.11), segments=18, rings=10)
    for v in car.verts:
        # hinge crest along the top, valves flared out low on the sides
        x = v.co.x
        v.co.z += 0.03 * math.exp(-(x / 0.03) ** 2) * (1 if v.co.z > 0.02 else 0)
    import bmesh
    bmesh.ops.delete(car, geom=[v for v in car.verts if v.co.z < -0.06], context="VERTS")
    mb.add(car, lambda co, n: nh.lerp(CARAPACE, CARAPACE_EDGE, nh.smoothstep(-0.0, -0.06, co.z)))
    # eggs brooded under the front of the carapace
    for k in range(7):
        a = k * 2.4
        mb.add(nh.ellipsoid((0.04 * math.cos(a), -0.27 + 0.04 * math.sin(a) + 0.01 * k, -0.06),
                            (0.018, 0.018, 0.018), subdivisions=1), EGG)
    # caudal rami
    for s in (-1, 1):
        r = ec.paddle(0.26, 0.055, n=10, taper=0.4, thickness=0.012)
        nh.transform(r, Matrix.Rotation(math.radians(75), 4, "Z"))
        ec.mirror(r, s)
        nh.transform(r, Matrix.Translation((s * 0.015, 0.6, 0.0)))
        mb.add(r, lambda co, n: nh.lerp(BODY, BODY_DARK, nh.smoothstep(0.7, 0.85, co.y)), smooth=False)
    # legs under the carapace
    for i in range(8):
        y = -0.40 + i * 0.045
        for s in (-1, 1):
            r0 = Vector((s * 0.04, y, -0.04))
            f = Vector((s * 0.13, y - 0.02, -0.14))
            mb.add(ec.jointed_leg([r0, r0.lerp(f, 0.5) + Vector((s * 0.03, 0, 0.02)), f], 0.01, 0.004, sides=4), LEG)
    # eyes on stalks and antennae
    for s in (-1, 1):
        e0 = Vector((s * 0.03, -0.48, 0.02))
        e1 = e0 + Vector((s * 0.05, -0.05, 0.02))
        mb.add(nh.tube([e0, e1], [0.014, 0.011], sides=5), BODY)
        mb.add(nh.ellipsoid(e1, (0.025, 0.025, 0.022), subdivisions=1), EYE)
        a0 = Vector((s * 0.015, -0.5, -0.01))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.06, -0.15, 0.02)), a0 + Vector((s * 0.13, -0.3, 0.0))],
                       [0.009, 0.006, 0.0], sides=4), LEG)
    return ec.centre(mb.to_object("Waptia", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Waptia")
