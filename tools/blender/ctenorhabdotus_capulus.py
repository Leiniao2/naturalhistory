"""
Procedural Ctenorhabdotus capulus (Burgess Shale comb jelly).

A translucent, bell- to egg-shaped comb jelly, mouth end down: twenty-four narrow rows
of comb plates (ctenes) run from the top pole down the body, shown as lines of small
iridescent rainbow-tinted plates; a small statocyst knob at the top pole and a wide oral
opening below. Glassy pale blue body. Float style: pivot at the body centre.

Output: Assets/Resources/Models/Species/Ctenorhabdotus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.62, 0.82, 0.90)
BODY_DEEP = (0.36, 0.58, 0.72)
MOUTH = (0.80, 0.46, 0.52)
RAINBOW = [(0.95, 0.40, 0.55), (0.98, 0.80, 0.35), (0.45, 0.95, 0.60), (0.40, 0.70, 1.00), (0.75, 0.45, 1.00)]


def build():
    mb = nh.MeshBuilder()
    R, H = 0.36, 0.5
    b = nh.uv_ellipsoid((0, 0, 0), (R, R, H), segments=24, rings=14)
    for v in b.verts:
        z = v.co.z / H
        k = 1.0 - 0.18 * max(0.0, -z) ** 2
        v.co.x *= k
        v.co.y *= k
        if z < -0.85:
            v.co.z = -H * 0.85
    mb.add(b, lambda co, n: nh.lerp(BODY_DEEP, BODY, nh.smoothstep(-0.4, 0.4, co.z)))
    mb.add(nh.uv_ellipsoid((0, 0, -H * 0.84), (0.16, 0.16, 0.02), segments=16, rings=4), MOUTH)
    mb.add(nh.ellipsoid((0, 0, H + 0.01), (0.04, 0.04, 0.03), subdivisions=2), (0.95, 0.95, 0.85))
    for k in range(24):
        a = k / 24 * math.tau
        for j in range(9):
            phi = math.radians(-60 + j * 14)
            x = math.cos(phi) * math.cos(a) * R * 1.01
            y = math.cos(phi) * math.sin(a) * R * 1.01
            z = math.sin(phi) * H * 1.0
            kk = 1.0 - 0.18 * max(0.0, -z / H) ** 2
            p = nh.ellipsoid((0, 0, 0), (0.012, 0.012, 0.022), subdivisions=1)
            nh.transform(p, Matrix.Rotation(a, 4, "Z"))
            nh.transform(p, Matrix.Translation((x * kk, y * kk, z)))
            mb.add(p, RAINBOW[(j + k) % len(RAINBOW)], smooth=False)
    return ec.centre(mb.to_object("Ctenorhabdotus", roughness=0.15))


if __name__ == "__main__":
    ec.export(build, "Ctenorhabdotus")
