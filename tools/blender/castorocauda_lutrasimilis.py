"""
Procedural Castorocauda lutrasimilis (Middle Jurassic docodont, Daohugou beds, Inner Mongolia)
for map colonies.

A semi-aquatic mammaliaform about 45 cm long and the largest Jurassic mammal relative known
when described (2006): an otter-like body with dense fur (hair impressions are preserved),
sprawling, webbed limbs built for swimming and digging, a long, low head with seal-like
fish-catching teeth, and a broad, flat, beaver-like tail covered in scales toward its tip.
Dark brown fur, paler throat and belly, grey scaly tail. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/castorocauda_lutrasimilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Castorocauda.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

FUR = (0.26, 0.18, 0.12)
BELLY = (0.66, 0.54, 0.40)
TAIL = (0.32, 0.30, 0.27)
SCALE_LINE = (0.18, 0.17, 0.15)
NOSE = (0.10, 0.08, 0.07)


def fur(co, n):
    c = nh.lerp(BELLY, FUR, nh.smoothstep(-0.5, 0.2, n.z))
    m = noise.noise((co.x * 50, co.y * 110, co.z * 50))
    return tuple(v * (1 + 0.15 * m) for v in c)


def tail_col(co, n):
    s = math.sin(co.y * 90) * math.sin(co.x * 90)
    return SCALE_LINE if abs(s) < 0.12 else TAIL


def build():
    H = 0.115
    rows = [(0, 0.32, H, 0.035, 0.03), (0, 0.22, H + 0.01, 0.09, 0.075), (0, 0.05, H + 0.02, 0.11, 0.09),
            (0, -0.12, H + 0.02, 0.1, 0.085), (0, -0.25, H + 0.03, 0.065, 0.06), (0, -0.33, H + 0.035, 0.06, 0.05),
            (0, -0.42, H + 0.025, 0.04, 0.035), (0, -0.49, H + 0.015, 0.02, 0.018), (0, -0.51, H + 0.012, 0, 0)]
    spine = kit.Spine(rows)
    fused = [spine.mesh(sides=18)]
    claws = []
    for sx in (1, -1):
        for y, st in ((-0.18, 0.04 * sx), (0.18, -0.04 * sx)):
            top = Vector((sx * 0.07, y, H))
            el = Vector((sx * 0.16, y + st, H * 0.75))
            ft = Vector((sx * 0.19, y + st - 0.03, 0.015))
            fused.append(kit.limb([top, el, ft], [0.04, 0.028, 0.02], sides=8))
            # webbed paddle foot
            fused.append(nh.ellipsoid((ft.x + sx * 0.01, ft.y - 0.035, 0.01), (0.035, 0.045, 0.01), subdivisions=2))
            for k in range(5):
                a = (k - 2) * 0.3
                d = Vector((math.sin(a) * sx * 0.6, -math.cos(a), 0)).normalized()
                b = Vector((ft.x + sx * 0.01, ft.y - 0.035, 0.012)) + d * 0.04
                claws.append((b, b + d * 0.015, 0.004))
    body = kit.fuse_parts(fused, 0.008, 9000)
    mb = nh.MeshBuilder()
    mb.add(body, fur)
    # broad flat tail
    out = []
    for i in range(13):
        t = i / 12
        out.append((0.075 * math.sin(t * math.pi) ** 0.7 + 0.025, 0.28 + 0.42 * t, H - 0.005 - 0.07 * t))
    pts = out + [(-x, y, z) for x, y, z in reversed(out)]
    tail = nh.tube([(0, y, z) for _, y, z in out], [max(0.004, x * 0.0) for x, _, _ in out], sides=4)
    tail.free()
    slab = bmesh.new()
    top = [slab.verts.new((x, y, z + 0.012)) for x, y, z in pts]
    bot = [slab.verts.new((x, y, z - 0.012)) for x, y, z in pts]
    slab.faces.new(top)
    slab.faces.new(list(reversed(bot)))
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        slab.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(slab, faces=slab.faces[:])
    bmesh.ops.subdivide_edges(slab, edges=slab.edges[:], cuts=2, use_grid_fill=True)
    bmesh.ops.recalc_face_normals(slab, faces=slab.faces[:])
    mb.add(slab, tail_col)
    kit.eyes(mb, (0.034, -0.4, H + 0.045), 0.009, iris=(0.05, 0.04, 0.04))
    mb.add(nh.ellipsoid((0, -0.505, H + 0.016), (0.012, 0.008, 0.009), subdivisions=1), NOSE)
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * 0.04, -0.32, H + 0.075), (0.012, 0.006, 0.01), subdivisions=1), FUR)
    kit.claws(mb, claws, (0.5, 0.45, 0.4))
    return kit.finish(mb, "Castorocauda")


if __name__ == "__main__":
    nh.run(build, "Castorocauda", ground=(0.33, 0.42, 0.24), views=((35, 22), (-90, 6), (25, 65)))
