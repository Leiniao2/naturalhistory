"""
Procedural Essexella asherae (Late Carboniferous of Mazon Creek, Illinois, a scyphozoan
jellyfish about 10-15 cm across and the most common fossil of the Essex fauna) for map
colonies (Drift style).

A domed, translucent-looking bell whose margin carries a long, pleated, curtain-like
"skirt" of tissue hanging down around the body, with four frilly oral arms dangling inside
it and short stinging tentacles along the skirt's lower edge. Milky blue-white bell, the
skirt and oral arms tinted pink-violet. Faces -Y (no real front), pivot at the body centre.

Usage:
  blender --background --python tools/blender/essexella_asherae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Essexella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

NAME = "Essexella"
BELL = (0.72, 0.80, 0.88)
BELL_TOP = (0.86, 0.90, 0.95)
SKIRT = (0.84, 0.74, 0.88)
SKIRT_EDGE = (0.56, 0.34, 0.60)
ARM = (0.86, 0.56, 0.70)
TENT = (0.92, 0.80, 0.88)

R = 0.42


def bell():
    bm = nh.uv_ellipsoid((0, 0, 0), (R, R, R * 0.75), segments=32, rings=14)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.25
    return bm


def skirt(n_a=48, n_z=10, depth=0.48, pleats=16):
    """Pleated open cylinder hanging from the bell margin, flaring slightly, solidified."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    rows = []
    for i in range(n_z + 1):
        t = i / n_z
        row = []
        for j in range(n_a):
            a = j / n_a * math.tau
            r = R * (0.97 + 0.22 * t) * (1.0 + 0.05 * math.sin(a * pleats) * (0.3 + t))
            z = -0.02 - depth * t * (1.0 + 0.06 * math.sin(a * 5 + 1.0))
            row.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        rows.append(row)
    for i in range(n_z):
        for j in range(n_a):
            k = (j + 1) % n_a
            f = bm.faces.new([rows[i][j], rows[i][k], rows[i + 1][k], rows[i + 1][j]])
            for l in f.loops:
                t = -l.vert.co.z / depth
                c = nh.lerp(SKIRT, SKIRT_EDGE, nh.smoothstep(0.6, 1.0, t))
                l[col] = (c[0], c[1], c[2], 1.0)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    mb = nh.MeshBuilder()
    mb.add(bell(), lambda co, n: nh.lerp(BELL, BELL_TOP, nh.smoothstep(0.0, R * 0.6, co.z)))
    mb.add(skirt(), None, smooth=False)
    # four frilly oral arms inside the skirt
    for k in range(4):
        a = k / 4 * math.tau + 0.4
        pts = [Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, -0.05))]
        for i in range(1, 7):
            t = i / 6
            pts.append(Vector((math.cos(a + t * 0.8) * (0.06 + 0.08 * t), math.sin(a + t * 0.8) * (0.06 + 0.08 * t),
                               -0.05 - 0.55 * t)))
        mb.add(nh.tube(pts, [0.045, 0.05, 0.045, 0.04, 0.035, 0.025, 0.0], sides=8,
                       scale_xy=(1.0, 0.45)), ARM)
    # short tentacles along the lower skirt edge
    n = 32
    for j in range(n):
        a = j / n * math.tau
        r = R * 1.19
        p = Vector((math.cos(a) * r, math.sin(a) * r, -0.50))
        q = p + Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, -0.14 - 0.04 * math.sin(j * 2.3)))
        mb.add(nh.tube([p, (p + q) / 2 + Vector((0.01, 0, 0)), q], [0.008, 0.006, 0.0], sides=4), TENT, smooth=False)
    obj = mb.to_object(NAME, roughness=0.3)
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    c = (min(zs) + max(zs)) / 2
    for v in vs:
        v.co.z -= c
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.04, 0.12, 0.18), views=((30, 20), (0, 70), (-90, 5)))
