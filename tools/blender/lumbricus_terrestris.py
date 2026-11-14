"""
Common earthworm (Lumbricus terrestris) half out of its burrow.

The worm rises from a small mound of dark soil, arches over, and its front
end lies along the ground in a loose loop, dragging a leaf fragment toward the
burrow; worm castings (coiled soil piles) sit beside the mound. Fine grooves
mark the segments (annuli), the swollen clitellum is a paler band near the
front, and the head ends in a pointed prostomium. Ground style: pivot on the
ground (z = 0), faces -Y.

  blender --background --python tools/blender/lumbricus_terrestris.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

from mathutils import Vector, noise  # noqa: E402
from mathutils.kdtree import KDTree  # noqa: E402

SEED = 5

SOIL = (0.30, 0.20, 0.12)
SOIL_DARK = (0.16, 0.10, 0.06)
CAST = (0.36, 0.25, 0.15)
WORM_TAIL = (0.62, 0.30, 0.30)     # pinkish-red
WORM_MID = (0.55, 0.22, 0.24)
WORM_HEAD = (0.35, 0.12, 0.16)     # darker, purplish-brown front
CLITELLUM = (0.86, 0.52, 0.42)     # paler, orange-pink saddle
LEAF = (0.46, 0.36, 0.10)
LEAF_DARK = (0.30, 0.22, 0.07)
LEAF_VEIN = (0.66, 0.54, 0.26)

WORM_R = 0.04
SEGMENTS = 95           # visible annuli
CLITELLUM_SEGS = (26, 34)  # counted from the head


def catmull_rom(ctrl, per_span=40):
    pts = []
    c = [ctrl[0]] + ctrl + [ctrl[-1]]
    for i in range(1, len(c) - 2):
        p0, p1, p2, p3 = c[i - 1], c[i], c[i + 1], c[i + 2]
        for k in range(per_span):
            t = k / per_span
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(ctrl[-1])
    return pts


def worm_path():
    """Head first: an S-curve lying on the ground in front, then an arch back up into the
    burrow on the front slope of the soil mound (the tail stays buried)."""
    g = WORM_R * 0.92
    ctrl = [
        Vector((0.00, -0.80, g)),    # head
        Vector((-0.10, -0.66, g)),
        Vector((0.10, -0.50, g)),
        Vector((-0.08, -0.32, g)),
        Vector((0.06, -0.14, g)),    # last ground contact
        Vector((0.04, 0.02, 0.20)),  # top of the arch
        Vector((0.00, 0.16, 0.16)),
        Vector((0.00, 0.24, 0.07)),  # burrow mouth
        Vector((0.00, 0.30, -0.06)), # buried tail
    ]
    return catmull_rom(ctrl)


def resample(pts, count):
    """Evenly spaced points along the polyline."""
    lens = [0.0]
    for a, b in zip(pts, pts[1:]):
        lens.append(lens[-1] + (b - a).length)
    total = lens[-1]
    out, j = [], 0
    for k in range(count + 1):
        d = total * k / count
        while j < len(lens) - 2 and lens[j + 1] < d:
            j += 1
        seg = lens[j + 1] - lens[j] or 1.0
        out.append(pts[j].lerp(pts[j + 1], (d - lens[j]) / seg))
    return out, total


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # soil mound around the burrow
    soil = nh.MeshBuilder()
    soil.add(nh.uv_ellipsoid((0.0, 0.36, 0.0), (0.26, 0.24, 0.11), 16, 8), SOIL)
    for _ in range(14):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0.05, 0.27)
        soil.add(nh.uv_ellipsoid((math.cos(a) * d, 0.36 + math.sin(a) * d, 0.03),
                                 (rng.uniform(0.04, 0.07),) * 2 + (rng.uniform(0.04, 0.07),), 6, 5), SOIL)
    mound = soil.fuse(voxel=0.032, smooth=2, max_tris=None)
    off = Vector((2.1, 7.3, 0.4))
    mound.normal_update()
    for v in mound.verts:
        v.co += v.normal * (noise.noise(v.co * 14 + off) * 0.014 + noise.noise(v.co * 45) * 0.006)

    def soil_color(co, n):
        c = nh.lerp(SOIL, SOIL_DARK, 0.5 + 0.5 * noise.noise(co * 12 + off))
        crumb = 0.5 + 0.5 * noise.noise(co * 60)
        return tuple(x * (0.8 + 0.4 * crumb) for x in c)
    mb.add(mound, soil_color, smooth=False)

    # castings: little coiled soil piles
    for cx, cy, s in ((0.34, 0.30, 1.0), (0.30, 0.02, 0.8), (-0.32, 0.18, 0.9)):
        coil = []
        for i in range(32):
            t = i / 31
            a = t * math.tau * 2.5
            rr = 0.05 * s * (1 - t * 0.7)
            coil.append(Vector((cx + math.cos(a) * rr, cy + math.sin(a) * rr, 0.012 * s + t * 0.06 * s)))
        radii = [0.018 * s * (1 - 0.4 * i / 31) for i in range(32)]
        radii[-1] = 0.0
        mb.add(nh.tube(coil, radii, sides=5), lambda co, n: nh.lerp(CAST, SOIL, 0.5 + 0.5 * noise.noise(co * 30)))

    # the worm: dense rings so each annulus gets a groove
    raw = worm_path()
    rings = SEGMENTS * 2
    pts, length = resample(raw, rings)
    radii = []
    for k, p in enumerate(pts):
        t = k / rings                # 0 = head tip, 1 = buried tail
        seg = k / 2.0
        groove = 0.93 if k % 2 == 0 else 1.0
        r = WORM_R
        # pointed prostomium / tapering head, slight thickening behind it
        r *= nh.smoothstep(0.0, 0.035, t) * 0.75 + 0.25 if t < 0.035 else 1.0
        r *= 1.0 + 0.08 * math.exp(-((t - 0.12) / 0.06) ** 2)
        if CLITELLUM_SEGS[0] <= seg <= CLITELLUM_SEGS[1]:
            r *= 1.16
            groove = 0.98 if groove < 1 else 1.0
        radii.append(r * groove)
    radii[0] = 0.0
    tube = nh.tube(pts, radii, sides=8, cap_start=False, cap_end=True)

    kd = KDTree(len(pts))
    for k, p in enumerate(pts):
        kd.insert(p, k)
    kd.balance()

    def worm_color(co, n):
        _p, k, _d = kd.find(co)
        t = k / rings
        seg = k / 2.0
        if CLITELLUM_SEGS[0] <= seg <= CLITELLUM_SEGS[1]:
            c = CLITELLUM
        elif t < 0.2:
            c = nh.lerp(WORM_HEAD, WORM_MID, t / 0.2)
        else:
            c = nh.lerp(WORM_MID, WORM_TAIL, min(1.0, (t - 0.2) / 0.5))
        if k % 2 == 0:                           # darker groove line between annuli
            c = tuple(x * 0.85 for x in c)
        # paler underside, darker back
        c = nh.lerp(c, tuple(min(1.0, x * 1.25) for x in c), max(0.0, -n.z) * 0.6)
        return c

    mb.add(tube, worm_color)

    # leaf fragment being dragged by the head: a pointed lens with a midrib, stem end in its mouth
    head = pts[0]
    ahead = (pts[0] - pts[10]).normalized()
    ahead.z = 0
    ahead.normalize()
    side = Vector((-ahead.y, ahead.x, 0))
    L, W = 0.34, 0.10
    base = head - ahead * 0.035  # stem end tucked under the head
    outline = []
    n = 18
    for i in range(n):
        u = i / (n - 1)                     # one side, base -> tip
        # pointed at both ends, widest a little past the middle, slightly ragged edge
        outline.append((u, math.sin(math.pi * u ** 0.85) ** 1.1 * W * (1 + 0.12 * math.sin(u * 23))))
    pts_leaf = [(u, w) for u, w in outline] + [(u, -w) for u, w in reversed(outline[1:-1])]
    world = []
    for u, w in pts_leaf:
        p = base + ahead * (u * L) + side * w
        world.append((p.x, p.y, 0.008 + 0.02 * math.sin(math.pi * u) * (1 - u) + 0.02 * (1 - u) ** 3))
    leaf = nh.flat_panel(world, thickness=0.005)

    mb.add(leaf, lambda co, n_: nh.lerp(LEAF, LEAF_DARK, 0.5 + 0.5 * noise.noise(co * 25)), smooth=False)

    def leaf_z(u):
        return 0.008 + 0.02 * math.sin(math.pi * u) * (1 - u) + 0.02 * (1 - u) ** 3

    # midrib and a few side veins as thin raised strips (the slab has no inner vertices to paint)
    rib = [base + ahead * (u * L) + Vector((0, 0, leaf_z(u) + 0.004 - (base.z))) for u in (0.0, 0.3, 0.6, 0.97)]
    mb.add(nh.tube(rib, [0.006, 0.005, 0.003, 0.0], sides=3), LEAF_VEIN)
    for u0 in (0.25, 0.45, 0.65):
        for sd in (-1, 1):
            a = base + ahead * (u0 * L)
            b = a + ahead * (0.07) + side * sd * W * 0.75 * math.sin(math.pi * (u0 + 0.1))
            a.z = leaf_z(u0) + 0.004
            b.z = leaf_z(u0 + 0.2) + 0.004
            mb.add(nh.tube([a, b], [0.0025, 0.0], sides=3), LEAF_VEIN)

    obj = mb.to_object("Earthworm", roughness=0.35)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Earthworm", ground=(0.30, 0.42, 0.22), views=((35, 30), (-90, 10), (10, 70)))
