"""
Procedural Hildoceras bifrons (Early Jurassic Toarcian ammonite) for map colonies.

A flat, widely umbilicate (evolute) ammonite up to about 10 cm across, an index fossil of
the Toarcian of Europe (Whitby, Yorkshire): compressed whorls with a sharp keel flanked by
two grooves on the venter, a smooth spiral groove along the middle of each flank, smooth
inner flanks and strong sickle-shaped (falcate) ribs on the outer flanks. Grey-cream shell
with warm brown ribs. The living animal sits in the aperture (nh_ammonite.soft_body).
The coil stands upright, aperture at the bottom; faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/hildoceras_bifrons.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hildoceras.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

CREAM = (0.84, 0.80, 0.70)
GREY = (0.62, 0.60, 0.55)
RIB = (0.50, 0.36, 0.22)
GROOVE = (0.30, 0.26, 0.22)

W = 1.85
K = math.log(W) / math.tau
WHORLS = 4.5
A_END = -math.pi / 2
PHI = [0.0, 0.1, 0.22, 0.4, 0.7, 1.0, 1.25, 1.45, 1.55, 1.65, 1.9, 2.3, 2.7]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """Compressed lanceolate whorl: (u radial, v lateral)."""
    c, s = math.cos(phi), math.sin(phi)
    u = math.copysign(abs(c) ** 0.85, c)
    v = math.copysign(abs(s) ** 0.8, s)
    u += 0.14 * math.exp(-(phi / 0.09) ** 2)                      # keel
    u -= 0.06 * math.exp(-((abs(phi) - 0.22) / 0.07) ** 2)         # grooves beside it
    v -= math.copysign(0.07 * math.exp(-((abs(phi) - 1.55) / 0.09) ** 2), s)  # spiral flank groove
    return u, v


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    i = 0
    while True:
        w = (a - a0) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * 1.0
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.5 * hh
        e = radial(a)
        rib = (1.0 if i % 2 == 0 else 0.0) * (1.0 - nh.smoothstep(0.94, 1.0, w))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            outer_flank = nh.smoothstep(0.3, 0.5, ap) * (1 - nh.smoothstep(1.35, 1.45, ap))
            # falcate ribs: shift the rib phase along the flank so they curve forward
            k = 1.0 + 0.12 * rib * outer_flank
            ring.append(e * (rc + u * hh * k) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, GREY, nh.smoothstep(1.3, 2.4, ap))
            if rib and outer_flank > 0.3:
                col = RIB
            if 1.47 < ap < 1.63:
                col = GROOVE
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        ribs = 14 + 18 * w
        a = min(A_END, a + math.tau / (2 * ribs))
        i += 1
    ap_c = radial(A_END) * (outer(A_END) + outer(A_END - math.tau)) / 2
    return am.grid_mesh(rings, colors), ap_c, (outer(A_END) - outer(A_END - math.tau)) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.6, arm_len=2.0, droop=0.45)
    return kit.finish(mb, "Hildoceras", pivot="center", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "Hildoceras", views=((35, 20), (-90, 5), (30, 50)))
