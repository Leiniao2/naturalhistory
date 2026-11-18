"""
Procedural Ceratiocaris papilio (Silurian phyllocarid crustacean of Lesmahagow, Scotland,
up to about 20 cm long with its tail spines) for map colonies (Swim style).

A shrimp-like crustacean: a large, smooth, bivalved carapace (two oval side valves
hinged along the back, with fine ridges running parallel to the lower edge and a small
pointed rostral plate in front) covering the head and thorax, leaf-like thoracic limbs
underneath, a long, muscular abdomen of seven ringed segments sticking out behind, and
a long, dagger-like telson flanked by two shorter spines (furcal rami): a three-pronged
tail that it flicked to dart backwards away from danger. Amber-brown with darker
segment margins. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ceratiocaris_papilio.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CeratiocarisPapilio.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

NAME = "CeratiocarisPapilio"
SHELL = (0.70, 0.50, 0.26)
SHELL_DARK = (0.40, 0.25, 0.11)
SHELL_LIGHT = (0.86, 0.70, 0.46)
SEG = (0.64, 0.44, 0.24)
SEG_DARK = (0.34, 0.20, 0.10)
SPINE = (0.30, 0.18, 0.08)
LIMB = (0.84, 0.66, 0.46)
EYE = (0.04, 0.03, 0.03)

CY, CL, CW, CH = -0.38, 0.36, 0.15, 0.17   # carapace centre y, half-length, half-width, half-height


def carapace_col(co, n):
    # fine ridges parallel to the lower margin, a dark hinge line along the top
    z = (co.z) / CH
    c = nh.lerp(SHELL, SHELL_LIGHT, 0.3 * (0.5 + 0.5 * math.sin(z * 40.0)) * nh.smoothstep(0.2, -0.6, z))
    c = nh.lerp(c, SHELL_DARK, nh.smoothstep(0.90, 0.99, z) * nh.smoothstep(0.02, 0.0, abs(co.x)) + 0.0)
    c = nh.lerp(c, SHELL_DARK, 0.6 * nh.smoothstep(0.012, 0.0, abs(co.x)) * nh.smoothstep(0.6, 0.9, z))
    return c


def build():
    mb = nh.MeshBuilder()
    # the two valves: one shell, flattened and slightly keeled on top, open-looking underneath
    def deform(n):
        k = 1.0
        if n.z < -0.55:
            k *= 0.92
        return k
    mb.add(nh.uv_ellipsoid((0, CY, 0.02), (CW, CL, CH), 24, 14, deform=deform), carapace_col)
    # gap between the valves underneath (dark), limbs peeking out
    mb.add(nh.uv_ellipsoid((0, CY, -0.10), (CW * 0.55, CL * 0.85, 0.05), 12, 6), SHELL_DARK)
    for k in range(8):
        y = CY - CL * 0.6 + k * CL * 1.2 / 7
        for sx in (-1, 1):
            p = Vector((sx * 0.05, y, -0.11))
            mb.add(nh.tube([p, p + Vector((sx * 0.04, 0.02, -0.06))], [0.02, 0.006], sides=5,
                           scale_xy=(0.4, 1.0)), LIMB)
    # rostral plate
    mb.add(nh.tube([(0, CY - CL * 0.92, 0.10), (0, CY - CL - 0.06, 0.09), (0, CY - CL - 0.13, 0.06)],
                   [0.035, 0.02, 0.0], sides=6, scale_xy=(1.0, 0.45)), SHELL)
    # eyes and short antennae
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.045, CY - CL + 0.01, 0.04), (0.028, 0.028, 0.028), 2), EYE)
        p = Vector((sx * 0.03, CY - CL + 0.02, -0.02))
        mb.add(nh.tube([p, p + Vector((sx * 0.05, -0.10, -0.01)), p + Vector((sx * 0.09, -0.18, 0.0))],
                       [0.008, 0.005, 0.0], sides=4), LIMB)
    # abdomen: seven rings tapering back, gently curved down then up
    y = CY + CL * 0.70
    r = 0.085
    for i in range(7):
        L = 0.105 - i * 0.004
        z0 = 0.03 - 0.012 * i
        r1 = r * 0.93
        pts = [(0, y - 0.01, z0), (0, y + L * 0.6, z0 - 0.004), (0, y + L, z0 - 0.008)]
        mb.add(nh.tube(pts, [r, r * 0.98, r1], sides=14, scale_xy=(0.85, 1.0)),
               lambda co, n, y=y, L=L: nh.lerp(SEG, SEG_DARK, nh.smoothstep(y + L * 0.7, y + L, co.y)))
        y += L
        r = r1
    # long telson and two furcal spines
    zt = 0.03 - 0.012 * 7
    base = Vector((0, y - 0.01, zt))
    mb.add(nh.tube([base, base + Vector((0, 0.22, 0.01)), base + Vector((0, 0.44, 0.02))], [0.032, 0.018, 0.0],
                   sides=7), SPINE)
    for sx in (-1, 1):
        mb.add(nh.tube([base + Vector((sx * 0.03, 0, 0)), base + Vector((sx * 0.09, 0.15, 0.0)),
                        base + Vector((sx * 0.13, 0.28, 0.01))], [0.022, 0.012, 0.0], sides=6), SPINE)
    obj = mb.to_object(NAME, roughness=0.4)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.05, 0.20, 0.24), views=((30, 30), (0, 85), (-90, 10)))
