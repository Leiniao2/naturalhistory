"""
Procedural Palaeoisopus problematicus (Early Devonian sea spider, Hunsrueck Slate, Germany)
for map colonies (Swim style).

A giant pycnogonid: a slim trunk of four segments only a few centimetres long, but a leg
span of up to about 40 cm. Its long, broad legs are flattened, the first pair most of all,
into paddle-like swimming legs held forward; a large, conical proboscis juts from the head,
with small chelifores beside it, a small eye tubercle on the head and a short spiky tail
behind. Reddish-brown. Reuses the jointed legs of nh_sil_eurypterid.py. Faces -Y, pivot at
the body centre.

Usage:
  blender --background --python tools/blender/palaeoisopus_problematicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeoisopus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

NAME = "Palaeoisopus"
SHELL = (0.52, 0.28, 0.18)
DARK = (0.32, 0.16, 0.10)
LEG = (0.62, 0.36, 0.22)
LEG_DARK = (0.38, 0.20, 0.12)
PALE = (0.82, 0.64, 0.46)
TRUNK = [-0.14, -0.05, 0.04, 0.13]


def flat_leg(mb, pts, widths, thick, color, joint):
    """Flattened (paddle) leg: a chain of flat tube segments with joint bands."""
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        w0, w1 = widths[i], widths[i + 1]
        mb.add(nh.tube([pts[i], pts[i + 1]], [w0, max(w1, 0.0)], sides=8, scale_xy=(1.0, thick)), color)
        if 0 < i < len(pts) - 2:
            mb.add(nh.ellipsoid(pts[i], (w0 * 1.02, w0 * 1.02, w0 * thick * 1.05), 2), joint)


def build():
    mb = nh.MeshBuilder()
    for i, y in enumerate(TRUNK):
        mb.add(nh.uv_ellipsoid((0, y, 0), (0.04, 0.06, 0.035), 10, 6), SHELL)
        for sx in (-1, 1):
            a = math.radians((-62, -20, 15, 45)[i])
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            base = Vector((0, y, 0))
            proc = base + d * 0.08
            mb.add(nh.tube([base, proc], [0.03, 0.025], sides=8), SHELL)
            if i == 0:  # big forward swimming paddles
                pts = [proc, proc + d * 0.12 + Vector((0, 0, 0.04)), proc + d * 0.36 + Vector((0, 0, 0.06)),
                       proc + d * 0.62 + Vector((0, 0, 0.02)), proc + d * 0.86 + Vector((0, 0, -0.02)), proc + d * 0.98]
                flat_leg(mb, pts, [0.03, 0.045, 0.06, 0.065, 0.05, 0.0], 0.28, LEG, LEG_DARK)
            else:
                pts = [proc, proc + d * 0.10 + Vector((0, 0, 0.06)), proc + d * 0.32 + Vector((0, 0, 0.08)),
                       proc + d * 0.55 + Vector((0, 0, 0.0)), proc + d * 0.74 + Vector((0, 0, -0.06)), proc + d * 0.82 + Vector((0, 0, -0.08))]
                flat_leg(mb, pts, [0.025, 0.03, 0.035, 0.03, 0.02, 0.0], 0.45, LEG, LEG_DARK)
    # head, eye tubercle, proboscis, chelifores
    mb.add(nh.uv_ellipsoid((0, -0.23, 0.0), (0.045, 0.06, 0.04), 10, 6), SHELL)
    mb.add(nh.tube([(0, -0.24, 0.03), (0, -0.24, 0.075)], [0.018, 0.01], sides=6), DARK)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.009, -0.248, 0.07), (0.007,) * 3, 1), (0.05, 0.04, 0.03))
    mb.add(nh.tube([(0, -0.27, -0.01), (0, -0.36, -0.015), (0, -0.48, -0.02), (0, -0.56, -0.025)],
                   [0.04, 0.05, 0.035, 0.0], sides=10), PALE)
    for sx in (-1, 1):
        b = Vector((sx * 0.03, -0.27, 0.02))
        mb.add(nh.tube([b, b + Vector((sx * 0.04, -0.08, 0.02)), b + Vector((sx * 0.03, -0.14, 0.0))], [0.012, 0.009, 0.0], sides=6), DARK)
    # short spiny tail
    mb.add(nh.tube([(0, 0.18, 0.0), (0, 0.26, 0.02), (0, 0.32, 0.03)], [0.022, 0.015, 0.0], sides=7), SHELL)
    obj = mb.to_object(NAME, roughness=0.5)
    vs = obj.data.vertices
    xs, zs, ys = [v.co.x for v in vs], [v.co.z for v in vs], [v.co.y for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **eu.VIEWS)
