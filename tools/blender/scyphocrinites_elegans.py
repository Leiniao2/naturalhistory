"""
Procedural Scyphocrinites elegans (latest Silurian to earliest Devonian camerate crinoid,
found worldwide, especially in Morocco and Bohemia) for map colonies (Float style).

A giant sea lily that hung upside down from the sea surface: at the top of its long
stem (up to a few metres) sat a "lobolith", a big, many-chambered bulb of plates that
is thought to have acted as a float; the stem hung straight down from it, and at its
lower end the large cup-shaped crown opened downward into ten long arms that branched
again and again into a dense, feathery fan to sieve plankton. Waterline at z = 0 (the
float just breaking the surface). Pale ivory float and stem, rose-brown crown.
Faces -Y.

Usage:
  blender --background --python tools/blender/scyphocrinites_elegans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ScyphocrinitesElegans.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402

NAME = "ScyphocrinitesElegans"
FLOAT = (0.86, 0.80, 0.66)
FLOAT_DARK = (0.56, 0.48, 0.36)
STEM = (0.80, 0.72, 0.58)
STEM_DARK = (0.56, 0.48, 0.38)
CUP = (0.62, 0.38, 0.32)
CUP_DARK = (0.40, 0.22, 0.18)
ARM = (0.74, 0.46, 0.38)
ARM_TIP = (0.94, 0.76, 0.62)

STEM_L = 1.25


def float_col(co, n):
    # lobolith: lobes of plates; dark seams between chambers
    a = math.atan2(co.y, co.x)
    seam = nh.smoothstep(0.85, 0.98, abs(math.cos(a * 2.5)))
    plate = 0.5 + 0.5 * math.sin(co.x * 60) * math.sin(co.y * 60) * math.sin(co.z * 60)
    c = nh.lerp(FLOAT, FLOAT_DARK, 0.25 * plate + 0.6 * seam)
    return c


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()
    # lobolith float: a five-lobed, chambered bulb, mostly under water
    mb.add(nh.uv_ellipsoid((0, 0, -0.06), (0.24, 0.24, 0.17), 30, 16,
                           deform=lambda v: 1.0 + 0.12 * math.cos(5 * math.atan2(v.y, v.x)) * (1 - abs(v.z))),
           float_col)
    # stem hanging down, slightly swaying, with dark columnal joints
    n = 16
    pts = [Vector((0.05 * math.sin(t * 2.0) * t, 0.03 * math.sin(t * 3.1) * t, -0.18 - STEM_L * t))
           for t in [i / n for i in range(n + 1)]]
    mb.add(nh.tube(pts, [0.032 - 0.006 * i / n for i in range(n + 1)], sides=8),
           lambda co, nn: STEM_DARK if math.cos(co.z * 150.0) > 0.7 else STEM)
    c = pts[-1]
    # crown: cup opening downward
    mb.add(nh.tube([c + Vector((0, 0, 0.02)), c + Vector((0, 0, -0.08)), c + Vector((0, 0, -0.16))],
                   [0.035, 0.10, 0.14], sides=10),
           lambda co, nn: CUP_DARK if math.cos(math.atan2(co.y, co.x) * 10) > 0.8 else CUP)
    base = c + Vector((0, 0, -0.15))

    def arm(p, d, L, r, level):
        steps = 3
        q = Vector(p)
        dd = Vector(d)
        path = [q.copy()]
        for _ in range(steps):
            dd = (dd + Vector((0, 0, -0.18))).normalized()
            q = q + dd * (L / steps)
            path.append(q.copy())

        def col(co, nn):
            return nh.lerp(ARM, ARM_TIP, nh.smoothstep(0.1, 0.6, (co - base).length))
        mb.add(kit.limb(path, [r, r * 0.85, r * 0.7, r * 0.55 if level < 2 else 0.0], sides=4, steps=2), col)
        # pinnules
        side = dd.cross(Vector((0, 0, 1)))
        if side.length > 1e-4:
            side.normalize()
            for k in range(1, steps + 1):
                b = path[k - 1].lerp(path[k], 0.5)
                for sg in (-1, 1):
                    mb.add(nh.tube([b, b + (side * sg + dd * 0.5).normalized() * L * 0.18], [r * 0.45, 0.0], sides=3),
                           col, smooth=False)
        if level < 2:
            perp = dd.cross(Vector((0, 0, 1)))
            if perp.length < 1e-4:
                perp = Vector((1, 0, 0))
            perp.normalize()
            for sg in (-1, 1):
                nd = (dd + perp * sg * 0.35 + Vector((rng.uniform(-0.05, 0.05),) * 3)).normalized()
                arm(q, nd, L * 0.75, r * 0.75, level + 1)

    for k in range(10):
        a = k / 10 * math.tau
        out = Vector((math.cos(a), math.sin(a), 0))
        arm(base + out * 0.12, (out * 0.75 + Vector((0, 0, -0.7))).normalized(), 0.32, 0.022, 0)
    obj = kit.finish(mb, NAME, pivot="none", roughness=0.6)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.04, 0.10, 0.13), views=((35, 10), (-90, 0), (30, -40)))
