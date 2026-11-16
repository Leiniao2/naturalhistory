"""
Procedural Yunnanoascus haikouensis (early Cambrian jellyfish-like animal, Chengjiang biota,
Ercaicun near Haikou, Kunming, Yunnan) for the map: a domed, sixteen-lobed bell trailing a fringe
of long tentacles, with a short manubrium hanging from the middle.

Known from a single specimen, roughly a centimetre or two across. It was first described (Hu et
al. 2007) as a comb jelly, because of the dark longitudinal strips on its bell, and reinterpreted
(Han et al. 2016) as a pelagic crown-group medusozoan with tetraradial symmetry: 16 marginal
lappets, 16 rhopalia (sense organs), 16 pairs of thick-based marginal tentacles and a manubrium;
its affinity is still debated. The model follows the 2016 reading:
  * Bell: a closed lathe shell (outer exumbrella down to the margin, then the inner subumbrella
    back up), its margin scalloped into 16 rounded lappets that droop slightly. 64 segments
    around, i.e. four per lappet.
  * 16 darker meridional strips (radial canals / the original "comb rows"), the four on the
    main axes a little broader to hint at the four-fold symmetry.
  * 16 rhopalia: small amber beads tucked into the notches between the lappets.
  * 16 pairs of tentacles, one pair per lappet, thick at the base and tapering, trailing down
    and slightly outward with a gentle wave; darker at the thick base (the fossil's tentacles show
    dark transverse striae, possible nematocyst batteries, too fine to model at map size).
  * A short four-lobed manubrium under the bell.
Colours are a guess for a living jelly: milky blue-white bell, pinkish-orange canals and
manubrium, pale pink tentacles.
Drift style: pivot at the body centre (the middle of the bell).

Usage:
  blender --background --python tools/blender/yunnanoascus_haikouensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Yunnanoascus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 3
LAPPETS = 16
SEGMENTS = 64            # around the bell (multiple of LAPPETS)
LAPPET_DEPTH = 0.05      # how far the notches between lappets cut into the margin
LAPPET_DROOP = 0.035     # how far the lappet tips hang below the notches
# bell profile (r, z) from the outer apex, down the exumbrella to the margin, then up the
# subumbrella to the inner apex
OUTER = [(0.0, 0.50), (0.12, 0.495), (0.24, 0.475), (0.34, 0.43), (0.42, 0.36), (0.48, 0.27), (0.515, 0.16),
         (0.53, 0.07), (0.53, 0.025)]
MARGIN = (0.52, 0.0)
INNER = [(0.48, 0.03), (0.44, 0.13), (0.36, 0.24), (0.22, 0.31), (0.0, 0.33)]
TENT_LEN = 0.95          # tentacle length
TENT_R = 0.022           # tentacle base radius
TENT_SPLAY = 0.12        # angle (fraction of a lappet) between the two tentacles of a pair
TENT_SEGS = 9
TENT_SIDES = 5
MANUBRIUM = 0.30         # manubrium length below the subumbrella apex

BELL = (0.80, 0.87, 0.93)      # milky blue-white bell
BELL_RIM = (0.90, 0.92, 0.95)  # paler margin
SUBUMB = (0.66, 0.74, 0.84)    # inside of the bell
CANAL = (0.88, 0.52, 0.42)     # radial canals / dark strips
RHOPALIUM = (0.62, 0.36, 0.12)
TENTACLE = (0.93, 0.78, 0.76)
STRIA = (0.78, 0.46, 0.42)     # darker tentacle bases
MANUB = (0.90, 0.56, 0.46)

WARP = Vector((5.1, 2.7, 9.3))


def margin_shape(a):
    """(radius scale, z drop) at angle a: rounded lappets with notches between them."""
    t = (a / math.tau * LAPPETS) % 1.0           # 0 and 1 = notch, 0.5 = lappet tip
    lobe = math.sin(t * math.pi) ** 0.6
    return 1.0 - LAPPET_DEPTH * (1.0 - lobe) / MARGIN[0], LAPPET_DROOP * lobe


def bell():
    """Closed lathe shell; the scalloped margin fades out up the exumbrella and subumbrella."""
    prof = [Vector(p) for p in OUTER] + [Vector(MARGIN)] + [Vector(p) for p in INNER]
    nmar = len(OUTER)
    bm = bmesh.new()
    top = bm.verts.new((0, 0, prof[0].y))
    bottom = bm.verts.new((0, 0, prof[-1].y))
    rings = []
    for i, p in enumerate(prof[1:-1], start=1):
        w = math.exp(-((i - nmar) / 1.6) ** 2)    # how much the lappet shape applies here
        ring = []
        for k in range(SEGMENTS):
            a = k / SEGMENTS * math.tau
            rs, dz = margin_shape(a)
            r = p.x * (1.0 + (rs - 1.0) * w)
            z = p.y - dz * w
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        rings.append(ring)
    for k in range(SEGMENTS):
        j = (k + 1) % SEGMENTS
        bm.faces.new([top, rings[0][k], rings[0][j]])
        bm.faces.new([bottom, rings[-1][j], rings[-1][k]])
    for a, b in zip(rings, rings[1:]):
        for k in range(SEGMENTS):
            j = (k + 1) % SEGMENTS
            bm.faces.new([a[k], b[k], b[j], a[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bell_color(co, n):
    a = math.atan2(co.y, co.x) % math.tau
    r = math.hypot(co.x, co.y)
    inner = n.dot(Vector((co.x, co.y, 0.0)).normalized() if r > 1e-6 else Vector((0, 0, 1))) < -0.1 \
        or (r < 0.4 and n.z < -0.3)
    c = SUBUMB if inner else nh.lerp(BELL, BELL_RIM, nh.smoothstep(0.2, 0.0, co.z))
    # radial canals run along the middle of each lappet, broader on the four main axes
    t = (a / math.tau * LAPPETS) % 1.0
    k = int(a / math.tau * LAPPETS) % LAPPETS
    width = 0.13 if k % 4 == 0 else 0.08
    stripe = nh.smoothstep(width, width * 0.4, abs(t - 0.5) / 1.0) * nh.smoothstep(0.03, 0.12, r)
    c = nh.lerp(c, CANAL, 0.75 * stripe)
    return nh.lerp(c, CANAL, 0.35 * nh.smoothstep(0.12, 0.0, r) * (0.0 if inner else 1.0))


def tentacles(mb, rng):
    for l in range(LAPPETS):
        for side in (-1, 1):
            a = (l + 0.5 + side * TENT_SPLAY) / LAPPETS * math.tau
            rs, dz = margin_shape(a)
            d = Vector((math.cos(a), math.sin(a), 0.0))
            tu = Vector((-d.y, d.x, 0.0))
            base = d * (MARGIN[0] * rs - 0.02) + Vector((0, 0, MARGIN[1] - dz + 0.01))
            phase = rng.uniform(0, math.tau)
            out = rng.uniform(0.12, 0.22)
            ln = TENT_LEN * rng.uniform(0.85, 1.05)
            pts, radii = [], []
            for i in range(TENT_SEGS + 1):
                t = i / TENT_SEGS
                wave = 0.05 * math.sin(t * 5.0 + phase) * t
                pts.append(base + d * (out * t ** 0.8 * ln) + tu * wave
                           + Vector((0, 0, -ln * t + 0.04 * t * t)))
                radii.append(TENT_R * (1.0 - t) ** 1.3 + 0.003)
            bm = nh.tube(pts, radii, sides=TENT_SIDES, cap_start=False, cap_end=True)

            def col(co, _n, base=base, ln=ln):
                depth = max(0.0, base.z - co.z) / ln
                return nh.lerp(STRIA, TENTACLE, nh.smoothstep(0.0, 0.35, depth))

            mb.add(bm, col)


def rhopalia(mb):
    for l in range(LAPPETS):
        a = l / LAPPETS * math.tau                    # in the notches
        rs, dz = margin_shape(a)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        c = d * (MARGIN[0] * rs - 0.005) + Vector((0, 0, MARGIN[1] - dz + 0.012))
        mb.add(nh.ellipsoid(c, (0.024, 0.024, 0.028), subdivisions=1), RHOPALIUM)


def manubrium(mb):
    """Short tube from the subumbrella apex, flaring into four lips."""
    z0 = INNER[-1][1] + 0.02
    pts = [(0, 0, z0 - MANUBRIUM * t) for t in (0.0, 0.3, 0.6, 0.85, 1.0)]
    radii = [0.07, 0.055, 0.05, 0.06, 0.075]
    bm = nh.tube(pts, radii, sides=16, cap_start=True, cap_end=True)
    for v in bm.verts:   # four lips: pinch the lower end into a cross
        t = max(0.0, (z0 - v.co.z) / MANUBRIUM - 0.45) / 0.55
        if t > 0:
            a = math.atan2(v.co.y, v.co.x)
            k = 1.0 + 0.45 * t * math.cos(4 * a)
            v.co.x *= k
            v.co.y *= k
            v.co.z -= 0.03 * t * max(0.0, math.cos(4 * a))
    mb.add(bm, lambda co, n: nh.lerp(MANUB, STRIA, 0.3 * nh.smoothstep(z0 - 0.1, z0 - MANUBRIUM, co.z)))


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(bell(), bell_color)
    rhopalia(mb)
    manubrium(mb)
    tentacles(mb, rng)
    nh.transform(mb.bm, Matrix.Translation((0, 0, -0.25)))   # pivot in the middle of the bell
    return mb.to_object("Yunnanoascus", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Yunnanoascus", background=(0.03, 0.12, 0.16), views=((30, 20), (10, 65), (-90, -5)))
