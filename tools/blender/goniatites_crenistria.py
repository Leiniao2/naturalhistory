"""
Procedural Goniatites crenistria for the map: the classic goniatite ammonoid of the Early
Carboniferous (Visean, about 335 million years ago) of Europe, North Africa and North
America; shells about 4-6 cm across.

A globular, tightly coiled (involute), almost spherical shell: each whorl wraps right round
the one before, leaving only a tiny navel (umbilicus); fine growth lines run across it, and
the distinctive zig-zag "goniatitic" sutures (pointed lobes and saddles, with a deep ventral
lobe) are drawn as dark zig-zag lines over the outer whorl. The tentacled soft body (head,
eyes, ten arms, funnel) peeks from the crescent-shaped aperture.

Shell swept along a logarithmic spiral like agoniatites_vanuxemi.py (nh_ammonite helpers);
the sutures are thin crisp tubes laid on the surface. Colours are unknown: cream/tan with
brown banding. The coil stands upright with the aperture at the bottom; the animal faces
-Y, pivot at the body centre (Swim style, swims backward).

Usage:
  blender --background --python tools/blender/goniatites_crenistria.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Goniatites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.90, 0.83, 0.66)
TAN = (0.74, 0.60, 0.42)
LINE = (0.58, 0.45, 0.30)
BAND = (0.40, 0.25, 0.13)
SUTURE = (0.20, 0.12, 0.07)

W = 1.95                     # whorl expansion per turn
K = math.log(W) / math.tau
WHORLS = 2.6
A_END = -math.pi / 2
INNER = 0.20                 # dorsum dips this far into the previous whorl (involute)
WIDTH = 1.4                  # whorl width / whorl height: globular
NPHI = 26
PHI = [-math.pi + (i + 0.5) / NPHI * math.tau for i in range(NPHI)]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def whorl(a):
    ro = outer(a)
    rd = outer(a - math.tau) * INNER
    return (ro + rd) / 2, (ro - rd) / 2


def section(phi):
    c, s = math.cos(phi), math.sin(phi)
    return math.copysign(abs(c) ** 0.85, c), math.copysign(abs(s) ** 0.85, s)


def point(a, phi, lift=0.0):
    rc, hh = whorl(a)
    hw = WIDTH * hh
    u, v = section(phi)
    p = radial(a) * (rc + u * hh) + Vector((v * hw, 0, 0))
    n = (radial(a) * (u / hh) + Vector((v / hw, 0, 0))).normalized()
    return p + n * lift


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    while True:
        band = nh.smoothstep(0.25, 0.75, math.sin(a * 2.5 + 0.7))
        ring, cols = [], []
        k = 1.0 + 0.04 * nh.smoothstep(A_END - 0.08, A_END, a)  # slight flare at the apertural lip
        rc, hh = whorl(a)
        for phi in PHI:
            u, v = section(phi)
            ring.append(radial(a) * (rc + u * hh * k) + Vector((v * WIDTH * hh * k, 0, 0)))
            ap = abs(phi)
            col = nh.lerp(CREAM, TAN, nh.smoothstep(0.6, 2.0, ap))
            gl = 0.5 + 0.5 * math.cos(a * 30.0 - 0.5 * math.sin(ap))
            col = nh.lerp(col, LINE, 0.35 * nh.smoothstep(0.75, 1.0, gl))
            col = nh.lerp(col, BAND, 0.75 * band * nh.smoothstep(0.2, 0.7, ap) * nh.smoothstep(2.6, 1.8, ap))
            col = nh.lerp(col, BAND, 0.8 * nh.smoothstep(A_END - 0.07, A_END - 0.01, a))  # dark lip
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        # fine steps on the visible outer whorl, coarse on the hidden inner ones
        step = math.tau / (56 if a > A_END - math.tau * 1.05 else 20)
        a = min(A_END, a + step)
    rc, hh = whorl(A_END)
    return am.grid_mesh(rings, colors), radial(A_END) * rc, hh


def suture_offset(phi):
    """Goniatitic suture: pointed lobes (back, toward the older shell) and saddles in a zig-zag,
    a deep ventral lobe at phi = 0."""
    t = (abs(phi) / 0.95) % 1.0
    tri = abs(t - 0.5) * 2.0          # 1 at the lobes, 0 at the saddles
    deep = 1.4 if abs(phi) < 0.48 else 1.0
    return -0.16 * (tri ** 1.3) * deep + 0.05


def sutures(mb):
    n = 9
    for i in range(n):
        a_s = A_END - 0.40 * math.tau - i * (0.58 * math.tau / n)
        pts = []
        for j in range(31):
            phi = -2.35 + 4.7 * j / 30
            pts.append(point(a_s + suture_offset(phi), phi, lift=0.004))
        mb.add(nh.tube(pts, [0.0075] * len(pts), sides=4), SUTURE, smooth=False)


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    sutures(mb)
    am.soft_body(mb, aperture + radial(A_END) * hh * 0.15, (0, -1, 0), (0, 0, 1), hh * 0.55,
                 arm_len=1.9, droop=0.4)
    obj = mb.to_object("Goniatites", roughness=0.4)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Goniatites", views=((35, 20), (-90, 5), (0, 10), (30, 50)))
