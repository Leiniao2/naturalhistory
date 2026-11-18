"""
Procedural Corumbella werneri (latest Ediacaran, Brazil / Paraguay / USA): a slender, upright,
four-sided tube built of a stack of overlapping rings of small hardened plates, narrowing to
a small attachment at the base; four darker grooves run down the corners (its four-fold
symmetry). At the open top the soft polyp shows a small ring of pale tentacles.
Grey-brown armour with paler ring edges. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/corumbella_werneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Corumbella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

PLATE = (0.52, 0.48, 0.42)
EDGE = (0.80, 0.76, 0.66)
GROOVE = (0.24, 0.20, 0.17)
TENT = (0.92, 0.80, 0.70)
N = 22
H = 1.2


def axis(t):
    return Vector((0.12 * math.sin(t * 2.2), 0.05 * t * t, t * H))


def build():
    mb = nh.MeshBuilder()
    sides = 16
    for i in range(N):
        t0, t1 = i / N, (i + 1.3) / N
        r0 = 0.04 + 0.1 * t0 ** 0.6
        r1 = 0.04 + 0.1 * min(1.0, t1) ** 0.6
        p0, p1 = axis(t0), axis(min(t1, 1.0))
        # square-ish cross-section: radius bulges between the four corner grooves
        ring = nh.tube([p0, p0.lerp(p1, 0.7), p1], [r0 * 0.96, r1 * 1.02, r1 * 1.12], sides=sides)
        for v in ring.verts:
            a = math.atan2(v.co.y - p0.y, v.co.x - p0.x)
            v.co.x = p0.x + (v.co.x - p0.x) * (1 - 0.1 * abs(math.cos(2 * a)))
            v.co.y = p0.y + (v.co.y - p0.y) * (1 - 0.1 * abs(math.cos(2 * a)))

        def col(co, n, z0=p0.z, z1=p1.z, c=p0):
            u = (co.z - z0) / max(z1 - z0, 1e-4)
            a = math.atan2(co.y - c.y, co.x - c.x)
            g = nh.smoothstep(0.9, 1.0, abs(math.sin(2 * a)))
            base = nh.lerp(PLATE, EDGE, nh.smoothstep(0.6, 1.0, u))
            return nh.lerp(base, GROOVE, g * 0.85)
        mb.add(ring, col)
    mb.add(ec.frond_disc(0.07, 0.025), GROOVE)
    top = axis(1.0) + Vector((0, 0, 0.02))
    mb.add(nh.ellipsoid(top, (0.1, 0.1, 0.03), subdivisions=2), TENT)
    kit.crown(mb, top, 0.08, 16, 0.14, 0.008, TENT, spread=40, droop=-0.3, seed=2)
    return ec.ground(mb.to_object("Corumbella", roughness=0.55))


if __name__ == "__main__":
    ec.export(build, "Corumbella", fixed=True)
