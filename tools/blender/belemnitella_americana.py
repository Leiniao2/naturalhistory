"""
Procedural Belemnitella americana (Late Cretaceous belemnite, Atlantic coastal plain, USA).

A squid-like belemnite about 30 cm long: a long, slender, muscular mantle ending in a
pointed rear where the bullet-shaped calcite guard lay inside, a pair of rounded rhombic
fins near the rear, a short head with large eyes, and ten slender arms of about equal
length armed with rows of small hooks. Reddish-brown chromatophore speckles over a pale
rosy body, darker along the back (colours conjectural, like living squid).
Swim style: arms forward (-Y), back up, pivot at the body centre.

Usage:
  blender --background --python tools/blender/belemnitella_americana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Belemnitella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

PALE = (0.90, 0.76, 0.70)
BACK = (0.55, 0.24, 0.16)
SPECK = (0.40, 0.14, 0.09)
FIN = (0.80, 0.52, 0.44)
ARM = (0.82, 0.58, 0.50)
HOOK = (0.15, 0.10, 0.08)


def body_paint(co, n):
    c = nh.lerp(PALE, BACK, nh.smoothstep(-0.2, 0.8, n.z))
    s = nh.smoothstep(0.25, 0.45, noise.noise(Vector(co) * 40.0))
    return nh.lerp(c, SPECK, 0.6 * s * nh.smoothstep(-0.4, 0.4, n.z))


def build():
    # mantle: pointed guard tip at +Y, open collar at the head end
    rows = [(1.00, 0.02, 0.0, 0.0), (0.94, 0.02, 0.025, 0.025), (0.80, 0.015, 0.06, 0.06),
            (0.50, 0.0, 0.095, 0.095), (0.15, 0.0, 0.11, 0.105), (-0.10, 0.0, 0.11, 0.10),
            (-0.20, 0.0, 0.10, 0.09), (-0.26, 0.0, 0.085, 0.08), (-0.36, 0.0, 0.09, 0.085),
            (-0.44, 0.0, 0.07, 0.065), (-0.50, -0.005, 0.0, 0.0)]
    parts = [cc.axis(rows, sides=18, power=2.0)]
    parts.append(nh.tube([(0, -0.18, -0.07), (0, -0.30, -0.08)], [0.03, 0.02], sides=8))   # funnel
    body = cc.fuse(parts, voxel=0.01, smooth=4, max_tris=5000)
    mb = nh.MeshBuilder()
    mb.add(body, body_paint)
    # rhombic fins near the rear
    for sx in (1, -1):
        mb.add(cc.membrane([(sx * 0.07, 0.55, 0.0), (sx * 0.06, 0.80, 0.01)],
                           [(sx * 0.30, 0.68, 0.0), (sx * 0.10, 0.95, 0.01)], nv=4, thickness=0.012,
                           normal_hint=Vector((0, 0, 1))), FIN)
    # big eyes
    for sx in (1, -1):
        c = Vector((sx * 0.08, -0.36, 0.02))
        mb.add(nh.ellipsoid(tuple(c), (0.035, 0.045, 0.045), subdivisions=2), (0.85, 0.75, 0.40))
        mb.add(nh.ellipsoid(tuple(c + Vector((sx * 0.02, -0.005, 0))), (0.02, 0.03, 0.03), subdivisions=2), (0.03, 0.02, 0.02))
    # ten arms with hook rows
    for i in range(10):
        a = (i + 0.5) / 10 * math.tau
        ca, sa = math.cos(a), math.sin(a)
        base = Vector((0.045 * ca, -0.47, 0.04 * sa))
        d = Vector((0.28 * ca, -1.0, 0.22 * sa - 0.08)).normalized()
        L = 0.42
        pts = [base + d * (L * t) + Vector((0, 0, -0.05 * t * t)) for t in (0, 0.25, 0.5, 0.75, 1.0)]
        mb.add(nh.tube(pts, [0.018, 0.014, 0.010, 0.006, 0.0], sides=6), ARM)
        for t in (0.3, 0.5, 0.7):
            p = base + d * (L * t) + Vector((0, 0, -0.05 * t * t))
            inward = -Vector((ca, 0, sa)) * 0.012
            mb.add(cc.cone(p, p + inward + Vector((0, 0.004, 0)), 0.004, sides=3), HOOK, smooth=False)
    obj = mb.to_object("Belemnitella", roughness=0.45)
    cc.centre(obj)
    cc.bounds_report(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Belemnitella", background=(0.05, 0.16, 0.22), views=((35, 22), (-90, 6), (20, 70)), size=640)
