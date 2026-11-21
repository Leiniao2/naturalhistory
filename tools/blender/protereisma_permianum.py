"""
Procedural Protereisma permianum (Early Permian mayfly, wingspan ~2-3 cm) for map colonies.

A Permian 'proto-mayfly' from Kansas: unlike living mayflies its fore and hind wings were
almost the same size and shape, held out to the sides, with a dense net of veins; a slim,
ringed abdomen ends in three long tail filaments, the head has big eyes and short
antennae, and the legs are slender. Smoky, glassy wings with brown veins, amber body.
Reuses the wing grid of nh_car_palaeodicty. Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/protereisma_permianum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protereisma.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_car_palaeodicty as pd  # noqa: E402

BODY = (0.46, 0.30, 0.14)
BODY_RING = (0.70, 0.52, 0.26)
EYE = (0.10, 0.08, 0.07)
WING = (0.80, 0.80, 0.74)
WING_ROOT = (0.55, 0.42, 0.24)
VEIN = (0.36, 0.26, 0.14)
L, BR = 0.62, 0.032


def wing_col(u, v):
    c = nh.lerp(WING_ROOT, WING, nh.smoothstep(0.0, 0.18, u))
    net = max(math.exp(-(((u * 14) % 1.0 - 0.5) / 0.12) ** 2), math.exp(-(((v * 6) % 1.0 - 0.5) / 0.15) ** 2))
    c = nh.lerp(c, VEIN, 0.35 * net)
    if v < 0.1:
        c = nh.lerp(c, VEIN, 0.75)
    return c


def build():
    mb = nh.MeshBuilder()
    yh = -L * 0.5
    body = nh.MeshBuilder()
    body.add(nh.ellipsoid((0, yh, 0.0), (BR * 1.15, BR, BR), 2), BODY)
    body.add(nh.uv_ellipsoid((0, yh + L * 0.17, 0.0), (BR * 1.3, L * 0.13, BR * 1.3), 14, 10), BODY)
    n = 10
    for i in range(n):
        t = i / (n - 1)
        y = yh + L * 0.32 + t * L * 0.66
        r = BR * (0.95 - 0.5 * t)
        body.add(nh.ellipsoid((0, y, 0.0), (r, L * 0.04, r * 0.9), 2), BODY_RING if i % 2 else BODY)
    mb.add(body.fuse(voxel=BR * 0.25, smooth=3, max_tris=2500))
    y_end = yh + L * 0.98
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * BR * 0.85, yh - BR * 0.25, BR * 0.35), (BR * 0.55,) * 3, 2), EYE)
        mb.add(nh.tube([(sx * BR * 0.3, yh - BR * 0.9, BR * 0.4), (sx * BR * 1.0, yh - BR * 2.6, BR * 0.9)],
                       [BR * 0.1, BR * 0.04], sides=4), BODY)
        for k in range(3):
            y = yh + L * (0.08 + 0.08 * k)
            mb.add(nh.tube([(sx * BR * 0.8, y, -BR * 0.5), (sx * BR * 2.6, y + 0.03 * (k - 1), -BR * 1.0),
                            (sx * BR * 3.2, y + 0.05 * (k - 1), -BR * 2.6)],
                           [BR * 0.16, BR * 0.12, BR * 0.06], sides=4), BODY)
    # three long tail filaments
    for dx in (-1, 0, 1):
        pts = [Vector((0, y_end, 0)), Vector((dx * 0.04, y_end + 0.25, 0.02)), Vector((dx * 0.09, y_end + 0.52, 0.05))]
        mb.add(nh.tube(pts, [BR * 0.14, BR * 0.09, 0.0], sides=4), BODY)
    x0 = BR * 0.9
    span = 0.62
    for sx in (-1, 1):
        for root_y, chord, sweep, sp in ((yh + L * 0.10, 0.17, 4, span), (yh + L * 0.24, 0.16, 12, span * 0.92)):
            w = pd.wing_grid((x0, root_y, BR * 0.4), sp - x0, chord, sweep, wing_col, th=0.004)
            mb.add(pd.mirror(w) if sx < 0 else w, smooth=False)
    obj = mb.to_object("Protereisma", roughness=0.45)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "Protereisma", background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
