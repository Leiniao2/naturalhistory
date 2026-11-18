"""
Procedural Zhongjianichthys rostratus (early Cambrian jawless vertebrate, Chengjiang, ~3 cm).

A tiny, slender, eel-like fish: a long, laterally flattened body with zig-zag muscle blocks,
a narrow head with a short projecting snout (rostrum) and a pair of eyes, a few gill pouches
behind the head, a low fin fold along the back and a fin fold round the pointed tail.
Olive-grey back, silvery belly, reddish gills. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/zhongjianichthys_rostratus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Zhongjianichthys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BACK = (0.34, 0.38, 0.30)
BELLY = (0.88, 0.88, 0.82)
MYO = (0.24, 0.26, 0.20)
FIN = (0.72, 0.72, 0.62)
GILL = (0.66, 0.30, 0.26)
EYE = (0.03, 0.03, 0.03)


def wig(y):
    return 0.05 * math.sin(y * 4.0 + 0.5)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    n = 30
    for i in range(n + 1):
        t = i / n
        y = -0.75 + 1.5 * t
        pts.append((wig(y), y, 0))
        r = 0.055 * math.sin(math.pi * min(1.0, t * 1.15 + 0.08)) ** 0.6
        radii.append(max(r, 0.004))
    radii[-1] = 0.0

    def col(co, n):
        c = nh.lerp(BELLY, BACK, nh.smoothstep(-0.4, 0.3, n.z))
        v = abs(((co.y * 22 + abs(co.z) * 25) % 1.0) - 0.5)
        return nh.lerp(c, MYO, (1 - nh.smoothstep(0.0, 0.08, v)) * 0.4 * nh.smoothstep(-0.65, -0.55, co.y))
    mb.add(nh.tube(pts, radii, sides=12, scale_xy=(0.55, 1.0)), col)
    # rostrum
    mb.add(nh.tube([(wig(-0.74), -0.73, 0.005), (wig(-0.8), -0.82, 0.0)], [0.02, 0.006], sides=8), BACK)
    for s in (-1, 1):
        mb.add(nh.ellipsoid((wig(-0.68) + s * 0.022, -0.68, 0.018), (0.012, 0.014, 0.012), subdivisions=2), EYE)
        for k in range(5):
            y = -0.6 + k * 0.03
            mb.add(nh.ellipsoid((wig(y) + s * 0.026, y, -0.01), (0.006, 0.009, 0.012), subdivisions=1), GILL)
    top = [(wig(-0.3 + 0.9 * i / 12), -0.3 + 0.9 * i / 12, 0.0) for i in range(13)]
    fin_up = [(wig(y), y, z + 0.035 * math.sin(math.pi * (y + 0.3) / 0.9) * 0.6 + 0.03) for (_x, y, z) in top]
    for k in range(12):
        a, b = top[k], top[k + 1]
        pa, pb = fin_up[k], fin_up[k + 1]
        panel = nh.tube([Vector(a).lerp(Vector(pa), 0.5), Vector(b).lerp(Vector(pb), 0.5)], [0.012, 0.012], sides=4,
                        scale_xy=(0.15, 1.0))
        mb.add(panel, FIN)
    tail = nh.tube([(wig(0.5), 0.5, 0), (wig(0.62), 0.62, 0), (wig(0.78), 0.8, 0)], [0.045, 0.04, 0.0], sides=8,
                   scale_xy=(0.12, 1.0))
    mb.add(tail, FIN)
    return ec.centre(mb.to_object("Zhongjianichthys", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Zhongjianichthys")
