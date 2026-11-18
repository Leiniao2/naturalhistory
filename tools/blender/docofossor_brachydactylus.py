"""
Procedural Docofossor brachydactylus (Middle-Late Jurassic docodont, Tiaojishan
Formation, Hebei, China) for map colonies.

A tiny, mole-like digging mammal relative about 9 cm long and weighing about 15 g: a
tubular, short-legged body, a long pointed snout, tiny eyes, no visible ears, a short
tail, and broad, spade-like front feet with shortened fingers and big flat claws for
scratching through soil after worms and insect grubs, like a modern golden mole.
Painted dark grey-brown fur with a paler belly and a pink nose. Built with nh_jur_kit
(the Castorocauda recipe). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/docofossor_brachydactylus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Docofossor.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

FUR = (0.22, 0.19, 0.16)
BELLY = (0.52, 0.46, 0.40)
NOSE = (0.78, 0.52, 0.48)
CLAW = (0.86, 0.80, 0.66)


def fur(co, n):
    c = nh.lerp(BELLY, FUR, nh.smoothstep(-0.5, 0.2, n.z))
    m = noise.noise((co.x * 60, co.y * 120, co.z * 60))
    c = tuple(v * (1 + 0.14 * m) for v in c)
    return nh.lerp(c, NOSE, nh.smoothstep(-0.5, -0.53, co.y))


def build():
    H = 0.09
    rows = [(0, 0.36, H - 0.02, 0.0, 0.0), (0, 0.33, H - 0.01, 0.012, 0.012), (0, 0.27, H, 0.05, 0.045),
            (0, 0.18, H + 0.01, 0.1, 0.085), (0, 0.02, H + 0.015, 0.11, 0.09), (0, -0.14, H + 0.012, 0.1, 0.085),
            (0, -0.27, H + 0.005, 0.075, 0.065), (0, -0.37, H - 0.002, 0.05, 0.045), (0, -0.46, H - 0.01, 0.025, 0.022),
            (0, -0.52, H - 0.014, 0.01, 0.009), (0, -0.54, H - 0.015, 0, 0)]
    spine = kit.Spine(rows)
    fused = [spine.mesh(sides=18)]
    claws = []
    for sx in (1, -1):
        for y, front in ((-0.17, True), (0.17, False)):
            top = Vector((sx * 0.07, y, H))
            el = Vector((sx * 0.13, y + (0.0 if front else 0.02), H * 0.6))
            ft = Vector((sx * 0.15, y - (0.04 if front else 0.0), 0.012))
            fused.append(kit.limb([top, el, ft], [0.038, 0.026, 0.018], sides=8))
            if front:
                # broad spade hand, turned outward
                fused.append(nh.ellipsoid((ft.x + sx * 0.015, ft.y - 0.03, 0.014), (0.04, 0.035, 0.012), subdivisions=2))
                for k in range(4):
                    a = (k - 1.5) * 0.32
                    d = Vector((math.sin(a) * sx + sx * 0.35, -math.cos(a), -0.1)).normalized()
                    b = Vector((ft.x + sx * 0.015, ft.y - 0.03, 0.014)) + d * 0.032
                    claws.append((b, b + d * 0.035, 0.008))
            else:
                fused.append(nh.ellipsoid((ft.x, ft.y - 0.02, 0.008), (0.022, 0.03, 0.008), subdivisions=2))
                for k in range(5):
                    a = (k - 2) * 0.3
                    d = Vector((math.sin(a) * sx * 0.6, -math.cos(a), 0)).normalized()
                    b = Vector((ft.x, ft.y - 0.02, 0.01)) + d * 0.026
                    claws.append((b, b + d * 0.01, 0.003))
    body = kit.fuse_parts(fused, 0.007, 8000)
    kit.pebble(body, 0.0015, 90.0)
    mb = nh.MeshBuilder()
    mb.add(body, fur)
    kit.eyes(mb, (0.03, -0.38, H + 0.026), 0.0055, iris=(0.04, 0.03, 0.03))
    mb.add(nh.ellipsoid((0, -0.54, H - 0.013), (0.011, 0.008, 0.008), subdivisions=1), NOSE)
    kit.claws(mb, claws, CLAW)
    return kit.finish(mb, "Docofossor")


if __name__ == "__main__":
    nh.run(build, "Docofossor", ground=(0.40, 0.33, 0.24), views=((35, 22), (-90, 6), (25, 65)))
