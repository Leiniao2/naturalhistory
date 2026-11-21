"""
Procedural Clypeaster aegyptiacus (Miocene to Pliocene of the Mediterranean and
Red Sea) for map colonies: a giant "sea biscuit", a thick relative of the sand
dollars.

A heavy, rounded-pentagonal sea urchin up to about 15 cm across, high-domed
on top and flat underneath, covered in a felt of tiny spines, with a large
five-petalled flower pattern (the rows of tube feet it breathed through) on
the dome. It lived half-buried in sand, sorting food particles from the
sediment. Sandy tan with darker brown petals. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/clypeaster_aegyptiacus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ClypeasterAegyptiacus.fbx
"""

import math
import sys
from pathlib import Path

import bmesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TEST = (0.80, 0.68, 0.48)
PETAL = (0.50, 0.36, 0.22)
PORE = (0.32, 0.22, 0.13)
UNDER = (0.86, 0.78, 0.62)

RAD = 0.75
H = 0.36


def outline(a):
    # rounded pentagon, a little longer than wide; corners at the petal tips (one petal points forward, -Y)
    return RAD * (1.0 + 0.07 * math.cos(5 * (a + math.pi / 2)))


def test():
    bm = bmesh.new()
    nr, na = 28, 100
    top = bm.verts.new((0, 0, H))
    rings = []
    for i in range(1, nr + 1):
        u = i / nr
        ring = []
        for j in range(na):
            a = j / na * math.tau
            r = outline(a) * u
            # high dome, steep sides, slight constriction at the margin
            z = H * (1.0 - u ** 2.6) ** 0.8 + 0.035
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        rings.append(ring)
    # rim and flat underside
    rim = []
    for j in range(na):
        a = j / na * math.tau
        r = outline(a) * 1.01
        rim.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0.015)))
    rings.append(rim)
    bottom = []
    for j in range(na):
        a = j / na * math.tau
        r = outline(a) * 0.9
        bottom.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0.0)))
    rings.append(bottom)
    centre = bm.verts.new((0, 0, 0.012))
    for j in range(na):
        k = (j + 1) % na
        bm.faces.new([top, rings[0][j], rings[0][k]])
        bm.faces.new([centre, rings[-1][k], rings[-1][j]])
    for a, b in zip(rings, rings[1:]):
        for j in range(na):
            k = (j + 1) % na
            bm.faces.new([a[j], b[j], b[k], a[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def colour(co, n):
    if n.z < -0.3:
        c = UNDER
        # five food grooves running to the central mouth
        a = math.atan2(co.y, co.x)
        g = math.cos(5 * (a + math.pi / 2))
        return nh.lerp(c, PETAL, 0.6 * nh.smoothstep(0.93, 0.99, g))
    r = Vector((co.x, co.y, 0)).length / RAD
    a = math.atan2(co.y, co.x)
    # petals: five lanceolate lobes from the apex out to ~70% of the radius
    best = 0.0
    for k in range(5):
        pa = -math.pi / 2 + k * math.tau / 5
        d = math.atan2(math.sin(a - pa), math.cos(a - pa))
        width = 0.36 * math.sin(min(1.0, r / 0.72) * math.pi) ** 0.7 + 0.02
        inside = (abs(d) < width) and r < 0.72
        if inside:
            edge = abs(abs(d) - width * 0.75)
            best = max(best, 1.0 - nh.smoothstep(0.0, 0.05, edge) * 0.0)
            # pore rows along the petal edges
            if abs(d) > width * 0.6:
                best = 2.0
    c = TEST
    if best >= 2.0:
        c = PORE
    elif best > 0:
        c = nh.lerp(TEST, PETAL, 0.55)
    c = nh.lerp(c, (1.0, 0.95, 0.85), 0.12 * max(0.0, noise.noise(co * 60)))      # spine felt
    return c


def build():
    mb = nh.MeshBuilder()
    mb.add(test(), colour)
    obj = mb.to_object("ClypeasterAegyptiacus", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ClypeasterAegyptiacus", ground=(0.74, 0.70, 0.56), views=((35, 35), (-90, 8), (0, 80)))
