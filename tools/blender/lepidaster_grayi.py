"""
Procedural Lepidaster grayi (a many-armed Silurian starfish, about 15-20 cm across, from
the Wenlock Limestone of Dudley, England) for map colonies (Fixed, like the other
starfish).

A sun-star-like early starfish: a broad, flat central disc covered in small scale-like
plates, ringed by thirteen tapering arms, each edged with rows of block-like marginal
plates and with tube feet underneath. It crept over the reef floor preying on shellfish
and other slow animals. Orange-tan with darker plates. Built in the style of
nh_ord_echino.seastar (which only makes five arms). Fixed style: pivot on the sea floor,
facing -Y.

Usage:
  blender --background --python tools/blender/lepidaster_grayi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LepidasterGrayi.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "LepidasterGrayi"
PLATE = (0.84, 0.52, 0.30)
PLATE_DARK = (0.56, 0.30, 0.16)
MARGINAL = (0.94, 0.74, 0.52)

ARMS, R, R_DISC, ARM_W, HEIGHT = 13, 0.80, 0.30, 0.075, 0.07


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, R * 1.15, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    z0 = 0.02
    mb.add(nh.ellipsoid((0, 0, z0 + HEIGHT * 0.3), (R_DISC, R_DISC, HEIGHT * 0.8), subdivisions=4),
           lambda co, n: nh.lerp(PLATE, PLATE_DARK, 0.6 * nh.smoothstep(0.1, 0.4, noise.noise(co * 40))))
    mb.add(nh.ellipsoid((0.06, 0.06, z0 + HEIGHT * 1.05), (0.03, 0.03, 0.012), subdivisions=2), MARGINAL)
    for k in range(ARMS):
        a = k / ARMS * math.tau - math.pi / 2
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-d.y, d.x, 0))
        bend = 0.08 * math.sin(k * 2.3)
        pts, radii = [], []
        for i in range(9):
            t = i / 8
            p = d * (R_DISC * 0.7 + (R - R_DISC * 0.7) * t) + side * bend * t * t \
                + Vector((0, 0, z0 + HEIGHT * 0.35 + 0.04 * t ** 3))
            pts.append(p)
            radii.append(ARM_W * (1.0 - 0.8 * t) + 0.006)
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.5)),
               lambda co, n, d=d: nh.lerp(PLATE, PLATE_DARK,
                                          0.6 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.sin(co.dot(d) * 80))))
        for i in range(7):
            t = (i + 0.5) / 8
            p = pts[int(t * 8)].lerp(pts[min(8, int(t * 8) + 1)], t * 8 - int(t * 8))
            w = ARM_W * (1.0 - 0.8 * t) + 0.006
            s = 0.02 * (1.0 - 0.6 * t) + 0.006
            for sg in (-1, 1):
                mb.add(nh.ellipsoid(tuple(p + side * sg * w * 0.85), (s, s, s * 0.7), subdivisions=1), MARGINAL)
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
