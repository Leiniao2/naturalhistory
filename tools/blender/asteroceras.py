"""
Procedural Asteroceras (Early Jurassic arietitid ammonite) for map colonies.

An evolute planispiral shell swept along a logarithmic spiral: subquadrate
whorls that just overlap the previous one, strong straight ribs on the flanks
(alternate rings are pushed out, so each rib is one crisp ridge), and a tall
keel flanked by two grooves on the venter. Warm cream-to-tan with broad brown
bands. The living animal sits in the aperture: a fleshy head with big eyes and
ten arms. The coil stands upright with the aperture at the bottom; the animal
faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/asteroceras.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Asteroceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.90, 0.80, 0.62)
TAN = (0.74, 0.55, 0.33)
BAND = (0.46, 0.28, 0.14)
DORSUM = (0.52, 0.38, 0.24)

W = 2.1                        # whorl expansion rate per turn
K = math.log(W) / math.tau
WHORLS = 4.0
A_END = -math.pi / 2           # aperture at the bottom of the coil
# Cross-section samples, denser at the venter for the keel and its grooves.
PHI = [0.0, 0.13, 0.3, 0.5, 0.95, 1.6, 2.3]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    # 2D spiral (p, q) mapped to world: p -> -Y, q -> Z, so growth at the bottom heads -Y.
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """(u, v) of the whorl section: u radial (+1 venter), v lateral."""
    c, s = math.cos(phi), math.sin(phi)
    n = 2.6
    u = math.copysign(abs(c) ** (2 / n), c)
    v = math.copysign(abs(s) ** (2 / n), s)
    u += 0.17 * math.exp(-(phi / 0.1) ** 2)                      # keel
    u -= 0.07 * math.exp(-((abs(phi) - 0.3) / 0.09) ** 2)         # grooves beside it
    return u, v


def shell():
    rings, colors = [], []
    a = A_END - WHORLS * math.tau
    i = 0
    while True:
        w = (a - (A_END - WHORLS * math.tau)) / (WHORLS * math.tau)  # 0 inner .. 1 aperture
        ro = outer(a)
        rd = outer(a - math.tau) * 0.96
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.92 * hh
        e = radial(a)
        rib = 1.0 if i % 2 == 0 else 0.0
        rib *= 1.0 - nh.smoothstep(0.93, 1.0, w)          # smooth rim at the aperture
        band = nh.smoothstep(0.55, 0.9, math.sin(a * 3.0 + 0.6))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            flank = nh.smoothstep(0.35, 0.6, ap) * (1 - nh.smoothstep(1.9, 2.5, ap))
            k = (1.0 + 0.10 * rib * flank) * (1.0 + 0.07 * nh.smoothstep(0.986, 1.0, w))  # flared rim
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, TAN, nh.smoothstep(0.2, 0.9, ap))
            col = nh.lerp(col, BAND, 0.7 * band * (0.35 + 0.65 * flank))
            col = tuple(x * (1.06 if rib else 0.86) for x in col) if flank > 0.2 else col
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.0, 2.8, ap))
            cols.append(tuple(min(1.0, x) for x in col))
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        ribs = 11 + 17 * w                                   # ribs per whorl, more as it grows
        a = min(A_END, a + math.tau / (2 * ribs))
        i += 1
    return am.grid_mesh(rings, colors), radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * 0.96) / 2, \
        (outer(A_END) - outer(A_END - math.tau) * 0.96) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.9, arm_len=1.9, droop=0.45)
    obj = mb.to_object("Asteroceras", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Asteroceras", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
