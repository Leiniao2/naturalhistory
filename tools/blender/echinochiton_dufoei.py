"""
Procedural Echinochiton dufoei (Late Ordovician chiton, Wisconsin; the oldest chiton known
from a complete, articulated specimen) for map colonies (Fixed style).

A small chiton a few centimetres long: an oval, low body covered by a row of eight
overlapping, arched shell plates (valves) set in a fleshy girdle, like all chitons, but
with a striking extra: the valves carried rows of long, hollow spines sticking out
sideways and up, a defence against predators. It crept slowly over the sea floor on its
broad muscular foot, scraping algae and films of microbes with its rasping tongue.
Olive-brown valves with pale bands, buff girdle, pale spines. Pivot on the sea floor
(z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/echinochiton_dufoei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EchinochitonDufoei.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "EchinochitonDufoei"
VALVE = (0.44, 0.40, 0.26)
VALVE_LIGHT = (0.72, 0.66, 0.46)
GIRDLE = (0.70, 0.60, 0.44)
GIRDLE_DARK = (0.50, 0.42, 0.30)
SPINE = (0.86, 0.80, 0.64)
FOOT = (0.84, 0.66, 0.54)

LEN, WID = 0.62, 0.30   # half-length / half-width of the girdle


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.95)
    z0 = 0.03
    # foot and girdle: a low oval slab with a soft, beaded edge
    mb.add(nh.uv_ellipsoid((0, 0, z0 + 0.03), (WID * 0.85, LEN * 0.92, 0.04), 24, 10), FOOT)
    mb.add(nh.uv_ellipsoid((0, 0, z0 + 0.06), (WID, LEN, 0.05), 32, 12),
           lambda co, n: nh.lerp(GIRDLE, GIRDLE_DARK, 0.4 * nh.smoothstep(0.3, 0.8, 0.5 + 0.5 * noise.noise(co * 40))))
    # eight arched valves, overlapping like roof tiles (front over back)
    n = 8
    span = 2 * LEN * 0.86
    seg = span / n
    for i in range(n):
        y0 = -LEN * 0.86 + i * seg
        yc = y0 + seg * 0.55
        w = WID * (0.70 if 0 < i < n - 1 else 0.62) * (1.0 - 0.15 * abs(i - 3.5) / 3.5)
        L = seg * (0.75 if 0 < i < n - 1 else 0.70)
        zc = z0 + 0.09 + 0.004 * (n - i)

        def col(co, nn, yc=yc, L=L):
            t = (co.y - (yc - L)) / (2 * L)
            c = nh.lerp(VALVE, VALVE_LIGHT, 0.5 * nh.smoothstep(0.4, 1.0, abs(co.x) / WID))
            c = nh.lerp(c, VALVE_LIGHT, 0.45 * nh.smoothstep(0.8, 1.0, t))
            return c
        mb.add(nh.uv_ellipsoid((0, yc, zc), (w, L, 0.075), 20, 10,
                               deform=lambda v: 1.0 + 0.25 * max(0.0, v.z) * (1 - abs(v.x))), col)
        # spines: two or three per side on each valve, angled out, back and up
        if 0 < i < n - 1 or True:
            for sx in (-1, 1):
                for k, (fy, up, Ls) in enumerate(((-0.3, 0.55, 0.22), (0.35, 0.30, 0.26))):
                    b = Vector((sx * w * 0.80, yc + fy * L, zc + 0.03))
                    d = Vector((sx * 1.0, 0.35 + 0.1 * k, up)).normalized()
                    mb.add(nh.tube([b, b + d * Ls * 0.5, b + d * Ls], [0.016, 0.011, 0.0], sides=5), SPINE)
    # head end of the foot peeking out in front
    mb.add(nh.ellipsoid((0, -LEN * 0.98, z0 + 0.03), (0.10, 0.05, 0.03), 2), FOOT)
    return kit.finish_fixed(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
