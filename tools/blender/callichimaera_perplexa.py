"""
Procedural Callichimaera perplexa (mid-Cretaceous raninoidan crab, Colombia), the
"platypus of crabs", for map colonies (Swim style).

A quarter-sized (about 3 cm) swimming crab with a larva-like mix of features: a long,
narrow, slightly flattened carapace, a pair of huge, bulging compound eyes with no
sockets to shelter them, small claws, flat oar-like paddle legs held out to the sides for
swimming, two small rear leg pairs, and an exposed, segmented abdomen stretched out behind
instead of tucked under. Orange-red shell with a paler underside, dark eyes (colours
conjectural).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/callichimaera_perplexa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Callichimaera.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

SHELL = (0.80, 0.36, 0.18)
SHELL_DARK = (0.55, 0.20, 0.10)
UNDER = (0.95, 0.78, 0.62)
LEG = (0.86, 0.48, 0.26)
EYE = (0.06, 0.05, 0.06)
EYE_SHEEN = (0.35, 0.32, 0.38)


def shell_col(co, n):
    c = nh.lerp(UNDER, SHELL, nh.smoothstep(-0.4, 0.3, n.z))
    return cc.mottle(nh.lerp(c, SHELL_DARK, 0.3 * nh.smoothstep(0.7, 1.0, n.z)), co, 0.12, 20.0)


def build():
    parts = []
    # carapace: long, narrow, a little flattened; front at -Y
    rows = [(0.30, 0.0, 0.0, 0.0), (0.27, 0.0, 0.08, 0.04), (0.18, 0.0, 0.13, 0.06), (0.0, 0.0, 0.15, 0.07),
            (-0.18, 0.0, 0.13, 0.065), (-0.30, 0.0, 0.10, 0.05), (-0.36, 0.0, 0.07, 0.035), (-0.38, 0.0, 0.0, 0.0)]
    parts.append(cc.axis(rows, sides=20, power=2.4))
    # exposed abdomen (pleon): segments trailing behind
    for k in range(6):
        y = 0.30 + 0.075 * k
        w = 0.08 - 0.008 * k
        parts.append(nh.ellipsoid((0, y, -0.01 - 0.004 * k), (w, 0.045, 0.025), subdivisions=2))
    body = cc.fuse([(p, SHELL) for p in parts], voxel=0.008, smooth=3, max_tris=5000)
    mb = nh.MeshBuilder()
    mb.add(body, shell_col)
    # telson
    mb.add(cc.membrane([(-0.04, 0.73, -0.03), (0.04, 0.73, -0.03)], [(-0.05, 0.80, -0.035), (0.05, 0.80, -0.035)],
                       nv=3, thickness=0.01), LEG)
    for sx in (1, -1):
        # the huge unprotected compound eyes
        c = Vector((sx * 0.08, -0.40, 0.03))
        mb.add(nh.tube([(sx * 0.04, -0.34, 0.02), c], [0.03, 0.035], sides=8), LEG)
        mb.add(nh.ellipsoid(tuple(c + Vector((sx * 0.02, -0.03, 0.01))), (0.062, 0.062, 0.058), subdivisions=3),
               lambda co, n: nh.lerp(EYE, EYE_SHEEN, max(0.0, n.dot(Vector((-0.4, -0.5, 0.75)).normalized())) ** 3))
        # antennae
        mb.add(nh.tube([(sx * 0.02, -0.38, -0.01), (sx * 0.05, -0.50, 0.0), (sx * 0.10, -0.62, 0.02)],
                       [0.008, 0.005, 0.0], sides=5), LEG)
        # small claws (chelipeds)
        sh = Vector((sx * 0.12, -0.22, -0.03))
        el = sh + Vector((sx * 0.08, -0.06, -0.01))
        wr = el + Vector((-sx * 0.02, -0.10, 0.0))
        mb.add(nh.tube([sh, el, wr], [0.022, 0.02, 0.022], sides=8), LEG)
        mb.add(nh.ellipsoid(tuple(wr + Vector((0, -0.035, 0))), (0.028, 0.045, 0.022), subdivisions=2), LEG)
        for d in (-0.012, 0.012):
            mb.add(cc.cone(wr + Vector((sx * d, -0.07, 0)), wr + Vector((sx * d * 0.6, -0.12, 0)), 0.009, sides=4), SHELL_DARK)
        # flat oar-like swimming legs (two big pairs) and two small rear pairs
        for k, (y, L, w) in enumerate(((-0.10, 0.36, 0.09), (0.04, 0.38, 0.10), (0.16, 0.16, 0.02), (0.24, 0.13, 0.018))):
            base = Vector((sx * 0.13, y, -0.03))
            knee = base + Vector((sx * L * 0.45, 0.02 + 0.05 * k, -0.03))
            tip = base + Vector((sx * L, 0.06 + 0.06 * k, -0.04))
            mb.add(nh.tube([base, knee], [0.018, 0.015], sides=7), LEG)
            if w > 0.03:
                mb.add(cc.membrane([knee - Vector((0, w * 0.4, 0)), tip - Vector((0, w * 0.5, 0))],
                                   [knee + Vector((0, w * 0.4, 0)), tip + Vector((0, w * 0.3, 0))],
                                   nv=3, thickness=0.012), LEG)
            else:
                mb.add(nh.tube([knee, tip], [0.013, 0.0], sides=6), LEG)
    obj = mb.to_object("Callichimaera", roughness=0.5)
    cc.centre(obj)
    cc.bounds_report(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Callichimaera", background=(0.05, 0.16, 0.22), views=((35, 25), (0, 80), (-90, 8)), size=640)
