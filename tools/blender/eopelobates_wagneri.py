"""
Procedural Eopelobates wagneri (middle Eocene, ~47 Ma, the Messel lake, Germany) for map
colonies.

An extinct spadefoot toad (Pelobatidae), about 6-8 cm long: a squat, rounded toad-like
body with smooth skin, a short blunt head, big bulging eyes with vertical, cat-like
pupils, short arms and strong hind legs folded at the sides. Its living relatives dig
backwards into soil with a horny spade on each hind foot. Colour (unknown, after living
spadefoots): olive-brown with darker brown blotches, a cream belly and golden eyes.
Faces -Y, pivot on the ground (Ground, Hop).

Usage:
  blender --background --python tools/blender/eopelobates_wagneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EopelobatesWagneri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

OLIVE = (0.46, 0.42, 0.24)
BACK = (0.38, 0.33, 0.18)
BLOTCH = (0.24, 0.17, 0.09)
BELLY = (0.88, 0.84, 0.68)
SPADE = (0.15, 0.12, 0.08)
IRIS = (0.85, 0.66, 0.22)
PUPIL = (0.02, 0.02, 0.02)


def paint(co, n):
    c = cc.countershade(n, BELLY, OLIVE, BACK, lo=-0.6, mid=-0.2, hi=0.7)
    top = nh.smoothstep(-0.1, 0.3, n.z)
    c = nh.lerp(c, BLOTCH, 0.85 * cc.spots(co, 11.0, 0.28) * top)
    return cc.mottle(c, co, 0.06)


def parts():
    p = []
    p.append(nh.uv_ellipsoid((0, 0.03, 0.10), (0.15, 0.17, 0.10), 28, 18,
                             deform=lambda v: 1.0 + 0.06 * max(0.0, v.y)))            # round body
    p.append(nh.uv_ellipsoid((0, 0.13, 0.08), (0.12, 0.08, 0.07), 20, 12))              # rump
    p.append(nh.uv_ellipsoid((0, -0.11, 0.12), (0.12, 0.09, 0.065), 24, 14))            # short blunt head
    p.append(nh.uv_ellipsoid((0, -0.10, 0.08), (0.11, 0.09, 0.045), 20, 12))            # throat
    for sx in (1, -1):
        p.append(nh.ellipsoid((sx * 0.07, -0.12, 0.175), (0.042, 0.045, 0.038), subdivisions=3))  # eye bulge
        p.append(nh.tube([(sx * 0.09, -0.06, 0.07), (sx * 0.13, -0.10, 0.04), (sx * 0.12, -0.13, 0.015),
                          (sx * 0.12, -0.14, 0.006)], [0.03, 0.025, 0.02, 0.017], sides=12))
        p.append(nh.uv_ellipsoid((sx * 0.12, -0.155, 0.006), (0.022, 0.02, 0.008), 12, 8))
        p.append(nh.tube([(sx * 0.08, 0.15, 0.08), (sx * 0.17, 0.09, 0.07), (sx * 0.20, 0.03, 0.05)],
                         [0.05, 0.045, 0.03], sides=12))
        p.append(nh.tube([(sx * 0.20, 0.03, 0.05), (sx * 0.18, 0.12, 0.03), (sx * 0.13, 0.19, 0.02)],
                         [0.03, 0.027, 0.02], sides=12))
        p.append(nh.tube([(sx * 0.13, 0.19, 0.016), (sx * 0.19, 0.15, 0.009), (sx * 0.24, 0.09, 0.007)],
                         [0.02, 0.018, 0.012], sides=10, scale_xy=(1.0, 0.6)))
    return p


def build():
    body = cc.fuse(parts(), voxel=0.007, smooth=5, max_tris=9000, disp=cc.scales_disp(0.0008, 30.0))
    mb = nh.MeshBuilder()
    mb.add(body, paint)
    for sx in (1, -1):
        for a in (-0.5, 0.0, 0.5):
            d = Matrix.Rotation(a * sx, 3, "Z") @ Vector((0, -1, 0))
            base = Vector((sx * 0.12, -0.16, 0.007))
            mb.add(nh.tube([base, base + d * 0.035], [0.007, 0.004], sides=6), OLIVE)
        for a in (-0.7, -0.3, 0.1, 0.5):
            d = Matrix.Rotation(a * sx, 3, "Z") @ Vector((sx * 0.6, -0.8, 0)).normalized()
            base = Vector((sx * 0.24, 0.09, 0.007))
            mb.add(nh.tube([base, base + d * 0.05], [0.007, 0.004], sides=6), OLIVE)
        # the dark horny spade on the inner side of each hind foot
        mb.add(nh.ellipsoid((sx * 0.215, 0.13, 0.008), (0.014, 0.022, 0.007), subdivisions=2), SPADE)
        # big bulging golden eye with a vertical slit pupil
        e = Vector((sx * 0.085, -0.13, 0.19))
        mb.add(nh.ellipsoid(tuple(e), (0.03, 0.032, 0.028), subdivisions=3), IRIS)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * 0.026, -0.008, 0.002))), (0.006, 0.006, 0.02), subdivisions=2), PUPIL)
    obj = mb.to_object("EopelobatesWagneri", roughness=0.4)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "EopelobatesWagneri", ground=(0.36, 0.40, 0.22), views=((35, 25), (-90, 8), (160, 55)), size=640)
