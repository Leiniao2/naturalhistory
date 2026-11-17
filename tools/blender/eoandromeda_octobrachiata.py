"""
Procedural low-poly Eoandromeda octobrachiata (Ediacaran octoradial, China and South Australia).

A low, round, umbrella-shaped body with a small domed polar knob at the top
and eight raised arms that spiral out from it in the same direction to the
margin, each arm crossed by fine ridges (like comb rows); a thin skirt between
the arms flares to the edge. Translucent bluish cream with rusty-orange arms.
Pivot on the seabed (Fixed; probably lived on the seafloor).

Output: Assets/Resources/Models/Species/Eoandromeda.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

SKIRT = (0.82, 0.84, 0.80)
SKIRT_EDGE = (0.64, 0.68, 0.66)
ARM = (0.82, 0.48, 0.26)
RIDGE = (0.56, 0.28, 0.14)
KNOB = (0.88, 0.66, 0.44)

R = 0.5
DOME = 0.16


def dome_z(r):
    return DOME * max(0.0, 1 - (r / R) ** 2) ** 0.8


def build():
    mb = nh.MeshBuilder()
    skirt = nh.uv_ellipsoid((0, 0, 0), (R, R, DOME), segments=48, rings=12,
                            deform=lambda n: 1.0 + 0.04 * math.cos(math.atan2(n.y, n.x) * 8) * (1 - abs(n.z)))
    for v in skirt.verts:
        if v.co.z < 0:
            v.co.z = 0.0
    mb.add(skirt, lambda co, n: nh.lerp(SKIRT, SKIRT_EDGE, nh.smoothstep(0.3, 0.5, math.hypot(co.x, co.y))))
    mb.add(nh.ellipsoid((0, 0, DOME), (0.07, 0.07, 0.05), subdivisions=2), KNOB)
    for k in range(8):
        a0 = k / 8 * math.tau
        pts, radii = [], []
        n = 14
        for i in range(n + 1):
            t = i / n
            r = 0.05 + (R - 0.07) * t
            a = a0 + 1.6 * t  # spiral
            pts.append(Vector((r * math.cos(a), r * math.sin(a), dome_z(r) + 0.012)))
            radii.append(0.035 * (0.6 + 0.6 * t) * (1 - 0.6 * t ** 4))
        radii[-1] = 0.0

        def col(co, nrm, pts=pts):
            j = min(range(len(pts)), key=lambda i: (pts[i] - co).length_squared)
            d = (co - pts[j]).length
            rr = math.hypot(co.x, co.y)
            ridge = 0.5 + 0.5 * math.cos(rr * math.tau / 0.035)
            return nh.lerp(ARM, RIDGE, 0.6 * nh.smoothstep(0.6, 1.0, ridge))

        mb.add(nh.tube(pts, radii, sides=6, scale_xy=(1.0, 0.5)), col)
    return ec.ground(mb.to_object("Eoandromeda", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Eoandromeda", fixed=True, views=((35, 35), (0, 80)))
