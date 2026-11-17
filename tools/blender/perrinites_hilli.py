"""
Procedural Perrinites hilli (Early Permian cyclolobid ammonoid, ~10 cm) for map colonies.

A tightly coiled (involute), smooth, disc-shaped shell from the Permian seas of west Texas
and Mexico: each whorl wraps almost completely over the one before, leaving only a small
navel (umbilicus), the flanks are smooth apart from fine growth lines, and the venter is
broadly rounded. Its fossils are known for very complex, finely frilled suture lines.
Pale buff with faint radial growth bands and darker zig-zag colour bands; the living animal
sits in the aperture (shared soft body from nh_ammonite). The coil stands upright with the
aperture at the bottom; faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/perrinites_hilli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Perrinites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Perrinites"
CREAM = (0.88, 0.80, 0.64)
TAN = (0.72, 0.60, 0.42)
BAND = (0.44, 0.30, 0.18)

W = 3.0                        # fast-expanding whorls
K = math.log(W) / math.tau
WHORLS = 3.0
A_END = -math.pi / 2
PHI = [i / 16 * math.tau - math.pi for i in range(16)]


def outer(a):
    return math.exp(K * (a - A_END))


def radial(a):
    return Vector((0.0, -math.cos(a), math.sin(a)))


def section(phi):
    """Compressed, rounded oval with a deep impressed dorsal zone (involute)."""
    c, s = math.cos(phi), math.sin(phi)
    return c, s


def shell():
    rings, colors = [], []
    a = A_END - WHORLS * math.tau
    while True:
        w = (a - (A_END - WHORLS * math.tau)) / (WHORLS * math.tau)
        ro = outer(a)
        rd = outer(a - math.tau) * 0.55            # inner edge tucked deep inside the previous whorl
        rc, hh = (ro + rd) / 2, (ro - rd) / 2
        hw = 0.48 * hh
        e = radial(a)
        growth = 0.5 + 0.5 * math.sin(a * 22.0)
        zig = nh.smoothstep(0.6, 0.9, math.sin(a * 4.0 + 1.0))
        ring, cols = [], []
        for phi in PHI:
            u, v = section(phi)
            ap = abs(phi)
            ring.append(e * (rc + u * hh) + Vector((v * hw * (1.0 - 0.25 * max(0.0, -u)), 0, 0)))
            col = nh.lerp(CREAM, TAN, 0.35 * growth)
            col = nh.lerp(col, BAND, 0.6 * zig * nh.smoothstep(0.3, 1.2, ap) * (1 - nh.smoothstep(2.2, 2.8, ap)))
            cols.append(col)
        rings.append(ring)
        colors.append(cols)
        if a >= A_END - 1e-6:
            break
        a = min(A_END, a + math.tau / 60)
    ap = radial(A_END) * (outer(A_END) + outer(A_END - math.tau) * 0.55) / 2
    return am.grid_mesh(rings, colors), ap, (outer(A_END) - outer(A_END - math.tau) * 0.55) / 2


def build():
    mb = nh.MeshBuilder()
    bm, aperture, hh = shell()
    mb.add(bm, None)
    am.soft_body(mb, aperture, (0, -1, 0), (0, 0, 1), hh * 0.7, arm_len=1.8, droop=0.45)
    obj = mb.to_object(NAME, roughness=0.45)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 20), (-90, 5), (0, 10)))
