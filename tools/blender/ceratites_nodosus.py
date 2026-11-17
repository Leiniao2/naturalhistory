"""
Procedural Ceratites nodosus (Middle Triassic ceratitid ammonoid, ~10 cm) for map
colonies (Swim style).

The classic ammonoid of the Upper Muschelkalk sea of Germany, about 240 million years
ago, and the namesake of the 'ceratitic' suture with its rounded saddles and toothed
lobes. A moderately involute, planispiral shell with flat, slightly converging flanks
and a broad, flat venter, crossed by strong, widely spaced ribs that swell into knobby
nodes at the shoulder of the venter (hence nodosus). The living animal sits in the
aperture: a fleshy head with big eyes and ten arms (nh_ammonite.soft_body). Shell
whorls swept along a logarithmic spiral as in asteroceras.py; cream with brown bands.
The coil stands upright with the aperture at the bottom; faces -Y, pivot at the body
centre.

Usage:
  blender --background --python tools/blender/ceratites_nodosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ceratites.fbx
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
BAND = (0.42, 0.28, 0.16)
DORSUM = (0.50, 0.38, 0.26)
NODE = (0.95, 0.90, 0.78)

W = 2.6                        # whorl expansion rate per turn (faster than Asteroceras: more involute)
K = math.log(W) / math.tau
WHORLS = 3.4
A_END = -math.pi / 2
OVERLAP = 0.80                 # inner whorl radius as a fraction of the previous whorl's outer radius
PHI = [0.0, 0.25, 0.5, 0.62, 0.75, 1.0, 1.5, 2.1, 2.6]
PHI = PHI + [math.pi] + [-p for p in reversed(PHI[1:])]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """(u, v) of the whorl section: u radial (+1 venter), v lateral. Flat venter, flat flanks."""
    c, s = math.cos(phi), math.sin(phi)
    n = 4.0
    u = math.copysign(abs(c) ** (2 / n), c)
    v = math.copysign(abs(s) ** (2 / n), s) * (0.85 + 0.15 * max(0.0, -c))   # flanks converge outward
    return u, v


def shell():
    rings, colors = [], []
    a0 = A_END - WHORLS * math.tau
    a = a0
    i = 0
    while True:
        w = (a - a0) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * OVERLAP
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.62 * hh
        e = radial(a)
        rib = (1.0, 0.55, 0.0)[i % 3]
        rib *= 1.0 - nh.smoothstep(0.95, 1.0, w)
        band = nh.smoothstep(0.55, 0.9, math.sin(a * 2.5 + 0.4))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            flank = nh.smoothstep(0.4, 0.7, ap) * (1 - nh.smoothstep(2.0, 2.6, ap))
            node = math.exp(-((ap - 0.62) / 0.14) ** 2)          # ventrolateral node
            k = 1.0 + rib * (0.10 * flank + 0.40 * node)
            ring.append(e * (rc + u * hh * (1.0 + rib * 0.06 * node)) + Vector((v * hw * k, 0, 0)))
            col = nh.lerp(CREAM, TAN, nh.smoothstep(0.3, 1.2, ap))
            col = nh.lerp(col, BAND, 0.65 * band * (0.3 + 0.7 * flank))
            if rib > 0.9:
                col = nh.lerp(col, NODE, 0.5 * node + 0.15 * flank)
            col = nh.lerp(col, DORSUM, nh.smoothstep(2.2, 2.9, ap))
            cols.append(tuple(min(1.0, x) for x in col))
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        ribs = 10 + 6 * w                                   # coarse, widely spaced ribs
        a = min(A_END, a + math.tau / (3 * ribs))
        i += 1
    ap = radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * OVERLAP) / 2
    return am.grid_mesh(rings, colors), ap, (outer(A_END) - outer(A_END - math.tau) * OVERLAP) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.75, arm_len=1.8, droop=0.45)
    obj = mb.to_object("Ceratites", roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Ceratites", views=((35, 20), (-90, 5), (0, 10)))
