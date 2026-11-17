"""
Procedural Gemuendina stuertzi for the map: a rhenanid placoderm from the Early Devonian
(Emsian, about 400 million years ago) Hunsrück Slate near Bundenbach, Germany; about
25-30 cm long.

It looks strikingly like a modern skate or ray - an example of convergent evolution: a
flat body with huge wing-like pectoral fins, a broad, rounded head with the mouth at the
front edge, the eyes on top looking upward, and a long, slender tail. Instead of large
armour plates its skin was covered in a mosaic of small bony tesserae and tubercles,
with a few larger plates on the head and back. It probably lay on the sea floor and
fed on small invertebrates.

Disc: nh_dev_fish.domed_slab; tail: tapering tube with small fins. Colours are unknown:
sandy-brown with darker mottling, like a bottom-dwelling ray.

Usage:
  blender --background --python tools/blender/gemuendina_stuertzi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gemuendina.fbx (Swim: pivot at the body centre,
facing -Y, back up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402
import nh_fish as fish  # noqa: E402

NAME = "Gemuendina"

SKIN = (0.62, 0.52, 0.36)
SKIN_DARK = (0.38, 0.30, 0.19)
TUB = (0.80, 0.72, 0.56)
PLATE = (0.50, 0.42, 0.28)
UNDER = (0.84, 0.80, 0.70)
MOUTH = (0.07, 0.05, 0.04)

# head + pectoral "wings" in one outline
HALF = [
    (0.00, -0.80), (0.08, -0.79), (0.15, -0.76), (0.20, -0.71), (0.26, -0.66), (0.36, -0.60),
    (0.48, -0.52), (0.58, -0.42), (0.64, -0.32), (0.66, -0.24), (0.62, -0.16), (0.52, -0.09),
    (0.38, -0.05), (0.24, -0.03), (0.14, 0.00), (0.08, 0.04), (0.05, 0.06), (0.00, 0.06),
]
DOME = 0.075
RIM = 0.22


def posterior(p):
    return p.y > 0.03 and abs(p.x) <= 0.06


def top_z(p, d):
    body = 1.0 - nh.smoothstep(0.05, 0.30, abs(p.x))
    return DOME * df.rise(d, RIM) * (0.35 + 0.65 * body)


def bot_z(p, d):
    body = 1.0 - nh.smoothstep(0.05, 0.30, abs(p.x))
    return -DOME * 0.5 * df.rise(d, RIM) * (0.3 + 0.7 * body)


def color(p, d, top):
    if not top:
        return UNDER
    c = nh.lerp(SKIN, SKIN_DARK, 0.55 * nh.smoothstep(0.1, 0.5, ef.mottle(Vector((p.x, p.y, 0)), 7.0, 3.0)))
    c = nh.lerp(c, TUB, 0.5 * df.tubercles(p, 80.0))
    # a row of larger median plates down the back
    if abs(p.x) < 0.05 and -0.55 < p.y < 0.0:
        ph = (p.y + 0.55) / 0.11
        c = nh.lerp(c, PLATE, 0.7 * (1 - nh.smoothstep(0.25, 0.4, abs(ph - round(ph)))))
    return c


def build():
    mb = nh.MeshBuilder()
    df.domed_slab(mb, HALF, top_z, bot_z, color, spacing=0.03, posterior=posterior)
    # slender tail
    pts = [(0, 0.02 + 0.78 * k / 8, 0.005 - 0.01 * (k / 8) ** 2) for k in range(9)]
    radii = [0.050, 0.040, 0.030, 0.022, 0.016, 0.012, 0.008, 0.005, 0.0]
    mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.8)),
           lambda co, n: nh.lerp(UNDER, nh.lerp(SKIN, SKIN_DARK, 0.4), nh.smoothstep(-0.6, 0.3, n.z)))
    fc = lambda u, v, co: nh.lerp(SKIN_DARK, SKIN, v)  # noqa: E731
    for y0, y1, h in ((0.20, 0.32, 0.05), (0.40, 0.50, 0.04)):
        b = [(0, y0 + (y1 - y0) * k / 5, 0.012) for k in range(6)]
        e = [(0, y0 + (y1 - y0) * k / 5 + 0.04, 0.012 + h * math.sin(math.pi * k / 5) ** 0.6 + 0.003)
             for k in range(6)]
        fish.fin(mb, b, e, fc, rows=1, th0=0.008, th1=0.003, normal=(1, 0, 0))
    # small pelvic fins at the tail base
    for s in (1, -1):
        b = [(s * 0.04, 0.04 + 0.08 * k / 4, -0.01) for k in range(5)]
        e = [(s * (0.10 + 0.02 * math.sin(math.pi * k / 4)), 0.08 + 0.08 * k / 4, -0.015) for k in range(5)]
        fish.fin(mb, b, e, fc, rows=1, th0=0.008, th1=0.003)
        # eyes on top, looking up
        z = top_z(Vector((s * 0.09, -0.62)), 0.2)
        mb.add(nh.uv_ellipsoid((s * 0.09, -0.62, z - 0.004), (0.035, 0.040, 0.014), 10, 5), SKIN_DARK)
        ef.eye(mb, (s * 0.09, -0.62, z + 0.004), (s * 0.35, -0.2, 0.9), 0.024, iris=(0.70, 0.60, 0.30))
    pts = [(x, -0.795 + 0.6 * x * x, 0.004) for x in [-0.07 + 0.14 * k / 6 for k in range(7)]]
    mb.add(nh.tube(pts, [0.004] + [0.007] * 5 + [0.004], sides=5, scale_xy=(1.0, 0.5)), MOUTH)
    return df.finish(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 35), (-90, 8), (0, 80), (-150, 20)), background=df.PREVIEW["background"])
