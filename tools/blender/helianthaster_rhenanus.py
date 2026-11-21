"""
Procedural Helianthaster rhenanus (Early Devonian sea star, Hunsrueck Slate, Germany) for
the map (Fixed style).

A "sun star" about 20 cm across: a small, low central disc ringed by about sixteen long,
slender, flexible arms, each with rows of small plates and short spines along its edges and
a slight curl at the tip; the arms lie in gentle sinuous curves over the sea floor. Built
after nh_ord_echino.seastar (which has five arms). Orange-red with paler plate rows (colour
conjectural).

Usage:
  blender --background --python tools/blender/helianthaster_rhenanus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Helianthaster.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

PLATE = (0.84, 0.42, 0.22)
PLATE_DARK = (0.56, 0.22, 0.12)
MARGINAL = (0.96, 0.74, 0.52)
DISC = (0.74, 0.34, 0.20)

ARMS, R, R_DISC, ARM_W, H = 16, 0.82, 0.13, 0.042, 0.05


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, R * 1.12, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    z0 = 0.02
    mb.add(nh.ellipsoid((0, 0, z0 + H * 0.4), (R_DISC * 1.05, R_DISC * 1.05, H * 0.9), subdivisions=3),
           lambda co, n: nh.lerp(DISC, PLATE_DARK, 0.4 + 0.3 * noise.noise(co * 30)))
    mb.add(nh.ellipsoid((0.03, 0.03, z0 + H * 1.25), (0.02, 0.02, 0.01), subdivisions=2), MARGINAL)
    for k in range(ARMS):
        a0 = k / ARMS * math.tau
        wig = 0.25 * math.sin(k * 2.3 + 1.0)
        L = R * (0.85 + 0.15 * math.sin(k * 1.7))
        pts, radii = [], []
        steps = 12
        for i in range(steps + 1):
            t = i / steps
            a = a0 + wig * t * t + 0.08 * math.sin(t * 6 + k)
            r = R_DISC * 0.6 + (L - R_DISC * 0.6) * t
            pts.append(Vector((math.cos(a) * r, math.sin(a) * r, z0 + H * 0.35 + 0.05 * t ** 4)))
            radii.append(ARM_W * (1.0 - 0.8 * t) + 0.006)
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=6, scale_xy=(1.0, 0.55)),
               lambda co, n: nh.lerp(PLATE, PLATE_DARK, 0.6 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.sin(co.length * 120))))
        # marginal plate knobs and little spines along the arm edges
        for i in range(1, steps, 1):
            p, q = pts[i], pts[i + 1]
            d = (q - p).normalized()
            side = Vector((-d.y, d.x, 0))
            w = radii[i]
            s = w * 0.45 + 0.004
            for sg in (-1, 1):
                b = p + side * sg * w * 0.85
                if i % 2 == 1:
                    mb.add(nh.ellipsoid(tuple(b), (s, s, s * 0.7), subdivisions=1), MARGINAL)
                else:
                    mb.add(nh.tube([b, b + side * sg * w * 0.9 + Vector((0, 0, 0.01))], [s * 0.5, 0.0], sides=3),
                           MARGINAL, smooth=False)
    return ec._finish(mb, "Helianthaster")


if __name__ == "__main__":
    nh.run(build, "Helianthaster", **ec.VIEWS)
