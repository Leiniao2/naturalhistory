"""
Procedural Caryocaris wrightii (Early-Middle Ordovician phyllocarid crustacean, found in
graptolite shales of Britain and elsewhere) for map colonies (Swim style).

A small, open-water shrimp-like crustacean a few centimetres long: a long, narrow,
pod-shaped carapace of two thin, smooth valves, pointed at both ends, enclosing the head
and thorax, with leaf-like swimming limbs beneath; a short, ringed abdomen sticks out
behind and ends in a pair of slender forked tail spines (furca). It drifted and swam in
the upper waters with the graptolites, which is why the two are so often found together.
Thin, translucent-looking straw-coloured shell. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/caryocaris_wrightii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CaryocarisWrightii.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "CaryocarisWrightii"
SHELL = (0.86, 0.80, 0.58)
SHELL_DARK = (0.60, 0.54, 0.34)
SEG = (0.80, 0.68, 0.46)
SEG_DARK = (0.52, 0.42, 0.26)
LIMB = (0.90, 0.78, 0.60)
EYE = (0.05, 0.04, 0.03)

CY, CL, CW, CH = -0.22, 0.56, 0.11, 0.14


def carapace_col(co, n):
    z = co.z / CH
    c = nh.lerp(SHELL, SHELL_DARK, 0.25 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.sin(z * 28)))
    c = nh.lerp(c, SHELL_DARK, 0.7 * nh.smoothstep(0.012, 0.0, abs(co.x)) * nh.smoothstep(0.5, 0.9, z))
    return c


def build():
    mb = nh.MeshBuilder()
    # pod-shaped carapace: an ellipsoid pinched to points at both ends
    def deform(v):
        return 1.0 - 0.45 * abs(v.y) ** 3 * (1 - abs(v.y)) * 4 if abs(v.y) < 1 else 1.0
    bm = nh.uv_ellipsoid((0, 0, 0), (CW, CL, CH), 28, 14)
    for v in bm.verts:
        t = abs(v.co.y) / CL
        k = (1 - t ** 2.2) ** 0.5 / max(1e-3, (1 - t ** 2) ** 0.5) if t < 0.999 else 0.0
        k = min(1.0, k) * (1 - 0.6 * t ** 4)
        v.co.x *= k
        v.co.z *= k
        v.co.y += CY
    mb.add(bm, carapace_col)
    # limbs underneath
    for k in range(9):
        y = CY - CL * 0.55 + k * CL * 1.1 / 8
        for sx in (-1, 1):
            p = Vector((sx * 0.03, y, -0.09))
            mb.add(nh.tube([p, p + Vector((sx * 0.03, 0.02, -0.06))], [0.016, 0.004], sides=5,
                           scale_xy=(0.4, 1.0)), LIMB)
    # eyes and antennae at the front
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.03, CY - CL * 0.80, 0.0), (0.02, 0.025, 0.02), 2), EYE)
        p = Vector((sx * 0.02, CY - CL * 0.85, -0.03))
        mb.add(nh.tube([p, p + Vector((sx * 0.05, -0.12, -0.01)), p + Vector((sx * 0.09, -0.22, 0.0))],
                       [0.007, 0.004, 0.0], sides=4), LIMB)
    # short abdomen
    y = CY + CL * 0.88
    r = 0.045
    for i in range(5):
        L = 0.07
        mb.add(nh.tube([(0, y - 0.01, -0.01), (0, y + L, -0.012)], [r, r * 0.92], sides=12),
               lambda co, n, y=y, L=L: nh.lerp(SEG, SEG_DARK, nh.smoothstep(y + L * 0.7, y + L, co.y)))
        y += L
        r *= 0.92
    # furca: two slender spines spreading apart, plus a short telson
    base = Vector((0, y - 0.01, -0.012))
    mb.add(nh.tube([base, base + Vector((0, 0.06, 0))], [0.02, 0.0], sides=6), SEG_DARK)
    for sx in (-1, 1):
        mb.add(nh.tube([base + Vector((sx * 0.012, 0, 0)), base + Vector((sx * 0.05, 0.14, 0.0)),
                        base + Vector((sx * 0.08, 0.26, 0.01))], [0.012, 0.008, 0.0], sides=5), SEG_DARK)
    return kit.finish_swim(mb, NAME, roughness=0.35)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.SWIM_VIEWS)
