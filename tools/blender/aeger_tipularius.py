"""
Procedural Aeger tipularius (Late Jurassic penaeoid prawn, Solnhofen) for map colonies.

A large prawn, around 15-20 cm long, of the Solnhofen lagoons: a slender, laterally flattened
body with a long, serrated rostrum, very long whip-like antennae, and its signature first
three pairs of walking legs, which are greatly elongated and fringed with long spines (a
basket for snatching small swimming prey). Curved abdomen with paddle-like swimmerets and a
tail fan. Translucent pinkish-orange with darker bands. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/aeger_tipularius.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Aeger.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.86, 0.50, 0.34)
BAND = (0.62, 0.25, 0.16)
LEG = (0.92, 0.66, 0.50)


def body_col(co, n):
    c = BODY
    if co.y > -0.05 and math.sin(co.y * 60) > 0.6:
        c = BAND
    return nh.lerp((0.96, 0.82, 0.72), c, nh.smoothstep(-0.6, 0.2, n.z))


def build():
    # carapace + abdomen curving down at the back
    rows = [(0, -0.4, 0.03, 0, 0), (0, -0.33, 0.03, 0.04, 0.05), (0, -0.2, 0.02, 0.07, 0.08), (0, -0.05, 0.02, 0.07, 0.08),
            (0, 0.08, 0.015, 0.06, 0.07), (0, 0.2, 0.0, 0.05, 0.06), (0, 0.3, -0.03, 0.04, 0.045), (0, 0.38, -0.07, 0.03, 0.035),
            (0, 0.42, -0.1, 0.02, 0.02)]
    spine = kit.Spine(rows)
    body = kit.fuse_parts([spine.mesh(sides=14, power=2.0)], 0.008, 5000)
    mb = nh.MeshBuilder()
    mb.add(body, body_col)
    # rostrum with teeth on top
    mb.add(nh.tube([(0, -0.38, 0.04), (0, -0.52, 0.06), (0, -0.62, 0.075)], [0.012, 0.006, 0.0], sides=5), BAND)
    for i in range(5):
        b = Vector((0, -0.42 - i * 0.035, 0.05 + i * 0.004))
        mb.add(kit.cone(b, b + Vector((0, 0.01, 0.018)), 0.004, sides=3), BAND, smooth=False)
    # tail fan
    mb.add(nh.flat_panel([(0, 0.4, -0.1), (0.07, 0.48, -0.14), (0.04, 0.53, -0.16), (0, 0.5, -0.15), (-0.04, 0.53, -0.16), (-0.07, 0.48, -0.14)], thickness=0.006), BAND)
    # antennae: long whips sweeping back over the body
    for sx in (1, -1):
        pts = [(sx * 0.03, -0.36, 0.04), (sx * 0.12, -0.6, 0.08), (sx * 0.3, -0.5, 0.06), (sx * 0.45, -0.1, 0.02), (sx * 0.5, 0.35, 0.0)]
        mb.add(kit.limb(pts, [0.006, 0.004, 0.003, 0.002, 0.001], sides=4, steps=4), LEG)
        mb.add(nh.tube([(sx * 0.03, -0.36, 0.03), (sx * 0.08, -0.55, 0.02)], [0.006, 0.002], sides=4), LEG)
    # three pairs of very long, spiny raptorial legs held forward, two short walking pairs
    for k, (ln, y) in enumerate(((0.55, -0.26), (0.62, -0.2), (0.58, -0.14))):
        for sx in (1, -1):
            b = Vector((sx * 0.04, y, -0.04))
            kn = b + Vector((sx * 0.12, -0.05, -0.1))
            tip = kn + Vector((sx * 0.05 * (k + 1), -ln * 0.7, 0.05))
            mb.add(kit.limb([b, kn, tip], [0.01, 0.007, 0.003], sides=5), LEG)
            for j in range(7):
                t = 0.15 + 0.8 * j / 6
                p = kn.lerp(tip, t)
                mb.add(nh.tube([p, p + Vector((sx * 0.03, 0.0, -0.035))], [0.002, 0.0], sides=3), BAND, smooth=False)
    for y in (-0.06, 0.0):
        for sx in (1, -1):
            b = Vector((sx * 0.04, y, -0.05))
            mb.add(kit.limb([b, b + Vector((sx * 0.08, -0.02, -0.07)), b + Vector((sx * 0.12, -0.04, -0.12))], [0.008, 0.005, 0.002], sides=5), LEG)
    # swimmerets
    for y in (0.1, 0.17, 0.24, 0.31):
        for sx in (1, -1):
            b = Vector((sx * 0.025, y, -0.04 - y * 0.1))
            mb.add(nh.tube([b, b + Vector((sx * 0.02, 0.02, -0.05))], [0.008, 0.003], sides=4), LEG)
    kit.eyes(mb, (0.04, -0.37, 0.06), 0.013, iris=(0.1, 0.08, 0.07), pupil=(0.02, 0.02, 0.02))
    return kit.finish(mb, "Aeger", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Aeger", background=(0.04, 0.10, 0.13), views=((35, 30), (-90, 5), (0, 89)))
