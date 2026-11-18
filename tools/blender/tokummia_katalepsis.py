"""
Procedural Tokummia katalepsis (Burgess Shale mandibulate arthropod, ~10 cm).

A broad, domed, two-halved (bivalved) carapace covers the front third; behind it a long,
narrow trunk of many short segments tapers to a small tail, with a row of many slender
legs beneath. At the front, below short antennae, a pair of large, robust pincer-like claws
(subchelate maxillipeds) reach forward. Rust-orange carapace with a paler hinge line,
darker trunk bands, pale legs. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/tokummia_katalepsis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tokummia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.78, 0.40, 0.20)
SHELL_DARK = (0.52, 0.24, 0.12)
HINGE = (0.92, 0.70, 0.46)
TRUNK = (0.70, 0.38, 0.22)
TRUNK_DARK = (0.44, 0.22, 0.12)
LEG = (0.92, 0.74, 0.56)
CLAW = (0.66, 0.28, 0.14)
CLAW_TIP = (0.25, 0.12, 0.08)


def build():
    mb = nh.MeshBuilder()
    # bivalved carapace: two domed halves meeting at a dorsal hinge
    for s in (-1, 1):
        half = nh.uv_ellipsoid((0, 0, 0), (0.16, 0.3, 0.17), segments=18, rings=10)
        for v in half.verts:
            v.co.x = abs(v.co.x) * 0.9 + 0.01
        nh.transform(half, Matrix.Rotation(math.radians(s * 12), 4, "Y"))
        if s < 0:
            nh.transform(half, Matrix.Scale(-1, 4, (1, 0, 0)))
            bmesh.ops.reverse_faces(half, faces=half.faces)
        nh.transform(half, Matrix.Translation((0, -0.32, 0.03)))
        mb.add(half, lambda co, n: nh.lerp(HINGE, nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(0.0, 0.15, -co.z + 0.03)),
                                           nh.smoothstep(0.01, 0.05, abs(co.x))))
    # long, many-segmented trunk
    mb.add(ec.segmented_trunk(-0.1, 0.62, 24, lambda t: 0.095 * (1 - 0.6 * t), flat=0.7, sides=8, tip=0.015),
           ec.banded(TRUNK, TRUNK_DARK, LEG, -0.1, 0.72 / 24, amount=0.6))
    for i in range(30):
        y = -0.5 + i * 0.045
        if y > 0.58:
            break
        w = 0.06 if y > -0.1 else 0.1
        for s in (-1, 1):
            p0 = Vector((s * w * 0.6, y, -0.03))
            mb.add(ec.jointed_leg([p0, p0 + Vector((s * 0.06, 0.0, -0.05)), p0 + Vector((s * 0.08, 0.02, -0.11))],
                                  r0=0.011, r1=0.006, sides=4), LEG)
    # big claws (subchelate maxillipeds)
    for s in (-1, 1):
        b = Vector((s * 0.05, -0.55, -0.06))
        k = b + Vector((s * 0.06, -0.12, -0.02))
        mb.add(nh.tube([b, b.lerp(k, 0.5), k], [0.03, 0.034, 0.03], sides=8), CLAW)
        hand = k + Vector((-s * 0.02, -0.14, 0.02))
        mb.add(nh.tube([k, k.lerp(hand, 0.5), hand], [0.032, 0.036, 0.02], sides=8), CLAW)
        finger = kit.curve(hand, hand + Vector((-s * 0.05, 0.03, -0.02)), hand + Vector((-s * 0.06, 0.1, -0.03)), 4)
        mb.add(nh.tube(finger, [0.018, 0.015, 0.012, 0.007, 0.0], sides=6), CLAW_TIP)
        for q in range(4):
            p = k.lerp(hand, 0.2 + q * 0.2)
            mb.add(ec.spike(p, p + Vector((-s * 0.04, 0.0, -0.01)), r=0.006, sides=3), CLAW_TIP, smooth=False)
        a0 = Vector((s * 0.03, -0.6, 0.04))
        mb.add(nh.tube(kit.curve(a0, a0 + Vector((s * 0.06, -0.12, 0.05)), a0 + Vector((s * 0.14, -0.2, 0.02)), 5),
                       [0.01, 0.008, 0.007, 0.005, 0.004, 0.0], sides=4), TRUNK_DARK)
    return ec.centre(mb.to_object("Tokummia", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Tokummia")
