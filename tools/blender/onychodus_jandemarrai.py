"""
Procedural Onychodus jandemarrai for the map: an onychodont lobe-finned fish from the
Late Devonian (Frasnian, about 380 million years ago) Gogo reef of Western Australia;
roughly a metre long.

A long-bodied ambush predator covered in rounded-rhombic scales, with a big head and a
wide gape. Its signature weapon was a pair of tooth whorls at the very front of the
lower jaw: curved rows of huge fangs that stuck up in front of the snout when the mouth
closed (they fitted into notches in the upper jaw), backed by rows of smaller sharp
teeth. Fleshy lobed paired fins, two dorsal fins far back and a tail with a long,
symmetrical fringe.

Bony head + rhombic scale lattice (nh_early_fish) with fin webs and lobes (nh_dev_fish).
Colours are unknown: dark green-olive back, mottled flanks, pale belly.

Usage:
  blender --background --python tools/blender/onychodus_jandemarrai.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Onychodus.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Onychodus"

BACK = (0.22, 0.30, 0.18)
FLANK = (0.56, 0.58, 0.36)
BELLY = (0.88, 0.86, 0.72)
BLOTCH = (0.10, 0.13, 0.08)
HEAD = (0.58, 0.58, 0.38)
HEAD_TOP = (0.26, 0.32, 0.19)
SUTURE = (0.10, 0.12, 0.07)
MOUTH = (0.12, 0.05, 0.05)
TOOTH = (0.95, 0.92, 0.82)
FIN = (0.26, 0.30, 0.18)
FIN_EDGE = (0.52, 0.54, 0.34)
RAY = (0.12, 0.14, 0.08)

PROF = ef.Profile([
    (-0.80, 0.014, 0.030, 0.024, -0.012),
    (-0.77, 0.052, 0.068, 0.058, -0.010),
    (-0.70, 0.090, 0.110, 0.096, -0.005),
    (-0.58, 0.112, 0.130, 0.118, 0.000),
    (-0.42, 0.106, 0.122, 0.112, 0.002),
    (-0.20, 0.090, 0.108, 0.100, 0.002),
    (0.00, 0.076, 0.094, 0.086, 0.002),
    (0.20, 0.056, 0.072, 0.064, 0.002),
    (0.38, 0.036, 0.046, 0.042, 0.002),
    (0.56, 0.020, 0.024, 0.022, 0.002),
    (0.72, 0.010, 0.012, 0.011, 0.002),
    (0.80, 0.002, 0.003, 0.003, 0.002),
], power=lambda y: 2.3 if y < -0.45 else 2.1)

Y_HEAD = -0.50


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.20


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.64, 0.25), (-0.58, 0.9), (-0.54, 1.4), (-0.66, 1.6), (-0.70, 2.1)]
    c = nh.lerp(c, SUTURE, 0.6 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.02 * abs(v))))))
    return c


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.6)


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fangs(mb):
    """Symphyseal tooth whorls: a row of big, recurved fangs on each side of the chin,
    sticking up in front of the snout."""
    for s in (1, -1):
        for k, (dy, h) in enumerate(((-0.006, 0.125), (0.012, 0.100), (0.030, 0.075), (0.046, 0.050))):
            y = -0.785 + dy
            x = s * (0.012 + 0.004 * k)
            z = mouth_z(y) - 0.012
            base = Vector((x, y, z))
            mid = base + Vector((0, -0.016, h * 0.6))
            tip = base + Vector((0, -0.002, h))
            mb.add(nh.tube([base, mid, tip], [0.013 - 0.0016 * k, 0.009 - 0.0012 * k, 0.0], sides=6), TOOTH)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.06, 0.18, lambda u: (0.05 * u + 0.03, 0.07 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.26, 0.38, lambda u: (0.05 * u + 0.03, 0.08 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.26, 0.38, lambda u: (0.05 * u + 0.03, -0.08 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    # long, symmetrical fringe round the tail
    for side in (1, -1):
        df.web(mb, PROF, 0.44, 0.80,
               lambda u, s=side: (0.06 * u, s * (0.11 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.005)), rays(8),
               side=side, n=ef.ray_cols(8), rows=3)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.46, -0.9, (0.55, 0.65, -0.45), 0.22, 0.028, lobe_paint, rays(5),
                     web_w=0.055, cols=ef.ray_cols(5))
        df.lobed_fin(mb, PROF, s, 0.02, -1.25, (0.45, 0.8, -0.4), 0.15, 0.022, lobe_paint, rays(4),
                     web_w=0.04, cols=ef.ray_cols(4))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 46, 20, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.56, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.74, -0.58, mouth_z, 6, 0.014, TOOTH)
    fangs(mb)
    ef.surface_eye(mb, PROF, -0.68, 0.45, 0.024, (0.9, -0.3, 0.3), iris=(0.80, 0.60, 0.20))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
