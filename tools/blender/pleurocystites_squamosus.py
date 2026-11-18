"""
Procedural Pleurocystites squamosus Forbes, 1848 (Late Ordovician pleurocystitid rhombiferan
"cystoid" of Britain and North America) for the map (Fixed style).

An unusual cystoid that was not fixed to the sea floor: a small (2-3 cm), flattened, oval theca
lying on its side, one face covered in a few large plates, with conspicuous pore rhombs (striped
diamond-shaped breathing structures) on the plates; two long, slender, jointed brachioles reaching
forward from the mouth end to gather food; and a flexible, muscular stem, thick near the theca and
tapering behind, that it may have used to push itself across the mud. Pale grey-buff plates
with darker sutures and rhombs (colour conjectural). Two animals on a mud patch.

Usage:
  blender --background --python tools/blender/pleurocystites_squamosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PleurocystitesSquamosus.fbx (pivot on the sea floor, z = 0)
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

PLATE = (0.80, 0.74, 0.62)
PLATE_DARK = (0.64, 0.56, 0.44)
SUTURE = (0.34, 0.26, 0.18)
RHOMB = (0.30, 0.22, 0.16)
RHOMB_LIGHT = (0.88, 0.82, 0.70)
STEM = (0.70, 0.62, 0.50)
STEM_DARK = (0.46, 0.38, 0.28)
BRACH = (0.78, 0.66, 0.52)
BRACH_DARK = (0.52, 0.40, 0.28)

W, L, H = 0.30, 0.40, 0.10       # theca half-sizes
# rhombs: centre (x, y) in units of W / L, half-diagonal, rotation
RHOMBS = ((-0.35, 0.25, 0.20, 0.3), (0.38, 0.22, 0.18, -0.3), (0.0, -0.35, 0.17, 0.0))


def plate_color(seeds):
    def col(co, n):
        if n.z < -0.4:
            return PLATE_DARK
        p = Vector((co.x / W, co.y / L))
        ds = sorted(((p - s).length, k) for s, k in seeds)[:2]
        (d0, k0), (d1, _k1) = ds
        c = nh.lerp(PLATE, PLATE_DARK, 0.5 * k0)
        for rx, ry, rr, rot in RHOMBS:
            q = Vector((p.x - rx, p.y - ry))
            q = Vector((q.x * math.cos(rot) - q.y * math.sin(rot), q.x * math.sin(rot) + q.y * math.cos(rot)))
            d = abs(q.x) + abs(q.y)
            if d < rr:
                stripe = 0.5 + 0.5 * math.sin((q.x - q.y) * 90.0)
                c = nh.lerp(RHOMB, RHOMB_LIGHT, 0.55 * stripe * nh.smoothstep(rr, rr * 0.7, d))
        c = nh.lerp(c, SUTURE, 1.0 - nh.smoothstep(0.03, 0.08, d1 - d0))
        # pale rim of marginal plates
        r = math.hypot(co.x / W, co.y / L)
        return nh.lerp(c, PLATE_DARK, 0.6 * nh.smoothstep(0.85, 1.0, r))
    return col


def animal(mb, m, rng):
    seeds = [(Vector((rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9))), rng.random()) for _ in range(9)]
    th = nh.ellipsoid((0, 0, H * 0.9), (W, L, H), subdivisions=4,
                      deform=lambda v: 1.0 - 0.25 * max(0.0, -v.z) ** 2)
    for v in th.verts:  # flatter top, a little pointed at the mouth end
        if v.co.y < 0:
            v.co.x *= 1.0 - 0.25 * (-v.co.y / L) ** 2
    nh.transform(th, m)
    inv = m.inverted()
    pc = plate_color(seeds)
    mb.add(th, lambda co, n: pc(inv @ co, (inv.to_3x3() @ n).normalized()))

    # two brachioles from the mouth end, jointed (alternating colour), arching forward and out
    for sx in (-1, 1):
        base = Vector((sx * 0.06, -L * 0.92, H * 1.3))
        pts, radii = [], []
        for k in range(9):
            t = k / 8
            pts.append(base + Vector((sx * (0.25 * t + 0.25 * t * t), -0.5 * t, 0.12 * math.sin(t * math.pi) - 0.08 * t)))
            radii.append(0.028 * (1 - 0.75 * t))
        for i in range(len(pts) - 1):
            bm = nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=6)
            nh.transform(bm, m)
            mb.add(bm, BRACH if i % 2 else BRACH_DARK)

    # stem: thick, ringed near the theca, tapering, curving behind across the mud
    n = 16
    pts, radii = [], []
    for k in range(n + 1):
        t = k / n
        pts.append(Vector((0.18 * math.sin(t * 2.6), L * 0.9 + 0.95 * t, H * 0.55 * (1 - t) + 0.035)))
        radii.append(0.075 * (1 - t) ** 1.3 + 0.012)
    for i in range(n):
        bm = nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=10)
        nh.transform(bm, m)
        mb.add(bm, STEM if i % 2 else STEM_DARK)


def build():
    rng = random.Random(4)
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.15, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    for x, y, yaw, k in ((-0.15, -0.25, 15, 1.0), (0.45, 0.35, 200, 0.7)):
        m = Matrix.Translation(Vector((x, y, 0.0))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Scale(k, 4)
        animal(mb, m, rng)
    obj = mb.to_object("PleurocystitesSquamosus", roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PleurocystitesSquamosus", **ec.VIEWS)
