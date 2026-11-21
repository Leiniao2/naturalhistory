"""
Procedural Antarctic krill (Euphausia superba, Pleistocene to today, Southern
Ocean) for map colonies.

A shrimp-like crustacean only about 6 cm long, yet with a total weight of some
300-500 million tonnes perhaps the most abundant wild animal on Earth: swarms
of up to 10,000 animals per cubic metre graze the phytoplankton and ice algae
and feed whales, seals, penguins, fish and squid. A slender, transparent body
with a short carapace, large black eyes on stalks, long antennae, a basket of
fine, hairy feeding legs under the thorax, five pairs of paddling swimmerets
and a tail fan. Glassy pink-orange with red pigment spots, and blue-green light
organs (photophores) under the eyes and abdomen.

Built with the prawn helpers of nh_jur_kit.py, like aeger_tipularius.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/euphausia_superba.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EuphausiaSuperba.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.95, 0.62, 0.52)
RED = (0.85, 0.20, 0.16)
LEG = (0.98, 0.78, 0.68)
GLOW = (0.30, 0.90, 0.80)


def body_col(co, n):
    c = nh.lerp((0.98, 0.86, 0.80), BODY, nh.smoothstep(-0.6, 0.2, n.z))
    if n.z > 0.2 and math.sin(co.y * 75) > 0.55:        # red chromatophore band on each segment
        c = nh.lerp(c, RED, 0.8)
    return c


def build():
    rows = [(0, -0.36, 0.02, 0, 0), (0, -0.32, 0.02, 0.045, 0.05), (0, -0.2, 0.02, 0.065, 0.07),
            (0, -0.06, 0.015, 0.06, 0.065), (0, 0.06, 0.005, 0.05, 0.055), (0, 0.18, -0.01, 0.042, 0.045),
            (0, 0.28, -0.03, 0.034, 0.036), (0, 0.36, -0.055, 0.026, 0.026), (0, 0.42, -0.08, 0.016, 0.016)]
    spine = kit.Spine(rows)
    body = kit.fuse_parts([spine.mesh(sides=14, power=2.0)], 0.007, 5000)
    mb = nh.MeshBuilder()
    mb.add(body, body_col)
    # short rostrum
    mb.add(nh.tube([(0, -0.34, 0.05), (0, -0.40, 0.055)], [0.008, 0.0], sides=5), RED)
    # tail fan
    mb.add(nh.flat_panel([(0, 0.40, -0.08), (0.06, 0.48, -0.11), (0.035, 0.52, -0.13), (0, 0.50, -0.12),
                          (-0.035, 0.52, -0.13), (-0.06, 0.48, -0.11)], thickness=0.005), RED)
    # big black stalked eyes
    for sx in (1, -1):
        b = Vector((sx * 0.03, -0.33, 0.05))
        e = b + Vector((sx * 0.035, -0.02, 0.01))
        mb.add(nh.tube([b, e], [0.010, 0.010], sides=6), BODY)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * 0.01, -0.005, 0))), (0.026, 0.026, 0.026), subdivisions=2),
               (0.03, 0.03, 0.03))
        # two pairs of antennae: long whips forward and outward
        mb.add(kit.limb([(sx * 0.02, -0.36, 0.03), (sx * 0.10, -0.60, 0.06), (sx * 0.22, -0.78, 0.04)],
                        [0.005, 0.003, 0.001], sides=4, steps=4), LEG)
        mb.add(kit.limb([(sx * 0.03, -0.36, 0.02), (sx * 0.06, -0.48, 0.0), (sx * 0.10, -0.56, -0.02)],
                        [0.006, 0.004, 0.002], sides=4), RED)
    # feeding basket: six pairs of fringed thoracic legs held forward and down
    for k in range(6):
        y = -0.26 + k * 0.045
        for sx in (1, -1):
            b = Vector((sx * 0.02, y, -0.05))
            kn = b + Vector((sx * 0.04, -0.03, -0.06))
            tip = kn + Vector((sx * 0.01, -0.06, -0.04))
            mb.add(kit.limb([b, kn, tip], [0.006, 0.004, 0.002], sides=4), LEG)
            for j in range(3):
                p = kn.lerp(tip, 0.3 + 0.3 * j)
                mb.add(nh.tube([p, p + Vector((-sx * 0.015, 0.0, -0.02))], [0.0015, 0.0], sides=3), LEG, smooth=False)
    # five pairs of swimmerets
    for y in (0.06, 0.13, 0.20, 0.27, 0.33):
        for sx in (1, -1):
            b = Vector((sx * 0.018, y, -0.04 - y * 0.08))
            mb.add(nh.tube([b, b + Vector((sx * 0.015, 0.02, -0.05))], [0.007, 0.003], sides=4), LEG)
        # blue-green light organs along the belly
        mb.add(nh.ellipsoid((0, y - 0.03, -0.05 - y * 0.08), (0.007,) * 3, subdivisions=1), GLOW)
    return kit.finish(mb, "EuphausiaSuperba", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "EuphausiaSuperba", background=(0.04, 0.10, 0.13), views=((35, 30), (-90, 5), (0, 89)))
