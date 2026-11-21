"""
Procedural Pentremites pyriformis (Early Carboniferous of North America, a blastoid
echinoderm with a cup 2-3 cm long on a short stem) for map colonies (Fixed style).

A small cluster of three on a patch of limy sea floor. Each has a jointed stem holding up
a pear-shaped, five-sided cup (narrow at the stem, broadest high up, flat-topped), with five
broad petal-shaped food grooves (ambulacra) running down from the star-shaped summit,
finely ribbed crosswise and coloured rust-orange against the cream plates, small dark
spiracle holes round the mouth, and a fringe of fine thread-like brachioles rising from the
edges of every groove. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pentremites_pyriformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pentremites.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

NAME = "Pentremites"
PLATE = (0.86, 0.78, 0.62)
PLATE_DARK = (0.66, 0.56, 0.42)
AMB = (0.78, 0.44, 0.20)
AMB_RIB = (0.55, 0.28, 0.12)
SPIRACLE = (0.10, 0.07, 0.05)
STEM = (0.70, 0.62, 0.48)
STEM_DARK = (0.50, 0.43, 0.32)
BRACH = (0.92, 0.70, 0.45)
SEABED = (0.50, 0.50, 0.44)
SEABED_DARK = (0.36, 0.37, 0.33)


def theca_radius(t):
    """t = 0 at the stem, 1 at the summit -> radius (pear profile, flat top)."""
    key = [(0.0, 0.03), (0.15, 0.07), (0.45, 0.16), (0.75, 0.22), (0.9, 0.21), (0.97, 0.15), (1.0, 0.0)]
    for (a, ra), (b, rb) in zip(key, key[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            u = u * u * (3 - 2 * u)
            return ra + (rb - ra) * u
    return 0.0


def theca(H, rings=26, seg=40):
    bm = bmesh.new()
    verts = []
    for i in range(rings + 1):
        t = i / rings
        r = theca_radius(t)
        row = []
        for k in range(seg):
            a = k / seg * math.tau
            # pentagonal section: bulge on the interambulacral corners, flat over the grooves
            pent = 1.0 + 0.07 * math.cos(5 * (a - math.pi / 5))
            row.append(bm.verts.new((math.cos(a) * r * pent, math.sin(a) * r * pent, t * H)))
        verts.append(row)
    for a, b in zip(verts, verts[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bot = bm.verts.new((0, 0, 0))
    top = bm.verts.new((0, 0, H))
    for k in range(seg):
        j = (k + 1) % seg
        bm.faces.new([verts[0][j], verts[0][k], bot])
        bm.faces.new([verts[-1][k], verts[-1][j], top])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def amb_half_width(t):
    """Half-angle (rad) of a groove at height t: petal from t=0.25 to the summit."""
    if t < 0.28:
        return 0.0
    u = (t - 0.28) / 0.72
    return math.radians(26) * (u ** 0.6) * (1 - 0.3 * u ** 4)


def one(mb, rng, origin, stem_h, H, lean):
    rot = Matrix.Rotation(lean[0], 4, "X") @ Matrix.Rotation(lean[1], 4, "Y")
    o = Vector(origin)

    def place(v):
        return o + (rot @ Vector(v).to_4d()).to_3d()

    # stem: stacked columnals
    n = 12
    for i in range(n):
        z0 = stem_h * i / n
        c = nh.ellipsoid((0, 0, z0 + stem_h / n * 0.5), (0.026, 0.026, stem_h / n * 0.62), 1)
        nh.transform(c, Matrix.Translation(o) @ rot)
        mb.add(c, STEM if i % 2 else STEM_DARK)
    # root holdfast
    for k in range(4):
        a = k * math.tau / 4 + rng.uniform(-0.3, 0.3)
        mb.add(nh.tube([o + Vector((0, 0, 0.02)), o + Vector((math.cos(a) * 0.07, math.sin(a) * 0.07, 0.0))],
                       [0.018, 0.008], sides=5), STEM_DARK)

    base = Vector((0, 0, stem_h))
    th = theca(H)
    nh.transform(th, Matrix.Translation(o) @ rot @ Matrix.Translation(base))

    def col(co, nrm):
        c = rot.inverted() @ (co - o).to_4d()
        c = c.to_3d() - base
        t = max(0.0, min(1.0, c.z / H))
        a = math.atan2(c.y, c.x)
        # grooves centred on a = 2*pi*k/5
        da = abs(((a + math.pi / 5) % (math.tau / 5)) - math.pi / 5)
        hw = amb_half_width(t)
        if hw > 0 and da < hw:
            rib = (t * 60.0) % 1.0
            cc = AMB_RIB if rib < 0.35 else AMB
            if da < hw * 0.18:
                cc = AMB_RIB
            return cc
        k = 0.5 + 0.5 * noise.noise(c * 30.0)
        cc = nh.lerp(PLATE_DARK, PLATE, 0.6 + 0.4 * k)
        if t < 0.3:
            cc = nh.lerp(cc, PLATE_DARK, 0.4)
        return cc
    mb.add(th, col)

    # spiracles round the summit and the mouth
    for k in range(5):
        a = k * math.tau / 5 + math.pi / 5
        p = place((math.cos(a) * 0.045, math.sin(a) * 0.045, stem_h + H * 0.985))
        mb.add(nh.ellipsoid(tuple(p), (0.014, 0.014, 0.008), 1), SPIRACLE)
    mb.add(nh.ellipsoid(tuple(place((0, 0, stem_h + H))), (0.02, 0.02, 0.01), 1), SPIRACLE)

    # brachioles: fine threads from both edges of each groove, curving up and out
    for k in range(5):
        a0 = k * math.tau / 5
        for side in (-1, 1):
            for j in range(6):
                t = 0.42 + 0.09 * j
                hw = amb_half_width(t)
                a = a0 + side * hw * 0.95
                r = theca_radius(t) * 1.03
                p0 = Vector((math.cos(a) * r, math.sin(a) * r, stem_h + t * H))
                out = Vector((math.cos(a), math.sin(a), 0))
                L = 0.20 + 0.06 * (1 - j / 5)
                p1 = p0 + out * L * 0.35 + Vector((0, 0, L * 0.45))
                p2 = p0 + out * L * 0.45 + Vector((0, 0, L * 1.0))
                mb.add(nh.tube([place(p0), place(p1), place(p2)], [0.006, 0.005, 0.002], sides=3), BRACH)


def build():
    rng = random.Random(5)
    mb = nh.MeshBuilder()

    def bed(n):
        return 1.0 + 0.15 * noise.noise(n * 2.5)
    mb.add(nh.ellipsoid((0, 0, 0.01), (0.62, 0.55, 0.05), subdivisions=3, deform=bed),
           lambda co, n: nh.lerp(SEABED_DARK, SEABED, 0.5 + 0.5 * noise.noise(co * 8.0)))
    one(mb, rng, (0.0, -0.08, 0.04), 0.42, 0.50, (math.radians(-6), math.radians(4)))
    one(mb, rng, (0.30, 0.18, 0.04), 0.26, 0.38, (math.radians(8), math.radians(14)))
    one(mb, rng, (-0.30, 0.20, 0.04), 0.18, 0.32, (math.radians(10), math.radians(-16)))
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.25, 0.32, 0.30), views=((35, 25), (-90, 8), (10, 75)))
