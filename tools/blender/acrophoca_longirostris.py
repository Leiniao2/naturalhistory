"""
Procedural Acrophoca longirostris (Late Miocene of Peru) for map colonies:
the "swan-necked seal", a slender early relative of the monk seals.

A seal about 1.5-2 m long with an unusually long neck and a long, narrow,
pointed snout for snapping fish, a slim body, long fore-flippers and trailing
hind flippers. Shown with a mottled grey coat, darker above. Adapted from
allodesmus_kernensis.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/acrophoca_longirostris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AcrophocaLongirostris.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BACK = (0.22, 0.23, 0.25)
FLANK = (0.42, 0.43, 0.45)
BELLY = (0.72, 0.71, 0.68)
FLIP = (0.15, 0.15, 0.16)
NOSE = (0.06, 0.05, 0.04)
WHISKER = (0.85, 0.80, 0.70)


def body_parts(b):
    # spindle body: chest deepest, tapering to the hips
    pts = [(0, -0.42, 0.02), (0, -0.28, 0.0), (0, -0.05, 0.0), (0, 0.22, 0.0), (0, 0.45, 0.01), (0, 0.60, 0.02)]
    rad = [0.11, 0.15, 0.16, 0.13, 0.08, 0.045]
    b.add(nh.tube(pts, rad, sides=18, scale_xy=(1.0, 0.92)), FLANK)
    # long neck, raised a little
    b.add(nh.tube([(0, -0.40, 0.02), (0, -0.58, 0.07), (0, -0.74, 0.11), (0, -0.84, 0.12)], [0.11, 0.08, 0.065, 0.06], sides=16), FLANK)
    # head: rounded cranium, short tapering muzzle
    b.add(nh.ellipsoid((0, -0.90, 0.12), (0.065, 0.09, 0.062)), FLANK)
    b.add(nh.tube([(0, -0.94, 0.115), (0, -1.04, 0.10), (0, -1.12, 0.09)], [0.045, 0.03, 0.02], sides=14), FLANK)
    b.add(nh.ellipsoid((0, -1.00, 0.085), (0.03, 0.09, 0.022)), FLANK)                       # lower jaw
    for sx in (-1, 1):
        b.add(nh.ellipsoid((sx * 0.022, -1.05, 0.095), (0.016, 0.03, 0.016)), FLANK)            # whisker pads
        # fore-flipper: broad, long, swept back and down
        sh = Vector((sx * 0.13, -0.26, -0.07))
        el = Vector((sx * 0.24, -0.18, -0.13))
        tip = Vector((sx * 0.48, 0.06, -0.20))
        b.add(nh.tube([tuple(sh), tuple(el), tuple(el.lerp(tip, 0.5)), tuple(tip)], [0.06, 0.065, 0.07, 0.015],
                      sides=12, scale_xy=(1.0, 0.22)), FLIP)
        # hind flippers trailing backwards, toes spread in a fan
        hip = Vector((sx * 0.04, 0.55, 0.0))
        ft = Vector((sx * 0.11, 0.80, 0.01))
        b.add(nh.tube([tuple(hip), tuple(hip.lerp(ft, 0.4)), tuple(hip.lerp(ft, 0.8)), tuple(ft)],
                      [0.045, 0.045, 0.06, 0.05], sides=10, scale_xy=(1.0, 0.25)), FLIP)

def _rot_z(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, "Z")


def paint(co, n, c):
    if c[0] < 0.17 and c[1] < 0.12:       # flippers stay dark
        return FLIP
    k = nh.smoothstep(-0.55, 0.1, n.z)
    col = nh.lerp(BELLY, FLANK, k)
    col = nh.lerp(col, BACK, nh.smoothstep(0.3, 0.9, n.z))
    col = nh.lerp(col, BACK, 0.7 * nh.smoothstep(0.25, 0.45, noise.noise(co * 14.0)))
    if co.y < -1.02:
        col = nh.lerp(col, BACK, 0.4)
    return col


def build():
    b = nh.MeshBuilder()
    body_parts(b)
    fused = b.fuse(voxel=0.010, smooth=8, smooth_factor=0.5, max_tris=9000)
    col = fused.loops.layers.color.get("Col")
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            nc = paint(l.vert.co, l.vert.normal, (c[0], c[1], c[2]))
            l[col] = (nc[0], nc[1], nc[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        # very large eyes
        nh.eye(mb, (sx * 0.052, -0.93, 0.14), (sx * 0.85, -0.35, 0.35), 0.019, FLANK,
               iris=(0.05, 0.04, 0.03))
        mb.add(nh.ellipsoid((sx * 0.045, -0.86, 0.165), (0.01, 0.01, 0.016), subdivisions=1), FLANK)  # ear stub
        for k in range(4):
            a = -0.3 + 0.2 * k
            p0 = Vector((sx * 0.03, -1.06, 0.095 - 0.006 * k))
            p1 = p0 + Vector((sx * 0.07 * math.cos(a), 0.02, -0.02 + 0.02 * math.sin(a)))
            mb.add(nh.tube([tuple(p0), tuple(p1)], [0.0025, 0.0], sides=3), WHISKER)
    mb.add(nh.ellipsoid((0, -1.125, 0.095), (0.015, 0.01, 0.01), subdivisions=2), NOSE)
    obj = mb.to_object("AcrophocaLongirostris")
    corners = [Vector(c) for c in obj.bound_box]
    c = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "AcrophocaLongirostris", background=(0.05, 0.18, 0.24),
           views=((35, 22), (-90, 6), (20, 70)), size=640)
