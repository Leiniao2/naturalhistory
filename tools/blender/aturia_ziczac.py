"""
Procedural Aturia ziczac (Eocene-Miocene nautilid, warm seas worldwide) for map colonies (Swim
style, swims backward). A relative of the living pearly nautilus with a smooth, tightly coiled
(involute) shell about 10-15 cm across, compressed and streamlined, whose inner chamber walls
met the shell in deep zig-zag suture lines that give it its name. Modelled like a living
Nautilus: creamy shell with wavy red-brown flame stripes over the back half, a leathery
mottled hood over the head, a large pinhole eye on each side and a ring of many thin, short
tentacles in the aperture.
Coil upright, aperture at the bottom front; faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/aturia_ziczac.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AturiaZiczac.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "AturiaZiczac"
SHELL = (0.93, 0.88, 0.78)
FLAME = (0.55, 0.24, 0.12)
UMB = (0.40, 0.36, 0.30)
HOOD = (0.42, 0.26, 0.16)
HOOD_SPOT = (0.85, 0.78, 0.66)
FLESH = (0.80, 0.62, 0.50)
TENT = (0.88, 0.74, 0.62)
EYE = (0.04, 0.03, 0.03)

W = 3.2
K = math.log(W) / math.tau
WHORLS = 3.0
A_END = -math.pi / 2
N_PHI = 30
PHI = [(-math.pi + (i + 0.5) / N_PHI * math.tau) for i in range(N_PHI)]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    c, s = math.cos(phi), math.sin(phi)
    return math.copysign(abs(c) ** (2 / 2.4), c), math.copysign(abs(s) ** (2 / 2.4), s)


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    while True:
        ro = outer(a)
        rd = outer(a - math.tau) * 0.15     # fully involute: covers the earlier whorls
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.62 * hh
        e = radial(a)
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            ring.append(e * (rc + u * hh) + Vector((v * hw, 0, 0)))
            col = SHELL
            # wavy zig-zag flame stripes across the older half of the last whorl, fading forward
            z = a * 7.0 + 0.6 * abs(((ap * 3.0) % 2.0) - 1.0) * 2.0
            fl = math.sin(z)
            fade = nh.smoothstep(A_END - 0.25 * math.tau, A_END - 0.75 * math.tau, a)
            col = nh.lerp(col, FLAME, 0.85 * nh.smoothstep(0.35, 0.75, fl) * fade * nh.smoothstep(0.1, 0.6, ap))
            col = nh.lerp(col, UMB, nh.smoothstep(2.6, 3.0, ap))
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        visible = a > A_END - 1.3 * math.tau
        a = min(A_END, a + math.tau / (90 if visible else 24))
    ap = radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * 0.4) / 2
    return am.grid_mesh(rings, colors), ap, (outer(A_END) - outer(A_END - math.tau) * 0.4) / 2


def soft(mb, o, r):
    o = Vector(o)
    f, s, u = Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))

    def at(a, b, c):
        return o + f * (a * r) + s * (b * r) + u * (c * r)

    def flesh(co, n):
        return nh.lerp(TENT, FLESH, nh.smoothstep(-0.6, 0.6, (co - o).dot(u) / r))
    mb.add(nh.tube([at(-0.4, 0, 0), at(0.2, 0, 0), at(0.7, 0, -0.05)], [0.85 * r, 0.9 * r, 0.75 * r], sides=12,
                   scale_xy=(1.0, 0.85)), flesh)

    # leathery hood over the top of the head
    def hood(co, n):
        m = noise.noise(co * (10.0 / r))
        return nh.lerp(HOOD, HOOD_SPOT, 0.75 * nh.smoothstep(0.25, 0.45, m))
    mb.add(nh.ellipsoid(tuple(at(0.35, 0, 0.45)), (0.85 * r, 0.65 * r, 0.42 * r), subdivisions=3), hood)
    # large pinhole eyes
    for sx in (-1, 1):
        c = at(0.25, sx * 0.86, 0.05)
        mb.add(nh.ellipsoid(tuple(c), (0.16 * r, 0.3 * r, 0.3 * r), subdivisions=2), (0.55, 0.45, 0.38))
        mb.add(nh.ellipsoid(tuple(c + s * sx * 0.12 * r), (0.06 * r, 0.12 * r, 0.12 * r), subdivisions=2), EYE)
    # many thin tentacles in a ring, short and splayed
    n = 26
    for i in range(n):
        a = (i + 0.5) / n * math.tau
        ca, sa = math.cos(a), math.sin(a)
        base = at(0.7, 0.55 * ca, 0.45 * sa - 0.1)
        d = (f + (s * ca + u * sa * 0.6) * 0.55 - u * 0.25).normalized()
        L = r * (1.0 + 0.35 * ((i * 7) % 5) / 4)
        pts = [base, base + d * L * 0.5, base + (d - u * 0.2).normalized() * L]
        mb.add(nh.tube([tuple(p) for p in pts], [0.07 * r, 0.05 * r, 0.02 * r], sides=4), TENT)
    # funnel
    mb.add(nh.tube([tuple(at(0.2, 0, -0.6)), tuple(at(0.65, 0, -0.8))], [0.2 * r, 0.15 * r], sides=6), FLESH)


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    soft(mb, aperture + Vector((0, 0.04, 0)), hh * 0.8)
    obj = mb.to_object(NAME, roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 20), (-90, 5), (0, 10)))
