"""
Procedural Anetoceras arduennense for the map: one of the earliest ammonoids, from the Early
Devonian (Emsian, about 400 million years ago) of the Ardennes, Germany and Morocco; shells
about 5-10 cm across.

Anetoceras shows the first step from straight-shelled bactritid ancestors to tightly coiled
ammonoids: a loosely coiled (gyroconic) shell of about two and a half whorls that do not
touch each other, leaving a large open hole in the middle; the slightly compressed tube is
crossed by fine growth lines and low ribs. The soft body (head, eyes, arms) peers out of the
aperture. Colours are unknown: buff with brown banding.

Shell swept along a fast-widening logarithmic spiral with the nh_ammonite helpers (as in
agoniatites_vanuxemi.py), with a gap between successive whorls. The animal faces -Y, pivot at
the body centre (Swim style).

Usage:
  blender --background --python tools/blender/anetoceras_arduennense.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anetoceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.86, 0.76, 0.58)
TAN = (0.68, 0.52, 0.34)
LINE = (0.46, 0.32, 0.18)
BAND = (0.40, 0.24, 0.12)
DORSUM = (0.66, 0.52, 0.36)

W = 2.7
F = 0.21          # tube radius as a fraction of the outer radius: whorls stay apart
K = math.log(W) / math.tau
WHORLS = 2.0
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
        hh = F * ro
        rc = ro - hh                            # gyroconic: inner edge clears the previous whorl
        hw = 0.80 * hh                          # slightly compressed whorl
        e = radial(a)
        band = nh.smoothstep(0.55, 0.95, math.sin(a * 5.0 + 0.4))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            k = (1.0 + 0.05 * nh.smoothstep(0.985, 1.0, w)) * (1.0 + 0.04 * max(0.0, math.cos(a * 15.0)))  # low ribs
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, TAN, nh.smoothstep(0.3, 1.4, ap))
            # fine growth lines (every other ring darker), swept back by the angle offset
            gl = 0.5 + 0.5 * math.cos(a * 30.0 - 1.2 * math.sin(ap) - 0.8 * math.exp(-(ap / 0.4) ** 2))
            col = nh.lerp(col, LINE, 0.4 * nh.smoothstep(0.7, 1.0, gl))
            col = nh.lerp(col, BAND, 0.55 * band * nh.smoothstep(0.2, 0.8, ap))
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.2, 2.9, ap))
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        a = min(A_END, a + math.tau / 60)
        i += 1
    ap = radial(A_END) * outer(A_END) * (1 - F)
    return am.grid_mesh(rings, colors), ap, F * outer(A_END)


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.62, arm_len=1.9, droop=0.45)
    obj = mb.to_object("Anetoceras", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Anetoceras", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
