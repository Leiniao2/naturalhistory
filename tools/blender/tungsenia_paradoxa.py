"""
Procedural Tungsenia paradoxa for the map: the earliest and most primitive known
tetrapodomorph (a lobe-finned fish on the line to four-legged animals), from the
Early Devonian (Pragian, about 409 million years ago) Posongchong Formation of
Zhaotong, Yunnan, China (Lu et al. 2012). A small predator, under about 20 cm long.

Tungsenia is known from parts of the skull roof, braincase and lower jaw (the skull
has an unusually large notch for the eye), so the body follows other early
tetrapodomorphs such as Kenichthys and Osteolepis: a long, rounded, cylindrical body
with a broad, rather flat-topped head and large eyes, thick rhombic scales with a
glossy cosmine coat, fleshy scaled lobes at the base of the pectoral and pelvic
fins, two dorsal fins set far back (the first over the pelvic fins, the second over
the anal fin), and a long, gently upturned (epicercal) tail with fin webs above and
below. No fin spines, unlike the older Guiyu and Psarolepis.

Built from nh_early_fish pieces (bony head shell, rhombic scale lattice, fleshy fin
lobes with fin-ray fringes). Colours are unknown: olive-brown with darker blotches
above, a paler belly.

Usage:
  blender --background --python tools/blender/tungsenia_paradoxa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tungsenia.fbx (map style Swim: pivot at the
body centre, facing -Y, dorsal fins up). About 1.7 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Tungsenia"

BACK = (0.24, 0.23, 0.13)
FLANK = (0.50, 0.44, 0.27)
BELLY = (0.80, 0.74, 0.56)
BLOTCH = (0.14, 0.13, 0.08)
COSMINE = (0.52, 0.47, 0.32)
COSMINE_TOP = (0.32, 0.30, 0.19)
PORE = (0.16, 0.14, 0.09)
SUTURE = (0.12, 0.10, 0.06)
MOUTH = (0.10, 0.07, 0.05)
FIN = (0.40, 0.35, 0.22)
FIN_EDGE = (0.62, 0.56, 0.40)
RAY = (0.22, 0.19, 0.11)
LOBE = (0.44, 0.39, 0.25)

# long cylindrical body, broad flat-topped head
PROF = ef.Profile([
    (-0.85, 0.014, 0.010, 0.012, -0.010),
    (-0.83, 0.050, 0.036, 0.040, -0.008),
    (-0.77, 0.090, 0.060, 0.066, -0.004),
    (-0.67, 0.118, 0.080, 0.084, 0.000),
    (-0.55, 0.124, 0.096, 0.096, 0.004),
    (-0.38, 0.116, 0.106, 0.102, 0.006),
    (-0.15, 0.104, 0.104, 0.098, 0.008),
    (0.08, 0.084, 0.088, 0.082, 0.012),
    (0.28, 0.058, 0.064, 0.058, 0.020),
    (0.45, 0.036, 0.040, 0.036, 0.036),
    (0.65, 0.016, 0.018, 0.015, 0.070),
    (0.85, 0.003, 0.004, 0.003, 0.110),
], power=lambda y: 2.9 if y < -0.6 else 2.2)

Y_HEAD = -0.545
EYE_Y = -0.715

HEAD_PLATES = [(-0.80, 0.0), (-0.72, 0.35), (-0.66, 0.0), (-0.60, 0.45), (-0.57, 0.0), (-0.66, 1.1),
               (-0.58, 1.3), (-0.72, 1.6), (-0.60, 2.2)]


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.32


def head_color(co, n):
    u, v = PROF.rel(co)
    phi = ef.phi_of(PROF, co)
    c = nh.lerp(COSMINE, COSMINE_TOP, nh.smoothstep(0.0, 0.85, v) * 0.7)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    c = nh.lerp(c, PORE, 0.45 * nh.smoothstep(0.15, 0.40, ef.mottle(co, 34.0, 4.0)))
    # the cosmine blurs the sutures: only faint
    c = nh.lerp(c, SUTURE, 0.35 * ef.plates(HEAD_PLATES, co.y, phi, sphi=0.10, width=0.024))
    c = nh.lerp(c, SUTURE, 0.7 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.02 - 0.03 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.75)
    return nh.lerp(c, BLOTCH, 0.35 * (1.0 - nh.smoothstep(0.03, 0.08, abs(v - 0.05))))


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    lobe_paint = lambda t, co: nh.lerp(LOBE, BLOTCH, 0.35 * t + 0.25 * nh.smoothstep(0.2, 0.5, ef.mottle(co, 40.0)))  # noqa: E731
    # two dorsal fins far back, small anal fin under the second, all on short fleshy bases
    ef.median_fin(mb, PROF, 0.02, 0.14, lambda u: 0.10 * math.sin(math.pi * (0.2 + 0.8 * u)) ** 0.6 + 0.01,
                  rays(4), sweep=0.9, cols=ef.ray_cols(4), rows=2)
    ef.median_fin(mb, PROF, 0.28, 0.38, lambda u: 0.08 * math.sin(math.pi * (0.2 + 0.8 * u)) ** 0.6 + 0.01,
                  rays(3), sweep=0.9, cols=ef.ray_cols(3), rows=2)
    ef.median_fin(mb, PROF, 0.27, 0.37, lambda u: 0.075 * math.sin(math.pi * (0.2 + 0.8 * u)) ** 0.6 + 0.01,
                  rays(3), sign=-1, sweep=0.9, cols=ef.ray_cols(3), rows=2)
    for y0, y1, sg in ((0.02, 0.14, 1), (0.28, 0.38, 1), (0.27, 0.37, -1)):
        ym = (y0 + y1) * 0.5
        z = PROF.top(ym) if sg > 0 else PROF.bot(ym)
        mb.add(nh.uv_ellipsoid((0.0, ym, z), (0.016, (y1 - y0) * 0.55, 0.022), 8, 5),
               lambda co, n: lobe_paint(0.3, co))
    # long epicercal tail: webs above and below the gently upturned axis
    axis, edge, axis_t, edge_t = [], [], [], []
    n = ef.ray_cols(8)
    for i in range(n):
        u = i / (n - 1)
        y = 0.44 + 0.41 * u
        hb = 0.11 * math.sin(math.pi * min(1.0, u * 1.02) ** 0.8) * (1 - 0.3 * u) + 0.004
        ht = 0.075 * math.sin(math.pi * min(1.0, u * 1.02) ** 0.9) * (1 - 0.4 * u) + 0.004
        axis.append((0.0, y, PROF.bot(y) + 0.004))
        edge.append((0.0, y + 0.5 * hb, PROF.bot(y) - hb))
        axis_t.append((0.0, y, PROF.top(y) - 0.004))
        edge_t.append((0.0, y + 0.5 * ht, PROF.top(y) + ht))
    ef.caudal_web(mb, axis, edge, rays(8), rows=2)
    ef.caudal_web(mb, axis_t, edge_t, rays(8), rows=2)

    for s in (1, -1):
        # fleshy lobed pectoral fins, low behind the head
        root = Vector((s * PROF.W(-0.50) * 0.85, -0.50, PROF.CZ(-0.50) - PROF.HB(-0.50) * 0.6))
        tip = root + Vector((s * 0.17, 0.19, -0.07))
        ef.lobe(mb, root, root.lerp(tip, 0.65), 0.034, lobe_paint, sides=8)
        ef.lobe_fringe(mb, root, tip, (-s * 0.5, 1.0, -0.15),
                       lambda t: 0.022 * math.sin(math.pi * t) + 0.005,
                       lambda t: 0.055 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 + 0.005, rays(4),
                       cols=ef.ray_cols(4))
        # lobed pelvic fins under the first dorsal
        root = Vector((s * PROF.W(0.02) * 0.6, 0.02, PROF.CZ(0.02) - PROF.HB(0.02) * 0.85))
        tip = root + Vector((s * 0.10, 0.14, -0.06))
        ef.lobe(mb, root, root.lerp(tip, 0.6), 0.026, lobe_paint, sides=8)
        ef.lobe_fringe(mb, root, tip, (-s * 0.5, 1.0, -0.1),
                       lambda t: 0.015 * math.sin(math.pi * t) + 0.004,
                       lambda t: 0.04 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 + 0.004, rays(3),
                       cols=ef.ray_cols(3))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=15, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.85, 42, 18, scale_color, lift=0.0035, shine=0.30,
                   fade_y=(0.55, 0.8))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.84, -0.62, mouth_z, MOUTH, grow=0.004)
    # large eyes high on the sides of the flat head
    ef.surface_eye(mb, PROF, EYE_Y, 0.62, 0.036, (0.80, -0.25, 0.55), iris=(0.66, 0.52, 0.20))
    for s in (1, -1):
        p = PROF.point(-0.815, 0.25)
        p.x *= s
        mb.add(nh.uv_ellipsoid(tuple(p), (0.006, 0.008, 0.005), 5, 3), MOUTH)
    obj = mb.to_object(NAME, roughness=0.35)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
