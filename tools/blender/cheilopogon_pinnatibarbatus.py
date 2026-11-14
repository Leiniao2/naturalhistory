"""
Procedural Bennett's flying fish (Cheilopogon pinnatibarbatus) for the map.

A torpedo-shaped, round-backed body with a blunt head and big eyes, and the
flying fish's hallmark: huge wing-like pectoral fins spread flat as in a glide,
reaching back past the dorsal fin, plus enlarged fan-shaped pelvic fins set far
back on the belly (the "four-winged" Cheilopogon plan). Small low dorsal and
anal fins sit far back, and the deeply forked tail has a longer, stiffer lower
lobe, used to scull along the surface before take-off. Adult colouring:
iridescent deep blue back, bright silver flanks and white belly, smoky
blue-grey wings with darker rays and a pale trailing margin. (The fringed chin
barbels that give the species its name are only carried by juveniles, so this
adult has none.)

Usage:
  blender --background --python tools/blender/cheilopogon_pinnatibarbatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FlyingFish.fbx (map style Swim:
pivot at the body centre, facing -Y, dorsal fin up). Body ~1 long, wingspan ~1.3.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

BLUE = (0.07, 0.17, 0.42)
BLUE_SHEEN = (0.14, 0.32, 0.62)
SILVER = (0.80, 0.83, 0.87)
BELLY = (0.95, 0.95, 0.94)
WING = (0.30, 0.37, 0.48)
WING_RAY = (0.16, 0.20, 0.30)
WING_EDGE = (0.78, 0.82, 0.86)
FIN = (0.26, 0.32, 0.42)
IRIS = (0.80, 0.82, 0.85)

Y_SNOUT, TAIL_Y = -0.42, 0.31
EYE = (-0.335, 0.012)


def interp(keys, y):
    for (y0, v0), (y1, v1) in zip(keys, keys[1:]):
        if y <= y1:
            s = nh.smoothstep(y0, y1, y) if y1 > y0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


TOP = [(-0.42, 0.0), (-0.41, 0.018), (-0.36, 0.048), (-0.26, 0.072), (-0.10, 0.080), (0.05, 0.072),
       (0.18, 0.050), (0.27, 0.031), (0.32, 0.028)]
BOT = [(-0.42, 0.0), (-0.41, -0.016), (-0.36, -0.045), (-0.26, -0.068), (-0.10, -0.075), (0.05, -0.068),
       (0.18, -0.045), (0.27, -0.026), (0.32, -0.024)]
WIDTH = [(-0.42, 0.0), (-0.41, 0.016), (-0.36, 0.042), (-0.24, 0.064), (-0.06, 0.064), (0.10, 0.052),
         (0.22, 0.033), (0.32, 0.018)]


def top(y):
    return interp(TOP, y)


def bot(y):
    return interp(BOT, y)


def width(y):
    return interp(WIDTH, y)


def body_color(co):
    y, z = co.y, co.z
    zt, zb = top(y), bot(y)
    rel = (z - (zt + zb) * 0.5) / max((zt - zb) * 0.5, 1e-4)
    sheen = 0.5 + 0.5 * noise.noise(Vector((y * 18.0, z * 30.0, 0.4)))
    back = nh.lerp(BLUE, BLUE_SHEEN, sheen * 0.6)
    col = nh.lerp(SILVER, BELLY, nh.smoothstep(-0.2, -0.7, rel))
    col = nh.lerp(col, back, nh.smoothstep(0.05, 0.28, rel))
    # faint scale rows on the flank
    rows = 0.5 + 0.5 * math.sin(y * 160.0 + rel * 6.0)
    col = nh.lerp(col, (0.62, 0.68, 0.78), rows * 0.15 * (1 - nh.smoothstep(0.0, 0.3, rel)))
    # dark snout tip and a thin mouth line
    col = nh.lerp(col, BLUE, nh.smoothstep(-0.395, -0.415, y) * 0.8)
    return col


def fan(root_a, root_b, lengths, angles, z_rise, cols=25):
    """Fan of rays from a short root line: base and edge point lists for fish.fin.
    lengths/angles: functions of u (0 = front ray .. 1 = back ray); angle is measured
    back from straight out (+X), in degrees. z_rise(r) lifts or droops the fin with distance."""
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        b = Vector(root_a).lerp(Vector(root_b), u)
        a = math.radians(angles(u))
        L = lengths(u)
        e = b + Vector((math.cos(a) * L, math.sin(a) * L, 0.0))
        e.z += z_rise(L)
        base.append(tuple(b))
        edge.append(tuple(e))
    return base, edge


def mirror(base, edge, sx):
    if sx > 0:
        return base, edge
    return fish.mirror_x(base), fish.mirror_x(edge)


def ray_color(dark, light, edge_col, cols, rim=0.85):
    def color(u, v, co):
        ray = 0.5 + 0.5 * math.cos(u * (cols - 1) * math.pi)
        col = nh.lerp(light, dark, ray * 0.7 * nh.smoothstep(0.05, 0.3, v))
        return nh.lerp(col, edge_col, nh.smoothstep(rim, 1.0, v) * nh.smoothstep(0.25, 0.6, u) * 0.8)
    return color


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, Y_SNOUT, TAIL_Y + 0.01, body_color, stations=48, ring=26, close_end=False)

    # Huge wing-like pectorals, set high on the flank and spread flat with a slight dihedral
    cols = 27
    for sx in (1, -1):
        y0, y1 = -0.215, -0.155
        z0 = 0.028
        ra = (fish.surface_x(top, bot, width, y0, z0) - 0.004, y0, z0)
        rb = (fish.surface_x(top, bot, width, y1, z0) - 0.004, y1, z0)
        base, edge = fan(ra, rb,
                         lengths=lambda u: 0.56 + 0.05 * math.sin(math.pi * min(1.0, u / 0.4)) - 0.36 * nh.smoothstep(0.3, 1.0, u),
                         angles=lambda u: 16.0 + 66.0 * u,
                         z_rise=lambda r: 0.10 * r * r, cols=cols)
        base, edge = mirror(base, edge, sx)
        fish.fin(mb, base, edge, ray_color(WING_RAY, WING, WING_EDGE, cols), rows=6, th0=0.010, th1=0.003)

    # Enlarged pelvic fins far back on the belly, spread out and slightly down
    cols = 15
    for sx in (1, -1):
        y0, y1 = 0.02, 0.055
        z0 = bot(0.04) + 0.012
        ra = (fish.surface_x(top, bot, width, y0, z0) * 0.6, y0, z0)
        rb = (fish.surface_x(top, bot, width, y1, z0) * 0.6, y1, z0)
        base, edge = fan(ra, rb,
                         lengths=lambda u: 0.25 - 0.10 * nh.smoothstep(0.3, 1.0, u),
                         angles=lambda u: 22.0 + 50.0 * u,
                         z_rise=lambda r: -0.25 * r, cols=cols)
        base, edge = mirror(base, edge, sx)
        fish.fin(mb, base, edge, ray_color(WING_RAY, WING, WING_EDGE, cols, rim=0.8), rows=4, th0=0.008, th1=0.003)

    # Low dorsal fin set far back, longest rays at the rear
    base, edge = [], []
    for i in range(11):
        u = i / 10
        y = 0.03 + 0.20 * u
        base.append((0.0, y, top(y) - 0.006))
        edge.append((0.0, y + 0.03, top(y) + 0.02 + 0.035 * math.sin(math.pi * min(1.0, u * 1.25)) ** 0.8))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(BLUE, FIN, v), rows=3, th0=0.008, th1=0.003)

    # Small anal fin opposite the rear of the dorsal
    base, edge = [], []
    for i in range(8):
        u = i / 7
        y = 0.10 + 0.13 * u
        base.append((0.0, y, bot(y) + 0.006))
        edge.append((0.0, y + 0.025, bot(y) - 0.015 - 0.025 * math.sin(math.pi * min(1.0, u * 1.2)) ** 0.8))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(SILVER, (0.6, 0.65, 0.72), v), rows=3, th0=0.008, th1=0.003)

    # Deeply forked tail, the lower lobe longer and stiffer
    up_tip, notch, lo_tip = (0.0, 0.53, 0.17), (0.0, 0.40, -0.01), (0.0, 0.64, -0.23)
    base, edge = [], []
    n = 17
    for i in range(n):
        u = i / (n - 1)
        base.append((0.0, TAIL_Y, -0.024 + 0.05 * u))
        if u < 0.5:
            p = fish.bezier(lo_tip, (0.0, 0.47, -0.10), notch, u / 0.5)
        else:
            p = fish.bezier(notch, (0.0, 0.45, 0.08), up_tip, (u - 0.5) / 0.5)
        edge.append(tuple(p))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(nh.lerp(BLUE, FIN, v), WING_RAY, nh.smoothstep(0.7, 1.0, v) * 0.6),
             rows=6, th0=0.014, th1=0.003)

    ex = fish.surface_x(top, bot, width, *EYE)
    fish.eyes(mb, EYE[0], EYE[1], ex, 0.024, IRIS)

    return mb.to_object("FlyingFish", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "FlyingFish", background=(0.04, 0.10, 0.13),
           views=((35, 25), (-90, 4), (30, 50), (0, 89), (160, -30)))
