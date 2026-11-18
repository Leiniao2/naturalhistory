"""
Procedural Uncus dzaugisi (Ediacaran, South Australia; the oldest known ecdysozoan, a
roundworm-like burrower). A long, thin, smooth worm a few centimetres long, curved like a
hook (uncus) at its front end, with fine annulations, a slightly blunter head with a small
mouth and a tapering tail, half emerging from a short stretch of its sandy burrow. Pale
pinkish cream. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/uncus_dzaugisi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Uncus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

SKIN = (0.90, 0.72, 0.64)
RING = (0.70, 0.50, 0.44)
MOUTH = (0.35, 0.18, 0.15)
BURROW = (0.56, 0.48, 0.34)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    n = 60
    for i in range(n + 1):
        t = i / n
        # hook: tight curl at the front (-Y end), gentle S behind
        if t < 0.3:
            a = (0.3 - t) / 0.3 * math.radians(150)
            c = Vector((0.18, -0.55, 0))
            p = c + Vector((-0.18 * math.cos(a), -0.18 * math.sin(a), 0.03 * math.sin(a)))
        else:
            u = (t - 0.3) / 0.7
            p = Vector((0.0 + 0.08 * math.sin(u * 4.0), -0.55 + u * 1.25, 0))
        pts.append(p)
        radii.append(0.035 * (1 - 0.7 * t ** 3) * (0.93 if i % 2 else 1.0))
    radii[-1] = 0.0
    radii[0] = 0.02
    mb.add(nh.tube(pts, radii, sides=10), lambda co, n: SKIN)
    # annulation rings
    for i in range(2, n - 4, 2):
        p, q = pts[i], pts[i + 1]
        mb.add(nh.tube([p, p.lerp(q, 0.25)], [radii[i] * 1.06, radii[i] * 1.06], sides=10), RING)
    mb.add(nh.ellipsoid(pts[0] + (pts[0] - pts[1]).normalized() * 0.012, (0.012, 0.012, 0.012), subdivisions=2), MOUTH)
    # a short open burrow mound the tail disappears into
    tail = pts[-12]
    mound = nh.uv_ellipsoid(tuple(tail + Vector((0, 0.16, -0.045))), (0.17, 0.3, 0.05), segments=14, rings=8)
    mb.add(mound, kit.mottled(BURROW, 0.15, 20))
    return ec.centre(mb.to_object("Uncus", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Uncus")
