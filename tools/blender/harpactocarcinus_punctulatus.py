"""
Procedural Harpactocarcinus punctulatus (Eocene true crab, shallow seas of Europe) for map
colonies. One of the commonest fossil crabs of the Eocene, about 10 cm across: a broad, smooth,
oval carapace wider than long, finely dotted (punctate) all over, with a toothed front edge
between small eyes on stalks, a pair of strong claws of unequal size (a heavy crusher and a
slimmer cutter), and four pairs of walking legs. Red-brown back fading to cream at the edges,
dark claw tips.
Faces -Y, pivot at the body centre (Swim, a seabed crawler).

Usage:
  blender --background --python tools/blender/harpactocarcinus_punctulatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HarpactocarcinusPunctulatus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.62, 0.30, 0.17)
EDGE = (0.88, 0.70, 0.48)
DOT = (0.36, 0.15, 0.08)
UNDER = (0.90, 0.80, 0.62)
LEG = (0.70, 0.40, 0.22)
TIP = (0.12, 0.08, 0.06)
EYE = (0.05, 0.04, 0.04)

W, D = 0.62, 0.42  # carapace half-width / half-length


def shell_col(co, n):
    r = math.sqrt((co.x / W) ** 2 + ((co.y + 0.02) / D) ** 2)
    c = nh.lerp(SHELL, EDGE, nh.smoothstep(0.75, 1.0, r))
    if n.z < -0.2:
        return UNDER
    # faint grooves outlining the gastric and cardiac regions
    g = abs(math.sqrt((co.x / 0.22) ** 2 + ((co.y + 0.05) / 0.2) ** 2) - 1.0)
    c = nh.lerp(c, DOT, 0.35 * (1 - nh.smoothstep(0.0, 0.12, g)))
    return c


def leg_col(co, n):
    return LEG if n.z > -0.3 else UNDER


def build():
    mb = nh.MeshBuilder()

    # carapace: broad smooth dome, flat-ish underside; slight bulge forward
    def dome(v):
        return 1.0
    shell = nh.uv_ellipsoid((0, 0, 0.0), (W, D, 0.2), segments=40, rings=20)
    for v in shell.verts:
        if v.co.z < 0:
            v.co.z *= 0.45
        # front edge a little straighter
        if v.co.y < -0.25:
            v.co.y = -0.25 + (v.co.y + 0.25) * 0.75
    mb.add(shell, shell_col)
    # fine punctate dots over the top of the carapace
    import random
    rnd = random.Random(4)
    for _ in range(90):
        x, y = rnd.uniform(-0.9, 0.9), rnd.uniform(-0.85, 0.9)
        if x * x + y * y > 0.8:
            continue
        z = 0.2 * math.sqrt(max(0.0, 1 - x * x - y * y))
        nrm = Vector((x / W, y / D, z / 0.04 if z > 0 else 1)).normalized()
        p = Vector((x * W, y * D, z))
        mb.add(nh.ellipsoid(tuple(p), (0.012, 0.012, 0.006), subdivisions=1), DOT)
    # small teeth along the front-lateral margin
    for i in range(7):
        a = math.radians(200 + i * 14)
        for sx in (1, -1):
            p = Vector((sx * abs(math.cos(a)) * W * 0.98, math.sin(a) * D * 0.82, 0.01))
            d = Vector((p.x, p.y, 0)).normalized()
            mb.add(nh.tube([tuple(p - d * 0.02), tuple(p + d * 0.05)], [0.022, 0.0], sides=5), EDGE)
    # front between the eyes: four small rostral teeth
    for x in (-0.09, -0.03, 0.03, 0.09):
        mb.add(nh.tube([(x, -0.3, 0.02), (x, -0.36, 0.01)], [0.02, 0.0], sides=5), EDGE)
    # eyes on short stalks in sockets
    for sx in (1, -1):
        b = Vector((sx * 0.17, -0.3, 0.04))
        t = b + Vector((sx * 0.03, -0.07, 0.03))
        mb.add(nh.tube([tuple(b), tuple(t)], [0.025, 0.022], sides=6), SHELL)
        mb.add(nh.uv_ellipsoid(tuple(t), (0.03, 0.03, 0.03), segments=8, rings=6), EYE)

    # walking legs: four pairs, jointed, splayed
    for sx in (1, -1):
        for k in range(4):
            ang = math.radians(-25 + k * 30)
            base = Vector((sx * W * 0.7, -0.08 + k * 0.11, -0.04))
            d = Vector((sx * math.cos(ang), math.sin(ang), 0))
            knee = base + d * 0.3 + Vector((0, 0, 0.12))
            tip = knee + d * 0.33 + Vector((0, 0, -0.22))
            mb.add(nh.tube([tuple(base), tuple(knee)], [0.045, 0.038], sides=7), leg_col)
            mb.add(nh.tube([tuple(knee), tuple(knee * 0.5 + tip * 0.5), tuple(tip)], [0.036, 0.028, 0.0],
                           sides=7), leg_col)

    # claws: right one a heavy crusher, left one slimmer
    for sx, big in ((1, 1.0), (-1, 0.72)):
        b = Vector((sx * 0.4, -0.25, -0.03))
        elbow = b + Vector((sx * 0.22, -0.18, 0.05))
        wrist = elbow + Vector((-sx * 0.06, -0.18, 0.02))
        mb.add(nh.tube([tuple(b), tuple(elbow)], [0.05, 0.055], sides=8), leg_col)
        mb.add(nh.tube([tuple(elbow), tuple(wrist)], [0.055, 0.065], sides=8), leg_col)
        palm_c = wrist + Vector((-sx * 0.05, -0.12 * big, 0.0))
        mb.add(nh.uv_ellipsoid(tuple(palm_c), (0.11 * big, 0.17 * big, 0.1 * big), segments=14, rings=10),
               leg_col)
        fdir = Vector((-sx * 0.45, -1.0, 0)).normalized()
        f0 = palm_c + fdir * 0.13 * big
        # fixed finger and movable dactyl, slightly open, dark tips
        fixed = [tuple(f0 + Vector((sx * 0.02, 0, -0.02))), tuple(f0 + fdir * 0.12 * big + Vector((0, 0, -0.03))),
                 tuple(f0 + fdir * 0.2 * big + Vector((0, 0, -0.02)))]
        dact = [tuple(f0 + Vector((sx * 0.02, 0, 0.04))), tuple(f0 + fdir * 0.12 * big + Vector((0, 0, 0.06))),
                tuple(f0 + fdir * 0.21 * big + Vector((0, 0, 0.03)))]
        tip_col = lambda co, n, f0=f0, big=big: TIP if (co - f0).length > 0.12 * big else LEG
        mb.add(nh.tube(fixed, [0.045 * big, 0.03 * big, 0.0], sides=7), tip_col)
        mb.add(nh.tube(dact, [0.04 * big, 0.028 * big, 0.0], sides=7), tip_col)

    obj = mb.to_object("HarpactocarcinusPunctulatus", roughness=0.45)
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) * 0.5
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "HarpactocarcinusPunctulatus", background=(0.05, 0.20, 0.26), views=((35, 35), (-90, 5), (0, 70)))
