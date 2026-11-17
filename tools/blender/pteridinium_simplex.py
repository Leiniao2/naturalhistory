"""
Procedural low-poly Pteridinium simplex (Ediacaran petalonamid, Nama Group, Namibia).

An elongate, boat-shaped body of three vanes meeting along a common midline
seam: two lateral vanes flaring up and out like the sides of a canoe and a
central vane standing up between them. Each vane is built of a row of narrow,
parallel, tube-like units (quilted ribs) running across it, those of
neighbouring vanes offset. It lay partly buried in the sand, so the keel sits
on the seabed. Sandy olive with darker rib grooves.
Faces -Y, pivot on the seabed (Fixed).

Output: Assets/Resources/Models/Species/Pteridinium.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

RIB = (0.74, 0.66, 0.46)
RIB_DARK = (0.50, 0.42, 0.28)
TIP = (0.84, 0.76, 0.56)
SEAM = (0.42, 0.34, 0.22)

L = 0.62     # half-length
UNITS = 26


def profile(y):
    """Vane height along the body: tapering to both pointed ends."""
    t = y / L
    return math.sqrt(max(0.0, 1 - t * t)) ** 0.8


def build():
    mb = nh.MeshBuilder()
    # midline keel
    mb.add(nh.tube([(0, -L, 0.02), (0, 0, 0.03), (0, L, 0.02)], [0.0, 0.035, 0.0], sides=8), SEAM)
    vanes = [(-1, math.radians(52)), (1, math.radians(52)), (0, 0.0)]
    for vi, (side, tilt) in enumerate(vanes):
        h_max = 0.3 if side else 0.2
        off = 0.5 * (vi % 2) if side else 0.25
        for k in range(UNITS):
            y = -L + (k + 0.5 + off * 0.5) * 2 * L / (UNITS + 0.5)
            h = h_max * profile(y)
            if h < 0.02:
                continue
            d = Vector((math.sin(tilt) * side, 0.08 * (y / L), math.cos(tilt))).normalized()
            base = Vector((0, y, 0.03))
            top = base + d * h
            mb.add(nh.tube([base, base.lerp(top, 0.5), top], [0.022, 0.024, 0.016], sides=6,
                           scale_xy=(1.0, 1.0)),
                   lambda co, n, base=base, h=h: nh.lerp(RIB, TIP, nh.smoothstep(0.5, 1.0, (co - base).length / max(h, 1e-3))))
            # groove between units
            mb.add(nh.tube([base + Vector((0, 0.02, 0)), base + Vector((0, 0.02, 0)) + d * h * 0.95],
                           [0.008, 0.006], sides=4), RIB_DARK)
    return ec.ground(mb.to_object("Pteridinium", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Pteridinium", fixed=True)
