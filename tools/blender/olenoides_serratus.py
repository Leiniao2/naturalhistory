"""
Procedural low-poly Olenoides serratus (Burgess Shale corynexochid trilobite).

Oval trilobite: semicircular cephalon with a large, parallel-sided raised
glabella, crescent eyes and short genal spines; seven thoracic segments with a
raised axis and pleurae ending in backswept spines; a semicircular pygidium
fringed with five or six pairs of short marginal spines. Famous for its
preserved soft parts, so shown with a pair of long curved antennae in front,
a pair of tail cerci (antenna-like rear appendages) and leg tips peeking from
under the shield. Dark brown-grey with a lighter axis.
Faces -Y, pivot at the body centre (Swim, like Redlichia).

Output: Assets/Resources/Models/Species/Olenoides.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.40, 0.34, 0.30)
SHELL_LIGHT = (0.62, 0.54, 0.44)
AXIS = (0.56, 0.44, 0.34)
SPINE = (0.30, 0.24, 0.20)
LEG = (0.62, 0.46, 0.32)
EYE = (0.08, 0.07, 0.06)


def build():
    mb = nh.MeshBuilder()
    # cephalon
    mb.add(ec.plate(-0.34, 0.36, 0.2, 0.06, edge_droop=0.8),
           lambda co, n: nh.lerp(SHELL_LIGHT, SHELL, nh.smoothstep(0.1, 0.3, abs(co.x))))
    mb.add(nh.uv_ellipsoid((0, -0.36, 0.04), (0.08, 0.17, 0.05), segments=12, rings=7), AXIS)
    for s in (-1, 1):
        mb.add(ec.spike((s * 0.33, -0.25, -0.02), (s * 0.4, -0.06, -0.03), r=0.03, sides=5), SPINE)
        mb.add(nh.uv_ellipsoid((s * 0.17, -0.31, 0.04), (0.03, 0.06, 0.03), segments=8, rings=5), EYE)
    # thorax, 7 segments
    for i in range(7):
        y = -0.14 + i * 0.065
        w = 0.33 - 0.015 * i
        mb.add(ec.plate(y, w, 0.042, 0.05, edge_droop=0.8),
               lambda co, n, w=w: nh.lerp(SHELL_LIGHT, SHELL, nh.smoothstep(0.08, 0.2, abs(co.x))))
        mb.add(nh.uv_ellipsoid((0, y, 0.03), (0.075, 0.035, 0.04), segments=10, rings=5), AXIS)
        for s in (-1, 1):
            mb.add(ec.spike((s * (w - 0.03), y, -0.02), (s * (w + 0.06), y + 0.08, -0.03), r=0.02, sides=4),
                   SPINE, smooth=False)
    # pygidium
    py = 0.42
    mb.add(ec.plate(py, 0.22, 0.11, 0.045, edge_droop=0.8), SHELL)
    mb.add(nh.uv_ellipsoid((0, py - 0.02, 0.025), (0.06, 0.09, 0.035), segments=10, rings=5), AXIS)
    for k in range(6):
        a = math.radians(15 + 13 * k)
        for s in (-1, 1):
            base = Vector((s * 0.2 * math.cos(a), py + 0.1 * math.sin(a), -0.01))
            tip = base + Vector((s * 0.035 * math.cos(a), 0.07, -0.01))
            mb.add(ec.spike(base, tip, r=0.015, sides=4), SPINE, smooth=False)
    # antennae, cerci, legs
    for s in (-1, 1):
        a0 = Vector((s * 0.06, -0.52, -0.02))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.08, -0.2, 0)), a0 + Vector((s * 0.22, -0.36, 0)),
                        a0 + Vector((s * 0.4, -0.42, -0.01))], [0.014, 0.011, 0.007, 0.0], sides=4), LEG)
        c0 = Vector((s * 0.03, 0.52, -0.02))
        mb.add(nh.tube([c0, c0 + Vector((s * 0.06, 0.15, 0)), c0 + Vector((s * 0.15, 0.28, 0))],
                       [0.01, 0.007, 0.0], sides=4), LEG)
        for i in range(8):
            y = -0.25 + i * 0.075
            r = Vector((s * 0.2, y, -0.03))
            mb.add(ec.jointed_leg([r, r + Vector((s * 0.14, 0.0, -0.03)), r + Vector((s * 0.2, 0.03, -0.08))],
                                  0.014, 0.006, sides=4), LEG)
    return ec.centre(mb.to_object("Olenoides", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Olenoides")
