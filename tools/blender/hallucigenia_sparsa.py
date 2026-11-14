"""
Procedural low-poly Hallucigenia sparsa (Burgess Shale lobopodian) for map colonies.

A thin, soft, tubular trunk held up on seven pairs of long, slender, stilt-like
legs, each tipped with a pair of tiny hooked claws; three pairs of thinner
tentacle-like appendages under the neck; seven pairs of long, rigid dorsal
spines fanning up and out in a V along the back; a slender neck curving down
and forward to a small rounded head with a pair of simple eyes and a dark ring
mouth; the rear end tapering and dipping a little. Pale pinkish-cream body with
tan, darker-based spines. Body and legs are fused into one seamless surface;
spines, claws and eyes are crisp details. Faces -Y, pivot at the body centre
(Swim style, like the other benthic Cambrian animals).

Usage:
  blender --background --python tools/blender/hallucigenia_sparsa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hallucigenia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.88, 0.70, 0.62)       # pale pinkish cream
BODY_BACK = (0.78, 0.56, 0.50)  # slightly darker along the back
ANNULUS = (0.68, 0.46, 0.40)    # soft ring creases
LEG = (0.90, 0.74, 0.66)
SPINE = (0.66, 0.44, 0.24)      # tan spine
SPINE_BASE = (0.36, 0.22, 0.14)
SPINE_TIP = (0.92, 0.80, 0.60)
CLAW = (0.22, 0.14, 0.10)
EYE = (0.05, 0.04, 0.05)
MOUTH = (0.40, 0.18, 0.16)

TRUNK_Z = 0.27          # height of the trunk midline above the feet
SPINE_Y = [-0.40 + 0.135 * i for i in range(7)]  # spine / walking-leg pairs, front to back
TENTACLE_Y = [-0.66, -0.60, -0.54]


def midline(t):
    """Body axis for t in 0 (head) .. 1 (tail tip): neck curls down and forward, tail dips."""
    y = -0.86 + 1.52 * t
    z = TRUNK_Z
    if y < -0.50:
        u = (-0.50 - y) / 0.36            # 0 at the neck base, 1 at the head
        z -= 0.13 * u ** 1.6
    if y > 0.46:
        u = (y - 0.46) / 0.20
        z -= 0.06 * u ** 2
    return Vector((0.0, y, z))


def trunk():
    n = 34
    pts, radii = [], []
    for i in range(n + 1):
        t = i / n
        p = midline(t)
        y = p.y
        if y < -0.74:
            r = 0.034                     # small rounded head
        elif y < -0.50:
            r = 0.026 + 0.012 * nh.smoothstep(-0.70, -0.50, y)  # slim neck
        else:
            r = 0.040 - 0.014 * nh.smoothstep(0.38, 0.66, y)
        pts.append(p)
        radii.append(r)
    radii[-1] = 0.012
    return nh.tube(pts, radii, sides=10)


def leg_points(y, side, length=0.27, spread=0.14, swing=0.0):
    """Stilt leg from the trunk's flank down to the foot, with a gentle outward knee bend."""
    top = midline((y + 0.86) / 1.52) + Vector((side * 0.025, 0, -0.015))
    foot = Vector((side * spread, y + swing, top.z - length))
    knee = top.lerp(foot, 0.45) + Vector((side * 0.035, 0, 0.01))
    return [top, knee, foot]


def tentacle_points(y, side):
    """Thin neck tentacle hanging down and forward."""
    top = midline((y + 0.86) / 1.52) + Vector((side * 0.015, 0, -0.012))
    mid = top + Vector((side * 0.035, -0.04, -0.07))
    tip = mid + Vector((side * 0.02, -0.06, -0.05))
    return [top, mid, tip]


