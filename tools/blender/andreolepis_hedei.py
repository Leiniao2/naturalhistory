"""
Procedural Andreolepis hedei for the map: one of the earliest known ray-finned fishes
(actinopterygians; some studies place it just outside the bony-fish crown), from the
late Silurian (Ludlow, about 425-420 million years ago) of Gotland, Sweden, with more
finds in Estonia, Latvia and Novaya Zemlya.

Andreolepis is known only from isolated rhombic scales with a thin shiny ganoine
layer and a few fragments of dermal bone, so the whole body is a cautious,
generalised early ray-finned fish in the style of later Devonian forms such as
Cheirolepis: a slender spindle-shaped body covered in small rhombic scales in oblique
rows, a short, blunt head with a large eye set far forward and a long, oblique gape
running back behind the eye, low pectoral fins, small pelvic fins, a single dorsal
fin set far back over the anal fin, and a strongly heterocercal tail whose scaled
upper lobe is long and thin. All fins are webs of fine rays (no spines, no fleshy
lobes), which keeps it clearly apart from the spiny, lobe-finned Guiyu and
Psarolepis.

Built from nh_early_fish pieces. Colours are unknown: olive above and silvery
below, with a faint golden sheen to suggest the ganoine.

Usage:
  blender --background --python tools/blender/andreolepis_hedei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Andreolepis.fbx (map style Swim: pivot at
the body centre, facing -Y, dorsal fin up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Andreolepis"

BACK = (0.28, 0.30, 0.20)
FLANK = (0.62, 0.58, 0.40)
BELLY = (0.84, 0.84, 0.78)
BLOTCH = (0.22, 0.24, 0.17)
BONE = (0.56, 0.52, 0.36)
BONE_DARK = (0.32, 0.32, 0.22)
SUTURE = (0.14, 0.13, 0.09)
MOUTH = (0.10, 0.07, 0.06)
FIN = (0.55, 0.52, 0.38)
FIN_EDGE = (0.78, 0.76, 0.64)
RAY = (0.30, 0.27, 0.17)

PROF = ef.Profile([
    (-0.80, 0.010, 0.012, 0.012, -0.004),
    (-0.78, 0.040, 0.052, 0.045, 0.000),
    (-0.73, 0.068, 0.088, 0.078, 0.006),
    (-0.65, 0.090, 0.112, 0.100, 0.010),
    (-0.52, 0.102, 0.128, 0.114, 0.012),
    (-0.35, 0.100, 0.126, 0.112, 0.014),
    (-0.15, 0.088, 0.112, 0.100, 0.018),
    (0.05, 0.068, 0.088, 0.078, 0.026),
    (0.22, 0.046, 0.060, 0.052, 0.040),
    (0.34, 0.032, 0.040, 0.034, 0.062),
    (0.56, 0.016, 0.020, 0.016, 0.140),
    (0.80, 0.003, 0.005, 0.004, 0.250),
], power=lambda y: 2.3 if y < -0.55 else 2.1)

Y_HEAD = -0.56
EYE_Y = -0.715

HEAD_PLATES = [(-0.77, 0.0), (-0.70, 0.3), (-0.64, 0.0), (-0.60, 0.35), (-0.70, 1.2), (-0.62, 1.0),
               (-0.60, 1.6), (-0.66, 2.2)]


def mouth_z(y):
    """Long oblique gape, from the snout tip sloping down to well behind the eye."""
    return PROF.CZ(y) - PROF.HB(y) * (0.05 + 0.55 * nh.smoothstep(-0.80, -0.62, y))


def head_color(co, n):
    u, v = PROF.rel(co)
    phi = ef.phi_of(PROF, co)
    c = nh.lerp(BONE, BONE_DARK, nh.smoothstep(0.0, 0.9, v) * 0.6)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.8, v) * 0.7)
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(HEAD_PLATES, co.y, phi, sphi=0.10, width=0.022))
    if co.y < -0.63 and abs(u) > 0.4:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.003, 0.009, abs(co.z - mouth_z(co.y))))
    c = nh.lerp(c, SUTURE, 0.7 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.02 - 0.03 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.25)
    # golden ganoine sheen along the mid flank
    c = nh.lerp(c, (0.74, 0.64, 0.38), 0.25 * (1.0 - nh.smoothstep(0.0, 0.45, abs(v + 0.05))))
    c = nh.lerp(c, BLOTCH, 0.4 * (1.0 - nh.smoothstep(0.03, 0.08, abs(v - 0.10))))
    return c


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n, ray_amount=0.7)  # noqa: E731
    # single dorsal fin set far back, over the anal fin
    ef.median_fin(mb, PROF, 0.04, 0.22, lambda u: 0.15 * (1 - u) ** 0.9 + 0.008, rays(7), sweep=0.75,
                  cols=ef.ray_cols(7), rows=2)
    ef.median_fin(mb, PROF, 0.10, 0.28, lambda u: 0.11 * (1 - u) ** 0.9 + 0.008, rays(6), sign=-1, sweep=0.8,
                  cols=ef.ray_cols(6), rows=2)
    # strongly heterocercal tail: deep, fan-like lower web under the thin scaled upper lobe
    axis, edge = [], []
    n = ef.ray_cols(10)
    for i in range(n):
        u = i / (n - 1)
        y = 0.30 + 0.50 * u
        axis.append((0.0, y, PROF.bot(y) + 0.004))
        L = 0.26 * math.sin(math.pi * min(1.0, u * 1.02) ** 0.7) ** 1.1 * (1 - 0.4 * u) + 0.003
        edge.append((0.0, y + 0.65 * L, PROF.bot(y) - L))
    ef.caudal_web(mb, axis, edge, rays(10), rows=3)

    for s in (1, -1):
        # low pectoral fins: broad ray fans
        ef.paired_fin(mb, PROF, s, -0.53, -0.47, -1.0, lambda u: 0.17 * (1 - u) ** 0.5 + 0.03,
                      0.75, 0.45, 0.9, rays(5), cols=ef.ray_cols(5), rows=2)
        # small pelvic fins
        ef.paired_fin(mb, PROF, s, -0.08, -0.03, -1.2, lambda u: 0.08 * (1 - u) ** 0.5 + 0.015,
                      0.5, 0.7, 0.9, rays(3), cols=ef.ray_cols(3), rows=2)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=14, na=24, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.80, 42, 18, scale_color, lift=0.003, shine=0.30,
                   fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.645, mouth_z, MOUTH, grow=0.005)
    # large eye far forward
    ef.surface_eye(mb, PROF, EYE_Y, 0.30, 0.036, (0.95, -0.25, 0.15), iris=(0.78, 0.70, 0.45))
    obj = mb.to_object(NAME, roughness=0.35)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
