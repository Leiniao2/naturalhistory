"""
Procedural Purussaurus brasiliensis (Late Miocene of the western Amazon, Brazil
and Peru) for map colonies: a giant caiman, one of the largest crocodylians
ever, perhaps 10-12 m long.

A caiman build scaled up: a huge, broad, rounded snout (the skull alone was
about 1.4 m long), a heavy body covered in rows of bony scutes, short sprawling
legs and a long, deep, crested tail. Olive-brown above with darker bands, a
pale yellowish belly. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/purussaurus_brasiliensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PurussaurusBrasiliensis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.30, 0.30, 0.20)
BAND = (0.16, 0.16, 0.11)
BELLY = (0.72, 0.68, 0.48)
EYE = (0.75, 0.62, 0.20)
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
    # neck and head
    b.add(nh.tube([(0, -0.52, H + 0.03), (0, -0.70, H + 0.04)], [0.14, 0.12], sides=14, scale_xy=(1.3, 0.75)), TOP)
    b.add(nh.ellipsoid((0, -0.78, H + 0.06), (0.15, 0.13, 0.085)), TOP)                     # skull table
    snout = nh.tube([(0, -0.82, H + 0.05), (0, -1.05, H + 0.02), (0, -1.28, H)], [0.10, 0.085, 0.075], sides=14,
                    scale_xy=(1.45, 0.55))
    b.add(snout, TOP)
    b.add(nh.ellipsoid((0, -1.27, H + 0.0), (0.11, 0.07, 0.045)), TOP)                       # rounded snout tip
    b.add(nh.tube([(0, -0.74, H - 0.03), (0, -1.24, H - 0.035)], [0.085, 0.07], sides=12, scale_xy=(1.45, 0.4)), BELLY)
    for sx in (-1, 1):
        b.add(nh.ellipsoid((sx * 0.07, -0.80, H + 0.12), (0.035, 0.04, 0.03)), TOP)              # eye bosses
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
            claws.append((ft + d * r * 1.4 + Vector((0, 0, 0.0)), d))
    fused = b.fuse(voxel=0.016, smooth=3, smooth_factor=0.5, max_tris=11000)
    fused.normal_update()
    # scute bumps on the back and tail crests
    for v in fused.verts:
        if v.normal.z > 0.5 and v.co.z > H:
            q = noise.voronoi(Vector((v.co.x * 22, v.co.y * 14, 0)), distance_metric="DISTANCE")[0][0]
            v.co.z += 0.012 * max(0.0, 0.6 - q) * (1.0 if v.co.y > -0.6 else 0.3)
            if v.co.y > 0.45 and abs(v.co.x - 0.03 * (v.co.y - 0.4)) < 0.04:
                v.co.z += 0.02 * nh.smoothstep(1.6, 0.6, v.co.y)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            p, n = l.vert.co, l.vert.normal
            c = nh.lerp(BELLY, TOP, nh.smoothstep(-0.4, 0.2, n.z))
            if p.y > -0.4 and n.z > -0.2:
                band = 0.5 + 0.5 * math.sin(p.y * 22)
                c = nh.lerp(c, BAND, 0.7 * nh.smoothstep(0.7, 0.9, band))
            c = nh.lerp(c, BAND, 0.3 * max(0.0, noise.noise(p * 20)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for i in range(12):
        y = -1.27 + 0.42 * i / 11
        for sx in (-1, 1):
            x = sx * (0.12 + 0.025 * math.sin(i * 0.9) - 0.03 * (1 - i / 11))
            mb.add(nh.tube([(x, y, H - 0.01), (x * 1.02, y, H - 0.05 - 0.01 * (i % 3 == 0))], [0.009, 0.0], sides=5), TOOTH)
            mb.add(nh.tube([(x * 0.93, y + 0.02, H - 0.03), (x * 0.95, y + 0.02, H + 0.01)], [0.008, 0.0], sides=5), TOOTH)
    for sx in (-1, 1):
        e = (sx * 0.075, -0.81, H + 0.145)
        mb.add(nh.ellipsoid(e, (0.022, 0.026, 0.016), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((e[0], e[1] - 0.008, e[2] + 0.009), (0.005, 0.016, 0.009), subdivisions=1), PUPIL)
    for tip, d in claws:
        mb.add(nh.tube([tuple(tip), tuple(tip + d * 0.03 + Vector((0, 0, -0.01)))], [0.008, 0.0], sides=5), CLAW)
    obj = mb.to_object("PurussaurusBrasiliensis")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PurussaurusBrasiliensis", ground=(0.35, 0.38, 0.28), views=((35, 25), (-90, 8), (10, 60)))
