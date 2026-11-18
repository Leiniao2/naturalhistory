"""
Procedural Allodesmus kernensis (Middle Miocene desmatophocid pinniped of the
North Pacific coast, California) for map colonies (Swim style).

A sea-lion-like seal about 2.2-2.5 m long: a sleek, spindle-shaped body, a long
flexible neck carrying the head raised a little ahead, a short-muzzled head with
very large eyes (it probably dived deep for squid and fish), small ear stubs,
long, broad fore-flippers held out and back like wings for "flying" underwater
and the hind flippers trailing behind in a fan. Dark brown above, paler tan below.
Parts are fused into one seamless surface (nh_model.MeshBuilder.fuse) and
repainted procedurally; eyes, whiskers and flipper claws are crisp shells.
Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/allodesmus_kernensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AllodesmusKernensis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BACK = (0.20, 0.14, 0.09)
FLANK = (0.33, 0.24, 0.16)
BELLY = (0.62, 0.50, 0.36)
FLIP = (0.15, 0.11, 0.08)
NOSE = (0.06, 0.05, 0.04)
WHISKER = (0.85, 0.80, 0.70)


def body_parts(b):
    # spindle body: chest deepest, tapering to the hips
    pts = [(0, -0.42, 0.02), (0, -0.28, 0.0), (0, -0.05, 0.0), (0, 0.22, 0.0), (0, 0.45, 0.01), (0, 0.60, 0.02)]
    rad = [0.12, 0.17, 0.185, 0.15, 0.09, 0.05]
    b.add(nh.tube(pts, rad, sides=18, scale_xy=(1.0, 0.92)), FLANK)
    # long neck, raised a little
    b.add(nh.tube([(0, -0.40, 0.02), (0, -0.55, 0.06), (0, -0.66, 0.09)], [0.12, 0.095, 0.08], sides=16), FLANK)
    # head: rounded cranium, short tapering muzzle
    b.add(nh.ellipsoid((0, -0.72, 0.10), (0.085, 0.10, 0.08)), FLANK)
    b.add(nh.tube([(0, -0.76, 0.095), (0, -0.84, 0.08), (0, -0.88, 0.07)], [0.06, 0.042, 0.03], sides=14), FLANK)
    b.add(nh.ellipsoid((0, -0.80, 0.06), (0.045, 0.06, 0.03)), FLANK)                       # lower jaw
    for sx in (-1, 1):
        b.add(nh.ellipsoid((sx * 0.035, -0.84, 0.07), (0.025, 0.03, 0.025)), FLANK)            # whisker pads
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
    col = nh.lerp(col, BACK, 0.25 * max(0.0, noise.noise(co * 8.0)))
    if co.y < -0.82:
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
        nh.eye(mb, (sx * 0.072, -0.765, 0.125), (sx * 0.85, -0.35, 0.35), 0.024, FLANK,
               iris=(0.05, 0.04, 0.03))
        mb.add(nh.ellipsoid((sx * 0.06, -0.70, 0.165), (0.012, 0.012, 0.02), subdivisions=1), FLANK)  # ear stub
        for k in range(4):
            a = -0.3 + 0.2 * k
            p0 = Vector((sx * 0.05, -0.85, 0.07 - 0.008 * k))
            p1 = p0 + Vector((sx * 0.09 * math.cos(a), 0.02, -0.02 + 0.02 * math.sin(a)))
            mb.add(nh.tube([tuple(p0), tuple(p1)], [0.0025, 0.0], sides=3), WHISKER)
    mb.add(nh.ellipsoid((0, -0.885, 0.078), (0.022, 0.012, 0.014), subdivisions=2), NOSE)
    obj = mb.to_object("AllodesmusKernensis")
    corners = [Vector(c) for c in obj.bound_box]
    c = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "AllodesmusKernensis", background=(0.05, 0.18, 0.24),
           views=((35, 22), (-90, 6), (20, 70)), size=640)
