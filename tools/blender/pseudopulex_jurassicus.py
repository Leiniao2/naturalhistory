"""
Procedural Pseudopulex jurassicus (Middle Jurassic giant flea-like insect, Daohugou beds,
Inner Mongolia, China) for map colonies.

One of the giant early fleas, females up to about 2 cm long, several times the size of a
modern flea: a wingless, flattened, broad oval body (flattened from top to bottom rather
than from side to side as in living fleas), a small head with short antennae and a very
long, saw-edged piercing siphon for driving through the skin of feathered dinosaurs or
pterosaurs, and long legs ending in long, strong claws for clinging to the host. Its legs
were not built for jumping. Painted glossy dark chestnut with paler segment margins and
legs. Built with nh_jur_kit. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pseudopulex_jurassicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pseudopulex.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.30, 0.14, 0.07)
MARGIN = (0.55, 0.34, 0.18)
LEG = (0.48, 0.28, 0.14)
SIPHON = (0.24, 0.12, 0.06)
CLAW = (0.10, 0.05, 0.03)

SEGS = [-0.26 + 0.07 * k for k in range(11)]


def shell(co, n):
    # dark tergites with paler hind margins, and a fake gloss on the upper surface
    c = BODY
    for y in SEGS:
        if 0.0 < co.y - y < 0.012:
            c = MARGIN
    g = nh.smoothstep(0.75, 0.98, n.z) * nh.smoothstep(0.1, -0.3, n.x)
    return nh.lerp(c, (0.85, 0.70, 0.55), 0.3 * g)


def build():
    H = 0.16
    rows = [(0, 0.5, H, 0.0, 0.0), (0, 0.47, H, 0.06, 0.03), (0, 0.38, H + 0.005, 0.16, 0.06),
            (0, 0.2, H + 0.01, 0.21, 0.075), (0, 0.0, H + 0.01, 0.22, 0.075), (0, -0.16, H + 0.005, 0.18, 0.06),
            (0, -0.27, H, 0.12, 0.05), (0, -0.33, H - 0.005, 0.09, 0.045), (0, -0.4, H - 0.01, 0.085, 0.045),
            (0, -0.46, H - 0.015, 0.06, 0.035), (0, -0.49, H - 0.02, 0.0, 0.0)]
    spine = kit.Spine(rows)
    body = kit.fuse_parts([spine.mesh(sides=20)], 0.008, 6000, smooth=4)
    mb = nh.MeshBuilder()
    mb.add(body, shell)
    # long legs: coxa under the body, femur out and up, tibia down to the ground, long tarsus
    for sx in (1, -1):
        for y, spread, ln in ((-0.22, -0.5, 0.9), (-0.05, 0.1, 1.0), (0.12, 0.6, 1.15)):
            c = Vector((sx * 0.08, y, H - 0.04))
            d = Vector((sx * math.cos(spread * 0.6), math.sin(spread * 0.6) * 0.8, 0)).normalized()
            knee = c + d * 0.2 * ln + Vector((0, 0, 0.1))
            ankle = knee + d * 0.17 * ln + Vector((0, 0, -0.2))
            foot = ankle + d * 0.14 * ln + Vector((0, 0, -ankle.z + 0.008))
            mb.add(kit.limb([c, knee, ankle, foot], [0.02, 0.014, 0.01, 0.006], sides=6), LEG)
            for k in (-1, 1):
                b = foot
                t = foot + (d + Vector((-d.y * k * 0.5, d.x * k * 0.5, 0))).normalized() * 0.04 + Vector((0, 0, -0.006))
                mb.add(kit.cone(b, t, 0.005, sides=4), CLAW, smooth=False)
            # a row of short spines on the tibia
            for t in (0.3, 0.6, 0.9):
                p = knee.lerp(ankle, t)
                mb.add(kit.cone(p, p + d * 0.02 + Vector((0, 0.01, 0.01)), 0.003, sides=3), CLAW, smooth=False)
    # siphon: a long, straight piercing beak angled down and forward under the head
    b = Vector((0, -0.46, H - 0.03))
    tip = Vector((0, -0.7, 0.03))
    mb.add(kit.limb([b, b.lerp(tip, 0.5), tip], [0.016, 0.01, 0.003], sides=6), SIPHON)
    # short antennae and small eyes
    for sx in (1, -1):
        a0 = Vector((sx * 0.04, -0.44, H + 0.01))
        mb.add(kit.limb([a0, a0 + Vector((sx * 0.05, -0.04, 0.03)), a0 + Vector((sx * 0.08, -0.03, 0.05))], [0.007, 0.006, 0.004], sides=5), LEG)
    kit.eyes(mb, (0.06, -0.41, H + 0.005), 0.012, iris=(0.05, 0.03, 0.02))
    return kit.finish(mb, "Pseudopulex", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Pseudopulex", ground=(0.55, 0.50, 0.42), views=((35, 22), (-90, 6), (25, 65)))
