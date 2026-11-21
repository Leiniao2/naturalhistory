"""
Procedural orca or killer whale (Orcinus orca, Pleistocene to today, all oceans)
for map colonies.

The largest dolphin, males up to about 8-9 m and 6 tonnes, a top predator that
hunts in family pods and takes fish, seals, penguins and even great white sharks
and whale calves. A heavy, rounded body with a blunt, beakless head, a very tall,
straight-edged dorsal fin (up to 1.8 m in males), big rounded paddle-shaped
flippers and broad flukes. Glossy black with a white oval patch behind each eye,
a white chin and belly that sends white lobes up the flanks behind the dorsal
fin, and a grey "saddle" behind the fin.

Reuses the dolphin loft from delphinus_delphis.py with orca proportions, fins
and colours. Pivot at the body centre, faces -Y, dorsal fin up (+Z).

Usage:
  blender --background --python tools/blender/orcinus_orca.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OrcinusOrca.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import delphinus_delphis as dd  # noqa: E402

BLACK = (0.03, 0.03, 0.04)
WHITE = (0.95, 0.95, 0.94)
SADDLE = (0.50, 0.51, 0.54)

# stocky body, blunt rounded head with no beak (Y_TIP -1 .. tail stock 0.80)
dd.HALF_W = [(-1.0, 0.02), (-0.97, 0.07), (-0.92, 0.11), (-0.84, 0.15), (-0.72, 0.185), (-0.50, 0.215),
             (-0.25, 0.225), (0.0, 0.21), (0.20, 0.175), (0.40, 0.12), (0.60, 0.065), (0.72, 0.040), (0.80, 0.032)]
dd.HALF_H_TOP = [(-1.0, 0.02), (-0.97, 0.06), (-0.92, 0.10), (-0.84, 0.15), (-0.72, 0.19), (-0.50, 0.22),
                 (-0.25, 0.235), (0.0, 0.22), (0.20, 0.19), (0.40, 0.14), (0.60, 0.10), (0.72, 0.07), (0.80, 0.04)]
dd.HALF_H_BOT = [(-1.0, 0.02), (-0.97, 0.05), (-0.92, 0.09), (-0.84, 0.14), (-0.72, 0.18), (-0.50, 0.21),
                 (-0.25, 0.22), (0.0, 0.20), (0.20, 0.16), (0.40, 0.11), (0.60, 0.075), (0.72, 0.05), (0.80, 0.035)]
dd.CENTER_Z = [(-1.0, -0.04), (-0.85, -0.02), (-0.60, 0.0), (0.8, 0.0)]
dd.Y_MELON = -2.0   # no beak


def dorsal():
    """Very tall, nearly triangular male dorsal fin with a straight trailing edge."""
    base_z = lambda y: dd.zc(y) + dd.ht(y) - 0.05  # noqa: E731
    front, back = (-0.30, base_z(-0.30)), (0.02, base_z(0.02))
    apex = (-0.14, dd.ht(-0.15) + 0.50)
    pts = [front] + dd.curve(front, apex, 0.02, 10) + dd.curve(apex, back, -0.02, 10) + [back]
    pts += dd.curve(back, front, 0.0, 4)[1:]
    th = [0.08 - 0.05 * min(1.0, max(0.0, (v - dd.ht(-0.15)) / 0.5)) for _u, v in pts]
    return dd.fin_slab(pts, th, lambda u, v: (Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))))


def flipper(sign):
    """Big, rounded, paddle-shaped pectoral flipper."""
    droop, sweep = math.radians(35), 0.55
    def frame(u, v):
        x = sign * (dd.w(u) * 0.75 + v * math.cos(droop))
        z = dd.zc(u) - dd.hb(u) * 0.55 - v * math.sin(droop)
        return Vector((x, u + v * sweep, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    a, b = (-0.66, 0.0), (-0.48, 0.0)
    tip = (-0.56, 0.30)
    pts = [a] + dd.curve(a, tip, 0.22, 9) + dd.curve(tip, b, 0.22, 9) + [b]
    th = [0.06 - 0.03 * min(1.0, v / 0.30) for _u, v in pts]
    return dd.fin_slab(pts, th, frame)


def flukes():
    half = [(0.0, 0.72), (0.05, 0.76)] + dd.curve((0.05, 0.76), (0.38, 0.97), -0.08, 9) \
        + dd.curve((0.38, 0.97), (0.03, 0.93), -0.04, 8) + [(0.03, 0.93), (0.0, 0.91)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    th = [0.06 - 0.03 * min(1.0, abs(x) / 0.38) for x, _y in pts]
    return dd.fin_slab(pts, th, lambda u, v: (Vector((u, v, dd.zc(dd.Y_PED))), Vector((0.0, 0.0, 1.0))))


def ell(p, c, r):
    """Inside-ness (0..1) of side-view point p=(y, rel_z) in an ellipse centre c, radii r."""
    d = math.sqrt(((p[0] - c[0]) / r[0]) ** 2 + ((p[1] - c[1]) / r[1]) ** 2)
    return 1.0 - nh.smoothstep(0.85, 1.05, d)


def body_color(p, n):
    y = p.y
    if dd.outside(p) > 0.012 or y > dd.Y_PED + 0.02:
        # fins black; the underside of the flukes white
        if y > dd.Y_PED and n.z < -0.3:
            return nh.lerp(BLACK, WHITE, 0.8)
        return BLACK
    r = dd.rel_z(p)
    col = BLACK
    # white chin, throat and belly band, narrowing between the flippers
    belly = -0.55 + 0.15 * nh.smoothstep(-0.6, -0.3, y) - 0.2 * nh.smoothstep(0.35, 0.7, y)
    if y < -0.55:
        belly = -0.35
    k = 1.0 - nh.smoothstep(belly - 0.05, belly + 0.05, r)
    if -0.5 < y < -0.25:   # black between the flippers
        k *= nh.smoothstep(0.08, 0.25, abs(p.x) / max(dd.w(y), 1e-3)) * 0.2 + 0.8 * (r < -0.85)
    # white flank lobe sweeping up behind the dorsal fin
    k = max(k, ell((y, r), (0.25, -0.25), (0.20, 0.35)))
    # white eye patch above and behind the eye
    k = max(k, ell((y, r), (-0.67, 0.24), (0.10, 0.16)))
    col = nh.lerp(col, WHITE, k)
    # grey saddle behind the dorsal fin
    s = ell((y, r), (0.08, 0.95), (0.16, 0.25)) * (n.z > 0.3)
    col = nh.lerp(col, SADDLE, 0.8 * s)
    return nh.lerp(col, nh.lerp(col, BLACK, 0.3), 0.15 * max(0.0, noise.noise(p * 12.0)))


dd.dorsal, dd.flipper, dd.flukes, dd.body_color = dorsal, flipper, flukes, body_color


def build():
    obj = dd.build()
    obj.name = "OrcinusOrca"
    return obj


if __name__ == "__main__":
    nh.run(build, "OrcinusOrca", background=(0.05, 0.18, 0.24), views=((35, 25), (-90, 4), (30, 62)))
