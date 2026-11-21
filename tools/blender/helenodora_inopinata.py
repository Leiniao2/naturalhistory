"""
Procedural Helenodora inopinata (Late Carboniferous of Mazon Creek, Illinois, a velvet worm
about 5 cm long) for map colonies (Ground style).

A soft, caterpillar-like onychophoran crawling on a gentle S-curve: one seamless fused
body, round in section and tapering at both ends, ringed all along by fine annuli of
tiny papillae (painted as alternating light and dark rings), carried on sixteen pairs of
short, stubby, conical lobopod legs, each ending in a pale foot with two tiny claws; at
the front a pair of ringed antennae curving forward and up, little dark eyes at their
bases and a pale mouth cone underneath. Dark slate blue-grey above, brownish, paler
underside. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/helenodora_inopinata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Helenodora.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "Helenodora"
BACK = (0.20, 0.22, 0.30)
BACK2 = (0.30, 0.30, 0.38)
SIDE = (0.36, 0.30, 0.28)
BELLY = (0.62, 0.52, 0.44)
LEG = (0.42, 0.36, 0.36)
FOOT = (0.75, 0.66, 0.56)
CLAW = (0.12, 0.10, 0.08)
EYE = (0.02, 0.02, 0.02)

L = 1.5
R = 0.085
Z = 0.10
NLEG = 16


def centre(t):
    y = -L / 2 + t * L
    x = 0.08 * math.sin(t * math.pi * 1.8 + 0.3)
    z = Z + 0.012 * math.sin(t * math.pi * 6)
    return Vector((x, y, z))


def radius(t):
    return R * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.08 + t * 0.92)) ** 0.5)


def build():
    body = nh.MeshBuilder()
    n = 60
    pts = [centre(i / n) for i in range(n + 1)]
    rads = [radius(i / n) for i in range(n + 1)]
    rads[0] = rads[-1] = 0.0
    body.add(nh.tube(pts, rads, sides=14), BACK)
    legs = []
    for i in range(NLEG):
        t = 0.1 + 0.85 * i / (NLEG - 1)
        c = centre(t)
        fwd = (centre(t + 0.01) - centre(t - 0.01)).normalized()
        side = Vector((-fwd.y, fwd.x, 0)).normalized()
        r = radius(t)
        for sx in (-1, 1):
            root = c + side * sx * r * 0.55 + Vector((0, 0, -r * 0.45))
            foot = Vector((root.x, root.y, 0)) + side * sx * r * 1.15 + fwd * (0.02 * math.sin(i * 1.3 + sx))
            foot.z = 0.012
            body.add(nh.tube([root, root.lerp(foot, 0.5), foot], [r * 0.42, r * 0.32, r * 0.2], sides=8), LEG)
            legs.append((foot, side * sx, fwd))
    # head lobe
    h = centre(0.0) + Vector((0, 0.03, 0))
    body.add(nh.ellipsoid(tuple(h), (R * 0.62, R * 0.7, R * 0.58), 2), BACK)
    fused = body.fuse(voxel=0.012, smooth=4, max_tris=5000)

    def paint(co, n):
        t = (co.y + L / 2) / L
        c = centre(max(0.0, min(1.0, t)))
        up = (co.z - c.z) / max(radius(max(0.0, min(1.0, t))), 1e-3)
        ring = (t * 70.0) % 1.0
        top = BACK2 if ring < 0.5 else BACK
        col = nh.lerp(SIDE, top, nh.smoothstep(-0.3, 0.5, up))
        col = nh.lerp(col, BELLY, nh.smoothstep(-0.35, -0.85, up))
        if co.z < Z * 0.55 and abs(up) > 0.9:   # legs
            col = nh.lerp(LEG, FOOT, nh.smoothstep(0.05, 0.02, co.z))
        k = 0.9 + 0.2 * (0.5 + 0.5 * noise.noise(co * 60.0))
        return (col[0] * k, col[1] * k, col[2] * k)

    mb = nh.MeshBuilder()
    mb.add(fused, paint)
    # claws
    for foot, out, fwd in legs:
        for k in (-1, 1):
            b = foot + out * 0.012 + fwd * 0.006 * k
            mb.add(nh.tube([b, b + (out * 0.7 + fwd * 0.3 * k).normalized() * 0.02 + Vector((0, 0, -0.008))],
                           [0.004, 0.0], sides=3), CLAW)
    # antennae, eyes, mouth
    h0 = centre(0.0)
    for sx in (-1, 1):
        a0 = h0 + Vector((sx * R * 0.3, -0.02, R * 0.2))
        pts = [a0]
        d = Vector((sx * 0.3, -1, 0.35)).normalized()
        for k in range(7):
            d = (d + Vector((sx * 0.05, 0, -0.07))).normalized()
            pts.append(pts[-1] + d * 0.045)
        rr = [0.018 - 0.002 * k for k in range(len(pts) - 1)] + [0.004]

        def ant(co, nn, a0=a0):
            return BACK2 if ((co - a0).length * 60) % 1.0 < 0.5 else BACK
        mb.add(nh.tube(pts, rr, sides=6), ant)
        mb.add(nh.ellipsoid(tuple(h0 + Vector((sx * R * 0.45, 0.0, R * 0.35))), (0.011, 0.011, 0.011), 1), EYE)
    mb.add(nh.ellipsoid(tuple(h0 + Vector((0, 0.02, -R * 0.45))), (0.025, 0.02, 0.012), 1), FOOT)

    obj = mb.to_object(NAME, roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.24, 0.22, 0.14), background=(0.20, 0.28, 0.18),
           views=((35, 30), (0, 80), (-90, 8)))
