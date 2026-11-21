"""
Procedural Micraster coranguinum (Late Cretaceous heart urchin, the European Chalk) for map
colonies (Fixed style).

An irregular, burrowing sea urchin about 6 cm long: a heart-shaped test, broad and
rounded behind, notched at the front where a deep groove runs from the top down to the
mouth, a low dome with the apex a little forward, four paired petal-shaped bands of pores
plus the front one in the groove, a flat underside, and a dense coat of short, fine spines
lying back. Shown half sunk in pale chalky mud. Pale buff test, brownish spines, darker
petals (colours conjectural).
Pivot on the sea floor (z = 0), faces -Y.

Usage:
  blender --background --python tools/blender/micraster_coranguinum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Micraster.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_b2_cretaceous_inverts as iv  # noqa: E402

TEST = (0.86, 0.78, 0.60)
PETAL = (0.50, 0.36, 0.22)
SPINE = (0.62, 0.46, 0.30)
MUD = ((0.80, 0.78, 0.72), (0.90, 0.88, 0.82))

FRONT = -math.pi / 2           # the -Y direction in the XY plane
PETALS = [FRONT + math.radians(a) for a in (0, 50, -50, 150, -150)]


def adiff(a, b):
    return abs(math.atan2(math.sin(a - b), math.cos(a - b)))


def radial(th, t):
    m = 1.0 - 0.16 * math.exp(-(adiff(th, FRONT) / 0.22) ** 2)      # the frontal notch
    m *= 1.0 + 0.08 * math.cos(th - FRONT)                          # narrower behind... wider at front shoulders
    return m


def color(th, t, z):
    c = TEST
    if t > 0.45:
        for k, p in enumerate(PETALS):
            w = 0.16 * math.sin(math.pi * min(1.0, (1.0 - t) / 0.55)) + 0.02
            if adiff(th, p) < w:
                c = nh.lerp(c, PETAL, 0.75)
    return c


def build():
    mb = nh.MeshBuilder()
    iv.floor_patch(mb, 0.9, MUD[0], MUD[1], seed=1.5, height=0.03)
    R = 0.5
    prof = [(0.0, 0.0), (0.85 * R, 0.0)]
    for k in range(13):
        a = k / 12 * math.pi / 2
        prof.append((R * math.cos(a) * (1.0 if k else 1.0), 0.04 + 0.46 * math.sin(a) ** 0.9))
    prof[-1] = (0.0, 0.5)
    test = iv.revolve(prof, segments=64, radial=radial, color=color)
    nh.transform(test, Matrix.Translation((0, 0.0, -0.02)) @ Matrix.Scale(1.0, 4) @ Matrix.Diagonal((1.0, 1.12, 1.0, 1.0)))
    test.normal_update()
    pts = []
    rnd = random.Random(5)
    for v in test.verts:
        if v.co.z > 0.06 and rnd.random() < 0.9:
            pts.append((v.co.copy(), v.normal.copy()))
    mb.add(test, None)
    iv.spine_fuzz(mb, pts, 0.03, 0.006, SPINE, tilt=(0, 0.6, -0.2))
    obj = mb.to_object("Micraster", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Micraster", background=(0.05, 0.15, 0.18), ground=(0.30, 0.29, 0.26),
           views=((30, 30), (0, 80), (-90, 8)))
