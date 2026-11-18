"""
Procedural Halkieria evangelista (early Cambrian, Sirius Passet, Greenland, ~8 cm).

An elongate, slug-like animal with a flat sole, its whole back armoured with a coat of mail of
small, overlapping, leaf-shaped sclerites set in rows (bigger, upturned blade-like ones along
the flanks), and a rounded, growth-ringed shell plate at each end of the back, the front one
smaller. Bronze-grey sclerites, paler shells with darker growth rings, pale sole.
Swim style (a slow seafloor crawler): pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/halkieria_evangelista.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Halkieria.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.40, 0.34, 0.26)
SOLE = (0.80, 0.70, 0.58)
SCL = (0.56, 0.50, 0.40)
SCL_EDGE = (0.78, 0.72, 0.58)
FLANK = (0.48, 0.40, 0.28)
SHELL = (0.86, 0.78, 0.62)
RING = (0.56, 0.46, 0.32)
L, W, H = 0.6, 0.16, 0.1


def surf(u, v):
    a = v * math.pi / 2
    f = math.sqrt(max(0.0, 1 - u ** 4))
    return Vector((math.sin(a) * W * f, u * L, math.cos(a) * H * f)), a


def build():
    mb = nh.MeshBuilder()
    body = nh.uv_ellipsoid((0, 0, 0), (W, L, H), segments=18, rings=12, deform=lambda n: 1.0)
    for v in body.verts:
        if v.co.z < 0:
            v.co.z *= 0.25
        u = v.co.y / L
        f = math.sqrt(max(0.0, 1 - u ** 4)) / max(math.sqrt(max(0.0, 1 - u * u)), 1e-3)
        v.co.x *= min(f, 1.5)
    mb.add(body, lambda co, n: nh.lerp(SOLE, BODY, nh.smoothstep(-0.5, 0.2, n.z)))
    for i in range(22):
        u = -0.86 + 1.72 * i / 21
        if abs(u + 0.72) < 0.14 or abs(u - 0.66) < 0.2:
            cols = [-0.95, -0.8, 0.8, 0.95]
        else:
            cols = [-0.95 + 1.9 * j / 7 for j in range(8)]
        for v in cols:
            p, a = surf(u, v)
            flank = abs(v) > 0.85
            sc = nh.uv_ellipsoid((0, 0, 0), (0.022, 0.045 if not flank else 0.06, 0.006), segments=8, rings=4)
            nh.transform(sc, Matrix.Rotation(math.radians(-25 if not flank else -50), 4, "X"))
            nh.transform(sc, Matrix.Rotation(a * (1.0 if not flank else 1.25), 4, "Y"))
            nh.transform(sc, Matrix.Translation(p + Vector((0, 0, 0.004))))
            mb.add(sc, (lambda c: lambda co, n: c)(FLANK if flank else nh.lerp(SCL, SCL_EDGE, (i % 2) * 0.35)))

    def shell(y, rx, ry, h):
        sh = nh.uv_ellipsoid((0, 0, 0), (rx, ry, h), segments=18, rings=8)
        for v in sh.verts:
            if v.co.z < 0:
                v.co.z *= 0.2
        nh.transform(sh, Matrix.Translation((0, y, H * 0.82)))

        def col(co, n, y=y):
            rr = math.hypot(co.x / rx, (co.y - y) / ry)
            return nh.lerp(SHELL, RING, nh.smoothstep(0.6, 1.0, math.sin(rr * 14) * 0.5 + 0.5) * 0.7)
        mb.add(sh, col)
    shell(-0.47, 0.1, 0.1, 0.05)
    shell(0.42, 0.12, 0.15, 0.06)
    return ec.centre(mb.to_object("Halkieria", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Halkieria")
