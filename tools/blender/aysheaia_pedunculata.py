"""
Procedural low-poly Aysheaia pedunculata (Burgess Shale lobopodian).

A plump, finely ringed caterpillar-like body on ten pairs of stubby, annulated
lobopod legs, each ending in a fan of small curved claws; the front pair of
legs points forward. At the blunt head end, a terminal mouth ringed with
papillae and a pair of grasping frontal appendages bearing finger-like spines.
Body and legs are fused into one surface; claws and spines are crisp details.
Pale greyish rose with darker ring creases.
Faces -Y, pivot at the body centre (Swim, like Hallucigenia).

Output: Assets/Resources/Models/Species/Aysheaia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.86, 0.62, 0.56)
RING = (0.62, 0.38, 0.34)
CLAW = (0.25, 0.16, 0.12)
SPINE = (0.92, 0.82, 0.70)
MOUTH = (0.40, 0.20, 0.20)

Z = 0.11
LEG_Y = [-0.40 + 0.085 * i for i in range(10)]


def mid(y):
    return Vector((0.0, y, Z + 0.015 * math.sin(y * 5)))


def build():
    mb = nh.MeshBuilder()
    pts = [mid(-0.52 + 1.04 * i / 24) for i in range(25)]
    radii = [0.065 if -0.48 < p.y < 0.44 else 0.05 for p in pts]
    radii[0], radii[-1] = 0.04, 0.03
    mb.add(nh.tube(pts, radii, sides=12), BODY)
    feet = []
    for k, y in enumerate(LEG_Y):
        for s in (-1, 1):
            top = mid(y) + Vector((s * 0.035, 0, -0.02))
            fwd = -0.06 if k == 0 else 0.0
            foot = Vector((s * 0.1, y + fwd, 0.02))
            mb.add(nh.tube([top, top.lerp(foot, 0.5) + Vector((s * 0.02, 0, 0)), foot],
                           [0.034, 0.03, 0.026], sides=8), BODY)
            feet.append((foot, s))
    body = mb.fuse(voxel=0.01, smooth=4, max_tris=3000)

    def color(co, n):
        ring = 0.5 + 0.5 * math.cos(co.y * math.tau / 0.03) if co.z > 0.05 else 0.5 + 0.5 * math.cos(co.z * math.tau / 0.025)
        c = nh.lerp(BODY, RING, 0.5 * nh.smoothstep(0.65, 1.0, ring))
        if co.y < -0.555:
            c = nh.lerp(c, MOUTH, 0.8)
        return c

    out = nh.MeshBuilder()
    out.add(body, color)
    for foot, s in feet:
        for c in (-1, 0, 1):
            b = foot + Vector((s * 0.008, c * 0.012, 0.0))
            out.add(nh.tube([b, b + Vector((s * 0.02, c * 0.01, -0.005)), b + Vector((s * 0.025, c * 0.012 - 0.008, -0.015))],
                            [0.006, 0.004, 0.0], sides=4), CLAW, smooth=False)
    # frontal appendages with finger-like spines
    for s in (-1, 1):
        b = mid(-0.5) + Vector((s * 0.04, 0, 0.0))
        p1 = b + Vector((s * 0.05, -0.08, -0.02))
        p2 = p1 + Vector((s * 0.0, -0.08, -0.04))
        out.add(nh.tube([b, p1, p2], [0.022, 0.016, 0.008], sides=6), BODY)
        for q in range(4):
            p = b.lerp(p1, 0.5) if q == 0 else p1.lerp(p2, q / 3)
            out.add(ec.spike(p, p + Vector((s * 0.04, -0.01, 0.01)), r=0.006, sides=3), SPINE, smooth=False)
    # papillae around the mouth
    m = mid(-0.54)
    for q in range(7):
        a = q / 7 * math.tau
        p = m + Vector((math.cos(a) * 0.03, -0.015, math.sin(a) * 0.03))
        out.add(ec.spike(p, p + Vector((math.cos(a) * 0.012, -0.02, math.sin(a) * 0.012)), r=0.006, sides=3),
                SPINE, smooth=False)
    return ec.centre(out.to_object("Aysheaia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Aysheaia")
