"""
Procedural Mimipiscis toombsi (formerly Mimia) for the map: a small early ray-finned fish
(Actinopterygii) from the Late Devonian (Frasnian, about 380 million years ago) Gogo reef
of Western Australia; about 20 cm long. Its perfectly preserved 3-D skeletons are a key
reference for the anatomy of the earliest ray-finned fishes.

A neat, fusiform reef fish: a short blunt head with very large eyes, a single dorsal fin
opposite the anal fin, rayed pectoral and pelvic fins, a strongly heterocercal tail, and
large, shiny, close-fitting rhombic ganoid scales. Colours unknown: dark bronze back, gold
flanks and a silvery belly.

Usage:
  blender --background --python tools/blender/mimipiscis_toombsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mimipiscis.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Mimipiscis"

BACK = (0.26, 0.18, 0.08)
FLANK = (0.86, 0.66, 0.28)
BELLY = (0.92, 0.90, 0.80)
BLOTCH = (0.16, 0.10, 0.04)
HEAD = (0.80, 0.64, 0.32)
HEAD_TOP = (0.34, 0.24, 0.10)
SUTURE = (0.12, 0.13, 0.15)
MOUTH = (0.08, 0.06, 0.06)
TOOTH = (0.94, 0.92, 0.86)
FIN = (0.50, 0.36, 0.16)
FIN_EDGE = (0.86, 0.70, 0.40)
RAY = (0.24, 0.16, 0.06)

PROF = ef.Profile([
    (-0.80, 0.014, 0.040, 0.030, 0.000),
    (-0.77, 0.055, 0.100, 0.085, 0.000),
    (-0.68, 0.092, 0.160, 0.140, 0.000),
    (-0.54, 0.112, 0.200, 0.180, 0.004),
    (-0.36, 0.110, 0.205, 0.185, 0.008),
    (-0.14, 0.094, 0.175, 0.160, 0.012),
    (0.06, 0.070, 0.130, 0.120, 0.020),
    (0.22, 0.048, 0.085, 0.078, 0.034),
    (0.36, 0.032, 0.050, 0.046, 0.058),
    (0.52, 0.018, 0.026, 0.023, 0.105),
    (0.68, 0.008, 0.011, 0.010, 0.165),
    (0.80, 0.002, 0.003, 0.003, 0.215),
], power=2.1)

Y_HEAD = -0.56


def mouth_z(y):
    # long gape sloping down and back
    return PROF.CZ(y) - PROF.HB(y) * (0.10 + 0.20 * nh.smoothstep(-0.80, -0.68, y))


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.2, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.25), (-0.64, 0.25), (-0.58, 1.0), (-0.66, 1.6), (-0.58, 2.1)]
    c = nh.lerp(c, SUTURE, 0.45 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.025 * abs(v))))))
    return c


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.2)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 38, 20, scale_color, lift=0.003, shine=0.45,
                   fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.00, 0.18, lambda u: (0.08 * u + 0.05, 0.13 * df.bump(u, 0.5, 0.2) * (1 - 0.4 * u) + 0.006),
           rays(6), side=1, n=ef.ray_cols(6), rows=2)
    df.web(mb, PROF, 0.06, 0.22, lambda u: (0.08 * u + 0.05, -(0.10 * df.bump(u, 0.5, 0.2) * (1 - 0.4 * u) + 0.006)),
           rays(6), side=-1, n=ef.ray_cols(6), rows=2)
    # deep, forked heterocercal tail
    df.web(mb, PROF, 0.34, 0.80, lambda u: (0.16 * u + 0.04 * u * u,
                                            -(0.30 * df.bump(min(1.0, u * 1.6), 0.9) * (1 - 0.7 * u) + 0.08 * u + 0.004)),
           rays(10), side=-1, n=ef.ray_cols(10), rows=3)
    df.web(mb, PROF, 0.36, 0.80, lambda u: (0.02, 0.03 * df.bump(u, 0.6) + 0.003), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.50, -0.44, -0.75, lambda u: 0.17 * (1 - u) ** 0.5 + 0.02,
                      0.6, 0.55, 1.0, rays(5), cols=ef.ray_cols(5), rows=3)
        ef.paired_fin(mb, PROF, s, -0.12, 0.04, -1.25, lambda u: 0.08 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.9, rays(5), cols=ef.ray_cols(5), rows=2)
    ef.mouth_line(mb, PROF, -0.79, -0.66, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.68, mouth_z, 5, 0.009, TOOTH)
    ef.surface_eye(mb, PROF, -0.70, 0.32, 0.055, (0.95, -0.25, 0.15), iris=(0.82, 0.78, 0.55))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
