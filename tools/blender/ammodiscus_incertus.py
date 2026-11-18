"""
Procedural low-poly Ammodiscus incertus (agglutinated foraminifer) for colony instancing.

A flat, disc-like planispiral test: one undivided tube, with no chambers or septa, coiled
round a tiny round first chamber (proloculus) in seven or so tight, touching whorls, growing
slowly wider like a coiled rope or a flat snail. The wall is built of cemented sand grains, so
the colour is a sandy grey-tan speckled with lighter and darker grains, a little darker in the
sutures between the whorls. At the open end of the coil the round aperture opens, and from it a
web of very fine, branching and joining reticulopodia spreads out in a fan.
Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/ammodiscus_incertus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ammodiscus.fbx
Coil lies flat in the XY plane with the aperture and pseudopod fan toward -Y, ~1.6 units across
including the reticulopodia. Pivot at the centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 4
WHORLS = 7
R_START = 0.014       # tube radius at the proloculus
R_END = 0.044         # tube radius at the aperture
RHO0 = 0.032          # spiral radius at the start
SIDES = 6
FLATTEN = 0.82        # tube cross-section height / width
THREADS = 13

SAND = (0.66, 0.60, 0.50)
SAND_PALE = (0.86, 0.82, 0.72)
SAND_DARK = (0.40, 0.36, 0.30)
GRAIN_RUST = (0.60, 0.44, 0.30)
SUTURE = (0.46, 0.42, 0.35)
APERTURE = (0.18, 0.15, 0.12)
THREAD = (0.88, 0.90, 0.84)
THREAD_TIP = (0.95, 0.97, 0.95)

THETA_MAX = WHORLS * math.tau
B = (R_END - R_START) / THETA_MAX


def tube_r(th):
    return R_START + B * th


def rho(th):
    """Spiral radius such that each whorl just touches the one inside it."""
    a = R_START
    return RHO0 + 0.93 * (2 * a * th / math.tau + B * th * th / math.tau)  # 0.93: whorls press together


def coil_point(th):
    return Vector((math.cos(th) * rho(th), math.sin(th) * rho(th), 0.0))


def sand_colour(end, end_r):
    def col(co, n):
        g = noise.noise(co * 90.0)
        h = (math.sin(co.x * 129.898 + co.y * 782.33 + co.z * 377.19) * 43758.5453) % 1.0  # per grain
        if h < 0.12:
            return SAND_DARK
        if h > 0.86:
            return SAND_PALE
        c = nh.lerp(SAND, SAND_PALE, nh.smoothstep(0.1, 0.5, g))
        c = nh.lerp(c, SAND_DARK, nh.smoothstep(0.1, 0.45, -g) * 0.8)
        c = nh.lerp(c, GRAIN_RUST, nh.smoothstep(0.62, 0.8, h) * 0.8)
        # darker in the sutures, where the tube turns down to meet its neighbour
        c = nh.lerp(c, SUTURE, nh.smoothstep(0.25, 0.85, 1.0 - abs(n.z)) * 0.45)
        if (co - end).length < end_r * 0.88:
            c = APERTURE
        return c
    return col


def thread(mb, pts, r0):
    radii = [r0 * (1.0 - 0.6 * k / (len(pts) - 1)) for k in range(len(pts) - 1)] + [0.0]
    start = pts[0]
    span = max((p - start).length for p in pts) or 1.0

    def col(co, n):
        return nh.lerp(THREAD, THREAD_TIP, nh.smoothstep(0.0, span, (co - start).length))

    mb.add(nh.tube(pts, radii, sides=3), col)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()

    # the coiled tube, sampled by roughly even arc length (coarser angle steps near the middle)
    pts, radii = [], []
    th = 0.0
    while th < THETA_MAX:
        pts.append(coil_point(th))
        radii.append(tube_r(th))
        th += min(0.36, 0.058 / rho(th))
    pts.append(coil_point(THETA_MAX))
    radii.append(tube_r(THETA_MAX))
    end, end_r = pts[-1], radii[-1]
    fwd = (pts[-1] - pts[-2]).normalized()
    # a lip at the aperture turning in to a dark throat
    pts += [end - fwd * 0.004, end - fwd * 0.03]
    radii += [end_r * 0.72, 0.0]
    mb.add(nh.tube(pts, radii, sides=SIDES, scale_xy=(1.0, FLATTEN)), sand_colour(end, end_r))
    # proloculus
    mb.add(nh.ellipsoid((0.0, 0.0, 0.0), (0.036, 0.036, 0.03), subdivisions=2),
           sand_colour(Vector((9, 9, 9)), 0.0))

    # reticulopodia: a fan of fine threads out of the aperture, branching and re-joining
    out = Vector((end.x, end.y, 0.0)).normalized()
    fan = (fwd + out * 0.8).normalized()               # fan centred out and away from the coil
    side = fan.cross(Vector((0, 0, 1))).normalized()
    tips = []
    for k in range(THREADS):
        spread = (k / (THREADS - 1) - 0.5) * math.radians(140) + rng.uniform(-0.08, 0.08)
        lift = rng.uniform(-0.35, 0.35)
        d = (fan * math.cos(spread) + side * math.sin(spread) + Vector((0, 0, lift))).normalized()
        length = rng.uniform(0.42, 0.62) * (1.0 - 0.35 * abs(spread))
        wob = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.5, 0.5))) * 0.025
        p0 = end + fwd * 0.005
        line = [p0 + d * (length * t) + wob * math.sin(t * math.pi * 2) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
        thread(mb, line, 0.0055)
        tips.append(line)
        # one branch off the outer half
        b0 = line[2]
        bd = (d + side * rng.choice((-1, 1)) * 0.6 + Vector((0, 0, rng.uniform(-0.2, 0.2)))).normalized()
        bl = length * rng.uniform(0.3, 0.45)
        thread(mb, [b0, b0 + bd * bl * 0.5, b0 + bd * bl], 0.0035)
    # anastomoses: fine cross-links joining neighbouring threads
    for a, b in zip(tips, tips[1:]):
        if rng.random() < 0.7:
            i = rng.choice((2, 3))
            pa, pb = a[i], b[i]
            mid = (pa + pb) / 2 + (pa - end).normalized() * 0.02
            mb.add(nh.tube([pa, mid, pb], [0.0028, 0.0025, 0.0028], sides=3), THREAD_TIP)

    obj = mb.to_object("Ammodiscus", roughness=0.75)
    # aperture and fan toward -Y
    rot = Matrix.Rotation(-math.pi / 2 - math.atan2(fan.y, fan.x), 4, "Z")
    for v in obj.data.vertices:
        v.co = rot @ v.co
    lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
    hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
    for v in obj.data.vertices:
        for a in range(3):
            v.co[a] -= (lo[a] + hi[a]) / 2
    return obj


if __name__ == "__main__":
    nh.run(build, "Ammodiscus", views=((35, 35), (-80, 12), (0, 88)))
