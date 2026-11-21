"""
Procedural Spartobranchus tenuis (Burgess Shale acorn worm, several cm).

A slender acorn worm emerging from a thin, fibrous, slightly branched tube that lies
along and rises from the seabed: an acorn-shaped proboscis, a short ringed collar, and a
long, soft trunk (front part with gill slits) arching out of the tube's mouth. A short
side branch of the tube shows its colonial-looking branching. Pinkish orange proboscis,
cream collar, peach trunk, grey-brown tube. Fixed: pivot on the seabed.

Output: Assets/Resources/Models/Species/Spartobranchus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

PROB = (0.95, 0.58, 0.40)
COLLAR = (0.96, 0.88, 0.70)
TRUNK = (0.92, 0.70, 0.58)
GILL = (0.70, 0.40, 0.36)
TUBE = (0.52, 0.46, 0.38)
TUBE_DARK = (0.38, 0.33, 0.27)


def build():
    mb = nh.MeshBuilder()
    tube_pts = [(0.0, 0.7, 0.04), (0.0, 0.3, 0.05), (0.02, -0.05, 0.08), (0.04, -0.25, 0.2), (0.04, -0.33, 0.36)]
    mb.add(nh.tube(tube_pts, [0.075, 0.08, 0.08, 0.08, 0.085], sides=10, cap_end=False),
           kit.ringed(TUBE, TUBE_DARK, period=0.05, sharp=0.25, axis=1))
    mb.add(nh.tube([(0.0, 0.25, 0.05), (0.18, 0.12, 0.05), (0.32, 0.0, 0.09)], [0.06, 0.06, 0.06], sides=8),
           kit.ringed(TUBE, TUBE_DARK, period=0.05, sharp=0.25, axis=0))
    worm = kit.curve((0.04, -0.33, 0.3), (0.05, -0.42, 0.62), (0.05, -0.68, 0.62), 8)
    radii = [0.06] * len(worm)
    mb.add(nh.tube(worm, radii, sides=10), lambda co, n: nh.lerp(TRUNK, GILL,
           0.6 * nh.smoothstep(0.6, 0.9, math.sin(co.z * 120)) * nh.smoothstep(0.45, 0.55, co.z)))
    tip = worm[-1]
    d = (worm[-1] - worm[-2]).normalized()
    mb.add(nh.tube([tip, tip + d * 0.03, tip + d * 0.06], [0.065, 0.072, 0.065], sides=10), COLLAR)
    pb = tip + d * 0.06
    mb.add(nh.tube([pb, pb + d * 0.07, pb + d * 0.14, pb + d * 0.19], [0.065, 0.07, 0.05, 0.0], sides=10), PROB)
    return ec.ground(mb.to_object("Spartobranchus", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Spartobranchus", fixed=True)
