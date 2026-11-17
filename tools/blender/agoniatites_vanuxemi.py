"""
Procedural Agoniatites vanuxemi for the map: one of the early goniatites (ammonoids of the
order Agoniatitida) from the Middle Devonian (Eifelian-Givetian, about 390 million years
ago) Marcellus Shale and Onondaga rocks of New York, also found in Europe and North
Africa; shells about 10-15 cm across.

A smooth, flattened (discoidal), rather open-coiled shell with a wide umbilicus, whorls
only partly covering the previous one, and fine growth lines that swing sharply back on
the flanks and outer edge (the deep ventral sinus typical of early goniatites); inside,
simple zig-zag "goniatitic" sutures. Early ammonoids like this were slow swimmers that
fed on small prey and plankton.

Shell swept along a logarithmic spiral with the nh_ammonite helpers; the soft body
(head, eyes, ten arms) sits in the aperture. Colours are unknown: cream with brown
growth-line banding. The coil stands upright with the aperture at the bottom; the
animal faces -Y, pivot at the body centre (Swim style, swims backward).

Usage:
  blender --background --python tools/blender/agoniatites_vanuxemi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Agoniatites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.88, 0.80, 0.64)
TAN = (0.70, 0.56, 0.38)
LINE = (0.50, 0.36, 0.22)
BAND = (0.42, 0.28, 0.16)
DORSUM = (0.50, 0.38, 0.26)

W = 1.95
K = math.log(W) / math.tau
WHORLS = 4.5
A_END = -math.pi / 2
PHI = [0.0, 0.2, 0.45, 0.8, 1.2, 1.7, 2.3, 2.8]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    c, s = math.cos(phi), math.sin(phi)
    return math.copysign(abs(c) ** (2 / 2.2), c), math.copysign(abs(s) ** (2 / 2.2), s)


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    i = 0
    while True:
        w = (a - a0) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * 0.80        # evolute: little overlap of the previous whorl
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.62 * hh                          # compressed whorl
        e = radial(a)
        band = nh.smoothstep(0.6, 0.95, math.sin(a * 2.0 + 0.4))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            k = 1.0 + 0.05 * nh.smoothstep(0.985, 1.0, w)
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, TAN, nh.smoothstep(0.3, 1.4, ap))
            # fine growth lines (every other ring darker), swept back by the angle offset
            gl = 0.5 + 0.5 * math.cos(a * 22.0 - 1.2 * math.sin(ap) - 0.8 * math.exp(-(ap / 0.4) ** 2))
            col = nh.lerp(col, LINE, 0.4 * nh.smoothstep(0.7, 1.0, gl))
            col = nh.lerp(col, BAND, 0.55 * band * nh.smoothstep(0.2, 0.8, ap))
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.2, 2.9, ap))
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        a = min(A_END, a + math.tau / 48)
        i += 1
    ap = radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * 0.80) / 2
    return am.grid_mesh(rings, colors), ap, (outer(A_END) - outer(A_END - math.tau) * 0.80) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.62, arm_len=1.9, droop=0.45)
    obj = mb.to_object("Agoniatites", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Agoniatites", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
