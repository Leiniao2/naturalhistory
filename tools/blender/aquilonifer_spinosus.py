"""
Procedural Aquilonifer spinosus (a small Silurian arthropod, about 1 cm long, from the
Herefordshire Lagerstaette of England, about 430 million years ago, described in 2016)
for map colonies (Swim).

The "kite-runner": a slim, segmented arthropod with a rounded head shield, a very long
pair of antennae, about ten body segments each drawn out into a long, curved spine at
either side, and short legs. Hovering above its back on long, fine threads are ten
tiny, flat capsules - most likely its own young - towed along like kites, a unique way
of caring for offspring. Pale yellow-brown body, translucent paler kites.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/aquilonifer_spinosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AquiloniferSpinosus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402

NAME = "AquiloniferSpinosus"
BODY = (0.78, 0.62, 0.38)
BODY_DARK = (0.52, 0.38, 0.20)
SPINE = (0.88, 0.74, 0.50)
LEG = (0.70, 0.54, 0.32)
THREAD = (0.92, 0.88, 0.78)
KITE = (0.96, 0.86, 0.62)
KITE_DARK = (0.70, 0.56, 0.36)
EYE = (0.06, 0.05, 0.05)

SEGS = 10


def build():
    mb = nh.MeshBuilder()
    # head shield
    mb.add(ec.plate(-0.50, 0.15, 0.13, 0.07), lambda co, n: nh.lerp(BODY_DARK, BODY, nh.smoothstep(-0.2, 0.8, n.z)))
    for s in (1, -1):
        mb.add(nh.uv_ellipsoid((s * 0.07, -0.58, 0.035), (0.022, 0.022, 0.018), 8, 5), EYE)
        # long antennae
        b = Vector((s * 0.05, -0.62, 0.0))
        pts = [b + Vector((s * 0.06 * t + s * 0.05 * t * t, -0.55 * t, 0.06 * t)) for t in [i / 6 for i in range(7)]]
        mb.add(nh.tube(pts, [0.014 * (1 - 0.8 * i / 6) for i in range(7)], sides=4), LEG)
    # trunk segments, each with a pair of long curved lateral spines and short legs
    for i in range(SEGS):
        t = i / (SEGS - 1)
        y = -0.36 + 0.09 * i
        w = 0.12 * (1 - 0.45 * t)
        mb.add(ec.plate(y, w, 0.055, 0.05), lambda co, n: nh.lerp(BODY_DARK, BODY, nh.smoothstep(-0.2, 0.8, n.z)))
        for s in (1, -1):
            r = Vector((s * w * 0.9, y, 0.0))
            L = 0.22 * (1 - 0.35 * t)
            sp = [r, r + Vector((s * L * 0.6, L * 0.15, 0.01)), r + Vector((s * L * 0.9, L * 0.55, 0.02))]
            mb.add(nh.tube(sp, [0.014, 0.008, 0.0], sides=4), SPINE)
            mb.add(nh.tube([r + Vector((-s * 0.02, 0, -0.02)), r + Vector((s * 0.05, -0.01, -0.07))],
                           [0.008, 0.0], sides=4), LEG)
    # tail spine
    mb.add(nh.tube([(0, 0.48, 0), (0, 0.62, 0.01), (0, 0.72, 0.03)], [0.02, 0.012, 0.0], sides=5), SPINE)
    # ten kites on threads above the back
    for k in range(10):
        a = k / 10 * math.tau
        anchor = Vector((0.0, -0.30 + 0.07 * k, 0.04))
        kite = Vector((0.20 * math.cos(a * 1.3), -0.30 + 0.08 * k + 0.08 * math.sin(a), 0.30 + 0.08 * math.sin(a * 2.1)))
        mb.add(nh.tube([anchor, anchor.lerp(kite, 0.5) + Vector((0, 0.02, 0)), kite], [0.003, 0.003, 0.003], sides=3),
               THREAD, smooth=False)
        mb.add(nh.uv_ellipsoid(tuple(kite), (0.045, 0.06, 0.012), 10, 5),
               lambda co, n, c=kite: nh.lerp(KITE, KITE_DARK, nh.smoothstep(0.02, 0.05, (co - c).length)))
    return ec.centre(mb.to_object(NAME, roughness=0.45))


if __name__ == "__main__":
    ec.export(build, NAME)
