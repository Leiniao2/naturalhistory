"""
Procedural Odontogriphus omalus (Burgess Shale stem mollusc, up to ~12 cm).

A flat, broadly oval, soft-bodied, slug-like animal with no shell or sclerites: a low
dorsal dome with faint transverse wrinkles, a slightly paler margin, a broad flat foot,
and at the front underside a mouth with a toothed radula flanked by a pair of small
sensory lobes. Pale pinkish grey-brown. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Odontogriphus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

TOP = (0.70, 0.56, 0.50)
WRINKLE = (0.52, 0.40, 0.36)
RIM = (0.86, 0.76, 0.68)
FOOT = (0.90, 0.80, 0.74)
MOUTH = (0.30, 0.18, 0.16)


def build():
    mb = nh.MeshBuilder()
    W, L = 0.3, 0.62
    b = nh.uv_ellipsoid((0, 0, 0), (W, L, 0.12), segments=32, rings=16)
    for v in b.verts:
        if v.co.z < 0:
            v.co.z *= 0.3
        else:
            v.co.z *= 1.0 + 0.06 * math.cos(v.co.y * 60)
    def col(co, n):
        e = (co.x / W) ** 2 + (co.y / L) ** 2
        w = 0.5 + 0.5 * math.cos(co.y * 60)
        c = nh.lerp(TOP, WRINKLE, 0.45 * w)
        c = nh.lerp(c, RIM, nh.smoothstep(0.7, 0.95, e))
        return nh.lerp(FOOT, c, nh.smoothstep(-0.5, 0.2, n.z))
    mb.add(b, col)
    mb.add(nh.uv_ellipsoid((0, -0.5, -0.03), (0.06, 0.04, 0.02), segments=10, rings=5), MOUTH)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid((s * 0.09, -0.56, -0.02), (0.05, 0.035, 0.018), segments=10, rings=5), RIM)
    return ec.centre(mb.to_object("Odontogriphus", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Odontogriphus")
