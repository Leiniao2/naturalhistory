"""
Procedural low-poly Naegleria gruberi (amoeboflagellate) in its amoeba (limax) form.

A slug-like, elongated, flattened cell crawling forward along -Y, led by one broad, rounded,
clear eruptive pseudopod (lobopod) bulging out at the front. The front cap is clear, glassy
hyaline ectoplasm; behind it the granular endoplasm is speckled grey-tan. Showing through the
upper surface: a pale vesicular nucleus with its large dark central nucleolus, a clear
contractile vacuole and a few food vacuoles toward the rear, and at the very back a small knobbly
trailing uroid with a few short sticky filaments. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/naegleria_gruberi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Naegleria.fbx
Faces -Y (front), long axis along Y, ~1.6 units long. Pivot at the body centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 3
MAX_TRIS = 2000

HYALINE = (0.80, 0.90, 0.94)      # clear glassy front
HYALINE_RIM = (0.92, 0.97, 0.99)
ENDO = (0.66, 0.62, 0.52)         # granular endoplasm
GRANULE = (0.42, 0.38, 0.30)
GRANULE_PALE = (0.84, 0.80, 0.68)
NUCLEUS = (0.80, 0.82, 0.78)      # pale vesicular nucleus
NUCLEOLUS = (0.26, 0.24, 0.30)
CONTRACTILE = (0.70, 0.88, 0.97)
FOOD = [(0.55, 0.50, 0.30), (0.46, 0.52, 0.30), (0.60, 0.46, 0.32)]
UROID = (0.56, 0.52, 0.44)

# body stations along Y: (y, half-width, half-height, z-centre)
BODY = [(-0.40, 0.20, 0.15, 0.00), (-0.20, 0.215, 0.16, 0.00), (0.02, 0.21, 0.155, 0.0),
        (0.22, 0.19, 0.145, -0.005), (0.40, 0.16, 0.125, -0.01), (0.55, 0.12, 0.10, -0.015)]


def build_body():
    mb = nh.MeshBuilder()
    for y, w, h, z in BODY:
        mb.add(nh.ellipsoid((0, y, z), (w, 0.30 if y < 0.5 else 0.17, h), subdivisions=3), ENDO)
    # the broad, rounded eruptive lobopod at the front, a little wider than the body
    mb.add(nh.ellipsoid((0.02, -0.56, -0.01), (0.27, 0.22, 0.15), subdivisions=3), HYALINE)
    mb.add(nh.ellipsoid((0.10, -0.66, -0.02), (0.16, 0.12, 0.11), subdivisions=2), HYALINE)
    # small knobbly uroid at the rear
    mb.add(nh.ellipsoid((0, 0.68, -0.02), (0.075, 0.08, 0.065), subdivisions=2), UROID)
    for x, y, z, r in ((0.065, 0.78, 0.0, 0.045), (-0.065, 0.79, -0.02, 0.043), (0.0, 0.82, -0.06, 0.04),
                       (0.02, 0.82, 0.045, 0.04)):
        mb.add(nh.ellipsoid((x, y, z), (r, r, r), subdivisions=1), UROID)
    return mb.fuse(voxel=0.034, smooth=12, smooth_factor=0.6, max_tris=MAX_TRIS)


def body_colour(co, n):
    front = 1.0 - nh.smoothstep(-0.50, -0.34, co.y)   # 1 on the clear front cap
    g = noise.noise(co * 26.0)
    g2 = noise.noise(co * 55.0 + Vector((3, 1, 7)))
    c = nh.lerp(ENDO, GRANULE, nh.smoothstep(0.0, 0.3, g))
    c = nh.lerp(c, GRANULE_PALE, nh.smoothstep(0.15, 0.4, g2) * 0.8)
    c = nh.lerp(c, UROID, nh.smoothstep(0.58, 0.68, co.y) * 0.6)
    glass = nh.lerp(HYALINE, HYALINE_RIM, nh.smoothstep(0.3, 1.0, 1.0 - abs(n.z)))
    return nh.lerp(c, glass, front)


def build():
    rng = random.Random(SEED)
    body = build_body()
    tree = BVHTree.FromBMesh(body)

    def top(x, y):
        hit = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        return hit[0].z if hit[0] is not None else 0.0

    def blister(x, y, radii, rgb, sink=0.6, sub=2):
        z = top(x, y) - radii[2] * sink
        mb.add(nh.ellipsoid((x, y, z), radii, subdivisions=sub), rgb)

    mb = nh.MeshBuilder()
    mb.add(body, body_colour)
    # vesicular nucleus with a large, dense central nucleolus
    nz = top(0.0, -0.18) + 0.006                       # top of the nucleus bulge
    mb.add(nh.ellipsoid((0.0, -0.18, nz - 0.045), (0.10, 0.10, 0.045), subdivisions=3), NUCLEUS)
    mb.add(nh.ellipsoid((0.0, -0.18, nz - 0.022), (0.05, 0.05, 0.03), subdivisions=2), NUCLEOLUS)
    # contractile vacuole toward the rear, food vacuoles in the granular endoplasm
    blister(-0.06, 0.40, (0.075, 0.075, 0.045), CONTRACTILE, sink=0.5)
    for x, y in ((-0.10, 0.05), (0.11, 0.17), (-0.04, 0.24)):
        r = rng.uniform(0.04, 0.055)
        blister(x, y, (r, r, r * 0.7), rng.choice(FOOD), sink=0.6)
    # a few short, sticky trailing filaments on the uroid
    for k in range(4):
        a = k / 4 * math.tau + rng.uniform(-0.3, 0.3)
        base = Vector((math.cos(a) * 0.05, 0.84, -0.02 + math.sin(a) * 0.035))
        d = Vector((math.cos(a) * 0.5, 1.0, math.sin(a) * 0.4)).normalized()
        side = d.cross(Vector((0, 0, 1))).normalized()
        ln = rng.uniform(0.07, 0.11)
        pts = [base + d * ln * t + side * 0.012 * math.sin(t * 7.0 + k) for t in (0, 0.33, 0.66, 1.0)]
        mb.add(nh.tube(pts, [0.008, 0.006, 0.005, 0.0], sides=4), UROID)

    obj = mb.to_object("Naegleria", roughness=0.35)
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    for v in obj.data.vertices:
        for a in range(3):
            v.co[a] -= (lo[a] + hi[a]) / 2
    return obj


if __name__ == "__main__":
    nh.run(build, "Naegleria", views=((35, 30), (-90, 10), (0, 85)))
