"""
Procedural Bojophlebia prokopi (Late Carboniferous of the Czech Republic, a giant mayfly-like
palaeopteran insect with a wingspan of about 45 cm) for map colonies (Soar style).

In level flight with both pairs of wings held straight out (it could not fold them back):
broad forewings and nearly as large, rounded hindwings, smoky brown with many dark
longitudinal veins, fine crossveins and a few dark spots; a slender dark body with a small
head, big eyes and short antennae (no beak, unlike the palaeodictyopterans), a stout thorax
with the legs tucked under, a long ringed abdomen and three long, thin tail filaments in
the mayfly manner. Wing helpers from nh_car_palaeodicty. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/bojophlebia_prokopi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Bojophlebia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_palaeodicty as pd  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "Bojophlebia"
BODY = (0.16, 0.12, 0.09)
BODY_MARK = (0.42, 0.30, 0.18)
EYE = (0.05, 0.05, 0.06)
WING = (0.62, 0.52, 0.40)
WING_ROOT = (0.36, 0.26, 0.17)
VEIN = (0.20, 0.14, 0.09)
SPOT = (0.24, 0.17, 0.11)

R = 0.04
NU, NV = 30, 15
L = 0.62
Y_HEAD = -0.30


def wing_col(hind):
    def c(u, v):
        col = nh.lerp(WING_ROOT, WING, nh.smoothstep(0.0, 0.25, u))
        # longitudinal veins
        j, i = round(v * NV), round(u * NU)
        if j % 3 == 0 or v < 0.08:
            col = nh.lerp(col, VEIN, 0.75)
        # cross-veins
        elif i % 5 == 0:
            col = nh.lerp(col, VEIN, 0.4)
        # dark spots / clouds
        for (su, sv) in ((0.55, 0.35), (0.8, 0.6), (0.35, 0.7)):
            m = math.exp(-(((u - su) / 0.08) ** 2 + ((v - sv) / 0.18) ** 2))
            col = nh.lerp(col, SPOT, 0.7 * m)
        return col
    return c


def build():
    mb = nh.MeshBuilder()
    body = nh.MeshBuilder()
    body.add(nh.ellipsoid((0, Y_HEAD, 0.0), (R * 1.05, R * 0.9, R * 0.9), 2), BODY)
    body.add(nh.uv_ellipsoid((0, Y_HEAD + L * 0.2, 0.0), (R * 1.25, L * 0.17, R * 1.25), 14, 10), BODY)
    n = 10
    for i in range(n):
        t = i / (n - 1)
        y = Y_HEAD + L * 0.36 + t * L * 0.66
        r = R * (0.85 - 0.4 * t)
        body.add(nh.ellipsoid((0, y, 0.01 * t), (r, L * 0.058, r * 0.9), 2), BODY_MARK if i % 2 else BODY)
    mb.add(body.fuse(voxel=R * 0.22, smooth=3, max_tris=2500))
    y_end = Y_HEAD + L * 1.02 + L * 0.04
    for sx in (-1, 1):
        # big compound eyes
        mb.add(nh.ellipsoid((sx * R * 0.85, Y_HEAD - R * 0.15, R * 0.35), (R * 0.55,) * 3, 2), EYE)
        # short antennae
        mb.add(nh.tube([(sx * R * 0.3, Y_HEAD - R * 0.8, R * 0.4), (sx * R * 0.9, Y_HEAD - R * 2.2, R * 0.9)],
                       [R * 0.1, R * 0.04], sides=4), BODY)
        # legs tucked under the thorax
        for k in range(3):
            y = Y_HEAD + L * (0.1 + 0.08 * k)
            mb.add(nh.tube([(sx * R * 0.8, y, -R * 0.6), (sx * R * 2.0, y + 0.02 * (k - 1), -R * 1.3),
                            (sx * R * 1.8, y + 0.07, -R * 2.0)], [R * 0.18, R * 0.14, R * 0.06], sides=4), BODY)
    # three long tail filaments
    for sx in (-1, 0, 1):
        p0 = Vector((0, y_end - 0.02, 0.01))
        pts = [p0, p0 + Vector((sx * 0.03, 0.18, 0.015)), p0 + Vector((sx * 0.07, 0.38, 0.03)),
               p0 + Vector((sx * 0.11, 0.56, 0.04))]
        mb.add(nh.tube(pts, [R * 0.16, R * 0.12, R * 0.08, 0.0], sides=4), BODY)

    x0 = R * 0.9
    span = 1.0
    for sx in (-1, 1):
        for root_y, chord, sweep, sp, hind in ((Y_HEAD + L * 0.10, 0.22, -4, span, False),
                                               (Y_HEAD + L * 0.27, 0.24, 8, span * 0.86, True)):
            w = pd.wing_grid((x0, root_y, R * 0.4), sp - x0, chord, sweep, wing_col(hind), nu=NU, nv=NV,
                             th=0.006, lead_curve=0.10 if not hind else 0.0)
            mb.add(pd.mirror(w) if sx < 0 else w, smooth=False)

    obj = mb.to_object(NAME, roughness=0.5)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
