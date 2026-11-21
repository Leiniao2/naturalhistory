"""
Procedural Hippurites radiosus (Late Cretaceous hippuritid rudist bivalve, southern Europe)
for map colonies (Fixed style).

A reef-building rudist: the right (lower) valve is a tall, thick, horn-shaped cone,
ribbed lengthwise and cemented upright in the sea floor, with the three characteristic
longitudinal furrows (over the internal pillars); the left (upper) valve is a low, flat
lid riddled with radial pores, through which it strained food. A small clump of three of
different heights, set in carbonate mud. Grey-cream shell, darker growth lines, a brown
lid and a hint of greenish mantle at the gape (colours conjectural).
Pivot on the sea floor (z = 0), faces -Y.

Usage:
  blender --background --python tools/blender/hippurites_radiosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hippurites.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_b2_cretaceous_inverts as iv  # noqa: E402

SHELL = (0.82, 0.78, 0.68)
SHELL_DARK = (0.56, 0.50, 0.42)
LID = (0.50, 0.38, 0.26)
PORE = (0.22, 0.16, 0.12)
MANTLE = (0.40, 0.48, 0.30)
MUD = ((0.62, 0.58, 0.48), (0.74, 0.70, 0.60))


def horn(mb, base, height, r_top, lean, seed):
    furrows = (0.3 + seed, 1.2 + seed, 1.9 + seed)

    def radial(th, t):
        m = 1.0 + 0.07 * math.cos(th * 18)                         # longitudinal ribs
        for f in furrows:
            m -= 0.2 * math.exp(-((math.atan2(math.sin(th - f), math.cos(th - f))) / 0.12) ** 2)
        return m

    def color(th, t, z):
        c = nh.lerp(SHELL_DARK, SHELL, nh.smoothstep(0.0, 0.8, t))
        band = 0.5 + 0.5 * math.sin(z / height * 40.0)
        c = nh.lerp(c, SHELL_DARK, 0.6 * nh.smoothstep(0.6, 1.0, band))
        return nh.lerp(c, SHELL, 0.25 * (0.5 + 0.5 * math.cos(th * 18)))

    prof = [(0.0, -0.05)] + [(r_top * (0.12 + 0.88 * (k / 10) ** 0.8), height * k / 10) for k in range(11)] + \
           [(r_top * 1.02, height + 0.005), (r_top * 0.92, height + 0.01)]
    bm = iv.revolve(prof, segments=72, radial=radial, color=color)
    rot = Matrix.Rotation(lean[0], 4, "X") @ Matrix.Rotation(lean[1], 4, "Y")
    nh.transform(bm, Matrix.Translation(Vector(base)) @ rot)
    mb.add(bm, None)
    # the gape: a thin dark-green mantle ring, then the porous lid
    top = Vector(base) + rot.to_3x3() @ Vector((0, 0, height + 0.012))
    up = rot.to_3x3() @ Vector((0, 0, 1))
    ring = nh.ellipsoid((0, 0, 0), (r_top * 0.95, r_top * 0.95, 0.012), subdivisions=3)
    nh.transform(ring, Matrix.Translation(top) @ rot)
    mb.add(ring, MANTLE)

    def lid_col(co, n):
        q = rot.to_3x3().inverted() @ (Vector(co) - top)
        rr = math.hypot(q.x, q.y) / r_top
        th = math.atan2(q.y, q.x)
        pore = nh.smoothstep(0.75, 0.95, 0.5 + 0.5 * math.cos(th * 24)) * nh.smoothstep(0.25, 0.4, rr)
        return nh.lerp(LID, PORE, 0.7 * pore)
    lid = nh.ellipsoid((0, 0, 0), (r_top * 0.98, r_top * 0.98, r_top * 0.12), subdivisions=3)
    nh.transform(lid, Matrix.Translation(top + up * 0.012) @ rot)
    mb.add(lid, lid_col)


def build():
    mb = nh.MeshBuilder()
    iv.floor_patch(mb, 0.55, MUD[0], MUD[1], seed=4.0)
    horn(mb, (0.0, 0.05, 0.0), 0.95, 0.17, (0.05, -0.04), 0.0)
    horn(mb, (0.22, -0.12, 0.0), 0.62, 0.13, (0.12, 0.25), 1.0)
    horn(mb, (-0.22, -0.08, 0.0), 0.45, 0.11, (0.15, -0.3), 2.0)
    obj = mb.to_object("Hippurites", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Hippurites", background=(0.05, 0.15, 0.18), ground=(0.30, 0.29, 0.26),
           views=((30, 25), (0, 70), (-90, 8)))
