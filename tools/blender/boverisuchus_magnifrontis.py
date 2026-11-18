"""
Procedural Boverisuchus magnifrontis (Messel, Germany, middle Eocene, ~47 Ma) for map colonies:
a "hoofed crocodile" (Planocraniidae), a land-hunting crocodylian about 3 m long.

Unlike living crocodiles it stood tall on long, upright legs and its toes ended in
blunt, hoof-like claws for running; the snout was deep and narrow (not flat) and
lined with blade-like, serrated teeth like a theropod's, for slicing up land prey.
Rows of bony scutes along the back, a long tail kept clear of the ground.
Shown dark brown with paler bands and a cream belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/boverisuchus_magnifrontis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BoverisuchusMagnifrontis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.30, 0.24, 0.16)
BAND = (0.50, 0.42, 0.28)
BELLY = (0.76, 0.70, 0.54)
EYE = (0.80, 0.60, 0.18)
PUPIL = (0.02, 0.02, 0.02)
TOOTH = (0.92, 0.88, 0.76)
HOOF = (0.14, 0.12, 0.10)


def build():
    b = nh.MeshBuilder()
    H = 0.34                              # height of the trunk axis: carried high on upright legs
    b.add(nh.tube([(0, -0.48, H + 0.02), (0, -0.22, H + 0.04), (0, 0.12, H + 0.04), (0, 0.36, H + 0.02)],
                  [0.11, 0.13, 0.13, 0.10], sides=16, scale_xy=(1.05, 0.95)), TOP)
    # long tail, held up and only drooping toward the tip
    pts = [(0, 0.32, H + 0.02), (0.01, 0.62, H - 0.01), (0.04, 0.92, H - 0.06), (0.07, 1.20, H - 0.12),
           (0.08, 1.42, H - 0.17)]
    b.add(nh.tube(pts, [0.09, 0.07, 0.05, 0.03, 0.01], sides=12, scale_xy=(0.6, 1.1)), TOP)
    # neck and the deep, narrow head
    b.add(nh.tube([(0, -0.45, H + 0.03), (0, -0.64, H + 0.06)], [0.10, 0.085], sides=14), TOP)
    b.add(nh.ellipsoid((0, -0.70, H + 0.08), (0.085, 0.10, 0.08)), TOP)                     # skull table
    b.add(nh.tube([(0, -0.74, H + 0.06), (0, -0.92, H + 0.03), (0, -1.08, H + 0.0)], [0.075, 0.062, 0.045],
                  sides=14, scale_xy=(0.62, 1.1)), TOP)                                        # tall, narrow snout
    b.add(nh.ellipsoid((0, -1.08, H - 0.005), (0.033, 0.05, 0.048)), TOP)
    b.add(nh.tube([(0, -0.68, H - 0.03), (0, -1.06, H - 0.045)], [0.06, 0.035], sides=12, scale_xy=(0.7, 0.6)),
          BELLY)                                                                               # lower jaw
    for sx in (-1, 1):
        b.add(nh.ellipsoid((sx * 0.05, -0.72, H + 0.14), (0.03, 0.035, 0.025)), TOP)        # eye bosses
    # upright legs, mid-stride; feet end in blunt hoof-like claws
    hooves = []
    for (y, sx, st, r) in ((-0.38, -1, -0.10, 0.04), (-0.38, 1, 0.08, 0.04), (0.28, -1, 0.08, 0.055),
                           (0.28, 1, -0.10, 0.055)):
        sh = Vector((sx * 0.11, y, H))
        kn = Vector((sx * 0.15, y + (0.05 if y > 0 else -0.02) + st * 0.4, H * 0.52))
        ft = Vector((sx * 0.15, y + st, 0.03))
        b.add(nh.ellipsoid(tuple(sh + Vector((sx * 0.01, 0, -0.03))), (r * 1.5, r * 2.2, r * 2.2)), TOP)
        b.add(nh.tube([tuple(sh), tuple(kn), tuple(ft)], [r * 1.3, r * 0.95, r * 0.7], sides=10), TOP)
        b.add(nh.ellipsoid(tuple(ft + Vector((0, -0.025, -0.008))), (r * 0.9, r * 1.4, 0.022)), TOP)
        for a in (-0.4, 0.0, 0.4):
            d = Vector((math.sin(a) * sx * 0.5, -1, 0)).normalized()
            hooves.append((ft + d * r * 1.3 + Vector((math.sin(a) * sx * r * 0.6, 0, -0.012)), d))
    fused = b.fuse(voxel=0.013, smooth=3, smooth_factor=0.5, max_tris=11000)
    fused.normal_update()
    for v in fused.verts:                      # scute bumps along the back
        if v.normal.z > 0.55 and v.co.z > H:
            q = noise.voronoi(Vector((v.co.x * 26, v.co.y * 16, 0)), distance_metric="DISTANCE")[0][0]
            v.co.z += 0.01 * max(0.0, 0.6 - q) * (1.0 if v.co.y > -0.55 else 0.2)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            p, n = l.vert.co, l.vert.normal
            c = nh.lerp(BELLY, TOP, nh.smoothstep(-0.4, 0.2, n.z))
            if p.y > -0.45 and n.z > -0.2 and p.z > H * 0.6:
                band = 0.5 + 0.5 * math.sin(p.y * 20)
                c = nh.lerp(c, BAND, 0.55 * nh.smoothstep(0.75, 0.95, band))
            c = nh.lerp(c, (0.15, 0.12, 0.08), 0.3 * max(0.0, noise.noise(p * 20)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    # blade-like teeth along the upper and lower jaw edges
    for i in range(11):
        t = i / 10
        y = -1.08 + 0.36 * t
        for sx in (-1, 1):
            x = sx * (0.024 + 0.018 * t)
            mb.add(nh.tube([(x, y, H - 0.01), (x * 1.05, y - 0.006, H - 0.045 - 0.012 * (i % 3 == 0))], [0.008, 0.0],
                           sides=4, scale_xy=(0.4, 1.0)), TOOTH)
    for sx in (-1, 1):
        e = (sx * 0.055, -0.73, H + 0.155)
        mb.add(nh.ellipsoid(e, (0.018, 0.022, 0.014), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((e[0] * 1.08, e[1] - 0.006, e[2] + 0.004), (0.004, 0.013, 0.009), subdivisions=1), PUPIL)
    for tip, d in hooves:
        mb.add(nh.ellipsoid(tuple(tip), (0.016, 0.02, 0.014), subdivisions=2), HOOF)
    obj = mb.to_object("BoverisuchusMagnifrontis")
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"BoverisuchusMagnifrontis: belly ~{H - 0.12:.3f}, height {top:.3f}, mapHip ~ {(H - 0.12) / top:.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "BoverisuchusMagnifrontis", ground=(0.35, 0.38, 0.28), views=((35, 25), (-90, 8), (10, 60)))
