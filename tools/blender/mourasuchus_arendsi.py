"""
Procedural Mourasuchus arendsi (Late Miocene of the Amazon and Orinoco basins,
Brazil and Venezuela) for map colonies: the "duck-faced" caiman, a giant
crocodylian about 8-10 m long that probably fed by gulping or sieving small
prey from the water.

Adapted from purussaurus_brasiliensis.py. An extremely long, broad and very
flat, duck-bill-like skull, almost parallel-sided with a rounded tip, lined
with many tiny, uniform teeth; slender, weak lower jaws hanging from it, with a
saggy throat pouch below; small eyes on top of the skull table. A heavy body
covered in rows of bony scutes, short sprawling legs and a long, deep, crested
tail. Dark olive above with faint bands, pale yellowish belly and throat.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mourasuchus_arendsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MourasuchusArendsi.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.24, 0.26, 0.17)
BAND = (0.13, 0.14, 0.09)
BELLY = (0.74, 0.70, 0.50)
EYE = (0.72, 0.60, 0.22)
PUPIL = (0.02, 0.02, 0.02)
TOOTH = (0.92, 0.88, 0.76)
CLAW = (0.15, 0.13, 0.10)


def build():
    b = nh.MeshBuilder()
    H = 0.15                              # belly height of the trunk axis
    # trunk: wide, flattened
    b.add(nh.tube([(0, -0.55, H + 0.02), (0, -0.25, H + 0.05), (0, 0.15, H + 0.05), (0, 0.45, H + 0.02)],
                  [0.14, 0.17, 0.17, 0.13], sides=16, scale_xy=(1.35, 0.75)), TOP)
    # tail: long, deep and flattened sideways
    pts = [(0, 0.40, H + 0.03), (0.02, 0.75, H), (0.06, 1.05, H - 0.04), (0.08, 1.35, H - 0.07), (0.07, 1.60, H - 0.09)]
    b.add(nh.tube(pts, [0.12, 0.09, 0.065, 0.04, 0.012], sides=12, scale_xy=(0.6, 1.1)), TOP)
    # neck and skull table
    b.add(nh.tube([(0, -0.52, H + 0.03), (0, -0.70, H + 0.04)], [0.14, 0.12], sides=14, scale_xy=(1.3, 0.72)), TOP)
    b.add(nh.ellipsoid((0, -0.76, H + 0.05), (0.14, 0.11, 0.07)), TOP)
    # the duck bill: very long, broad and paper-flat, a little wider toward the rounded tip
    snout = nh.tube([(0, -0.80, H + 0.05), (0, -1.05, H + 0.035), (0, -1.25, H + 0.03), (0, -1.40, H + 0.03)],
                    [0.10, 0.105, 0.115, 0.11], sides=16, scale_xy=(1.55, 0.26))
    b.add(snout, TOP)
    b.add(nh.ellipsoid((0, -1.42, H + 0.03), (0.165, 0.06, 0.03)), TOP)                     # rounded tip
    # slender lower jaws and the saggy throat pouch between them
    for sx in (-1, 1):
        b.add(nh.tube([(sx * 0.12, -0.74, H - 0.02), (sx * 0.15, -1.10, H - 0.0), (sx * 0.15, -1.37, H + 0.005)],
                      [0.03, 0.022, 0.018], sides=8, scale_xy=(1.0, 0.7)), BELLY)
        b.add(nh.ellipsoid((sx * 0.075, -0.79, H + 0.10), (0.03, 0.035, 0.03)), TOP)         # small eye bosses
    b.add(nh.ellipsoid((0, -0.92, H - 0.04), (0.12, 0.26, 0.07)), BELLY)                      # gular pouch
    # legs: sprawling, elbows out
    claws = []
    for (y, sx, st, r) in ((-0.42, -1, -0.08, 0.045), (-0.42, 1, 0.06, 0.045), (0.32, -1, 0.06, 0.06), (0.32, 1, -0.08, 0.06)):
        sh = Vector((sx * 0.16, y, H))
        el = Vector((sx * 0.33, y + st * 0.5, H + 0.01))
        ft = Vector((sx * 0.38, y + st - 0.03, 0.02))
        b.add(nh.tube([tuple(sh), tuple(el), tuple(ft)], [r * 1.3, r, r * 0.8], sides=10), TOP)
        b.add(nh.ellipsoid(tuple(ft + Vector((0, -0.03, -0.0))), (r * 1.2, r * 1.5, 0.025)), TOP)
        for a in (-0.6, -0.2, 0.2, 0.6):
            d = Vector((math.sin(a) * sx, -math.cos(a), 0))
            claws.append((ft + d * r * 1.4, d))
    fused = b.fuse(voxel=0.012, smooth=3, smooth_factor=0.5, max_tris=14000)
    fused.normal_update()
    # scute rows on the back, crests on the tail (not on the smooth bill)
    for v in fused.verts:
        if v.normal.z > 0.5 and v.co.z > H and v.co.y > -0.75:
            q = noise.voronoi(Vector((v.co.x * 22, v.co.y * 14, 0)), distance_metric="DISTANCE")[0][0]
            v.co.z += 0.014 * max(0.0, 0.6 - q)
            if v.co.y > 0.45 and abs(v.co.x - 0.03 * (v.co.y - 0.4)) < 0.04:
                v.co.z += 0.02 * nh.smoothstep(1.6, 0.6, v.co.y)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            p, n = l.vert.co, l.vert.normal
            c = nh.lerp(BELLY, TOP, nh.smoothstep(-0.4, 0.2, n.z))
            if p.y > -0.7 and n.z > -0.2:
                band = 0.5 + 0.5 * math.sin(p.y * 20)
                c = nh.lerp(c, BAND, 0.65 * nh.smoothstep(0.7, 0.9, band))
            if p.y < -0.8 and n.z > 0.3:      # mottled brown bill
                c = nh.lerp(c, (0.30, 0.28, 0.18), 0.5)
            c = nh.lerp(c, BAND, 0.3 * max(0.0, noise.noise(p * 20)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    # many tiny uniform teeth along the bill edge
    n = 24
    for i in range(n):
        y = -1.42 + 0.58 * i / (n - 1)
        for sx in (-1, 1):
            x = sx * (0.165 - 0.035 * (i / (n - 1)) ** 2) if i > 0 else sx * 0.15
            mb.add(nh.tube([(x, y, H + 0.02), (x * 1.01, y, H - 0.005)], [0.005, 0.0], sides=4), TOOTH)
    for sx in (-1, 1):
        e = (sx * 0.075, -0.80, H + 0.128)
        mb.add(nh.ellipsoid(e, (0.017, 0.02, 0.013), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((e[0], e[1] - 0.006, e[2] + 0.007), (0.004, 0.012, 0.007), subdivisions=1), PUPIL)
        mb.add(nh.ellipsoid((sx * 0.03, -1.42, H + 0.055), (0.01, 0.01, 0.006), subdivisions=1), BAND)   # nostrils
    for tip, d in claws:
        mb.add(nh.tube([tuple(tip), tuple(tip + d * 0.03 + Vector((0, 0, -0.01)))], [0.008, 0.0], sides=5), CLAW)
    obj = mb.to_object("MourasuchusArendsi")
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"MourasuchusArendsi: belly ~{H - 0.12 * 0.75:.3f}, height {top:.3f}, mapHip ~ {(H - 0.09) / top:.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "MourasuchusArendsi", ground=(0.35, 0.38, 0.28), views=((35, 25), (-90, 8), (10, 60)))
