"""
Procedural Parapuzosia seppenradensis (Late Cretaceous desmoceratid ammonite, Campanian,
Westphalia, Germany), the largest known ammonite, for map colonies.

A huge, smooth, involute planispiral shell (up to about 1.8 m across): each tall, laterally
compressed whorl wraps over most of the previous one, leaving a small, deep umbilicus. The
flanks carry only faint, gently sinuous growth ribs and periodic constrictions. Pale
grey-cream with soft brown flank bands. The living animal sits in the aperture: a fleshy
head with large eyes and ten arms. The coil stands upright with the aperture at the bottom;
the animal faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/parapuzosia_seppenradensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Parapuzosia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.86, 0.82, 0.72)
GREY = (0.66, 0.63, 0.56)
BAND = (0.50, 0.38, 0.26)
DORSUM = (0.42, 0.36, 0.28)

W = 2.6                        # whorl expansion rate per turn
K = math.log(W) / math.tau
WHORLS = 3.5
A_END = -math.pi / 2           # aperture at the bottom of the coil
INVOLUTE = 0.55                # the inner edge of each whorl reaches this fraction of the previous outer radius
PHI = [0.0, 0.25, 0.55, 0.9, 1.3, 1.75, 2.2, 2.65]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """(u, v) of the compressed, oval whorl section: u radial (+1 venter), v lateral."""
    c, s = math.cos(phi), math.sin(phi)
    n = 2.2
    u = math.copysign(abs(c) ** (2 / n), c)
    v = math.copysign(abs(s) ** (2 / n), s)
    return u, v


def shell():
    rings, colors = [], []
    a = A_END - WHORLS * math.tau
    i = 0
    while True:
        w = (a - (A_END - WHORLS * math.tau)) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * INVOLUTE
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.42 * hh
        e = radial(a)
        rib = 1.0 if i % 2 == 0 else 0.0
        rib *= 1.0 - nh.smoothstep(0.93, 1.0, w)
        constr = nh.smoothstep(0.92, 1.0, math.cos(a * 5.0))        # periodic constrictions
        band = nh.smoothstep(0.5, 0.9, math.sin(a * 2.0 + 0.4))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            flank = nh.smoothstep(0.3, 0.7, ap) * (1 - nh.smoothstep(2.2, 2.7, ap))
            k = (1.0 + 0.025 * rib * flank - 0.05 * constr * flank) * (1.0 + 0.05 * nh.smoothstep(0.986, 1.0, w))
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, GREY, nh.smoothstep(0.3, 1.2, ap))
            col = nh.lerp(col, BAND, 0.55 * band * flank)
            col = nh.lerp(col, DORSUM, 0.7 * constr)
            col = tuple(x * (1.03 if rib else 0.95) for x in col)
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.3, 2.9, ap))
            cols.append(tuple(min(1.0, x) for x in col))
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        ribs = 22 + 30 * w
        a = min(A_END, a + math.tau / (2 * ribs))
        i += 1
    ro, rd = outer(A_END), outer(A_END - math.tau) * INVOLUTE
    return am.grid_mesh(rings, colors), radial(A_END) * (ro + rd) / 2, (ro - rd) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture + Vector((0, 0.02, 0)), (0, -1, 0), (0, 0, 1), hh * 0.44, arm_len=2.6, droop=0.45)
    obj = mb.to_object("Parapuzosia", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Parapuzosia", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
