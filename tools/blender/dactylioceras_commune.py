"""
Procedural Dactylioceras commune (Early Jurassic dactylioceratid ammonite) for map colonies.

The famous "snakestone" of Whitby: a flat, very evolute (serpenticone) shell up to about
8 cm across with many slowly expanding, rounded whorls that barely overlap, all visible
from the side, and dense, fine, straight ribs that split in two as they cross the rounded
venter (no keel). Grey-buff shell with faint darker growth bands. The living animal sits in
the aperture: a fleshy head with big eyes and ten arms. The coil stands upright with the
aperture at the bottom; faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/dactylioceras_commune.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dactylioceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

PALE = (0.80, 0.76, 0.66)
GREY = (0.62, 0.58, 0.50)
BAND = (0.38, 0.34, 0.28)
DORSUM = (0.45, 0.40, 0.33)

W = 1.55                       # slow whorl expansion: many whorls
K = math.log(W) / math.tau
WHORLS = 5.5
A_END = -math.pi / 2
PHI = [0.0, 0.25, 0.5, 0.8, 1.2, 1.6, 2.1, 2.6]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """Round whorl section (u radial, v lateral), slightly flattened on the dorsum."""
    return math.cos(phi), math.sin(phi)


def shell():
    rings, colors = [], []
    a = A_END - WHORLS * math.tau
    i = 0
    while True:
        w = (a - (A_END - WHORLS * math.tau)) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * 1.0
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.95 * hh
        e = radial(a)
        rib = 1.0 if i % 2 == 0 else 0.0
        rib *= 1.0 - nh.smoothstep(0.95, 1.0, w)
        band = nh.smoothstep(0.7, 0.95, math.sin(a * 2.2 + 0.4))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            ribzone = 1.0 - nh.smoothstep(2.2, 2.7, ap)   # ribs cross flanks and venter
            k = (1.0 + 0.09 * rib * ribzone) * (1.0 + 0.06 * nh.smoothstep(0.988, 1.0, w))
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(PALE, GREY, nh.smoothstep(0.3, 1.4, ap))
            col = nh.lerp(col, BAND, 0.6 * band)
            col = tuple(x * (1.08 if rib else 0.84) for x in col) if ribzone > 0.3 else col
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.3, 2.9, ap))
            cols.append(tuple(min(1.0, x) for x in col))
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        ribs = 30 + 20 * w                                  # dense fine ribs
        a = min(A_END, a + math.tau / (2 * ribs))
        i += 1
    return am.grid_mesh(rings, colors), radial(A_END) * (outer(A_END) + outer(A_END - math.tau)) / 2, \
        (outer(A_END) - outer(A_END - math.tau)) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.95, arm_len=2.0, droop=0.45)
    obj = mb.to_object("Dactylioceras", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Dactylioceras", views=((35, 20), (-90, 5), (30, 50)))
