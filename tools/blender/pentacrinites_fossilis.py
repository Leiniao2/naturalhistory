"""
Procedural Pentacrinites fossilis (Early Jurassic crinoid, Lyme Regis, Dorset) for map colonies.

A sea lily that lived not on the seabed but hanging from floating driftwood: colonies of
hundreds grew down from logs drifting in the open sea, their long, five-sided stems
bearing whorls of short tendrils (cirri), and each crown a dense bunch of many finely
branched, feathery arms (pinnules) for straining plankton. The 'Pentacrinite bed' of the Dorset
coast preserves masses of them tangled around fossil driftwood. Here a waterlogged driftwood log floats at the surface with
a cluster of crinoids hanging beneath. Pivot at the waterline (Float style).

Usage:
  blender --background --python tools/blender/pentacrinites_fossilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pentacrinites.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

WOOD = (0.30, 0.22, 0.15)
WOOD_DARK = (0.18, 0.13, 0.09)
STEM = (0.72, 0.58, 0.44)
ARM = (0.80, 0.42, 0.30)
ARM_TIP = (0.95, 0.75, 0.55)


def wood(co, n):
    s = 0.5 + 0.5 * math.sin(co.y * 30 + noise.noise(co * 6) * 3)
    return nh.lerp(WOOD, WOOD_DARK, s * 0.7)


def build():
    rng = random.Random(7)
    mb = nh.MeshBuilder()
    # log along Y, half submerged (centre at z = 0.02, radius 0.09)
    log = nh.tube([(0, -0.7, 0.0), (0, -0.2, 0.01), (0, 0.3, 0.0), (0, 0.7, -0.005)], [0.08, 0.095, 0.09, 0.075], sides=12)
    mb.add(log, wood)
    mb.add(nh.tube([(0.05, 0.1, 0.03), (0.2, 0.25, 0.06)], [0.03, 0.012], sides=6), wood)  # snapped branch
    for i in range(7):
        y = -0.55 + i * 0.18 + rng.uniform(-0.04, 0.04)
        x = rng.uniform(-0.04, 0.04)
        length = rng.uniform(0.35, 0.6)
        top = Vector((x, y, -0.07))
        sway = Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0))
        pts = [top, top + Vector((0, 0, -length * 0.5)) + sway * 0.4, top + Vector((0, 0, -length)) + sway]
        mb.add(kit.limb(pts, [0.012, 0.01, 0.009], sides=5), STEM)
        # cirri whorls
        for k in range(1, 5):
            p = top.lerp(pts[-1], k / 5)
            for j in range(5):
                a = j / 5 * math.tau + k
                d = Vector((math.cos(a), math.sin(a), -0.3)).normalized()
                mb.add(nh.tube([p, p + d * 0.05], [0.003, 0.0], sides=3), STEM, smooth=False)
        # crown: calyx plus ten feathery arms curling outward and up
        c = pts[-1]
        mb.add(nh.ellipsoid(c + Vector((0, 0, -0.02)), (0.022, 0.022, 0.03), subdivisions=2), STEM)
        for j in range(10):
            a = j / 10 * math.tau
            d = Vector((math.cos(a), math.sin(a), 0))
            arm = [c + Vector((0, 0, -0.03)), c + d * 0.07 + Vector((0, 0, -0.12)), c + d * 0.14 + Vector((0, 0, -0.18)), c + d * 0.2 + Vector((0, 0, -0.17))]

            def col(co, n, c=c):
                return nh.lerp(ARM, ARM_TIP, nh.smoothstep(0.06, 0.2, (co - c).length))
            mb.add(kit.limb(arm, [0.008, 0.007, 0.005, 0.002], sides=4, steps=2), col)
            for k in range(4):
                p = arm[1].lerp(arm[3], k / 3)
                side = d.cross(Vector((0, 0, 1)))
                for s in (1, -1):
                    mb.add(nh.tube([p, p + side * s * 0.035 + Vector((0, 0, -0.01))], [0.002, 0.0], sides=3), col, smooth=False)
    obj = kit.finish(mb, "Pentacrinites", pivot="none", roughness=0.6)
    return obj


if __name__ == "__main__":
    nh.run(build, "Pentacrinites", background=(0.04, 0.10, 0.13), views=((35, 10), (-90, 0), (30, -40)))
