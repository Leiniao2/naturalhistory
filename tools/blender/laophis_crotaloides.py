"""
Procedural Laophis crotaloides (Early Pliocene of northern Greece) for map
colonies: a giant viper, estimated at 3-4 m long and up to ~26 kg, the largest
viper known.

Built like an outsized Old World viper: a very heavy, thick body that narrows to a
short, abruptly tapering tail and to a slim neck, and a broad, flat, triangular head
far wider than the neck (the big venom glands behind the eyes), with a short
rounded snout and raised brows over the eyes. Rough, keeled dorsal scales (a fine
displaced diamond grain with ridges), broad belly plates. Colour pattern (unknown
in life; viper-like): a dark brown zigzag band down the back on grey-brown, dark
blotches along the flanks, a dark stripe from the eye to the jaw corner, pale belly.
Straight along Y so the map shader can bend it (Slither gait). Crisp eyes with
vertical pupils, nostrils and a forked tongue.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/laophis_crotaloides.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LaophisCrotaloides.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BASE = (0.50, 0.45, 0.37)
DARK = (0.20, 0.15, 0.11)
BELLY = (0.78, 0.74, 0.62)
EYE = (0.70, 0.50, 0.18)
PUPIL = (0.02, 0.02, 0.02)
TONGUE = (0.12, 0.08, 0.09)

LENGTH = 2.4
GIRTH = 0.115
HEAD_LEN = 0.23
HEAD_W = 0.16
NECK = 0.36
TAIL = 0.10


def radius(t):
    r = GIRTH * (NECK + (1 - NECK) * nh.smoothstep(0.0, 0.28, t))
    r *= 1.0 - nh.smoothstep(1 - TAIL - 0.22, 1.0, t) ** 0.8 * 0.95
    return r


def build():
    b = nh.MeshBuilder()
    n = 60
    y0 = -LENGTH / 2 + HEAD_LEN * 0.75
    pts, rr = [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (LENGTH / 2 - y0) * t
        r = max(radius(t), 0.012)
        pts.append((0, y, r * 0.85))
        rr.append(r)
    b.add(nh.tube(pts, rr, sides=18, scale_xy=(1.15, 0.85)), BASE)
    hy = -LENGTH / 2 + HEAD_LEN * 0.5
    hz = rr[0] * 0.75
    # triangular head: wide jowls at the back, short blunt snout in front
    b.add(nh.ellipsoid((0, hy + HEAD_LEN * 0.18, hz), (HEAD_W, HEAD_LEN * 0.36, HEAD_W * 0.48)), BASE)
    b.add(nh.ellipsoid((0, hy - HEAD_LEN * 0.12, hz + 0.004), (HEAD_W * 0.62, HEAD_LEN * 0.34, HEAD_W * 0.42)), BASE)
    b.add(nh.ellipsoid((0, hy - HEAD_LEN * 0.36, hz - 0.004), (HEAD_W * 0.34, HEAD_LEN * 0.18, HEAD_W * 0.32)), BASE)
    for sx in (-1, 1):  # venom-gland jowls
        b.add(nh.ellipsoid((sx * HEAD_W * 0.66, hy + HEAD_LEN * 0.24, hz - HEAD_W * 0.08),
                           (HEAD_W * 0.40, HEAD_LEN * 0.24, HEAD_W * 0.32)), BASE)
        b.add(nh.ellipsoid((sx * HEAD_W * 0.42, hy - HEAD_LEN * 0.08, hz + HEAD_W * 0.30),
                           (HEAD_W * 0.18, HEAD_LEN * 0.12, HEAD_W * 0.10)), BASE)           # brow
    fused = b.fuse(voxel=0.014, smooth=4, smooth_factor=0.5)
    fused.normal_update()
    head_end = -LENGTH / 2 + HEAD_LEN * 1.05
    # keeled scales: diamond grain on the back and flanks
    for v in fused.verts:
        if v.co.y < head_end - 0.05 or v.normal.z < -0.35:
            continue
        u = v.co.y * 70.0
        a = math.atan2(v.co.x, v.co.z - 0.05) * 9.0
        du = abs((u + a) % 1.0 - 0.5) + abs((u - a) % 1.0 - 0.5)
        keel = 1.0 - nh.smoothstep(0.0, 0.25, abs((a % 1.0) - 0.5))
        v.co += v.normal * (0.0025 * nh.smoothstep(0.1, 0.5, du) + 0.0015 * keel)
    fused.normal_update()
    body_len = LENGTH / 2 - head_end

    def zig(u):
        f = u % 1.0
        return (abs(f - 0.5) * 4 - 1)

    def paint(co, nrm):
        c = BASE
        c = nh.lerp(c, (0.42, 0.38, 0.31), 0.5 + 0.5 * noise.noise(co * 12))
        if co.y > head_end - 0.02:
            t = (co.y - head_end) / body_len
            r = max(radius(min(1.0, t * 0.92 + 0.05)), 0.02)
            zc = r * 0.85
            ang = math.atan2(co.x, co.z - zc + 0.0001)
            u = (co.y - head_end) / 0.12
            off = 0.48 * zig(u)
            band = 1.0 - nh.smoothstep(0.30, 0.40, abs(ang - off))
            c = nh.lerp(c, DARK, 0.92 * band)
            # flank blotches, alternating with the zigzag peaks
            side = nh.smoothstep(1.0, 1.25, abs(ang)) * (1 - nh.smoothstep(1.7, 1.95, abs(ang)))
            ph = (u + (0.5 if ang > 0 else 0.0)) % 1.0
            c = nh.lerp(c, DARK, 0.75 * side * (1 - nh.smoothstep(0.18, 0.28, abs(ph - 0.5))))
        else:
            # head: dark crown chevron and a dark stripe from the eye back to the jaw corner
            dy = co.y - hy
            crown = nh.smoothstep(0.5, 0.8, nrm.z) * (1 - nh.smoothstep(0.02, 0.035, abs(abs(co.x) * 1.2 - (dy + 0.10) * 0.55)))
            c = nh.lerp(c, DARK, 0.85 * crown * (dy > -0.06))
            stripe = (abs(nrm.z) < 0.55) * (1 - nh.smoothstep(0.008, 0.02, abs(co.z - (hz + 0.012) + dy * 0.18)))
            c = nh.lerp(c, DARK, 0.9 * stripe * (dy > -0.05))
        c = nh.lerp(c, BELLY, nh.smoothstep(-0.25, -0.6, nrm.z))
        return c

    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for sx in (-1, 1):
        e = Vector((sx * HEAD_W * 0.56, hy - HEAD_LEN * 0.08, hz + HEAD_W * 0.18))
        mb.add(nh.ellipsoid(tuple(e), (HEAD_W * 0.11,) * 3, subdivisions=2), EYE)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * HEAD_W * 0.08, 0, 0))), (HEAD_W * 0.035, HEAD_W * 0.025, HEAD_W * 0.09),
                            subdivisions=1), PUPIL)
        mb.add(nh.ellipsoid((sx * HEAD_W * 0.22, hy - HEAD_LEN * 0.52, hz + HEAD_W * 0.08), (HEAD_W * 0.04,) * 3,
                            subdivisions=1), PUPIL)  # nostrils
    tip = Vector((0, -LENGTH / 2 - HEAD_LEN * 0.02, hz - HEAD_W * 0.15))
    fork = tip + Vector((0, -HEAD_LEN * 0.4, -HEAD_W * 0.08))
    mb.add(nh.tube([tuple(tip + Vector((0, HEAD_LEN * 0.1, 0))), tuple(fork)], [HEAD_W * 0.035, HEAD_W * 0.03], sides=5),
           TONGUE)
    for sx in (-1, 1):
        mb.add(nh.tube([tuple(fork), tuple(fork + Vector((sx * HEAD_W * 0.12, -HEAD_LEN * 0.12, 0)))],
                       [HEAD_W * 0.025, 0.0], sides=5), TONGUE)
    obj = mb.to_object("LaophisCrotaloides")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "LaophisCrotaloides", ground=(0.45, 0.42, 0.30), views=((35, 30), (-90, 8), (0, 75), (20, 20)))
