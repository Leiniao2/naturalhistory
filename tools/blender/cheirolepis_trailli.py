"""
Procedural Cheirolepis trailli for the map: one of the earliest well-known ray-finned
fishes (Actinopterygii), from the Middle Devonian (Givetian, about 385 million years ago)
lake beds of the Orcadian Basin, northern Scotland; usually 25-55 cm long.

A slim, fast predator: a big head with large eyes set far forward, long jaws reaching back
behind the eye and lined with small sharp teeth (it swallowed prey up to a third of its
own length), a single dorsal fin set far back opposite the anal fin, broad-based pelvic
fins, rayed (not lobed) pectoral fins, and a deep, strongly heterocercal tail. The
trunk is covered in tiny, close-set rhombic ganoid scales.

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: dark grey-blue back,
silvery flanks and belly.

Usage:
  blender --background --python tools/blender/cheirolepis_trailli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cheirolepis.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Cheirolepis"

BACK = (0.18, 0.22, 0.27)
FLANK = (0.58, 0.62, 0.64)
BELLY = (0.88, 0.88, 0.84)
BLOTCH = (0.12, 0.15, 0.19)
HEAD = (0.56, 0.58, 0.58)
HEAD_TOP = (0.22, 0.26, 0.30)
SUTURE = (0.12, 0.13, 0.15)
MOUTH = (0.08, 0.06, 0.06)
TOOTH = (0.94, 0.92, 0.86)
FIN = (0.34, 0.38, 0.42)
FIN_EDGE = (0.62, 0.66, 0.68)
RAY = (0.14, 0.16, 0.20)

PROF = ef.Profile([
    (-0.80, 0.012, 0.030, 0.022, 0.000),
    (-0.77, 0.045, 0.075, 0.065, 0.000),
    (-0.68, 0.075, 0.120, 0.110, 0.000),
    (-0.54, 0.092, 0.150, 0.140, 0.004),
    (-0.36, 0.090, 0.150, 0.140, 0.008),
    (-0.14, 0.078, 0.130, 0.122, 0.012),
    (0.06, 0.060, 0.100, 0.094, 0.020),
    (0.22, 0.044, 0.070, 0.064, 0.034),
    (0.36, 0.030, 0.044, 0.040, 0.058),
    (0.52, 0.018, 0.024, 0.021, 0.105),
    (0.68, 0.008, 0.011, 0.010, 0.165),
    (0.80, 0.002, 0.003, 0.003, 0.215),
], power=2.1)

Y_HEAD = -0.53


def mouth_z(y):
    # long gape sloping down and back
    return PROF.CZ(y) - PROF.HB(y) * (0.05 + 0.25 * nh.smoothstep(-0.80, -0.60, y))


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
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 56, 24, scale_color, lift=0.002, shine=0.30,
                   fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.06, 0.22, lambda u: (0.08 * u + 0.05, 0.12 * df.bump(u, 0.5, 0.2) * (1 - 0.4 * u) + 0.006),
           rays(6), side=1, n=ef.ray_cols(6), rows=2)
    df.web(mb, PROF, 0.10, 0.26, lambda u: (0.08 * u + 0.05, -(0.10 * df.bump(u, 0.5, 0.2) * (1 - 0.4 * u) + 0.006)),
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
    ef.mouth_line(mb, PROF, -0.79, -0.60, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.62, mouth_z, 8, 0.011, TOOTH)
    ef.surface_eye(mb, PROF, -0.715, 0.30, 0.036, (0.95, -0.25, 0.15), iris=(0.82, 0.78, 0.55))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