def claws(mb, foot, direction, side):
    """Pair of small hooked claws at the end of a leg, pointing forward-down."""
    for s in (-1, 1):
        base = foot - direction * 0.012 + Vector((s * 0.008, 0, 0))
        mid = foot + Vector((s * 0.01, -0.018, -0.006))
        tip = mid + Vector((s * 0.004, -0.012, 0.008))
        mb.add(nh.tube([base, mid, tip], [0.0075, 0.005, 0.0], sides=4), CLAW, smooth=False)


def spine(mb, i, side):
    """Long dorsal spine: rigid, tapering, angled out and up, leaning slightly back."""
    y = SPINE_Y[i]
    base = midline((y + 0.86) / 1.52) + Vector((side * 0.012, 0, 0.03))
    length = 0.24 + 0.08 * math.sin(math.pi * (i + 1) / 8)  # middle spines the longest
    d = Vector((side * 0.42, 0.18 + 0.03 * i, 0.89)).normalized()
    mid = base + d * length * 0.5 + Vector((side * 0.008, 0, 0))
    tip = base + d * length
    pts = [base - d * 0.02, base + d * length * 0.2, mid, base + d * length * 0.8, tip]
    radii = [0.015, 0.013, 0.010, 0.006, 0.0]

    def color(co, n):
        t = max(0.0, min(1.0, (co - base).dot(d) / length))
        c = nh.lerp(SPINE_BASE, SPINE, nh.smoothstep(0.0, 0.3, t))
        return nh.lerp(c, SPINE_TIP, nh.smoothstep(0.65, 1.0, t))

    mb.add(nh.tube(pts, radii, sides=5), color)


def build():
    mb = nh.MeshBuilder()
    mb.add(trunk(), BODY)
    feet = []
    for k, y in enumerate(SPINE_Y):
        for side in (-1, 1):
            # legs splay a little fore and aft from the middle of the body
            pts = leg_points(y, side, swing=-0.03 * (3 - k) / 3)
            mb.add(nh.tube(pts, [0.017, 0.013, 0.009], sides=6), LEG)
            feet.append((pts[-1], (pts[-1] - pts[-2]).normalized(), side))
    for y in TENTACLE_Y:
        for side in (-1, 1):
            mb.add(nh.tube(tentacle_points(y, side), [0.012, 0.010, 0.008], sides=5), LEG)

    # rounded head bulb at the end of the neck
    mb.add(nh.ellipsoid(midline(0.03) + Vector((0, 0.0, 0.004)), (0.037, 0.05, 0.036), subdivisions=2), BODY)
    body = mb.fuse(voxel=0.008, smooth=4, smooth_factor=0.5, max_tris=2600)

    def color(co, n):
        c = nh.lerp(BODY, BODY_BACK, nh.smoothstep(0.1, 0.9, n.z) * nh.smoothstep(0.18, 0.24, co.z))
        on_trunk = co.z > 0.2 and co.y > -0.5
        if on_trunk:
            ring = 0.5 + 0.5 * math.cos(co.y * math.tau / 0.045)   # fine annulations
            c = nh.lerp(c, ANNULUS, 0.35 * nh.smoothstep(0.6, 1.0, ring))
        if co.y < -0.83:
            c = nh.lerp(c, MOUTH, nh.smoothstep(-0.83, -0.875, co.y))  # ring mouth at the snout
        return c

    out = nh.MeshBuilder()
    out.add(body, color)
    for i in range(7):
        for side in (-1, 1):
            spine(out, i, side)
    for foot, direction, side in feet:
        claws(out, foot, direction, side)
    # pair of simple eyes on top of the head
    head = midline(0.06)
    for s in (-1, 1):
        out.add(nh.ellipsoid(head + Vector((s * 0.018, -0.005, 0.026)), (0.009, 0.009, 0.008),
                             subdivisions=1), EYE)

    obj = out.to_object("Hallucigenia", roughness=0.45)
    # pivot at the body centre
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "Hallucigenia", background=(0.05, 0.22, 0.30), views=((35, 25), (-90, 6), (0, 75)))
