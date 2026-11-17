"""
Procedural low-poly Salpingoeca rosetta: a rosette colony of choanoflagellates.

A ball of a dozen teardrop-shaped cells joined at their narrow bases in the middle, each facing
outward with a collar of fine microvilli round a long beating flagellum, as the colonies that
form when the cells divide without separating. Pale cream cells, darker nucleus showing near the
base, clear collars. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/choanoflagellate.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Choanoflagellate.fbx
About 1.6 units across including the flagella. Pivot at the colony centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 7
CELLS = 13
CELL_LEN = 0.30        # length of one cell from its base (centre side) to the collar
CELL_R = 0.11          # radius of a cell at its widest
COLLAR_LEN = 0.13
MICROVILLI = 14
FLAGELLUM = 0.42

CELL = (0.88, 0.84, 0.66)
CELL_DEEP = (0.74, 0.70, 0.50)
NUCLEUS = (0.50, 0.44, 0.30)
COLLAR = (0.90, 0.94, 0.90)
FLAG = (0.95, 0.96, 0.92)
MATRIX = (0.80, 0.82, 0.70)


def frame(d):
    side = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
    return side, side.cross(d).normalized()


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    # a little extracellular matrix holding the bases together in the middle
    mb.add(nh.ellipsoid((0, 0, 0), (0.13, 0.13, 0.13), subdivisions=2), MATRIX)
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(CELLS):
        z = 1.0 - (i + 0.5) / CELLS * 2.0
        r = math.sqrt(1.0 - z * z)
        a = golden * i
        d = Vector((math.cos(a) * r, math.sin(a) * r, z))
        d = (d + Vector((rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)))).normalized()
        side, up = frame(d)
        base = d * 0.06
        # teardrop cell: narrow at the base, round toward the collar
        pts, radii = [], []
        for k in range(7):
            t = k / 6
            pts.append(base + d * (CELL_LEN * t))
            radii.append(CELL_R * (0.25 + 0.75 * math.sin(math.pi * (0.15 + 0.7 * t)) ** 0.8) if 0 < k < 6 else CELL_R * (0.25 if k == 0 else 0.45))

        def cell_col(co, n, d=d):
            along = co.dot(d)
            c = nh.lerp(CELL_DEEP, CELL, nh.smoothstep(0.08, 0.25, along))
            return nh.lerp(c, NUCLEUS, (1 - nh.smoothstep(0.0, 0.05, abs(along - 0.17))) * 0.6)

        mb.add(nh.tube(pts, radii, sides=10), cell_col)
        tip = base + d * CELL_LEN
        # collar of microvilli flaring a little outward
        for k in range(MICROVILLI):
            a2 = k / MICROVILLI * math.tau
            ring = side * math.cos(a2) + up * math.sin(a2)
            p0 = tip + ring * CELL_R * 0.42 - d * 0.01
            p1 = p0 + d * COLLAR_LEN + ring * 0.035
            mb.add(nh.tube([p0, p1], [0.006, 0.003], sides=3), COLLAR)
        # flagellum out of the collar, gently wavy
        fl = []
        for k in range(8):
            t = k / 7
            fl.append(tip + d * (0.02 + FLAGELLUM * t) + side * 0.03 * math.sin(t * math.tau * 1.3 + i))
        mb.add(nh.tube(fl, [0.010, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004, 0.0], sides=4), FLAG)
    return mb.to_object("Choanoflagellate", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Choanoflagellate", views=((35, 40), (-80, 15), (180, 60)))
