"""
Procedural low-poly Leanchoilia superlata (Burgess Shale "great-appendage" arthropod).

A slim, arched body: a short head shield with a downturned snout, eleven
tergites whose pleurae curve down into pointed tips, and a lanceolate telson
fringed with small spines; flap-like swimming exopods along the sides. Its
signature great appendages: a pair of stout jointed arms folded forward from
under the head, each branching into three long, whip-like flagella that sweep
forward and back. Reddish tan with darker tergite margins.
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Leanchoilia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.74, 0.46, 0.30)
SHELL_DARK = (0.46, 0.24, 0.14)
FLAP = (0.84, 0.60, 0.44)
APP = (0.68, 0.38, 0.24)
WHIP = (0.88, 0.70, 0.52)
EYE = (0.06, 0.04, 0.04)


def arch(y):
    return 0.04 * math.cos(y * 2.2)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.plate(-0.42, 0.14, 0.11, 0.07, z=arch(-0.42)), SHELL)
    # snout
    mb.add(nh.tube([(0, -0.5, arch(-0.5)), (0, -0.58, arch(-0.5) - 0.03), (0, -0.62, arch(-0.5) - 0.07)],
                   [0.04, 0.025, 0.0], sides=6), SHELL)
    n = 11
    for i in range(n):
        t = i / (n - 1)
        y = -0.32 + i * 0.07
        w = 0.15 - 0.06 * t ** 1.5
        mb.add(ec.plate(y, w, 0.05, 0.065, z=arch(y), edge_droop=1.4),
               lambda co, nn, w=w: nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(0.6, 1.0, abs(co.x) / w)))
        for s in (-1, 1):
            p = Vector((s * w * 0.9, y, arch(y) - 0.06))
            mb.add(ec.spike(p + Vector((-s * 0.02, -0.01, 0.03)), p + Vector((s * 0.015, 0.03, -0.035)),
                            r=0.016, sides=4), SHELL_DARK, smooth=False)
            f = ec.paddle(0.12 - 0.04 * t, 0.025, n=8, thickness=0.005)
            nh.transform(f, Matrix.Rotation(math.radians(-25), 4, "Y") @ Matrix.Rotation(math.radians(-15), 4, "Z"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * w * 0.6, y, arch(y) - 0.05)))
            mb.add(f, FLAP, smooth=False)
    # telson
    ty = 0.45
    tel = nh.flat_panel([(0, ty - 0.02, 0), (0.045, ty + 0.06, 0), (0.0, ty + 0.25, 0), (-0.045, ty + 0.06, 0)],
                        thickness=0.02)
    nh.transform(tel, Matrix.Translation((0, 0, arch(ty))))
    mb.add(tel, SHELL_DARK, smooth=False)
    # great appendages: peduncle forward, then three flagella
    for s in (-1, 1):
        b = Vector((s * 0.05, -0.46, arch(-0.46) - 0.05))
        k = b + Vector((s * 0.1, -0.1, 0.01))
        h = k + Vector((s * 0.02, -0.12, 0.04))
        mb.add(nh.tube([b, k, h], [0.03, 0.024, 0.018], sides=6), APP)
        for j in range(3):
            ang = math.radians(-40 + 45 * j) * s
            d = Vector((math.sin(ang), -math.cos(ang), 0.0))
            pts = [h]
            for q in range(1, 6):
                u = q / 5
                pts.append(h + d * 0.55 * u + Vector((s * 0.12 * u * u, 0.25 * u * u * (j - 0.5), 0.05 * math.sin(u * 3))))
            mb.add(nh.tube(pts, [0.012, 0.009, 0.007, 0.005, 0.003, 0.0], sides=4), WHIP)
        mb.add(nh.ellipsoid((s * 0.06, -0.5, arch(-0.5) + 0.0), (0.018, 0.018, 0.016), subdivisions=1), EYE)
    return ec.centre(mb.to_object("Leanchoilia", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Leanchoilia")
