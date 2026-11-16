"""
Procedural Eocyathispongia qiania (tiny Ediacaran sponge-grade fossil, Doushantuo Formation,
Guizhou) for the map: three adjacent hollow tubes rising from one shared, lumpy base on a little
patch of phosphatic grit.

The real animal is only about 1.2 mm wide and 1.1 mm tall, with roughly those proportions here.
The largest tube stands in the middle and opens into a wide outflow funnel; the two smaller
tubes lean outward from either side of it, each ending in a smaller osculum-like opening. Each
tube is a closed, hollow, open-topped annular solid whose inner wall follows the outer profile
(so the flared funnel stays hollow), letting the voxel fuse keep the openings while merging the tubes and the base into one seamless body. The surface is
dimpled with a Voronoi pattern of small pores (shallow dents with darker centres) over a
faint polygonal cell texture. Pale cream-tan, darker inside the openings.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/eocyathispongia_qiania.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eocyathispongia.fbx
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

SEED = 4
PORE_FREQ = 12.0      # Voronoi cells per unit (pore spacing)
MAX_TRIS = 4800
# (base xy, lean direction xy, lean, height, radii from base to rim, wall, rings left solid at the base)
TUBES = [
    ((0.0, 0.04), (0.0, 1.0), 0.04, 1.00, (0.22, 0.21, 0.18, 0.16, 0.2, 0.27, 0.31), 0.04, 1),  # funnel
    ((-0.23, -0.03), (-1.0, -0.2), 0.16, 0.62, (0.19, 0.18, 0.16, 0.145, 0.14, 0.145, 0.15), 0.035, 2),
    ((0.22, -0.07), (1.0, -0.4), 0.14, 0.50, (0.18, 0.17, 0.15, 0.135, 0.13, 0.135, 0.14), 0.035, 2),
]
PROFILE = (0.0, 0.18, 0.38, 0.58, 0.76, 0.9, 1.0)   # ring heights along each tube

CREAM = (0.88, 0.80, 0.64)    # pale cream-tan body
TAN = (0.74, 0.64, 0.48)      # shaded creases and lower body
PORE = (0.46, 0.37, 0.27)     # pore centres
VENT = (0.22, 0.16, 0.11)     # inside the openings
RIM = (0.95, 0.89, 0.75)      # pale rims of the openings

WARP = Vector((4.1, 1.7, 8.3))


def hollow_tube(points, radii, wall, solid, sides=18):
    """Closed, hollow, open-topped tube (an annular solid) so the voxel remesh keeps the opening:
    outer wall up `points`, a lip at the top, then an inner wall that follows the outer profile
    (offset inward by `wall`) back down to ring `solid`, closed by a floor."""
    pts = [Vector(p) for p in points]
    bm = bmesh.new()
    frames = []
    prev = None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = fwd.cross(Vector((1, 0, 0))).normalized() if prev is None else (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        frames.append((p, side, side.cross(fwd).normalized()))

    def ring(i, r):
        p, side, up = frames[i]
        return [bm.verts.new(p + side * math.cos(k / sides * math.tau) * r + up * math.sin(k / sides * math.tau) * r)
                for k in range(sides)]

    rings = [ring(i, r) for i, r in enumerate(radii)]
    rings += [ring(i, max(0.02, radii[i] - wall)) for i in range(len(pts) - 1, solid - 1, -1)]
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    vents = []
    for (bx, by), (lx, ly), lean, h, radii, wall, solid in TUBES:
        d = Vector((lx, ly, 0.0)).normalized()
        # each tube rises from the shared base and bends outward, more toward its top
        pts = [Vector((bx, by, 0.02)) + d * h * lean * t ** 1.5 + Vector((0, 0, h * t)) for t in PROFILE]
        mb.add(hollow_tube(pts, radii, wall, solid), CREAM)
        vents.append((pts[-1], (pts[-1] - pts[-2]).normalized(), radii[-1] - wall, pts, radii, wall, solid))
    # shared base: a low, lumpy foot joining the three tubes
    for _ in range(7):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.0, 0.2)
        s = rng.uniform(0.14, 0.2)
        mb.add(nh.ellipsoid((math.cos(a) * r, math.sin(a) * r - 0.02, 0.05), (s, s * 0.9, s * 0.6),
                            subdivisions=3), TAN)

    bm = mb.fuse(voxel=0.019, smooth=6, smooth_factor=0.5)

    def pore(co):
        d = noise.voronoi(co * PORE_FREQ + WARP)[0]
        return nh.smoothstep(0.36, 0.16, d[0]), nh.smoothstep(0.06, 0.2, d[1] - d[0])

    for v in bm.verts:
        p, _cell = pore(v.co)
        v.co += v.normal * (-0.012 * p + 0.004 * noise.noise(v.co * 9 + WARP))
    bm = nc.decimate(bm, MAX_TRIS)

    def inside(co, n):
        """Darkens the inner walls: below a rim, facing the tube axis."""
        k = 0.0
        for top, axis, _ri, pts, radii, wall, solid in vents:
            if not (pts[solid].z - 0.02 < co.z < top.z + 0.01):
                continue
            i = max([j for j in range(len(pts) - 1) if pts[j].z <= co.z] or [0])
            t = max(0.0, min(1.0, (co.z - pts[i].z) / max(1e-6, pts[i + 1].z - pts[i].z)))
            c = pts[i].lerp(pts[i + 1], t)
            r = radii[i] + (radii[i + 1] - radii[i]) * t
            radial = Vector((co.x - c.x, co.y - c.y, 0.0))
            if radial.length < 1e-6:
                continue
            facing = nh.smoothstep(0.1, -0.4, n.dot(radial.normalized()))
            k = max(k, facing * nh.smoothstep(r - wall * 0.2, r - wall * 0.8, radial.length)
                    * nh.smoothstep(top.z + 0.01, top.z - 0.05, co.z))
        return k

    def rim(co):
        k = 0.0
        for top, axis, ri, *_tube in vents:
            rel = co - top
            k = max(k, nh.smoothstep(0.05, 0.0, abs(rel.dot(axis) + 0.01)) *
                    nh.smoothstep(ri - 0.03, ri + 0.01, (rel - axis * rel.dot(axis)).length))
        return k

    def color(co, n):
        p, cell = pore(co)
        crease = nh.smoothstep(0.2, -0.4, noise.noise(co * 7 + WARP))
        c = nh.lerp(CREAM, TAN, 0.45 * crease + 0.5 * nh.smoothstep(0.18, 0.0, co.z))
        c = nh.lerp(c, TAN, 0.25 * (1.0 - cell))          # faint polygonal cell outlines
        c = nh.lerp(c, PORE, 0.85 * p)
        c = nh.lerp(c, RIM, 0.6 * rim(co))
        return nh.lerp(c, VENT, inside(co, n))

    out = nh.MeshBuilder()
    out.add(bm, color)
    nc.rubble(out, rng, 0.38, 0.6, count=7, size=(0.04, 0.08))
    obj = out.to_object("Eocyathispongia", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Eocyathispongia", ground=(0.62, 0.58, 0.48), views=((20, 30), (70, 40), (10, 70)))
