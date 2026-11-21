"""
Procedural Mollisonia plenovenatrix (Burgess Shale early chelicerate, a few cm).

A compact, tough-looking arthropod: a high, rounded semicircular head shield, a short
trunk of six broad tergites with blunt pleural tips, and a large rounded tail shield.
In front, beneath the head, a pair of small pincers (the chelicerae) reach forward; the
tips of walking legs show at the sides. Dark brown with a greyish sheen. Faces -Y, pivot
at the body centre (Swim).

Output: Assets/Resources/Models/Species/Mollisonia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.36, 0.28, 0.22)
EDGE = (0.58, 0.50, 0.42)
LEG = (0.58, 0.44, 0.32)
CLAW = (0.30, 0.20, 0.14)


def shade(co, n):
    return nh.lerp(SHELL, EDGE, nh.smoothstep(0.2, 0.38, abs(co.x)))


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.plate(-0.3, 0.42, 0.26, 0.16, edge_droop=0.8), shade)
    ck.tergites(mb, -0.06, 0.32, 6, lambda t: 0.42 - 0.08 * t, 0.1, lambda i, t: shade)
    mb.add(ec.plate(0.46, 0.3, 0.17, 0.09, edge_droop=0.7), shade)
    for s in (-1, 1):
        b = Vector((s * 0.06, -0.5, -0.04))
        mb.add(nh.tube([b, b + Vector((s * 0.01, -0.08, 0)), b + Vector((0, -0.14, 0))], [0.025, 0.022, 0.018], sides=6), CLAW)
        tip = b + Vector((0, -0.14, 0))
        mb.add(ec.spike(tip, tip + Vector((-s * 0.02, -0.06, 0.01)), r=0.012, sides=4), CLAW)
        mb.add(ec.spike(tip, tip + Vector((s * 0.015, -0.05, -0.01)), r=0.01, sides=4), CLAW)
    ck.legs_under(mb, -0.35, 0.3, 9, lambda t: 0.62, LEG, z=-0.04, reach=0.1, drop=0.07, r=0.013)
    return ec.centre(mb.to_object("Mollisonia", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Mollisonia")
