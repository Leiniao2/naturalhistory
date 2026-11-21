"""
Procedural Palaeopalaemon newberryi (Late Devonian, Ohio / Iowa) for map colonies.

The oldest known decapod crustacean: a small, lobster-like shrimp about 6 cm long with a
cylindrical, finely granular carapace, a short rostrum, a straight segmented abdomen ending in
a tail fan, and a first pair of slender, elongated claws (chelae) held forward. Brownish
olive with darker abdominal bands. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/palaeopalaemon_newberryi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeopalaemon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.46, 0.40, 0.24)
BAND = (0.26, 0.20, 0.12)
BELLY = (0.80, 0.70, 0.50)
LEG = (0.62, 0.50, 0.32)
CLAW = (0.70, 0.30, 0.16)


def body_col(co, n):
    c = BODY
    if co.y > 0.02 and math.sin(co.y * 55) > 0.55:
        c = BAND
    if co.y < 0.0 and co.y > -0.06:
        c = BAND  # carapace groove
    return nh.lerp(BELLY, c, nh.smoothstep(-0.6, 0.2, n.z))


def claw(mb, sx, base):
    kn = base + Vector((sx * 0.10, -0.06, -0.03))
    wr = kn + Vector((sx * 0.02, -0.18, 0.02))
    mb.add(kit.limb([base, kn, wr], [0.012, 0.010, 0.010], sides=6), LEG)
    palm_end = wr + Vector((0, -0.10, 0.0))
    mb.add(nh.tube([wr, palm_end], [0.018, 0.016], sides=8), CLAW)
    # two slender fingers
    mb.add(nh.tube([palm_end + Vector((sx * 0.006, 0, 0.004)), palm_end + Vector((sx * 0.002, -0.12, 0.006))], [0.009, 0.0], sides=5), CLAW)
    mb.add(nh.tube([palm_end + Vector((-sx * 0.006, 0, -0.004)), palm_end + Vector((-sx * 0.004, -0.11, -0.006))], [0.008, 0.0], sides=5), CLAW)


def build():
    rows = [(0, -0.30, 0.03, 0, 0), (0, -0.26, 0.03, 0.045, 0.05), (0, -0.15, 0.03, 0.065, 0.07), (0, -0.0, 0.03, 0.065, 0.068),
            (0, 0.06, 0.03, 0.055, 0.058), (0, 0.16, 0.025, 0.05, 0.05), (0, 0.26, 0.02, 0.042, 0.04), (0, 0.34, 0.012, 0.032, 0.03),
            (0, 0.40, 0.005, 0.02, 0.018)]
    spine = kit.Spine(rows)
    body = kit.fuse_parts([spine.mesh(sides=14, power=2.0)], 0.007, 5000)
    mb = nh.MeshBuilder()
    mb.add(body, body_col)
    mb.add(nh.tube([(0, -0.28, 0.06), (0, -0.36, 0.065), (0, -0.40, 0.06)], [0.012, 0.006, 0.0], sides=5), BAND)
    # tail fan: telson + uropods
    mb.add(nh.flat_panel([(0, 0.38, 0.005), (0.02, 0.40, 0.005), (0.012, 0.50, 0.0), (0, 0.51, 0.0), (-0.012, 0.50, 0.0), (-0.02, 0.40, 0.005)], 0.006), BAND)
    for sx in (1, -1):
        mb.add(nh.flat_panel([(sx * 0.015, 0.38, 0.005), (sx * 0.07, 0.44, 0.0), (sx * 0.06, 0.49, 0.0), (sx * 0.02, 0.45, 0.004)], 0.006), BODY)
    # antennae + antennules
    for sx in (1, -1):
        pts = [(sx * 0.03, -0.28, 0.04), (sx * 0.10, -0.48, 0.07), (sx * 0.22, -0.55, 0.05), (sx * 0.34, -0.40, 0.03), (sx * 0.40, -0.10, 0.02)]
        mb.add(kit.limb(pts, [0.005, 0.004, 0.003, 0.002, 0.001], sides=4, steps=4), LEG)
        mb.add(nh.tube([(sx * 0.02, -0.29, 0.05), (sx * 0.05, -0.42, 0.07)], [0.005, 0.001], sides=4), LEG)
        claw(mb, sx, Vector((sx * 0.04, -0.18, -0.02)))
    # four pairs of walking legs
    for y in (-0.12, -0.07, -0.02, 0.03):
        for sx in (1, -1):
            b = Vector((sx * 0.04, y, -0.025))
            mb.add(kit.limb([b, b + Vector((sx * 0.08, -0.01, -0.03)), b + Vector((sx * 0.11, 0.0, -0.09))], [0.007, 0.005, 0.002], sides=5), LEG)
    for y in (0.10, 0.17, 0.24, 0.31):
        for sx in (1, -1):
            b = Vector((sx * 0.02, y, -0.015))
            mb.add(nh.tube([b, b + Vector((sx * 0.015, 0.02, -0.04))], [0.007, 0.002], sides=4), LEG)
    kit.eyes(mb, (0.035, -0.27, 0.06), 0.014, iris=(0.1, 0.08, 0.07), pupil=(0.02, 0.02, 0.02))
    return kit.finish(mb, "Palaeopalaemon", pivot="center", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "Palaeopalaemon", background=(0.04, 0.10, 0.13), views=((35, 30), (-90, 5), (0, 89)))
