"""
Procedural Uintacrinus socialis (Late Cretaceous free-living crinoid, Western Interior
Seaway, Kansas) for map colonies (Float style).

A stalkless sea lily: a large, globe-shaped cup (calyx) of thin, smooth polygonal
plates, without any stem, and ten extremely long, slender arms (up to a metre or more)
fringed with fine pinnules, spread out and trailing in a wide, drooping fan as it drifted
or lay in huge groups. Pale cream calyx with darker plate sutures, the arms shading from
buff to a soft purple at their tips (colours conjectural).
Pivot at the body centre, the cup on top (faces -Y by convention).

Usage:
  blender --background --python tools/blender/uintacrinus_socialis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Uintacrinus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402

CUP = (0.90, 0.84, 0.70)
SUTURE = (0.55, 0.45, 0.36)
ARM = (0.82, 0.70, 0.56)
ARM_TIP = (0.55, 0.36, 0.52)


def cup_col(co, n):
    d = noise.cell(Vector(co) * 14.0)
    edge = nh.smoothstep(0.02, 0.0, abs(noise.noise(Vector(co) * 10.0)))
    return nh.lerp(CUP, SUTURE, 0.6 * edge)


def build():
    mb = nh.MeshBuilder()
    R = 0.16
    mb.add(nh.ellipsoid((0, 0, 0.05), (R, R, R * 0.92), subdivisions=4), cup_col)
    mb.add(nh.ellipsoid((0, 0, 0.05 + R * 0.85), (R * 0.55, R * 0.55, R * 0.25), subdivisions=3), SUTURE)  # oral disc
    L = 1.0
    for i in range(10):
        a = (i + 0.5) / 10 * math.tau + (0.08 if i % 2 else -0.08)
        out = Vector((math.cos(a), math.sin(a), 0))
        base = Vector((0, 0, 0.05)) + out * R * 0.85 + Vector((0, 0, R * 0.25))
        n = 22
        pts, radii = [], []
        for k in range(n + 1):
            t = k / n
            d = out * (L * t) * (0.9 + 0.1 * math.sin(i * 1.7))
            z = 0.06 * math.sin(t * math.pi * 1.5 + i) - 0.22 * t * t
            pts.append(base + d * 1.0 + Vector((0, 0, z)) + out.cross(Vector((0, 0, 1))) * 0.06 * math.sin(t * 5 + i))
            radii.append(0.014 * (1 - t) + 0.004)
        radii[-1] = 0.0

        def arm_col(co, n, base=base):
            t = min(1.0, (Vector(co) - base).length / L)
            return nh.lerp(ARM, ARM_TIP, nh.smoothstep(0.3, 1.0, t))
        mb.add(nh.tube(pts, radii, sides=6), arm_col)
        side = out.cross(Vector((0, 0, 1))).normalized()
        for k in range(1, n):
            p = pts[k]
            t = k / n
            fwd = (pts[k + 1] - pts[k - 1]).normalized()
            for sg in (-1, 1):
                tip = p + (side * sg * 0.8 + fwd * 0.45 + Vector((0, 0, -0.1))).normalized() * (0.11 * (1 - 0.6 * t))
                mb.add(cc.cone(p, tip, 0.006 * (1 - 0.5 * t), sides=3), arm_col(p, None), smooth=False)
    obj = mb.to_object("Uintacrinus", roughness=0.6)
    cc.centre(obj)
    cc.bounds_report(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Uintacrinus", background=(0.05, 0.16, 0.22), views=((35, 25), (0, 80), (-90, 8)), size=640)
