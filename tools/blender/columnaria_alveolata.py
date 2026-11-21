"""
Procedural Columnaria alveolata (Ordovician colonial rugose coral, North America) for map
colonies (Fixed style).

A massive, cushion-shaped coral head built of hundreds of long, slender corallites packed
so tightly that their walls are shared and polygonal (mostly six-sided), like a honeycomb
seen from above. Each corallite opens in a shallow cup (calice) with fine radiating septa,
where a small polyp lived. Built as a dome of hexagonal prisms, each with a pale wall rim,
a darker sunken calice with radial septa and, in some, an extended polyp. Cream walls,
brown calices. Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/columnaria_alveolata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ColumnariaAlveolata.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "ColumnariaAlveolata"
WALL = (0.86, 0.80, 0.66)
SIDE = (0.62, 0.55, 0.42)
CALICE = (0.48, 0.32, 0.20)
SEPTA = (0.70, 0.58, 0.42)
POLYP = (0.82, 0.58, 0.46)

R = 0.62      # colony radius
HT = 0.42     # colony height
S = 0.075     # hexagon circumradius


def dome(x, y):
    r = math.hypot(x, y) / R
    return 0.06 + HT * max(0.0, 1.0 - r ** 2.4) ** 0.55 + 0.02 * noise.noise(Vector((x * 3, y * 3, 0.5)))


def prism(mb, cx, cy, polyp):
    top = dome(cx, cy)
    bm = bmesh.new()
    cl = bm.loops.layers.color.new("Col")
    k = 0.995
    outer = [Vector((cx + S * k * math.cos(a), cy + S * k * math.sin(a), 0)) for a in
             [math.pi / 6 + i * math.pi / 3 for i in range(6)]]
    bot = [bm.verts.new((p.x, p.y, 0.0)) for p in outer]
    rim = [bm.verts.new((p.x, p.y, top)) for p in outer]
    inner = [bm.verts.new((cx + (p.x - cx) * 0.62, cy + (p.y - cy) * 0.62, top - 0.01)) for p in outer]
    c = bm.verts.new((cx, cy, top - 0.045))

    def face(vs, colfn):
        f = bm.faces.new(vs)
        for l in f.loops:
            col = colfn(l.vert.co)
            l[cl] = (col[0], col[1], col[2], 1.0)

    for i in range(6):
        j = (i + 1) % 6
        face([bot[i], bot[j], rim[j], rim[i]], lambda co: nh.lerp(SIDE, WALL, co.z / max(top, 1e-3) * 0.6))
        face([rim[i], rim[j], inner[j], inner[i]], lambda co: WALL)
        face([inner[i], inner[j], c], lambda co: CALICE)
    face(list(reversed(bot)), lambda co: SIDE)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mb.add(bm, None, smooth=False)
    # septa: thin radial ridges in the calice
    for i in range(12):
        a = i / 12 * math.tau
        p0 = Vector((cx + 0.012 * math.cos(a), cy + 0.012 * math.sin(a), top - 0.035))
        p1 = Vector((cx + S * 0.55 * math.cos(a), cy + S * 0.55 * math.sin(a), top - 0.008))
        mb.add(nh.tube([p0, p1], [0.004, 0.004], sides=3), SEPTA, smooth=False)
    if polyp:
        cz = top - 0.03
        mb.add(nh.tube([(cx, cy, cz), (cx, cy, cz + 0.04)], [0.022, 0.02], sides=8), POLYP)
        for i in range(10):
            a = i / 10 * math.tau
            b = Vector((cx + 0.018 * math.cos(a), cy + 0.018 * math.sin(a), cz + 0.04))
            mb.add(nh.tube([b, b + Vector((math.cos(a) * 0.035, math.sin(a) * 0.035, 0.03))], [0.006, 0.0],
                           sides=4), POLYP)


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, R * 1.35)
    rnd = kit.seeded(5)
    w = S * math.sqrt(3)
    n = int(R / w) + 2
    for q in range(-n, n + 1):
        for r in range(-n, n + 1):
            x = w * (q + r / 2.0)
            y = S * 1.5 * r
            a = math.atan2(y, x)
            if math.hypot(x, y) > R * (1.0 + 0.06 * math.sin(a * 3 + 1)) - S * 0.5:
                continue
            prism(mb, x, y, rnd.random() < 0.3)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
