"""
Procedural Glyptodon clavipes (Pleistocene of South America) for map colonies:
a car-sized armoured relative of armadillos.

A tall, rigid domed carapace about 1.5 m high made of over a thousand fused,
rosette-patterned bony plates (osteoderms), with a flared lower rim; a bony
helmet on top of the short, deep head, short pillar-like legs and a thick
tail armoured with rings of knobbly plates. Shell painted brown with paler
rosette centres. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/glyptodon_clavipes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GlyptodonClavipes.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.42, 0.33, 0.22)
SHELL_PALE = (0.62, 0.52, 0.38)
SKIN = (0.36, 0.31, 0.26)
EYE = (0.06, 0.04, 0.03)
CLAW = (0.18, 0.15, 0.12)

CLUB = False       # Doedicurus-style tail club (unused for Glyptodon)


def shell_deform(v):
    # flatten the lower half into a flaring skirt
    return 1.0 + 0.06 * max(0.0, -v.z) - 0.04 * max(0.0, v.z) ** 3


def build():
    b = nh.MeshBuilder()
    SH, LG = SHELL, SKIN
    zc = 0.42
    b.add(nh.ellipsoid((0, 0, zc), (0.42, 0.62, 0.46), subdivisions=4, deform=shell_deform), SH)
    b.add(nh.ellipsoid((0, 0, 0.30), (0.34, 0.50, 0.14)), LG)                               # belly under the shell
    # head with helmet, low at the front of the shell
    b.add(nh.ellipsoid((0, -0.66, 0.28), (0.12, 0.14, 0.12)), LG)
    b.add(nh.ellipsoid((0, -0.76, 0.22), (0.085, 0.10, 0.10)), LG)
    b.add(nh.ellipsoid((0, -0.66, 0.37), (0.10, 0.12, 0.05)), SH)                            # helmet
    # tail with knobbly rings
    pts = [Vector((0, 0.55, 0.30)), Vector((0, 0.75, 0.25)), Vector((0, 0.92, 0.19)), Vector((0, 1.05, 0.14))]
    b.add(nh.tube([tuple(p) for p in pts], [0.11, 0.085, 0.06, 0.035], sides=12), SH)
    for i in range(5):
        t = i / 5
        p = pts[0].lerp(pts[-1], t + 0.05)
        b.add(nh.tube([tuple(p + Vector((0, -0.015, 0))), tuple(p + Vector((0, 0.015, 0)))],
                      [0.115 - 0.07 * t] * 2, sides=12), SH)
    claws = []
    for (x, y, st) in ((-0.25, -0.33, -0.05), (0.25, -0.33, 0.05), (-0.25, 0.33, 0.04), (0.25, 0.33, -0.05)):
        b.add(nh.tube([(x * 0.9, y, 0.32), (x, y + st, 0.05)], [0.085, 0.075], sides=12), LG)
        b.add(nh.ellipsoid((x, y + st - 0.02, 0.04), (0.085, 0.10, 0.045)), LG)
        for a in (-0.5, 0.0, 0.5):
            claws.append(Vector((x + math.sin(a) * 0.07, y + st - 0.11, 0.025)))
    fused = b.fuse(voxel=0.016, smooth=3, smooth_factor=0.5, max_tris=11000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    shell_v = {}
    for v in fused.verts:
        q = v.co - Vector((0, 0, zc))
        on = (q.x / 0.42) ** 2 + (q.y / 0.62) ** 2 + (q.z / 0.46) ** 2 > 0.8 and v.co.z > 0.16 and abs(v.co.y) < 0.66
        if on:
            dist, _p = noise.voronoi(v.co * 11.0, distance_metric="DISTANCE")
            d = dist[1] - dist[0]
            v.co += v.normal * 0.008 * nh.smoothstep(0.0, 0.25, d)
            shell_v[v] = d
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            v = l.vert
            if v in shell_v:
                d = shell_v[v]
                c = nh.lerp((0.20, 0.15, 0.10), nh.lerp(SHELL, SHELL_PALE, nh.smoothstep(0.25, 0.6, d)),
                            nh.smoothstep(0.02, 0.12, d))
                if v.co.z < 0.24:                       # dark flared rim
                    c = nh.lerp(c, (0.25, 0.19, 0.13), 0.5)
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.085, -0.76, 0.27), (0.016,) * 3, subdivisions=2), EYE)
    for c in claws:
        mb.add(nh.tube([tuple(c + Vector((0, 0.02, 0.01))), tuple(c + Vector((0, -0.04, -0.015)))], [0.014, 0.0],
                       sides=5), CLAW)
    obj = mb.to_object("GlyptodonClavipes")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GlyptodonClavipes", ground=(0.45, 0.42, 0.30), views=((35, 20), (-90, 5), (0, 10)))
