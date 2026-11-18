"""
Procedural low-poly Dictyostelium discoideum, a social amoeba (cellular slime mould).

A small patch of soil with a cluster of six fruiting bodies (sorocarps), each a thin, tall,
slightly tapering cellulose stalk on a little basal disc, varied in height and lean, topped by a
round lemon-yellow ball of spores (the sorus). Beside them a migrating slug (the
pseudoplasmodium), a small cream-white sausage with a paler raised tip, crawls toward -Y and
leaves a faint slime trail behind it over the ground, and one culminant mid-way through
fruiting has the "Mexican hat" shape: a wide brim of cells round a raised conical crown.
The ground is a thin brownish disc. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/dictyostelium_discoideum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dictyostelium.fbx
About 1.6 units across (the ground disc); the tallest stalk ~1 unit. The slug faces -Y.
Pivot at the bottom of the ground disc (Fixed).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 5
GROUND_R = 0.8
GROUND_H = 0.04

# fruiting bodies: (x, y, height, lean x, lean y, sorus radius)
FRUITING = [
    (0.10, 0.22, 0.98, 0.05, 0.03, 0.075),
    (0.28, 0.12, 0.78, 0.16, -0.04, 0.066),
    (-0.08, 0.36, 0.70, -0.14, 0.08, 0.062),
    (0.22, 0.42, 0.88, 0.07, 0.14, 0.070),
    (0.42, 0.32, 0.56, 0.17, 0.05, 0.055),
    (-0.02, 0.06, 0.62, -0.08, -0.12, 0.058),
]

# the slug's path over the ground (rear to front tip), toward -Y
SLUG = [(-0.20, -0.08), (-0.25, -0.18), (-0.30, -0.28), (-0.33, -0.38), (-0.34, -0.47)]
# the slime trail it has left behind it
TRAIL = [(0.05, 0.30), (-0.02, 0.20), (-0.10, 0.08), (-0.17, -0.02), (-0.21, -0.10)]
HAT = (0.34, -0.22)

SOIL = (0.40, 0.29, 0.19)
SOIL_DARK = (0.30, 0.21, 0.13)
SOIL_RIM = (0.33, 0.24, 0.16)
STALK = (0.93, 0.89, 0.74)
STALK_BASE = (0.84, 0.78, 0.60)
SORUS = (1.0, 0.94, 0.28)
SORUS_DEEP = (0.98, 0.80, 0.10)
SLUG_BODY = (0.93, 0.90, 0.80)
SLUG_TIP = (0.99, 0.98, 0.94)
SLIME = (0.62, 0.57, 0.48)


def lathe(profile, segments, center=(0, 0, 0)):
    """Surface of revolution about Z from a profile of (r, z) points; r = 0 makes a pole."""
    bm = bmesh.new()
    cx, cy, cz = center
    rings = []
    for r, z in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((cx, cy, cz + z))])
        else:
            rings.append([bm.verts.new((cx + math.cos(k / segments * math.tau) * r,
                                        cy + math.sin(k / segments * math.tau) * r, cz + z))
                          for k in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def smooth_path(pts, n):
    """Catmull-Rom resample of a 2D polyline to n points."""
    pts = [Vector((p[0], p[1], 0.0)) for p in pts]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    segs = len(pts) - 1
    for i in range(n):
        u = i / (n - 1) * segs
        s = min(int(u), segs - 1)
        t = u - s
        p0, p1, p2, p3 = ext[s], ext[s + 1], ext[s + 2], ext[s + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return out


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # the ground: a thin disc of soil, slightly uneven in tone
    prof = [(0.0, GROUND_H)] + [(GROUND_R * f, GROUND_H) for f in (0.2, 0.4, 0.6, 0.8, 0.95)]
    prof += [(GROUND_R, GROUND_H * 0.6), (GROUND_R * 0.98, 0.0), (0.0, 0.0)]

    def soil(co, n):
        k = noise.noise(Vector((co.x * 5.0, co.y * 5.0, 0.3)))
        c = nh.lerp(SOIL, SOIL_DARK, 0.5 + 0.5 * k)
        return nh.lerp(c, SOIL_RIM, nh.smoothstep(0.035, 0.0, co.z))

    mb.add(lathe(prof, 36), soil)

    # fruiting bodies: tapering stalk on a basal disc, a yellow sorus on top
    for x, y, h, lx, ly, sr in FRUITING:
        base = Vector((x, y, GROUND_H))
        pts, radii = [base - Vector((0, 0, 0.01)), base + Vector((0, 0, 0.012))], [0.034, 0.018]
        n = 6
        for k in range(1, n + 1):
            t = k / n
            pts.append(base + Vector((lx * t ** 1.6, ly * t ** 1.6, h * t)))
            radii.append(0.016 - 0.007 * t)
        top = pts[-1]
        d = (pts[-1] - pts[-2]).normalized()

        def stalk_col(co, nrm, z0=base.z, h=h):
            return nh.lerp(STALK_BASE, STALK, nh.smoothstep(0.0, 0.08, co.z - z0))

        mb.add(nh.tube(pts, radii, sides=6), stalk_col)
        c = top + d * sr * 0.75
        sq = rng.uniform(0.92, 1.0)

        def sorus_col(co, nrm, c=c, sr=sr):
            k = (co.z - c.z) / sr
            col = nh.lerp(SORUS_DEEP, SORUS, nh.smoothstep(-0.9, 0.6, k))
            return nh.lerp(col, (1.0, 0.97, 0.55), nh.smoothstep(0.6, 1.0, k) * 0.5)

        mb.add(nh.uv_ellipsoid(tuple(c), (sr, sr, sr * sq), segments=10, rings=7), sorus_col)

    # the slime trail: a faint, glossy flat ribbon over the soil behind the slug
    tp = smooth_path(TRAIL, 9)
    for p in tp:
        p.z = GROUND_H + 0.002
    tw = [0.020 + 0.018 * (i / (len(tp) - 1)) for i in range(len(tp))]
    tw[0] = 0.0
    mb.add(nh.tube(tp, tw, sides=8, scale_xy=(1.0, 0.06)), SLIME)

    # the migrating slug: a cream sausage, rear rounded, the front tip narrower and lifted
    sp = smooth_path(SLUG, 10)
    radii = []
    for i, p in enumerate(sp):
        t = i / (len(sp) - 1)
        r = 0.062 * (math.sin(math.pi * min(1.0, 0.08 + t * 0.92)) ** 0.35) * (1.0 - 0.3 * t)
        radii.append(r)
        p.z = GROUND_H + r * 0.75 + 0.03 * nh.smoothstep(0.7, 1.0, t)
    radii[0] = 0.03
    radii[-1] = 0.0
    sp[0].z = GROUND_H + 0.03
    front = Vector(sp[-1])
    length = sum((b - a).length for a, b in zip(sp, sp[1:]))

    def slug_col(co, nrm):
        f = 1.0 - (co - front).length / length
        return nh.lerp(SLUG_BODY, SLUG_TIP, nh.smoothstep(0.65, 0.85, f))

    mb.add(nh.tube(sp, radii, sides=10, scale_xy=(1.0, 0.9)), slug_col)

    # the "Mexican hat" culminant: a brim of cells round a raised conical crown
    hat = [(0.0, 0.205), (0.012, 0.198), (0.024, 0.17), (0.034, 0.12), (0.042, 0.075),
           (0.062, 0.042), (0.090, 0.030), (0.112, 0.022), (0.118, 0.008), (0.112, -0.004), (0.0, -0.004)]

    def hat_col(co, nrm):
        k = nh.smoothstep(0.08, 0.20, co.z - GROUND_H)
        return nh.lerp(SLUG_BODY, SLUG_TIP, k)

    mb.add(lathe(hat, 16, (HAT[0], HAT[1], GROUND_H)), hat_col)
    obj = mb.to_object("Dictyostelium", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Dictyostelium", views=((35, 25), (-60, 12), (10, 70)))
