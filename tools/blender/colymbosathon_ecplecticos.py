"""
Procedural Colymbosathon ecplecticos (a myodocopid ostracod - a "seed shrimp" - about
5 mm long, preserved with its soft parts in the Herefordshire Lagerstaette of England,
about 425 million years ago) for map colonies (Swim).

A tiny crustacean enclosed in a smooth, bean-shaped, two-valved carapace with a notch
at the front, through which it rowed with a pair of big, bristly swimming antennae.
A large compound eye shows through the front of the shell; a few small limbs, the
feathery gills and the furca (tail) peek out of the gape along the underside. It is
the oldest known male animal preserved with its copulatory organ - its name means
"amazing swimmer with a large penis". Amber-brown shell. Faces -Y, pivot at the body
centre.

Usage:
  blender --background --python tools/blender/colymbosathon_ecplecticos.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ColymbosathonEcplecticos.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402

NAME = "ColymbosathonEcplecticos"
SHELL = (0.70, 0.46, 0.22)
SHELL_DARK = (0.44, 0.26, 0.12)
SHELL_LIGHT = (0.90, 0.72, 0.46)
LINE = (0.20, 0.12, 0.06)
LIMB = (0.86, 0.62, 0.42)
SETA = (0.96, 0.90, 0.74)
EYE = (0.08, 0.06, 0.06)

L, H, W = 0.62, 0.40, 0.30


def build():
    mb = nh.MeshBuilder()

    def shape(n):
        k = 1.0
        # rostral notch: pinch the front-lower part of the outline
        if n.y < -0.6 and -0.5 < n.z < 0.15:
            k *= 0.88
        return k

    def col(co, n):
        c = nh.lerp(SHELL_DARK, SHELL, nh.smoothstep(-0.3, 0.6, n.z))
        c = nh.lerp(c, SHELL_LIGHT, 0.4 * nh.smoothstep(0.6, 0.95, n.z))
        # concentric hint around the valve centre
        d = math.hypot(co.y / L, co.z / H)
        c = nh.lerp(c, SHELL_DARK, 0.25 * nh.smoothstep(0.85, 1.0, math.cos(d * 18.0)))
        return c
    mb.add(nh.ellipsoid((0, 0, 0), (W, L, H), subdivisions=4, deform=shape), col)
    # hinge line where the two valves meet along the back
    hinge = [(0.0, L * math.sin(a) * 1.0, H * math.cos(a) * 1.0 + 0.004) for a in [math.radians(-80 + 16 * i) for i in range(11)]]
    mb.add(nh.tube(hinge, [0.014] * 11, sides=6), LINE)
    # eye showing through the front of each valve
    for s in (1, -1):
        mb.add(nh.uv_ellipsoid((s * W * 0.72, -L * 0.62, H * 0.18), (0.035, 0.07, 0.07), 10, 6), EYE)
        mb.add(nh.uv_ellipsoid((s * W * 0.80, -L * 0.66, H * 0.24), (0.012, 0.02, 0.02), 6, 4), (0.9, 0.9, 0.85))
    # big swimming antennae out of the notch, each with a fan of long bristles
    for s in (1, -1):
        b = Vector((s * 0.06, -L * 0.88, -H * 0.15))
        j = b + Vector((s * 0.16, -0.12, -0.02))
        tip = j + Vector((s * 0.12, 0.10, -0.05))
        mb.add(nh.tube([b, j, tip], [0.035, 0.028, 0.016], sides=6), LIMB)
        for k in range(6):
            d = Vector((s * (0.6 + 0.1 * k), 0.2 + 0.25 * k, -0.25 + 0.05 * k)).normalized()
            mb.add(nh.tube([tip, tip + d * 0.30], [0.006, 0.0], sides=3), SETA, smooth=False)
        # small first antenna with sensory bristles
        a = Vector((s * 0.04, -L * 0.90, -H * 0.02))
        mb.add(nh.tube([a, a + Vector((s * 0.05, -0.10, 0.04)), a + Vector((s * 0.08, -0.16, 0.10))],
                       [0.016, 0.012, 0.0], sides=5), LIMB)
    # limbs, gills and furca along the ventral gape
    for k in range(3):
        b = Vector((0.0, -0.18 + 0.18 * k, -H * 0.92))
        for s in (1, -1):
            mb.add(nh.tube([b + Vector((s * 0.03, 0, 0)), b + Vector((s * 0.06, 0.02, -0.08))],
                           [0.014, 0.0], sides=4), LIMB)
    f = Vector((0.0, L * 0.70, -H * 0.62))
    mb.add(nh.tube([f, f + Vector((0, 0.05, -0.10)), f + Vector((0, 0.02, -0.18))], [0.02, 0.016, 0.0], sides=5), LIMB)
    return ec.centre(mb.to_object(NAME, roughness=0.35))


if __name__ == "__main__":
    ec.export(build, NAME)
