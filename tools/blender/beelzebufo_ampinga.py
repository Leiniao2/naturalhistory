"""
Procedural Beelzebufo ampinga (latest Cretaceous giant frog, Madagascar).

The 'devil frog': a squat, enormous frog about 40 cm long, as wide as it is long, with a
huge head taking up nearly half the body, a cavernous wide mouth, a rough bony shield over
the skull with short horn-like ridges above the eyes, stout arms and powerful folded hind
legs. Coloured like its horned-frog relatives: olive green with chocolate-brown blotches
edged in yellow, a cream throat and belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/beelzebufo_ampinga.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Beelzebufo.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix  # noqa: E402
import math  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

OLIVE = (0.40, 0.44, 0.20)
BLOTCH = (0.26, 0.16, 0.08)
EDGE = (0.78, 0.66, 0.22)
BELLY = (0.88, 0.84, 0.66)
LIP = (0.20, 0.14, 0.08)
SHIELD = (0.46, 0.40, 0.24)


def paint(co, n):
    c = cc.countershade(n, BELLY, OLIVE, OLIVE, lo=-0.6, mid=-0.25, hi=0.6)
    top = nh.smoothstep(-0.2, 0.3, n.z)
    sp = cc.spots(co, 9.0, 0.30)
    ring = cc.spots(co, 9.0, 0.42) - sp
    c = nh.lerp(c, EDGE, 0.8 * max(0.0, ring) * top)
    c = nh.lerp(c, BLOTCH, 0.9 * sp * top)
    # dark lip line along the mouth
    if -0.26 < co.y < -0.02 and abs(co.z - mouth_z(co.y)) < 0.006 and n.z < 0.6:
        c = LIP
    return cc.mottle(c, co, 0.08)


def mouth_z(y):
    return 0.115 + 0.02 * (y + 0.26) / 0.24


def parts():
    p = []
    torso = nh.uv_ellipsoid((0, 0.03, 0.10), (0.17, 0.17, 0.095), 28, 18,
                            deform=lambda v: 1.0 + 0.08 * max(0.0, v.y))
    p.append(torso)
    p.append(nh.uv_ellipsoid((0, 0.13, 0.085), (0.13, 0.08, 0.07), 20, 12))              # rump
    # huge broad head with a wide, flat, rounded snout
    p.append(nh.uv_ellipsoid((0, -0.13, 0.135), (0.17, 0.12, 0.06), 28, 16,
                             deform=lambda v: 1.0 - 0.08 * max(0.0, v.z) ** 2))
    p.append(nh.uv_ellipsoid((0, -0.12, 0.085), (0.16, 0.12, 0.05), 24, 12))            # deep lower jaw / throat
    for sx in (1, -1):
        p.append(nh.ellipsoid((sx * 0.085, -0.12, 0.185), (0.035, 0.035, 0.03), subdivisions=3))   # eye bulge
        # bony brow ridges, raised into short horns
        p.append(nh.tube([(sx * 0.05, -0.16, 0.19), (sx * 0.085, -0.115, 0.215), (sx * 0.11, -0.08, 0.20)],
                         [0.012, 0.016, 0.01], sides=8))
        # stout front legs
        p.append(nh.tube([(sx * 0.11, -0.06, 0.08), (sx * 0.15, -0.10, 0.05), (sx * 0.14, -0.13, 0.02),
                          (sx * 0.135, -0.145, 0.008)], [0.045, 0.036, 0.028, 0.024], sides=12))
        p.append(nh.uv_ellipsoid((sx * 0.14, -0.165, 0.008), (0.03, 0.028, 0.01), 12, 8))
        # hind legs folded at the sides
        p.append(nh.tube([(sx * 0.09, 0.15, 0.08), (sx * 0.19, 0.09, 0.07), (sx * 0.23, 0.03, 0.055)],
                         [0.055, 0.05, 0.036], sides=12))
        p.append(nh.tube([(sx * 0.23, 0.03, 0.055), (sx * 0.21, 0.12, 0.035), (sx * 0.16, 0.20, 0.022)],
                         [0.036, 0.032, 0.022], sides=12))
        p.append(nh.tube([(sx * 0.16, 0.20, 0.018), (sx * 0.22, 0.16, 0.01), (sx * 0.27, 0.10, 0.008)],
                         [0.022, 0.02, 0.013], sides=10, scale_xy=(1.0, 0.6)))
    return p


def build():
    body = cc.fuse(parts(), voxel=0.008, smooth=5, max_tris=11000, disp=cc.scales_disp(0.0025, 35.0))
    mb = nh.MeshBuilder()
    mb.add(body, paint)
    # skull shield: a rough, slightly paler plate over the top of the head
    mb.add(nh.uv_ellipsoid((0, -0.10, 0.185), (0.075, 0.07, 0.012), 16, 8), SHIELD)
    for sx in (1, -1):
        cc.eye  # noqa: B018 (eyes added below, both sides at once)
        # fingers and toes
        for k, a in enumerate((-0.5, 0.0, 0.5)):
            d = Matrix.Rotation(a * sx, 3, "Z") @ Vector((0, -1, 0))
            base = Vector((sx * 0.14, -0.17, 0.008))
            mb.add(nh.tube([base, base + d * 0.04], [0.008, 0.005], sides=6), OLIVE)
        for k, a in enumerate((-0.7, -0.3, 0.1, 0.5)):
            d = Matrix.Rotation(a * sx, 3, "Z") @ Vector((sx * 0.6, -0.8, 0)).normalized()
            base = Vector((sx * 0.27, 0.10, 0.008))
            mb.add(nh.tube([base, base + d * 0.06], [0.008, 0.004], sides=6), OLIVE)
    cc.eye(mb, (0.10, -0.125, 0.195), 0.022, iris=(0.80, 0.62, 0.18))
    obj = mb.to_object("Beelzebufo", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Beelzebufo", ground=(0.36, 0.40, 0.22), views=((35, 25), (-90, 8), (160, 55)), size=640)
