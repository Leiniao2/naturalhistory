"""
Procedural Drepanaspis gemuendenensis for the map: a psammosteid heterostracan, a
jawless armoured fish from the Early Devonian (Emsian, about 400 million years ago)
Hunsrück Slate of Germany; about 35 cm long.

Very flat and very broad, like a dinner plate with a tail: the head and front of the
body are covered by a wide, low armour shield made of a few large central plates (a
big median dorsal plate) set in a mosaic of many small polygonal tesserae. The tiny eyes
sit far apart at the front corners, and the mouth, without jaws, opens upward at the front
edge - perhaps for scooping food off the sea floor. Behind the shield a short, scaly tail
ends in a fin. It probably lay and grubbed on the muddy bottom.

Shield: nh_dev_fish.domed_slab with painted tesserae; trunk: nh_early_fish scale lattice.
Colours are unknown: grey-brown with pale tesserae borders.

Usage:
  blender --background --python tools/blender/drepanaspis_gemuendenensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Drepanaspis.fbx (Swim: pivot at the body centre,
facing -Y, shield up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Drepanaspis"

PLATE = (0.50, 0.46, 0.38)
PLATE_DARK = (0.32, 0.29, 0.23)
TESS = (0.62, 0.58, 0.48)
GROOVE = (0.20, 0.18, 0.14)
UNDER = (0.72, 0.68, 0.58)
MOUTH = (0.06, 0.04, 0.04)
BACK = (0.26, 0.24, 0.19)
FLANK = (0.42, 0.39, 0.31)
BELLY = (0.72, 0.68, 0.58)
BLOTCH = (0.18, 0.16, 0.12)
FIN = (0.36, 0.33, 0.27)
FIN_EDGE = (0.58, 0.55, 0.46)
RAY = (0.20, 0.18, 0.14)

HALF = [
    (0.00, -0.80), (0.12, -0.80), (0.24, -0.78), (0.34, -0.74), (0.42, -0.67), (0.48, -0.57),
    (0.51, -0.45), (0.52, -0.33), (0.51, -0.21), (0.48, -0.10), (0.42, -0.01), (0.34, 0.06),
    (0.24, 0.10), (0.14, 0.11), (0.07, 0.10), (0.00, 0.10),
]
DOME = 0.07
RIM = 0.16


def posterior(p):
    return p.y > 0.05 and abs(p.x) <= 0.09


def top_z(p, d):
    return DOME * df.rise(d, RIM)


def bot_z(p, d):
    return -0.4 * DOME * nh.smoothstep(0.0, RIM, d) ** 0.8


def shield_color(p, d, top):
    if not top:
        return UNDER
    # big central plates: median dorsal and a pair of branchials toward the sides
    med = ((p.x / 0.22) ** 2 + ((p.y + 0.34) / 0.30) ** 2) < 1.0
    branch = ((abs(p.x) - 0.36) / 0.07) ** 2 + ((p.y + 0.25) / 0.20) ** 2 < 1.0
    rost = (p.x / 0.12) ** 2 + ((p.y + 0.72) / 0.05) ** 2 < 1.0
    if med or branch or rost:
        c = nh.lerp(PLATE, PLATE_DARK, 0.4 * nh.smoothstep(0.2, 0.6, ef.mottle(Vector((p.x, p.y, 0)), 8.0)))
        return nh.lerp(c, TESS, 0.3 * df.tubercles(p, 90.0))
    t = df.tesserae(p, 0.07, 0.10)
    c = nh.lerp(TESS, PLATE_DARK, 0.3 * nh.smoothstep(0.0, 0.2, d))
    return nh.lerp(c, GROOVE, 0.8 * t)


TRUNK = ef.Profile([
    (0.00, 0.100, 0.055, 0.035, 0.010),
    (0.15, 0.095, 0.062, 0.040, 0.012),
    (0.30, 0.072, 0.055, 0.036, 0.014),
    (0.45, 0.040, 0.034, 0.024, 0.018),
    (0.62, 0.020, 0.018, 0.013, 0.024),
    (0.80, 0.002, 0.003, 0.002, 0.030),
], power=2.4)


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)


def build():
    mb = nh.MeshBuilder()
    df.domed_slab(mb, HALF, top_z, bot_z, shield_color, spacing=0.024, posterior=posterior)
    # upward-opening mouth slit along the front edge
    pts = [(x, -0.79 + 0.4 * x * x, 0.010) for x in [-0.12 + 0.24 * k / 8 for k in range(9)]]
    mb.add(nh.tube(pts, [0.004] + [0.008] * 7 + [0.004], sides=5, scale_xy=(1.0, 0.5)), MOUTH)
    for s in (1, -1):
        ef.eye(mb, (s * 0.40, -0.69, 0.012), (s * 0.7, -0.6, 0.4), 0.014, iris=(0.55, 0.50, 0.30))
    ef.scale_shell(mb, TRUNK, 0.03, 0.80, 22, 14, scale_color, lift=0.003, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    for side in (1, -1):
        df.web(mb, TRUNK, 0.50, 0.80, lambda u, s=side: (0.06 * u, s * (0.09 * df.bump(u, 0.8, 0.05) + 0.004)),
               rays(6), side=side, n=ef.ray_cols(6), rows=2)
    return df.finish(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 35), (-90, 8), (0, 80), (-150, 20)), background=df.PREVIEW["background"])
