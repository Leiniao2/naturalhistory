"""
Procedural Gogia spiralis (middle Cambrian eocrinoid echinoderm, a few cm).

A small, elongate, egg-shaped cup (theca) of irregular polygonal plates set on a short,
ringed stalk that ends in a small holdfast; from the top rise five long, slender
feeding arms (brachioles) that coil round each other in a loose spiral. Cream and
rust-coloured plates. Fixed: pivot on the seabed.

Output: Assets/Resources/Models/Species/Gogia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

PLATE = (0.90, 0.78, 0.60)
SEAM = (0.62, 0.34, 0.20)
ARM = (0.80, 0.50, 0.32)
STALK = (0.66, 0.46, 0.30)


def plates(co, n):
    u, v = co.x * 38, co.z * 30 + co.y * 38
    k = abs(math.sin(u) * math.sin(v) + 0.5 * math.sin(u * 0.7 + v * 1.3))
    return nh.lerp(SEAM, PLATE, nh.smoothstep(0.08, 0.35, k))


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.frond_disc(0.09, 0.03, rings=2), STALK)
    mb.add(nh.tube([(0, 0, 0.0), (0.01, 0, 0.12), (0, 0.01, 0.24)], [0.03, 0.026, 0.035], sides=8),
           kit.ringed(STALK, SEAM, period=0.03, axis=2))
    mb.add(nh.uv_ellipsoid((0, 0, 0.38), (0.11, 0.11, 0.17), segments=20, rings=12), plates)
    for k in range(5):
        a0 = k / 5 * math.tau
        pts, radii = [], []
        n = 14
        for i in range(n + 1):
            t = i / n
            a = a0 + t * 2.4
            r = 0.04 + 0.12 * t
            pts.append((math.cos(a) * r, math.sin(a) * r, 0.54 + 0.62 * t))
            radii.append(0.016 * (1 - 0.7 * t))
        radii[-1] = 0.0
        mb.add(nh.tube(pts, radii, sides=5), kit.ringed(ARM, SEAM, period=0.04, sharp=0.2, axis=2))
    return ec.ground(mb.to_object("Gogia", roughness=0.55))


if __name__ == "__main__":
    ec.export(build, "Gogia", fixed=True)
