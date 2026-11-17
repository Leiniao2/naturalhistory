"""
Procedural low-poly Sidneyia inexpectans (Burgess Shale artiopodan arthropod predator).

Broad, flattened body: a short semicircular head shield with a pair of stalked
eyes and short stout antennae, nine wide overlapping thoracic tergites with
backswept pointed pleural tips, a narrow three-segment abdomen without legs and
a broad tail fan (a rounded telson flanked by a pair of paddle-like uropods).
Robust walking legs with spiny bases (gnathobases for crushing shelly prey)
show beneath the thorax. Olive brown with darker segment edges.
Faces -Y, pivot at the body centre (Swim, a bottom-walking predator).

Output: Assets/Resources/Models/Species/Sidneyia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.52, 0.44, 0.28)
SHELL_DARK = (0.34, 0.27, 0.16)
SHELL_LIGHT = (0.66, 0.57, 0.38)
LEG = (0.62, 0.48, 0.32)
FAN = (0.58, 0.44, 0.26)
EYE = (0.06, 0.05, 0.04)


def build():
    mb = nh.MeshBuilder()
    # head shield
    mb.add(ec.plate(-0.52, 0.30, 0.14, 0.06), SHELL_LIGHT)
    # thorax: 9 tergites, widest in the middle
    for i in range(9):
        t = i / 8
        y = -0.40 + i * 0.085
        w = 0.33 + 0.05 * math.sin(math.pi * t) - 0.08 * t
        mb.add(ec.plate(y, w, 0.06, 0.07 - 0.015 * t, z=0.01),
               lambda co, n, w=w: nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(0.7, 1.0, abs(co.x) / w)))
        # pointed pleural tips
        for s in (-1, 1):
            p = Vector((s * w * 0.92, y, -0.01))
            mb.add(ec.spike(p - Vector((s * 0.04, 0, 0)), p + Vector((s * 0.03, 0.06, -0.01)), r=0.022, sides=4),
                   SHELL_DARK, smooth=False)
    # abdomen: three narrow, rounded rings
    for k in range(3):
        y = 0.38 + k * 0.08
        mb.add(nh.uv_ellipsoid((0, y, 0.0), (0.13 - 0.012 * k, 0.05, 0.05), segments=12, rings=6),
               SHELL if k % 2 == 0 else SHELL_DARK)
    # tail fan
    mb.add(ec.plate(0.70, 0.11, 0.13, 0.025), FAN)
    for s in (-1, 1):
        u = ec.paddle(0.26, 0.09, n=12, taper=0.5, thickness=0.015)
        nh.transform(u, Matrix.Rotation(math.radians(-60), 4, "Z"))
        ec.mirror(u, s)
        nh.transform(u, Matrix.Translation((s * 0.05, 0.6, 0.0)))
        mb.add(u, lambda co, n: nh.lerp(FAN, SHELL_DARK, nh.smoothstep(0.12, 0.24, abs(co.x))), smooth=False)
    # legs under the head and thorax
    for i in range(10):
        y = -0.52 + i * 0.085
        for s in (-1, 1):
            r = Vector((s * 0.1, y, -0.02))
            k = Vector((s * 0.26, y - 0.02, -0.04))
            f = Vector((s * 0.34, y + 0.03, -0.09))
            mb.add(ec.jointed_leg([r, k, f], 0.022, 0.008, sides=5), LEG)
    # eyes and antennae
    for s in (-1, 1):
        e0 = Vector((s * 0.08, -0.62, 0.03))
        mb.add(nh.tube([e0, e0 + Vector((s * 0.05, -0.04, 0.02))], [0.015, 0.012], sides=5), SHELL)
        mb.add(nh.ellipsoid(e0 + Vector((s * 0.06, -0.05, 0.025)), (0.022, 0.022, 0.02), subdivisions=1), EYE)
        a0 = Vector((s * 0.04, -0.64, 0.0))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.07, -0.1, 0.0)), a0 + Vector((s * 0.15, -0.16, -0.01))],
                       [0.014, 0.01, 0.0], sides=5), LEG)
    return ec.centre(mb.to_object("Sidneyia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Sidneyia")
