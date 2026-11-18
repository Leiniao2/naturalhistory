"""
Procedural Manticoceras sinuosum for the map: a goniatite ammonoid from the Late Devonian
(Frasnian, about 380-372 million years ago) seas of New York, Europe, North Africa and
Australia; shells up to about 15 cm across. Manticoceras is so widespread and common that
it marks the Frasnian stage worldwide.

Unlike the open-coiled Agoniatites, the shell is involute: each new whorl wraps almost
completely round the last, leaving only a narrow umbilicus, and the whorls are high and
flattened (compressed) with a rounded outer edge. Its internal walls met the shell in
zig-zag "goniatitic" suture lines of rounded saddles and pointed lobes, shown here on the
chambered part of the shell; the last part, the body chamber, has none.

Shell swept along a logarithmic spiral with the nh_ammonite helpers (finer rings on the
visible outer whorl so the painted sutures stay crisp); the soft body (head, eyes, ten
arms) sits in the aperture. Colours are unknown: olive-grey with dark reddish-brown
radial flame bands, brown sutures. The coil stands upright with the aperture at the
bottom; the animal faces -Y, pivot at the body centre (Swim style, swims backward).

Usage:
  blender --background --python tools/blender/manticoceras_sinuosum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Manticoceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Manticoceras"

SHELL = (0.70, 0.68, 0.56)
SHELL_DARK = (0.50, 0.48, 0.38)
FLAME = (0.42, 0.20, 0.12)
SUTURE = (0.22, 0.12, 0.07)
VENTER = (0.84, 0.80, 0.68)
UMB = (0.30, 0.26, 0.20)

W = 2.6                       # whorl expansion per turn
K = math.log(W) / math.tau
WHORLS = 3.5
A_END = -math.pi / 2
N_PHI = 30
PHI = [(-math.pi + (i + 0.5) / N_PHI * math.tau) for i in range(N_PHI)]
BODY_CHAMBER = 0.85 * math.pi          # last stretch without sutures
SUTURE_STEP = math.tau / 16


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    c, s = math.cos(phi), math.sin(phi)
    return math.copysign(abs(c) ** (2 / 2.8), c), math.copysign(abs(s) ** (2 / 2.8), s)


def suture_shift(phi):
    """Angular offset of the suture at section angle phi (0 = venter, pi = dorsum): a
    small ventral lobe, then rounded saddles and pointed lobes (negative = toward the apex)."""
    ap = abs(phi)
    f = math.sin(ap * 2.6 + 0.6)
    lobe = f if f > 0 else -abs(f) ** 2.5 * 1.6
    return 0.09 * lobe - 0.05 * math.exp(-(ap / 0.25) ** 2)


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    while True:
        w = (a - a0) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * 0.30     # involute: the whorl wraps deep round the last one
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.60 * hh                      # compressed, high whorl
        e = radial(a)
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            k = 1.0 + 0.05 * nh.smoothstep(0.99, 1.0, w)
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(SHELL, SHELL_DARK, 0.6 * nh.smoothstep(0.6, 1.8, ap))
            col = nh.lerp(col, VENTER, nh.smoothstep(0.55, 0.15, ap))
            # radial flame bands, swept forward on the flanks
            fl = math.sin(a * 9.0 + 0.9 * math.sin(ap) + 0.5)
            col = nh.lerp(col, FLAME, 0.45 * nh.smoothstep(0.6, 0.95, fl) * nh.smoothstep(0.3, 0.9, ap)
                          * nh.smoothstep(2.5, 2.0, ap))
            col = nh.lerp(col, UMB, nh.smoothstep(2.3, 2.9, ap))
            # goniatitic sutures on the chambered part (phragmocone)
            if a < A_END - BODY_CHAMBER:
                q = (a - A_END + BODY_CHAMBER) - suture_shift(phi)
                d = abs(q - SUTURE_STEP * round(q / SUTURE_STEP))
                col = nh.lerp(col, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.018, 0.040, d)))
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        visible = a > A_END - 1.3 * math.tau
        a = min(A_END, a + math.tau / (110 if visible else 30))
    ap = radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * 0.55) / 2
    return am.grid_mesh(rings, colors), ap, (outer(A_END) - outer(A_END - math.tau) * 0.55) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.42, arm_len=1.9, droop=0.45)
    obj = mb.to_object(NAME, roughness=0.40)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 20), (-90, 5), (0, 10), (30, 50)))
