"""
Procedural fire sponge (Tedania ignis) for the map: a bright red-orange encrusting mass of
soft lobes, topped by volcano-like oscular chimneys with dark open vents, spreading over a
little rubble patch. Ground style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/tedania_ignis.py -- [--render out.png]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402

SEED = 7
RADIUS = 0.55  # footprint of the encrusting mass

ORANGE = (1.00, 0.30, 0.03)
RED = (0.80, 0.08, 0.03)        # deeper red in the creases
TIP = (1.00, 0.58, 0.16)        # sunlit yellow-orange on lobe tops and chimney rims
VENT = (0.22, 0.05, 0.03)       # inside the oscula
BASE = (0.55, 0.16, 0.06)

WARP = Vector((2.3, 7.1, 4.4))
MAX_TRIS = 4400


def chimney(points, radii, wall, depth, sides=14):
    """Closed, hollow, open-topped tube (an annular solid) so the voxel remesh keeps the vent:
    outer wall up `points`, a lip at the top, then the inner wall back down `depth` and a floor."""
    pts = [Vector(p) for p in points]
    bm = bmesh.new()
    frames = []
    prev = None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = fwd.cross(Vector((1, 0, 0))).normalized() if prev is None else (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        frames.append((p, side, side.cross(fwd).normalized(), fwd))

    def ring(p, side, up, r):
        return [bm.verts.new(p + side * math.cos(k / sides * math.tau) * r + up * math.sin(k / sides * math.tau) * r)
                for k in range(sides)]

    outer = [ring(p, s, u, r) for (p, s, u, _f), r in zip(frames, radii)]
    top, s_, u_, f_ = frames[-1]
    inner = [ring(top - f_ * depth * t, s_, u_, radii[-1] - wall) for t in (0.0, 0.5, 1.0)]
    rings = outer + inner
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(outer[0])))
    bm.faces.new(inner[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # encrusting base: a low, lumpy mat of overlapping flattened blobs
    for _ in range(22):
        a = rng.uniform(0, math.tau)
        r = RADIUS * math.sqrt(rng.random()) * 0.82
        s = rng.uniform(0.12, 0.22)
        mb.add(nh.ellipsoid((math.cos(a) * r, math.sin(a) * r, 0.0),
                            (s, s * rng.uniform(0.7, 1.3), s * rng.uniform(0.35, 0.55)),
                            subdivisions=3), ORANGE)
    # low ridges and knobs rising out of the mat
    for _ in range(6):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.1, RADIUS * 0.65)
        s = rng.uniform(0.08, 0.12)
        mb.add(nh.ellipsoid((math.cos(a) * r, math.sin(a) * r, s * 0.8),
                            (s, s * 1.4, s), subdivisions=3), ORANGE)

    # oscular chimneys of varied height spread over the mass, leaning outward
    chimneys = []
    n = 7
    for i in range(n):
        a = i / (n - 1) * math.tau + rng.uniform(-0.3, 0.3)
        r = rng.uniform(0.22, 0.4) if i else 0.0
        h = rng.uniform(0.2, 0.42) if i else 0.55
        ro = rng.uniform(0.07, 0.09) if i else 0.1
        base = Vector((math.cos(a) * r, math.sin(a) * r, 0.04))
        lean = Vector((math.cos(a), math.sin(a), 0)) * h * rng.uniform(0.15, 0.35)
        top = base + lean + Vector((0, 0, h))
        mid = base.lerp(top, 0.5) - lean * 0.1
        mb.add(chimney([base, mid, top], [ro * 1.9, ro * 1.0, ro * 1.1], wall=0.035, depth=min(h, 0.3)), ORANGE)
        chimneys.append((top, (top - mid).normalized(), ro * 1.1 - 0.035))

    bm = mb.fuse(voxel=0.016, smooth=6, smooth_factor=0.5)

    # sponge surface: soft conules and a fine pore texture
    for v in bm.verts:
        bump = 0.012 * noise.noise(v.co * 20 + WARP) + 0.007 * max(0.0, noise.noise(v.co * 60))
        v.co += v.normal * bump
    bm = nc.decimate(bm, MAX_TRIS)

    def vent(co):
        k = 0.0
        for top, axis, ri in chimneys:
            rel = co - top
            along = rel.dot(axis)
            d = (rel - axis * along).length
            if along < 0.005:
                k = max(k, nh.smoothstep(ri + 0.02, ri - 0.01, d) * nh.smoothstep(0.0, -0.06, along))
        return k

    def color(co, n):
        crease = nh.smoothstep(0.25, -0.35, noise.noise(co * 9 + WARP))
        c = nh.lerp(ORANGE, RED, 0.6 * crease)
        c = nh.lerp(c, TIP, 0.55 * nh.smoothstep(0.3, 0.95, n.z) * nh.smoothstep(0.08, 0.35, co.z))
        c = nh.lerp(BASE, c, nh.smoothstep(0.0, 0.08, co.z))
        k = 0.92 + 0.12 * noise.noise(co * 45)
        c = tuple(min(1.0, x * k) for x in c)
        return nh.lerp(c, VENT, vent(co))

    out = nh.MeshBuilder()
    out.add(bm, color)
    nc.rubble(out, rng, RADIUS * 0.8, RADIUS * 1.15, count=10, size=(0.05, 0.1))
    obj = out.to_object("FireSponge", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "FireSponge", ground=(0.75, 0.70, 0.55), views=((35, 30), (10, 70), (-90, 10)))
