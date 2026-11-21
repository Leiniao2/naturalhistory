"""
Procedural Orthrozanclus reburrus (Burgess Shale stem mollusc, ~1 cm).

A tiny oval, domed body covered in rows of small scale-like sclerites, with a small
cap-shaped shell on top at the front, and a fringe of long, slender, curving spines all
round the margin sweeping out and up (longest at the sides and back). Greenish ochre
scales, pale spines, brown shell. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Orthrozanclus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SCALE = (0.62, 0.58, 0.34)
SCALE_DARK = (0.42, 0.40, 0.22)
SPINE = (0.90, 0.86, 0.70)
SHELL = (0.50, 0.34, 0.20)
FOOT = (0.80, 0.70, 0.56)


def build():
    mb = nh.MeshBuilder()
    W, L = 0.24, 0.42
    b = nh.uv_ellipsoid((0, 0, 0), (W, L, 0.13), segments=24, rings=12)
    for v in b.verts:
        if v.co.z < 0:
            v.co.z *= 0.3
    def col(co, n):
        k = 0.5 + 0.5 * math.sin(co.y * 80) * math.sin(co.x * 80)
        return nh.lerp(FOOT, nh.lerp(SCALE, SCALE_DARK, 0.6 * k), nh.smoothstep(-0.5, 0.1, n.z))
    mb.add(b, col)
    cap = nh.uv_ellipsoid((0, 0, 0), (0.11, 0.1, 0.07), segments=16, rings=8)
    for v in cap.verts:
        if v.co.z < 0:
            v.co.z = 0
    nh.transform(cap, Matrix.Translation((0, -0.26, 0.08)))
    mb.add(cap, SHELL)
    N = 22
    for k in range(N):
        a = k / N * math.tau
        x, y = math.sin(a), -math.cos(a)
        base = Vector((x * W * 0.92, y * L * 0.92, 0.03))
        out = Vector((x, y, 0)).normalized()
        L0 = 0.18 + 0.14 * (1 - abs(y)) + 0.08 * max(0, y)
        tip = base + out * L0 * 0.75 + Vector((0, 0, L0 * 0.6))
        mid = base + out * L0 * 0.55 + Vector((0, 0, L0 * 0.2))
        mb.add(ec.spike(base, tip, r=0.012, sides=4, mid=mid), SPINE, smooth=False)
    return ec.centre(mb.to_object("Orthrozanclus", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Orthrozanclus")
