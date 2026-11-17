"""
Procedural Rhizodus hibberti (Early Carboniferous of Scotland, the largest rhizodont
lobe-finned fish, perhaps about 7 m long) for map colonies (Swim style).

A huge, long-bodied lobe-finned predator: a broad, slightly flattened head with a wide
mouth armed with enormous fangs, big fleshy lobed pectoral and pelvic fins fringed with
fin rays, the second dorsal and anal fins set far back, and a symmetrical diamond-shaped
tail. Olive-brown back with darker mottling over big rounded scales, pale belly.
Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/rhizodus_hibberti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhizodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

LOBE = (0.36, 0.33, 0.20)
FANG = (0.95, 0.93, 0.85)


def lobes(sp):
    out = []
    for sx in (-1, 1):
        out.append(nh.tube([(sx * 0.07, -0.30, -0.05), (sx * 0.14, -0.25, -0.06), (sx * 0.20, -0.18, -0.065)],
                           [0.03, 0.026, 0.012], sides=10))
        out.append(nh.tube([(sx * 0.05, 0.05, -0.05), (sx * 0.10, 0.10, -0.06), (sx * 0.135, 0.15, -0.065)],
                           [0.022, 0.018, 0.008], sides=10))
    return out


def fangs(sp, tree):
    out = []
    for sx in (-1, 1):
        for y, L in ((-0.585, 0.04), (-0.56, 0.03), (-0.5, 0.026)):
            loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, y, -0.012)), Vector((-sx, 0, 0)))
            if loc is not None:
                b = loc + Vector((-sx * 0.006, 0, 0.004))
                out.append((nh.tube([b, b + Vector((0, -0.004, -L))], [0.007, 0.0], sides=5), FANG))
    return out


SPEC = cf.Spec(
    name="Rhizodus",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.59, 0.03), (-0.5, 0.06), (-0.3, 0.085), (0.0, 0.08), (0.3, 0.05),
            (0.48, 0.025), (0.6, 0.004)],
    width=[(-0.6, 0.0), (-0.59, 0.045), (-0.5, 0.075), (-0.3, 0.08), (0.0, 0.07), (0.3, 0.04),
           (0.48, 0.02), (0.6, 0.003)],
    fins=[
        ("mid", [(0.44, 0.02), (0.53, 0.13), (0.64, 0.0), (0.53, -0.13), (0.44, -0.02)]),
        ("mid", [(0.22, 0.05), (0.27, 0.12), (0.33, 0.11), (0.36, 0.04)]),
        ("mid", [(0.22, -0.05), (0.27, -0.12), (0.33, -0.11), (0.36, -0.04)]),
        ("mid", [(-0.02, 0.07), (0.03, 0.12), (0.08, 0.11), (0.1, 0.07)]),
        ("pair", (0.19, -0.19, -0.065), [(0, -0.04, 0), (0.06, 0.0, -0.01), (0.03, 0.07, -0.005), (-0.06, 0.06, 0.0)]),
        ("pair", (0.125, 0.14, -0.065), [(0, -0.03, 0), (0.04, 0.02, -0.01), (0.0, 0.07, 0.0), (-0.05, 0.03, 0.0)]),
    ],
    fused_extra=[lobes],
    back=(0.24, 0.24, 0.15), flank=(0.40, 0.38, 0.24), belly=(0.80, 0.76, 0.60),
    fin_col=(0.30, 0.28, 0.18), pattern="mottle", pattern_col=(0.12, 0.12, 0.07),
    eye=(-0.52, 0.03, 0.016), iris=(0.75, 0.62, 0.25), gills=0,
    teeth=8, tooth_len=0.012, mouth_y=(-0.58, -0.47), mouth_z=-0.015,
    extra=[fangs],
)

if __name__ == "__main__":
    cf.run(SPEC)
