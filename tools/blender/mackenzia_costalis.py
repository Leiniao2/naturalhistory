"""
Procedural Mackenzia costalis (Burgess Shale anemone-like cnidarian, up to ~15 cm).

An upright, elongate, soft sac with a rounded top and a slightly flared base attached to
a shell fragment on the seabed; long longitudinal ribs (the "costae") run down its body.
At the top, a ring of short, stubby tentacles round the mouth. Translucent olive-ochre
with darker ribs, pale tentacles. Fixed: pivot on the seabed.

Output: Assets/Resources/Models/Species/Mackenzia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.76, 0.66, 0.40)
RIB = (0.48, 0.40, 0.22)
TENT = (0.92, 0.84, 0.66)
SHELL = (0.62, 0.58, 0.52)


def build():
    mb = nh.MeshBuilder()
    H = 1.1
    n = 10
    pts = [(0.02 * math.sin(i * 0.6), 0, H * i / n) for i in range(n + 1)]
    radii = [0.17 + 0.03 * math.sin(math.pi * i / n) for i in range(n + 1)]
    radii[0] = 0.2
    radii[-1] = 0.12
    t = nh.tube(pts, radii, sides=24)
    for v in t.verts:
        a = math.atan2(v.co.y, v.co.x)
        r = math.hypot(v.co.x, v.co.y)
        if r > 1e-4:
            k = 1 + 0.06 * max(0.0, math.cos(12 * a))
            v.co.x *= k
            v.co.y *= k
    def col(co, nrm):
        a = math.atan2(co.y, co.x)
        return nh.lerp(BODY, RIB, nh.smoothstep(0.6, 0.95, math.cos(12 * a)))
    mb.add(t, col)
    top = nh.uv_ellipsoid((0.0, 0, H), (0.12, 0.12, 0.07), segments=24, rings=8)
    mb.add(top, BODY)
    kit.crown(mb, (0, 0, H + 0.04), 0.09, 14, 0.12, 0.022, TENT, spread=40, droop=-0.2)
    sh = nh.uv_ellipsoid((0, 0, 0), (0.32, 0.26, 0.06), segments=16, rings=6)
    nh.transform(sh, Matrix.Translation((0.04, 0, 0.0)))
    mb.add(sh, SHELL)
    return ec.ground(mb.to_object("Mackenzia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Mackenzia", fixed=True)
