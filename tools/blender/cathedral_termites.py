"""
Cathedral termites (Nasutitermes triodiae), shown on the map by their mound.

A tall red-orange laterite mound: a main spire plus several fused buttress
spires and pinnacles of different heights, fluted with vertical ridges and
gullies and weathered into lumps, darker and moister at the foot, with
spinifex tufts around the base and a few pale nasute soldiers on the lower
walls. Ground style: pivot on the ground (z = 0), faces -Y.

  blender --background --python tools/blender/cathedral_termites.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

SEED = 11

LATERITE = (0.62, 0.24, 0.09)    # rusty red-orange
OCHRE = (0.78, 0.45, 0.16)
DARK_RED = (0.36, 0.11, 0.05)
MOIST = (0.24, 0.10, 0.06)
SPINIFEX = (0.62, 0.62, 0.30)
SPINIFEX_TIP = (0.85, 0.78, 0.45)
TERMITE_BODY = (0.92, 0.86, 0.70)
TERMITE_HEAD = (0.30, 0.16, 0.07)

# (x, y, height, base radius) - main spire first
SPIRES = [
    (0.00, 0.02, 2.30, 0.30),
    (0.27, -0.12, 1.70, 0.21),
    (-0.28, 0.06, 1.95, 0.22),
    (0.10, 0.30, 1.35, 0.19),
    (-0.12, -0.30, 1.15, 0.18),
    (0.36, 0.20, 0.85, 0.15),
    (-0.38, -0.16, 0.70, 0.14),
    (0.05, -0.18, 1.55, 0.17),
]


def spire(x, y, h, r, rng):
    """Tapered, slightly leaning column with a rounded top."""
    lean = Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), 0))
    pts, radii = [], []
    n = 9
    for i in range(n + 1):
        t = i / n
        p = Vector((x, y, -0.05 + t * h)) + lean * t * t * h
        pts.append(p)
        # buttress-like flare at the base, a soft waist, pointed but rounded top
        # buttress flare at the foot, then a fairly straight column that narrows to a blunt point
        rr = r * (1.0 - 0.72 * t ** 1.6) * (1.0 + 0.6 * max(0.0, 0.22 - t) / 0.22)
        radii.append(max(rr, r * 0.16))
    pts.append(pts[-1] + Vector((0, 0, r * 0.12)))
    radii.append(0.0)
    return nh.tube(pts, radii, sides=12, cap_start=True, cap_end=False)


def build():
    rng = random.Random(SEED)
    body = nh.MeshBuilder()
    # broad, lumpy footing that ties the spires together
    body.add(nh.uv_ellipsoid((0, 0, 0.0), (0.58, 0.52, 0.14), 20, 10), LATERITE)
    body.add(nh.uv_ellipsoid((0.0, 0.0, 0.35), (0.30, 0.28, 0.40), 16, 10), LATERITE)
    for x, y, h, r in SPIRES:
        body.add(spire(x, y, h, r, rng), LATERITE)
    # a couple of lumpy knobs / side pinnacles part-way up
    for _ in range(7):
        a = rng.uniform(0, math.tau)
        z = rng.uniform(0.4, 1.2)
        d = 0.24 * (1.5 - z / 1.2)
        body.add(nh.uv_ellipsoid((math.cos(a) * d, math.sin(a) * d, z),
                                 (0.08, 0.08, rng.uniform(0.14, 0.24)), 10, 8), LATERITE)

    fused = body.fuse(voxel=0.046, smooth=4, smooth_factor=0.5, max_tris=None)

    # weathering: vertical flutes (ridges and gullies) + lumps, before colouring
    fused.normal_update()
    off = Vector((3.7, 1.3, 8.1))
    disp = {}
    for v in fused.verts:
        p = v.co
        ang = math.atan2(p.y, p.x)
        h = max(p.z, 0.0)
        warp = noise.noise(Vector((p.x * 2, p.y * 2, p.z * 0.8)) + off) * 1.6
        # vertical flutes: noise stretched along z gives ridges and gullies running down the walls
        flute = noise.noise(Vector((p.x * 9, p.y * 9, p.z * 1.2)) + off + Vector((warp, 0, 0)))
        flute += 0.5 * math.cos(ang * 9 + warp * 2.0)
        lumps = noise.noise(p * 6.0 + off) * 0.5 + noise.noise(p * 15.0 - off) * 0.25
        amp_f = 0.05 * nh.smoothstep(0.08, 0.45, h)           # flutes fade out at the foot
        d = flute * amp_f + lumps * 0.035
        disp[v] = (d, flute)
    for v, (d, _f) in disp.items():
        v.co += v.normal * d
    fused.normal_update()

    def mound_color(co, n):
        h = co.z
        v = noise.noise(co * 3.0 + off) * 0.5 + 0.5
        fine = noise.noise(co * 18.0) * 0.5 + 0.5
        c = nh.lerp(LATERITE, OCHRE, nh.smoothstep(0.35, 0.8, v) * 0.7)
        c = nh.lerp(c, DARK_RED, nh.smoothstep(0.55, 0.9, 1 - v) * 0.55)
        # sun-bleached, dustier upper faces; darker gullies (normals facing down / inward)
        c = nh.lerp(c, OCHRE, max(0.0, n.z) * 0.25)
        c = tuple(x * (0.86 + 0.24 * fine) for x in c)
        # moist, darker base
        wet = 1.0 - nh.smoothstep(0.02, 0.32, h + (noise.noise(co * 5) * 0.08))
        c = nh.lerp(c, MOIST, wet * 0.8)
        return c

    mb = nh.MeshBuilder()
    # keep a copy for ray-casting termites onto the surface
    tree = BVHTree.FromBMesh(fused)
    mb.add(fused, color=mound_color)

    # spinifex tufts around the foot
    for k in range(11):
        a = k / 11 * math.tau + rng.uniform(-0.25, 0.25)
        d = rng.uniform(0.58, 0.95)
        base = Vector((math.cos(a) * d, math.sin(a) * d, -0.02))
        for _ in range(16):
            ba = rng.uniform(0, math.tau)
            tilt = rng.uniform(0.2, 1.0)
            ln = rng.uniform(0.25, 0.45)
            dirv = Vector((math.cos(ba) * math.sin(tilt), math.sin(ba) * math.sin(tilt), math.cos(tilt)))
            tip = base + dirv * ln + Vector((0, 0, -0.03 * tilt))
            mid = base + dirv * ln * 0.5
            blade = nh.tube([base, mid, tip], [0.01, 0.006, 0.0], sides=3, cap_start=False)
            mb.add(blade, lambda co, n, b=base: nh.lerp(SPINIFEX, SPINIFEX_TIP,
                                                         min(1.0, (co - b).length / 0.4)))

    # a few nasute soldiers clinging to the lower walls
    for k in range(5):
        a = rng.uniform(-math.pi * 0.9, -math.pi * 0.1) if k < 3 else rng.uniform(0, math.tau)
        z = rng.uniform(0.25, 0.6)
        origin = Vector((math.cos(a) * 2.0, math.sin(a) * 2.0, z))
        hit, normal, _i, _d = tree.ray_cast(origin, (Vector((0, 0, z)) - origin).normalized())
        if hit is None:
            continue
        add_termite(mb, hit, normal, rng)

    obj = mb.to_object("CathedralTermiteMound", roughness=0.85)
    nh.ground_to_zero(obj)
    return obj


def add_termite(mb, pos, normal, rng):
    """Tiny pale soldier: abdomen, thorax, dark head with a pointed nasus, six legs."""
    n = normal.normalized()
    up = Vector((0, 0, 1))
    fwd = (up - n * up.dot(n)).normalized()
    fwd.rotate(__import__("mathutils").Quaternion(n, rng.uniform(-0.8, 0.8)))
    side = fwd.cross(n).normalized()
    s = 0.022
    lift = n * s * 0.55

    def at(f, sd=0.0, h=0.0):
        return pos + lift + fwd * f * s + side * sd * s + n * h * s

    mb.add(nh.uv_ellipsoid(at(-1.1), (s * 0.55,) * 3, 8, 6), TERMITE_BODY)
    mb.add(nh.uv_ellipsoid(at(0.0), (s * 0.38,) * 3, 8, 6), TERMITE_BODY)
    mb.add(nh.uv_ellipsoid(at(0.8), (s * 0.45,) * 3, 8, 6), TERMITE_HEAD)
    mb.add(nh.tube([at(1.1), at(1.9, 0, 0.15)], [s * 0.22, 0.0], sides=5), TERMITE_HEAD)
    for f in (-0.35, 0.0, 0.35):
        for sd in (-1, 1):
            mb.add(nh.tube([at(f * 0.6, sd * 0.3), at(f, sd * 1.1, 0.2), at(f * 1.3, sd * 1.5, -0.5)],
                           [s * 0.07, s * 0.06, s * 0.04], sides=3), TERMITE_BODY)


if __name__ == "__main__":
    nh.run(build, "CathedralTermiteMound", ground=(0.55, 0.40, 0.25),
           views=((35, 25), (-90, 8), (20, 65)))
