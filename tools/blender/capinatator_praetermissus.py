"""
Procedural Capinatator praetermissus (Burgess Shale giant arrow worm, ~10 cm).

A long, slim, torpedo-shaped body; a rounded head ringed by a crown of about 50 long,
curved grasping spines in two fans (about 25 a side) that close over prey; a pair of
lateral fins on the rear body and a broad, rounded tail fin. Translucent amber-cream body with
darker gut line, glossy dark amber spines. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/capinatator_praetermissus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Capinatator.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.88, 0.80, 0.66)
GUT = (0.62, 0.46, 0.30)
FIN = (0.94, 0.90, 0.80)
SPINE = (0.42, 0.24, 0.10)
SPINE_TIP = (0.20, 0.10, 0.04)
EYE = (0.05, 0.04, 0.03)


def build():
    mb = nh.MeshBuilder()
    pts = [(0, -0.6 + 1.3 * i / 16, 0) for i in range(17)]
    radii = [0.06, 0.075, 0.07, 0.065, 0.065, 0.066, 0.066, 0.065, 0.062, 0.058, 0.053, 0.047, 0.04, 0.033, 0.025, 0.015, 0.0]
    mb.add(nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.85)),
           lambda co, n: nh.lerp(GUT, BODY, nh.smoothstep(0.01, 0.035, abs(co.x)) * 0.6 + 0.4 * nh.smoothstep(-0.5, 0.5, n.z)))
    mb.add(nh.uv_ellipsoid((0, -0.62, 0.0), (0.08, 0.07, 0.065), segments=14, rings=8), BODY)
    # lateral fins and tail fin
    for s in (-1, 1):
        f = nh.flat_panel([(0, 0.15, 0), (0.1, 0.25, 0), (0.12, 0.38, 0), (0.0, 0.48, 0)], thickness=0.008)
        ec.mirror(f, s)
        nh.transform(f, Matrix.Translation((s * 0.03, 0, 0)))
        mb.add(f, FIN, smooth=False)
    tail = nh.flat_panel([(0, 0.62, 0), (-0.13, 0.72, 0), (-0.1, 0.84, 0), (0, 0.8, 0), (0.1, 0.84, 0), (0.13, 0.72, 0)], thickness=0.008)
    mb.add(tail, FIN, smooth=False)
    # grasping spine crown: two fans curving forward and in
    for s in (-1, 1):
        for k in range(25):
            a = math.radians(-80 + 160 * k / 24)
            root = Vector((s * 0.05, -0.64, 0.0)) + Vector((0, 0, math.sin(a) * 0.05)) + Vector((s * 0.01 * math.cos(a), 0, 0))
            out = Vector((s * math.cos(a) * 0.7, -0.35, math.sin(a) * 0.9)).normalized()
            ln = 0.2 + 0.05 * math.cos(a)
            tip = root + out * ln * 0.75 + Vector((-s * ln * 0.25, -ln * 0.45, -math.sin(a) * ln * 0.15))
            mid = root + out * ln * 0.6
            mb.add(nh.tube(kit.curve(root, mid, tip, 4), [0.008, 0.007, 0.005, 0.003, 0.0], sides=4),
                   lambda co, n, r=root, ln=ln: nh.lerp(SPINE, SPINE_TIP, nh.smoothstep(0.1, 0.25, (co - r).length)), smooth=False)
        mb.add(nh.ellipsoid((s * 0.035, -0.6, 0.055), (0.012, 0.012, 0.01), subdivisions=1), EYE)
    return ec.centre(mb.to_object("Capinatator", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Capinatator")
