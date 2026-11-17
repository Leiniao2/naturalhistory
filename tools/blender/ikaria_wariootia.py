"""
Procedural low-poly Ikaria wariootia (Ediacaran, ~555 Ma), one of the earliest bilaterians.

A rice-grain-sized burrower: a smooth, slightly flattened ovoid with a distinct, blunter front
and a narrower rear, faint ring-like annulations, a darker gut line showing through along the
back and a small mouth at the front, as reconstructed from 3D laser scans of its burrows.
Shown swimming / ploughing through the sediment surface. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ikaria_wariootia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ikaria.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402

SKIN = (0.86, 0.66, 0.60)
SKIN_DEEP = (0.72, 0.50, 0.46)
BELLY = (0.92, 0.80, 0.72)
GUT = (0.48, 0.30, 0.26)
MOUTH = (0.30, 0.16, 0.14)


def radius(t):
    """0 = front, 1 = rear: blunt rounded head, widest a third back, tapering rear."""
    return 0.16 * math.sin(math.pi * min(1.0, 0.06 + t * 0.94)) ** 0.55 * (1.0 - 0.3 * t) + 0.004


def build():
    mb = nh.MeshBuilder()
    n = 24
    pts, radii = [], []
    for i in range(n + 1):
        t = i / n
        pts.append((0.0, -0.5 + t, 0.012 * math.sin(t * math.pi)))
        radii.append(radius(t))
    radii[0], radii[-1] = 0.03, 0.0

    def col(co, nrm):
        t = co.y + 0.5
        c = nh.lerp(BELLY, SKIN, nh.smoothstep(-0.06, 0.06, co.z))
        ring = 0.5 + 0.5 * math.cos(t / 0.075 * math.tau)          # faint annulations
        c = nh.lerp(c, SKIN_DEEP, 0.35 * nh.smoothstep(0.7, 1.0, ring))
        gut = math.exp(-(co.x / 0.03) ** 2) * nh.smoothstep(0.0, 0.08, co.z) * nh.smoothstep(0.05, 0.2, t) * (1 - nh.smoothstep(0.85, 0.98, t))
        return nh.lerp(c, GUT, 0.55 * gut)

    mb.add(nh.tube(pts, radii, sides=14, scale_xy=(1.0, 0.72)), col)
    mb.add(nh.ellipsoid((0, -0.505, 0.0), (0.025, 0.012, 0.018), subdivisions=1), MOUTH)
    return ec.centre(mb.to_object("Ikaria", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Ikaria")
