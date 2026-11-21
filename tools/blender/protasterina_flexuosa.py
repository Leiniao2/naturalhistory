"""
Procedural Protasterina flexuosa (Late Ordovician brittle star, Cincinnati region) for map
colonies (Swim style, like the other brittle stars).

An early brittle star a few centimetres across: a small, soft, rounded central disc and
five long, slender, flexible arms, each a chain of paired plates with a fringe of short
spines along the sides. The arms curl and snake as it crawls quickly over the sea floor,
picking up detritus and small food particles. Arms posed in sinuous curves. Pale orange-
brown with darker banding. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/protasterina_flexuosa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProtasterinaFlexuosa.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "ProtasterinaFlexuosa"
DISC = (0.76, 0.52, 0.34)
DISC_DARK = (0.52, 0.32, 0.20)
ARM = (0.82, 0.60, 0.40)
BAND = (0.50, 0.30, 0.18)
SPINE = (0.92, 0.80, 0.62)

R = 0.82


def build():
    mb = nh.MeshBuilder()
    mb.add(nh.ellipsoid((0, 0, 0.0), (0.17, 0.17, 0.07), 3,
                        deform=lambda v: 1.0 + 0.10 * math.cos(5 * math.atan2(v.y, v.x))),
           lambda co, n: nh.lerp(DISC, DISC_DARK, 0.5 * nh.smoothstep(0.3, 1.0,
                                 0.5 + 0.5 * math.cos(5 * math.atan2(co.y, co.x) + math.pi))))
    for k in range(5):
        a0 = k / 5 * math.tau - math.pi / 2
        wig = (0.5, -0.6, 0.4, -0.35, 0.6)[k]
        pts = []
        n = 16
        for i in range(n + 1):
            t = i / n
            a = a0 + wig * math.sin(t * math.pi * 1.4) * 0.6
            r = 0.12 + (R - 0.12) * t
            pts.append(Vector((math.cos(a) * r, math.sin(a) * r, -0.01 + 0.04 * math.sin(t * math.pi))))
        radii = [0.045 * (1 - 0.8 * i / n) + 0.006 for i in range(n + 1)]
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.7)),
               lambda co, nn: nh.lerp(ARM, BAND, 0.55 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.sin(co.length * 55))))
        # lateral arm spines
        for i in range(1, n - 1):
            p = pts[i]
            d = (pts[i + 1] - pts[i - 1]).normalized()
            side = d.cross(Vector((0, 0, 1))).normalized()
            for sg in (-1, 1):
                L = 0.05 * (1 - 0.5 * i / n)
                b = p + side * sg * radii[i] * 0.8
                mb.add(nh.tube([b, b + (side * sg + d * 0.5).normalized() * L], [0.007, 0.0], sides=3),
                       SPINE, smooth=False)
    return kit.finish_swim(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.SWIM_VIEWS)
