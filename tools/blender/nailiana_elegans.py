"""
Procedural Nailiana elegans (early Cambrian stem-group anthozoan, Chengjiang biota, Yunnan)
for the map: a slender, sea-anemone-like polyp whose lower column is dug into a low mound of
mud, crowned by eight long, unbranched, prehensile tentacles.

Not a sponge: Ou et al. (2022, The Innovation) described it as a soft-bodied polyp in the stem
lineage of Anthozoa, from the Yu'anshan Member (Heilinpu Formation, Cambrian Stage 3, ~520 Ma)
at Erjie, Yunnan. Specimens are centimetre-scale. The anatomy modelled here follows their
description:
  * a slender, extensible, gently bending cylindrical column with 6-12 fine longitudinal
    grooves (10 here, in relief and as darker lines);
  * the aboral end tapering into the sediment (the column probably anchored the animal by
    peristaltic burrowing), shown as a narrow base sunk into a small mud mound;
  * the upper column swollen around the gastric cavity (often preserved dark in the fossils,
    hinted here by a slightly darker, warmer band);
  * a circular oral disc with a raised central mouth protuberance, ringed by a single whorl of
    eight long, smooth, tapering tentacles: some arch out and droop, some hang loose, as if
    groping for prey (one fossil holds a lingulid brachiopod in its tentacles).
Colours are unknown; pale salmon-buff, like many living anemones, with a darker mouth.
Fixed style: pivot at the base of the mud mound (z = 0).

Usage:
  blender --background --python tools/blender/nailiana_elegans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NailianaElegans.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 3
SIDES = 40            # column segments around
GROOVES = 10          # longitudinal striae on the column (6-12 in the fossils)
GROOVE_DEPTH = 0.07   # as a fraction of the radius
BEND = 0.16           # sideways offset of the oral end (column leans and curves)
MOUND_Z = 0.07        # mud surface height around the column
# column profile (radius, height): narrow buried aboral end -> slender trunk -> gastric bulge
# -> oral margin -> oral disc -> mouth protuberance
PROFILE = [
    (0.0, -0.02), (0.035, -0.015), (0.055, 0.03), (0.062, 0.12), (0.064, 0.25), (0.066, 0.38),
    (0.072, 0.50), (0.086, 0.60), (0.104, 0.69), (0.116, 0.77), (0.118, 0.83), (0.112, 0.88),
    (0.100, 0.905), (0.080, 0.915), (0.055, 0.918), (0.036, 0.925), (0.026, 0.945),
    (0.016, 0.955), (0.0, 0.950),
]
DISC_Z = 0.905        # tentacle ring height (on the oral margin)
DISC_R = 0.098        # tentacle ring radius
# eight tentacles: (length, start elevation deg, curl deg along the length, side curl deg)
TENTACLES = [
    (0.64, 55, -150, 10), (0.58, 70, -70, -30), (0.70, 50, -120, 0), (0.60, 68, -20, 45),
    (0.66, 58, -135, -10), (0.55, 72, -85, 25), (0.68, 48, -110, -5), (0.62, 66, -35, -45),
]

COLUMN = (0.86, 0.62, 0.50)       # pale salmon-buff column
COLUMN_LOW = (0.66, 0.46, 0.36)   # darker, mud-stained lower column
GROOVE = (0.58, 0.36, 0.28)       # longitudinal striae
GUT = (0.74, 0.42, 0.30)          # warmer band over the gastric cavity
DISC = (0.94, 0.74, 0.62)         # oral disc
MOUTH = (0.52, 0.24, 0.20)        # mouth protuberance
TENT_BASE = (0.90, 0.64, 0.52)
TENT_TIP = (0.98, 0.90, 0.82)
MUD = (0.42, 0.35, 0.26)
MUD_LIGHT = (0.56, 0.48, 0.36)


def bend(p):
    """Leans and curves the column: offset grows with height (quadratic), mostly toward +X."""
    t = max(0.0, p.z) / DISC_Z
    return Vector((p.x + BEND * t * t, p.y + 0.03 * t * t, p.z))


def bend_dir(p, d):
    """Bends a direction at p consistently with bend()."""
    return (bend(p + d * 0.01) - bend(p)).normalized()


def groove(a):
    return nh.smoothstep(0.75, 1.0, math.cos(a * GROOVES))


def column():
    bm = bmesh.new()
    rings = []
    for r, z in PROFILE:
        if r <= 1e-6:
            rings.append([bm.verts.new(bend(Vector((0, 0, z))))])
            continue
        g = GROOVE_DEPTH * nh.smoothstep(0.88, 0.0, z) * nh.smoothstep(0.0, 0.1, z)
        ring = []
        for j in range(SIDES):
            a = j / SIDES * math.tau
            rr = r * (1.0 - g * groove(a) + 0.02 * noise.noise(Vector((math.cos(a), math.sin(a), z * 6))))
            ring.append(bm.verts.new(bend(Vector((math.cos(a) * rr, math.sin(a) * rr, z)))))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        if len(ra) == 1:
            for j in range(SIDES):
                bm.faces.new([ra[0], rb[j], rb[(j + 1) % SIDES]])
        elif len(rb) == 1:
            for j in range(SIDES):
                bm.faces.new([ra[j], ra[(j + 1) % SIDES], rb[0]])
        else:
            for j in range(SIDES):
                k = (j + 1) % SIDES
                bm.faces.new([ra[j], ra[k], rb[k], rb[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        z = co.z
        # undo the bend to get the straight-column angle
        t = max(0.0, z) / DISC_Z
        x, y = co.x - BEND * t * t, co.y - 0.03 * t * t
        r = math.hypot(x, y)
        a = math.atan2(y, x)
        if z > 0.9 and n.z > 0.3:
            # oral disc and mouth protuberance
            return nh.lerp(DISC, MOUTH, nh.smoothstep(0.05, 0.03, r))
        c = nh.lerp(COLUMN_LOW, COLUMN, nh.smoothstep(MOUND_Z, 0.35, z))
        c = nh.lerp(c, GUT, 0.55 * nh.smoothstep(0.55, 0.68, z) * nh.smoothstep(0.88, 0.78, z))
        g = groove(a) * nh.smoothstep(0.88, 0.8, z)
        return nh.lerp(c, GROOVE, 0.7 * g)
    return bm, color


def tentacle(rng, a, length, elev0, curl, side_curl):
    base = Vector((math.cos(a) * DISC_R, math.sin(a) * DISC_R, DISC_Z - 0.005))
    out = Vector((math.cos(a), math.sin(a), 0.0))
    side = Vector((-out.y, out.x, 0.0))
    steps = 10
    seg = length / steps
    pts, radii = [], []
    p = base.copy()
    r0 = 0.028 * rng.uniform(0.9, 1.1)
    for k in range(steps + 1):
        t = k / steps
        pts.append(bend(p))
        radii.append(r0 * (1.0 - 0.75 * t ** 1.1))
        e = math.radians(elev0 + curl * t ** 1.3)
        s = math.radians(side_curl * t)
        d = (out * math.cos(e) + Vector((0, 0, math.sin(e)))) * math.cos(s) + side * math.sin(s)
        p = p + d.normalized() * seg
    pts.append(bend(p))
    radii.append(0.0)
    bm = nh.tube(pts, radii, sides=6, cap_start=False)
    total = sum((q - o).length for o, q in zip(pts, pts[1:]))
    b = pts[0]

    def color(co, n):
        return nh.lerp(TENT_BASE, TENT_TIP, nh.smoothstep(0.2, 1.0, (co - b).length / total))
    return bm, color


def mound(rng):
    seed = Vector((rng.random() * 40, rng.random() * 40, 3.0))
    bm = nh.ellipsoid((0.0, 0.0, 0.0), (0.30, 0.27, MOUND_Z), subdivisions=3,
                      deform=lambda n: 1.0 + 0.15 * noise.noise(n * 2.0 + seed))

    def color(co, n):
        k = 0.5 + 0.5 * noise.noise(co * 12 + seed)
        return nh.lerp(MUD, MUD_LIGHT, k)
    return bm, color


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(*mound(rng))
    mb.add(*column())
    off = rng.uniform(0, math.tau)
    for i, (length, e0, curl, sc) in enumerate(TENTACLES):
        a = off + i / len(TENTACLES) * math.tau + rng.uniform(-0.06, 0.06)
        mb.add(*tentacle(rng, a, length * rng.uniform(0.95, 1.05), e0, curl, sc))
    obj = mb.to_object("NailianaElegans", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "NailianaElegans", background=(0.04, 0.18, 0.26), ground=(0.36, 0.33, 0.28),
           views=((20, 20), (100, 15), (10, 70)))
