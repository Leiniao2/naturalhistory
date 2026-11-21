"""
Procedural Acanthotelson stimpsoni (Late Carboniferous of Mazon Creek, Illinois, a syncarid
crustacean about 6 cm long) for map colonies (Swim style).

A shrimp without a carapace, so every segment shows: a small head with two pairs of long
antennae (the inner pair split in two) and stalked dark eyes, eight similar thoracic segments
carrying long, spiny walking legs that hang down and forward, six abdominal segments curving
gently down, small swimming legs beneath, and a tail fan of four paddle-shaped uropods
round a long, spiny telson. Translucent tan-orange with darker segment margins.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/acanthotelson_stimpsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Acanthotelson.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Acanthotelson"
BODY = (0.86, 0.56, 0.32)
EDGE = (0.56, 0.30, 0.16)
BELLY = (0.95, 0.80, 0.62)
LEG = (0.84, 0.58, 0.36)
SPINE = (0.98, 0.88, 0.70)
EYE = (0.05, 0.04, 0.04)
ANT = (0.70, 0.44, 0.24)


def centre(t):
    """Body centre line: t = 0 head .. 1 telson base; the abdomen curves down."""
    y = -0.55 + t * 1.05
    z = 0.03 * math.sin(t * math.pi) - 0.16 * max(0.0, (t - 0.55) / 0.45) ** 2
    return Vector((0, y, z))


def segcol(c, L):
    def col(co, n):
        d = co.y - c.y
        if n.z < -0.3:
            return BELLY
        return EDGE if d > L * 0.55 else BODY
    return col


def build():
    mb = nh.MeshBuilder()
    body = nh.MeshBuilder()
    nseg = 15   # head + 8 thoracic + 6 abdominal
    for i in range(nseg):
        t = i / (nseg - 1)
        c = centre(t)
        L = 1.05 / nseg
        if i == 0:
            w, h = 0.045, 0.05
        elif i <= 8:
            w, h = 0.05, 0.068
        else:
            k = (i - 8) / 6
            w, h = 0.05 - 0.018 * k, 0.068 - 0.03 * k
        body.add(nh.uv_ellipsoid(tuple(c), (w, L * 1.15, h), 12, 8), BODY)
        # pleura: side flaps hanging over the leg bases
        for sx in (-1, 1):
            body.add(nh.ellipsoid(tuple(c + Vector((sx * w * 0.8, 0, -h * 0.35))), (0.012, L * 0.5, h * 0.55), 1), BODY)
        side_y = c.y
        if 1 <= i <= 8:
            # walking legs: long, jointed, spiny, hanging down and forward
            for sx in (-1, 1):
                root = c + Vector((sx * w * 0.7, 0, -h * 0.6))
                knee = root + Vector((sx * 0.07, -0.03, -0.04))
                foot = knee + Vector((sx * 0.03, -0.05 - 0.005 * i, -0.08))
                mb.add(nh.tube([root, knee, foot], [0.008, 0.006, 0.003], sides=4), LEG)
                for k in (0.3, 0.6):
                    q = knee.lerp(foot, k)
                    mb.add(nh.tube([q, q + Vector((sx * 0.012, 0.012, 0.004))], [0.003, 0.0], sides=3), SPINE)
        elif i > 8:
            for sx in (-1, 1):
                root = c + Vector((sx * w * 0.5, 0, -h * 0.8))
                mb.add(nh.tube([root, root + Vector((sx * 0.02, 0.02, -0.04))], [0.006, 0.002], sides=4), LEG)

    fused = body.fuse(voxel=0.008, smooth=3, max_tris=3000)

    def body_col(co, n):
        t = (co.y + 0.55) / 1.05 * (nseg - 1)
        f = t - math.floor(t + 0.5)
        if n.z < -0.4:
            return BELLY
        c = EDGE if 0.22 < f < 0.42 else BODY
        return nh.lerp(c, BELLY, 0.35 * nh.smoothstep(0.0, -0.4, n.z))
    mb.add(fused, body_col)

    # head: eyes on stalks, antennae
    h0 = centre(0.0)
    for sx in (-1, 1):
        b = h0 + Vector((sx * 0.035, -0.03, 0.02))
        tip = b + Vector((sx * 0.035, -0.02, 0.012))
        mb.add(nh.tube([b, tip], [0.010, 0.009], sides=5), BODY)
        mb.add(nh.ellipsoid(tuple(tip + Vector((sx * 0.006, -0.004, 0))), (0.016, 0.016, 0.016), 2), EYE)
        # outer antenna (long)
        a0 = h0 + Vector((sx * 0.04, -0.05, -0.01))
        pts = [a0]
        d = Vector((sx * 0.25, -1, 0.1)).normalized()
        for k in range(8):
            d = (d + Vector((sx * 0.07, 0.05, 0.0))).normalized()
            pts.append(pts[-1] + d * 0.09)
        mb.add(nh.tube(pts, [0.006] + [0.004] * (len(pts) - 2) + [0.0], sides=4), ANT)
        # inner antenna: two flagella
        a1 = h0 + Vector((sx * 0.018, -0.055, 0.0))
        for f in (0, 1):
            pts = [a1]
            d = Vector((sx * (0.1 + 0.15 * f), -1, 0.15 - 0.1 * f)).normalized()
            for k in range(4):
                d = (d + Vector((sx * 0.05, 0.03, 0))).normalized()
                pts.append(pts[-1] + d * 0.07)
            mb.add(nh.tube(pts, [0.004] * (len(pts) - 1) + [0.0], sides=3), ANT)
        # antennal scale
        mb.add(nh.ellipsoid(tuple(h0 + Vector((sx * 0.05, -0.08, -0.01))), (0.018, 0.04, 0.006), 1), BODY)

    # tail fan: telson with marginal spines, two pairs of uropods
    tb = centre(1.0) + Vector((0, 0.03, 0))
    tel_tip = tb + Vector((0, 0.22, -0.04))
    mb.add(nh.tube([tb, tb.lerp(tel_tip, 0.5), tel_tip], [0.03, 0.022, 0.0], sides=6, scale_xy=(1.0, 0.35)), BODY)
    for k in range(5):
        q = tb.lerp(tel_tip, 0.2 + 0.15 * k)
        for sx in (-1, 1):
            mb.add(nh.tube([q, q + Vector((sx * 0.025, 0.02, 0))], [0.004, 0.0], sides=3), SPINE)
    for sx in (-1, 1):
        for k, (ang, L) in enumerate(((0.3, 0.30), (0.65, 0.26))):
            d = Vector((sx * math.sin(ang), math.cos(ang), -0.12)).normalized()
            base = tb + Vector((sx * 0.02, 0.0, 0))
            mb.add(nh.tube([base, base + d * L * 0.5, base + d * L], [0.012, 0.05, 0.0], sides=6,
                           scale_xy=(1.0, 0.2)), EDGE if k else BODY)

    obj = mb.to_object(NAME, roughness=0.35)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.06, 0.18, 0.22), views=((35, 25), (0, 85), (-90, 8)))
