"""
Procedural Chironex fleckeri (the Australian box jellyfish or sea wasp, coastal
waters of northern Australia and the Indo-West Pacific) for the map (Drift style).

The most venomous jellyfish known: a nearly transparent, cube-shaped bell up to about
30 cm across, its four flat sides meeting in rounded vertical edges. From each lower
corner hangs a pedalium, a flattened, muscular, hand-like arm, which fans out into a
bundle of up to 15 long tentacles (up to 3 m) carrying millions of stinging cells. A
sense organ (rhopalium, with true lens eyes) sits in a niche low on each flat side, and
the inner rim of the bell is closed by a shelf (velarium) that jets water out, so it
swims actively rather than drifting. Adapted from yunnanoascus_haikouensis.py.
  * Bell: a closed lathe shell whose cross-section is a rounded square (superellipse),
    taller than wide, with a slightly domed top.
  * Four pedalia at the corners, each with 9 tentacles fanning out and trailing down
    with a gentle wave, faintly banded with nematocyst rings.
  * Four rhopalia, a velarium shelf and a short manubrium inside.
Colours: translucent pale blue-white (vertex colours only), the pedalia a little milkier,
the tentacles pale lilac-blue with paler bands.
Drift style: pivot at the body centre (the middle of the bell).

Usage:
  blender --background --python tools/blender/chironex_fleckeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChironexFleckeri.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 5
SEGMENTS = 64
SQUARE = 4.0             # superellipse exponent of the cross-section (2 = round)
# bell profile (r, z): outer apex down to the margin, then up the inside
OUTER = [(0.0, 0.62), (0.14, 0.61), (0.26, 0.58), (0.32, 0.52), (0.35, 0.42), (0.36, 0.28), (0.36, 0.14),
         (0.355, 0.04)]
MARGIN = (0.345, 0.0)
INNER = [(0.30, 0.03), (0.30, 0.18), (0.27, 0.36), (0.18, 0.48), (0.0, 0.52)]
TENT_PER = 9
TENT_LEN = 1.35
TENT_R = 0.010
TENT_SEGS = 12
TENT_SIDES = 4

BELL = (0.74, 0.86, 0.95)
BELL_EDGE = (0.86, 0.93, 0.98)
SUBUMB = (0.62, 0.76, 0.88)
PEDAL = (0.84, 0.88, 0.94)
TENT = (0.74, 0.74, 0.92)
BAND = (0.92, 0.92, 0.98)
RHOP = (0.25, 0.20, 0.12)
MANUB = (0.80, 0.70, 0.78)


def sq(a):
    """Radius scale of a rounded square at angle a (corners on the diagonals)."""
    a = a - math.pi / 4          # put the flat sides on the x/y axes, corners on the diagonals
    c, s = abs(math.cos(a)), abs(math.sin(a))
    return 1.0 / ((c ** SQUARE + s ** SQUARE) ** (1.0 / SQUARE)) / 1.12


def bell():
    prof = [Vector(p) for p in OUTER] + [Vector(MARGIN)] + [Vector(p) for p in INNER]
    bm = bmesh.new()
    top = bm.verts.new((0, 0, prof[0].y))
    bottom = bm.verts.new((0, 0, prof[-1].y))
    rings = []
    for p in prof[1:-1]:
        ring = []
        for k in range(SEGMENTS):
            a = k / SEGMENTS * math.tau
            r = p.x * sq(a + math.pi / 4)
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, p.y)))
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
    r = math.hypot(co.x, co.y)
    inner = r > 1e-6 and n.dot(Vector((co.x, co.y, 0.0)).normalized()) < -0.1
    c = SUBUMB if inner else BELL
    # paler along the four rounded vertical edges (on the diagonals)
    a = math.atan2(co.y, co.x)
    edge = 1.0 - abs(math.sin(2 * a - math.pi / 2))   # 1 on the diagonals
    return nh.lerp(c, BELL_EDGE, 0.6 * nh.smoothstep(0.6, 0.95, edge))


def corner(k):
    a = math.pi / 4 + k * math.pi / 2
    d = Vector((math.cos(a), math.sin(a), 0.0))
    return a, d


def pedalia(mb, rng):
    for k in range(4):
        a, d = corner(k)
        tu = Vector((-d.y, d.x, 0.0))
        r0 = MARGIN[0] * sq(a + math.pi / 4)
        root = d * (r0 - 0.035) + Vector((0, 0, 0.12))
        hand = d * (r0 + 0.06) + Vector((0, 0, -0.14))
        # a flat, blade-like arm, broadening into the "hand"
        bm = nh.tube([tuple(root), tuple(root.lerp(hand, 0.5)), tuple(hand)], [0.045, 0.05, 0.065], sides=10,
                     scale_xy=(1.0, 0.5))
        mb.add(bm, PEDAL)
        for i in range(TENT_PER):
            u = (i / (TENT_PER - 1) - 0.5)
            base = hand + tu * (u * 0.09) + Vector((0, 0, 0.0))
            phase = rng.uniform(0, math.tau)
            out = rng.uniform(0.04, 0.12)
            ln = TENT_LEN * rng.uniform(0.8, 1.05)
            pts, radii = [], []
            for s in range(TENT_SEGS + 1):
                t = s / TENT_SEGS
                wave = 0.06 * math.sin(t * 6.0 + phase) * t
                pts.append(base + d * (out * t ** 0.7) + tu * (u * 0.12 * t + wave) + Vector((0, 0, -ln * t)))
                radii.append(TENT_R * (1.0 - 0.6 * t) + 0.002)
            tb = nh.tube(pts, radii, sides=TENT_SIDES, cap_start=False, cap_end=True)

            def col(co, _n, base=base):
                depth = max(0.0, base.z - co.z)
                band = 0.5 + 0.5 * math.sin(depth * 70.0)
                return nh.lerp(TENT, BAND, 0.6 * nh.smoothstep(0.75, 0.95, band))

            mb.add(tb, col)


def rhopalia(mb):
    for k in range(4):
        a = k * math.pi / 2        # middle of each flat side
        d = Vector((math.cos(a), math.sin(a), 0.0))
        r = MARGIN[0] * sq(a + math.pi / 4)
        mb.add(nh.ellipsoid(tuple(d * (r - 0.005) + Vector((0, 0, 0.09))), (0.018, 0.018, 0.022), subdivisions=1), RHOP)


def velarium_manubrium(mb):
    # velarium: a thin inward shelf closing part of the bell opening
    mb.add(nh.ellipsoid((0, 0, 0.02), (0.31, 0.31, 0.012), subdivisions=3), SUBUMB)
    mb.add(nh.tube([(0, 0, 0.50), (0, 0, 0.32), (0, 0, 0.18)], [0.05, 0.04, 0.05], sides=10), MANUB)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(bell(), bell_color)
    pedalia(mb, rng)
    rhopalia(mb)
    velarium_manubrium(mb)
    nh.transform(mb.bm, Matrix.Translation((0, 0, -0.31)))   # pivot in the middle of the bell
    return mb.to_object("ChironexFleckeri", roughness=0.3)


if __name__ == "__main__":
    nh.run(build, "ChironexFleckeri", background=(0.03, 0.12, 0.16), views=((30, 20), (10, 65), (-90, -5)))
