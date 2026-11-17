"""
Procedural low-poly Wiwaxia corrugata (Burgess Shale scaly, spined mollusc relative).

An oval, slug-like animal with a flat sole, its back shingled with rows of
small, overlapping, ribbed scale-like sclerites, and two rows of long, slightly
curved, blade-like spines (about eight a side) rising up and out in a V along
the back. Spines and sclerites are dark amber-bronze with paler ribs; the
sole is pale. Faces -Y, pivot at the body centre (Swim, a slow seafloor grazer).

Output: Assets/Resources/Models/Species/Wiwaxia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.46, 0.32, 0.20)
SOLE = (0.80, 0.68, 0.56)
SCALE = (0.62, 0.44, 0.22)
SCALE_RIB = (0.82, 0.66, 0.38)
SPINE = (0.38, 0.24, 0.12)
SPINE_TIP = (0.78, 0.60, 0.34)

L, W, H = 0.45, 0.2, 0.12


def surface(u, v):
    """u along the body (-1..1), v around the back (-1 left .. 1 right): point on the dome."""
    a = v * math.pi / 2
    w = W * math.sqrt(max(0.0, 1 - u * u)) + 0.01
    return Vector((math.sin(a) * w, u * L, math.cos(a) * H * math.sqrt(max(0.0, 1 - u * u)) * 1.0)), a


def build():
    mb = nh.MeshBuilder()
    body = nh.uv_ellipsoid((0, 0, 0), (W, L, H), segments=18, rings=10)
    for v in body.verts:
        if v.co.z < 0:
            v.co.z *= 0.2
    mb.add(body, lambda co, n: nh.lerp(SOLE, BODY, nh.smoothstep(-0.5, 0.2, n.z)))
    # sclerites: rows of small overlapping ribbed scales
    for i in range(13):
        u = -0.9 + 1.8 * i / 12
        for j in range(7):
            v = -0.95 + 1.9 * j / 6
            p, a = surface(u, v)
            sc = nh.uv_ellipsoid((0, 0, 0), (0.035, 0.055, 0.008), segments=8, rings=4)
            nh.transform(sc, Matrix.Rotation(math.radians(-18), 4, "X"))
            nh.transform(sc, Matrix.Rotation(a, 4, "Y"))
            nh.transform(sc, Matrix.Translation(p + Vector((0, 0, 0.006))))
            mb.add(sc, lambda co, n, p=p: nh.lerp(SCALE, SCALE_RIB,
                                                   nh.smoothstep(0.4, 1.0, math.cos((co.x - p.x) * 120.0) * 0.5 + 0.5)))
    # two rows of spines
    for i in range(8):
        u = -0.65 + 1.3 * i / 7
        for s in (-1, 1):
            p, _ = surface(u, s * 0.38)
            ln = 0.22 + 0.1 * math.sin(math.pi * (i + 0.5) / 8)
            d = Vector((s * 0.45, 0.25, 0.86)).normalized()
            blade = nh.flat_panel([(0, -0.025, 0), (ln * 0.5, -0.03, 0), (ln, 0, 0), (ln * 0.5, 0.02, 0), (0, 0.02, 0)],
                                  thickness=0.012)
            # orient blade's +X along d, its flat face facing fore-aft
            rot = Vector((1, 0, 0)).rotation_difference(d).to_matrix().to_4x4()
            nh.transform(blade, Matrix.Rotation(math.radians(90), 4, "X"))
            nh.transform(blade, rot)
            nh.transform(blade, Matrix.Translation(p))
            mb.add(blade, lambda co, n, p=p, ln=ln: nh.lerp(SPINE, SPINE_TIP,
                                                             nh.smoothstep(0.4, 1.0, (co - p).length / ln)),
                   smooth=False)
    return ec.centre(mb.to_object("Wiwaxia", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Wiwaxia")
