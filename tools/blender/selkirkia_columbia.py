"""
Procedural Selkirkia columbia (Burgess Shale tube-dwelling priapulid worm, ~7 cm).

A tough, slightly tapering, faintly ringed tube set upright in a low mud mound, open at the
top; from it the worm thrusts out its turned-out proboscis: a pink, rounded, spiny head
covered in rows of small backward-pointing hooks, with a ring of longer teeth round the
mouth. Brown-grey tube, pink proboscis, ivory hooks. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/selkirkia_columbia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Selkirkia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

TUBE = (0.50, 0.42, 0.34)
TUBE_DARK = (0.34, 0.28, 0.22)
WORM = (0.90, 0.58, 0.56)
HOOK = (0.96, 0.90, 0.80)
MOUTH = (0.30, 0.12, 0.12)
MUD = (0.56, 0.50, 0.40)


def build():
    mb = nh.MeshBuilder()
    tube_pts = kit.curve((0, 0, -0.02), (0.03, 0, 0.4), (0.06, 0.0, 0.8), 8)
    mb.add(nh.tube(tube_pts, [0.05 + 0.04 * i / 8 for i in range(9)], sides=14, cap_end=False),
           kit.ringed(TUBE, TUBE_DARK, period=0.06, sharp=0.15))
    top = Vector(tube_pts[-1])
    # trunk emerging, then the everted spiny proboscis
    neck = kit.curve(top - Vector((0, 0, 0.06)), top + Vector((0.01, 0, 0.08)), top + Vector((-0.04, -0.06, 0.2)), 5)
    mb.add(nh.tube(neck, [0.07, 0.07, 0.068, 0.066, 0.065, 0.065], sides=12), WORM)
    head_c = Vector(neck[-1]) + Vector((-0.01, -0.02, 0.06))
    mb.add(nh.ellipsoid(head_c, (0.075, 0.075, 0.09), subdivisions=3), WORM)
    for r in range(6):
        el = math.radians(-50 + r * 20)
        n = 12
        for k in range(n):
            a = k / n * math.tau + r * 0.25
            d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
            p = head_c + Vector((d.x * 0.075, d.y * 0.075, d.z * 0.09))
            mb.add(ec.spike(p, p + d * 0.02 - Vector((0, 0, 0.025)), r=0.006, sides=3), HOOK, smooth=False)
    mouth = head_c + Vector((0, 0, 0.09))
    mb.add(nh.ellipsoid(mouth, (0.025, 0.025, 0.01), subdivisions=2), MOUTH)
    for k in range(10):
        a = k / 10 * math.tau
        p = mouth + Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0))
        mb.add(ec.spike(p, p + Vector((math.cos(a) * 0.02, math.sin(a) * 0.02, 0.04)), r=0.006, sides=3), HOOK, smooth=False)
    mound = nh.uv_ellipsoid((0, 0, 0), (0.28, 0.28, 0.07), segments=24, rings=8)
    for v in mound.verts:
        v.co.z = max(v.co.z, 0.0)
    mb.add(mound, kit.mottled(MUD, 0.15, 8))
    return ec.ground(mb.to_object("Selkirkia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Selkirkia", fixed=True)
