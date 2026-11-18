"""
Procedural Chancelloria eros (Burgess Shale chancelloriid, ~10 cm).

A soft, vase-shaped sac narrowing to a small attachment point on the seabed and opening at
the top, its whole surface studded with star-shaped clusters (rosettes) of five to seven
sharp, radiating spines, each with one more upright central spine. Pale olive-tan skin,
ivory spines. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/chancelloria_eros.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Chancelloria.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

SKIN = (0.66, 0.60, 0.44)
SKIN_DARK = (0.44, 0.38, 0.26)
SPINE = (0.94, 0.90, 0.80)
INSIDE = (0.20, 0.16, 0.10)
PROF = [(0.02, 0.0), (0.06, 0.06), (0.12, 0.25), (0.17, 0.5), (0.19, 0.75), (0.18, 0.95), (0.15, 1.05)]


def radius_at(z):
    for (r0, z0), (r1, z1) in zip(PROF, PROF[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return PROF[-1][0]


def build():
    mb = nh.MeshBuilder()
    pts = [(0, 0, z) for _r, z in PROF]
    mb.add(nh.tube(pts, [r for r, _z in PROF], sides=16, cap_end=True),
           lambda co, n: nh.lerp(SKIN_DARK, SKIN, nh.smoothstep(0.0, 0.5, co.z)))
    mb.add(nh.ellipsoid((0, 0, 1.05), (0.12, 0.12, 0.02), subdivisions=2), INSIDE)
    mb.add(ec.frond_disc(0.06, 0.02), SKIN_DARK)
    rng = random.Random(5)
    for i in range(16):
        z = 0.1 + 0.9 * i / 15
        r = radius_at(z)
        n = max(4, int(r * 45))
        for k in range(n):
            a = k / n * math.tau + (i % 2) * math.pi / n + rng.uniform(-0.1, 0.1)
            out = Vector((math.cos(a), math.sin(a), 0.0))
            c = Vector((0, 0, z)) + out * r
            up = Vector((0, 0, 1))
            side = out.cross(up)
            m = rng.choice([5, 6, 7])
            ln = 0.05 + 0.03 * r / 0.19
            for q in range(m):
                b = q / m * math.tau
                d = (side * math.cos(b) + up * math.sin(b)) * 0.9 + out * 0.35
                mb.add(ec.spike(c, c + d.normalized() * ln, r=0.005, sides=3), SPINE, smooth=False)
            mb.add(ec.spike(c, c + out * ln * 0.9, r=0.006, sides=3), SPINE, smooth=False)
    return ec.ground(mb.to_object("Chancelloria", roughness=0.55))


if __name__ == "__main__":
    ec.export(build, "Chancelloria", fixed=True)
