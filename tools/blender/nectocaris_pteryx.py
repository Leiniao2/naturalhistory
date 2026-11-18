"""
Procedural Nectocaris pteryx (Burgess Shale, ~5 cm; a possible early cephalopod relative).

A flattened, kite-shaped body (widest at the front third, tapering to a pointed tail), with a
broad, finely striated fin running along each side; a small head with a pair of large eyes
on short stalks and two long, flexible tentacles reaching forward; a short funnel tube
projecting under the front of the body. Translucent pinkish lilac with darker fin rays and a
dark axial line. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/nectocaris_pteryx.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Nectocaris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.84, 0.66, 0.74)
AXIS = (0.50, 0.32, 0.42)
FIN = (0.90, 0.76, 0.84)
RAY = (0.62, 0.42, 0.54)
TENT = (0.80, 0.56, 0.66)
EYE = (0.04, 0.03, 0.05)


def half_w(y):
    # kite outline: y from -0.45 (front) to 0.6 (tail)
    if y < -0.2:
        return 0.08 + 0.1 * (y + 0.45) / 0.25
    return max(0.005, 0.18 * (1 - (y + 0.2) / 0.8) ** 1.1)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    for i in range(21):
        y = -0.45 + 1.05 * i / 20
        pts.append((0, y, 0))
        radii.append(half_w(y) * 0.45)
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.45)),
           lambda co, n: nh.lerp(AXIS, BODY, nh.smoothstep(0.005, 0.03, abs(co.x))))
    for s in (-1, 1):
        outline = []
        for i in range(15):
            y = -0.36 + 0.9 * i / 14
            outline.append((half_w(y) * 0.4, y, 0))
        for i in range(14, -1, -1):
            y = -0.36 + 0.9 * i / 14
            outline.append((half_w(y) * 1.25 + 0.03 * math.sin(i * 0.8) * 0, y, 0))
        fin = nh.flat_panel(outline, thickness=0.008)
        ec.mirror(fin, s)
        mb.add(fin, lambda co, n: nh.lerp(FIN, RAY, nh.smoothstep(0.6, 1.0, math.sin(co.y * 140) * 0.5 + 0.5) * 0.7),
               smooth=False)
    mb.add(nh.uv_ellipsoid((0, -0.5, 0.0), (0.06, 0.07, 0.04), segments=12, rings=7), BODY)
    for s in (-1, 1):
        e0 = Vector((s * 0.03, -0.52, 0.02))
        e1 = e0 + Vector((s * 0.05, -0.02, 0.025))
        mb.add(nh.tube([e0, e1], [0.012, 0.01], sides=6), BODY)
        mb.add(nh.ellipsoid(e1 + Vector((s * 0.012, 0, 0)), (0.026, 0.028, 0.024), subdivisions=2), EYE)
        t0 = Vector((s * 0.02, -0.56, -0.01))
        mb.add(nh.tube(kit.curve(t0, t0 + Vector((s * 0.06, -0.2, 0.02)), t0 + Vector((s * 0.02, -0.42, -0.04)), 8),
                       [0.012, 0.011, 0.01, 0.009, 0.008, 0.007, 0.006, 0.004, 0.0], sides=5), TENT)
    mb.add(nh.tube([(0, -0.3, -0.03), (0, -0.4, -0.05), (0, -0.46, -0.05)], [0.02, 0.016, 0.014], sides=8), AXIS)
    return ec.centre(mb.to_object("Nectocaris", roughness=0.3))


if __name__ == "__main__":
    ec.export(build, "Nectocaris")
