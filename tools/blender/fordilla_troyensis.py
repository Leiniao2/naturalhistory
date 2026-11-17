"""
Procedural Fordilla troyensis (Early Cambrian), the earliest known bivalve, for the map
(Fixed style).

A tiny clam, about 4 mm long: two smooth, thin, laterally compressed valves of equal
size, longer than high, with the beaks (umbones) set forward and low, a straight hinge
along the top and fine concentric growth lines. The valves gape a little along the
bottom, where a pale muscular foot reaches down into the sediment; the shell sits half
sunk in a low mound of sand. Colours are speculative: a pale horn-brown shell with
darker growth bands.

Usage:
  blender --background --python tools/blender/fordilla_troyensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Fordilla.fbx
Pivot at the base (z = 0), front (beaks) toward -Y.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402

SHELL = (0.78, 0.66, 0.48)
SHELL_DARK = (0.52, 0.40, 0.28)
BEAK = (0.62, 0.50, 0.36)
FOOT = (0.92, 0.74, 0.62)
SAND = (0.80, 0.74, 0.60)
SAND_DARK = (0.66, 0.60, 0.48)

LENGTH = 0.62   # half-length of the shell (along Y)
HEIGHT = 0.42   # half-height (along Z)
WIDTH = 0.24    # half-width across both valves (along X)
BASE_Z = 0.30   # centre height of the shell above the ground (half sunk)
BEAK_Y = -0.26  # beaks forward of the middle
GAPE = 0.035    # the valves stand apart this much along the bottom


def shell():
    """Both valves as one closed shell: compressed sideways, longer behind the beaks, a
    straight hinge along the top, low umbones near the front, and a narrow groove along
    the commissure where the valves meet (wider at the bottom, where they gape)."""
    def shape(n):
        k = 1.0 + 0.10 * max(0.0, n.y) - 0.06 * max(0.0, -n.y)
        if n.z > 0.6:
            k *= 1.0 - 0.2 * (n.z - 0.6)
        return k

    bm = nh.ellipsoid((0, 0, 0), (WIDTH, LENGTH, HEIGHT), subdivisions=4, deform=shape)
    for v in bm.verts:
        # umbones: a low swelling on each valve near the top front
        d = math.hypot(v.co.y - BEAK_Y, v.co.z - HEIGHT * 0.72)
        bump = nh.smoothstep(0.3, 0.0, d)
        v.co.x *= 1.0 + 0.25 * bump
        v.co.z += 0.05 * bump
        # the commissure: pull the surface in along the plane where the valves meet
        groove = nh.smoothstep(0.05, 0.0, abs(v.co.x)) * (0.4 + 0.6 * nh.smoothstep(0.0, -HEIGHT, v.co.z))
        v.co.z += GAPE * groove if v.co.z > 0 else -0.0
        v.co.y *= 1.0
    nh.transform(bm, Matrix.Translation(Vector((0, 0, BASE_Z))))

    def col(co, n):
        z = co.z - BASE_Z
        # concentric growth bands around the beaks
        d = math.hypot(co.y - BEAK_Y, z - HEIGHT * 0.72)
        band = nh.smoothstep(0.45, 0.9, math.sin(d * 44.0))
        c = nh.lerp(SHELL, SHELL_DARK, band * 0.4)
        c = nh.lerp(c, BEAK, nh.smoothstep(0.22, 0.0, d) * 0.6)
        # the dark line of the commissure, widening into the gape along the bottom
        w = 0.012 + 0.03 * nh.smoothstep(0.0, -HEIGHT, z)
        c = nh.lerp(c, (0.22, 0.16, 0.12), nh.smoothstep(w, w * 0.4, abs(co.x)) * (0.5 if z > 0 else 0.9))
        return c

    return bm, col


def build():
    mb = nh.MeshBuilder()
    mb.add(*shell())

    # the foot pushes down out of the gape into the sand, toward the front
    foot = [(0, -0.10, BASE_Z - 0.20), (0, -0.22, BASE_Z - 0.34), (0, -0.34, BASE_Z - 0.40), (0, -0.44, BASE_Z - 0.40)]
    mb.add(nh.tube(foot, [0.06, 0.07, 0.06, 0.0], sides=10, scale_xy=(0.7, 1.0)), FOOT)

    # a low mound of sand the clam sits in
    def mound(n):
        return 1.0 + 0.06 * math.sin(n.x * 9.0) * math.cos(n.y * 7.0)

    sand = nh.ellipsoid((0, 0, 0.0), (0.62, 0.95, 0.20), subdivisions=3, deform=mound)

    def sand_col(co, n):
        return nh.lerp(SAND_DARK, SAND, nh.smoothstep(-0.05, 0.15, co.z))

    mb.add(sand, sand_col)

    obj = mb.to_object("Fordilla", roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Fordilla", ground=(0.55, 0.50, 0.40), views=((35, 25), (-90, 8), (0, 90)))
