"""
Procedural Atractosteus simplex (early Eocene gar, Green River lakes of Wyoming) for map colonies.
A gar about 1 m long: a long, nearly cylindrical body sheathed in thick, shiny, diamond-shaped
ganoid scales in diagonal rows, a long narrow snout lined with needle teeth, and the dorsal and
anal fins set far back near the rounded tail, like living alligator gars. Olive-brown back with
dark spots, bronze flanks, pale belly.
Built with nh_jur_fish (nh_fish). Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/atractosteus_simplex.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AtractosteusSimplex.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402
from mathutils import noise, Vector  # noqa: E402

BACK = (0.22, 0.24, 0.13)
SCALE = (0.55, 0.46, 0.24)
BELLY = (0.86, 0.82, 0.66)
RIM = (0.14, 0.12, 0.07)
SPOT = (0.10, 0.09, 0.06)
FIN = (0.36, 0.30, 0.18)
TOOTH = (0.92, 0.89, 0.80)

OUT = jf.Outline([(-0.98, 0.0, -0.012, 0.008), (-0.95, 0.014, -0.016, 0.016), (-0.8, 0.02, -0.022, 0.022),
                  (-0.66, 0.035, -0.035, 0.035), (-0.56, 0.07, -0.06, 0.055), (-0.45, 0.085, -0.08, 0.07),
                  (-0.2, 0.09, -0.09, 0.075), (0.1, 0.085, -0.085, 0.07), (0.35, 0.065, -0.06, 0.05),
                  (0.52, 0.04, -0.035, 0.03), (0.6, 0.035, -0.03, 0.022), (0.64, 0.035, -0.03, 0.018)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.005, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, SCALE, nh.smoothstep(-0.7, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.25, 0.85, z))
    if co.y > -0.52:
        f = 46.0
        a = math.sin((co.y + co.z * 1.4) * f)
        b = math.sin((co.y - co.z * 1.4) * f)
        c = nh.lerp(RIM, c, nh.smoothstep(0.05, 0.3, min(abs(a), abs(b))))
        if z > -0.3 and noise.noise(Vector((co.x * 9, co.y * 9, co.z * 9))) > 0.32:
            c = nh.lerp(c, SPOT, 0.8)
    else:
        c = tuple(v * 0.8 for v in c)
        if co.y < -0.6 and noise.noise(Vector((co.x * 20, co.y * 20, co.z * 20))) > 0.3:
            c = nh.lerp(c, SPOT, 0.7)
    return c


def fin_col(u, v, co):
    c = nh.lerp(FIN, (0.2, 0.17, 0.1), v * 0.6)
    if noise.noise(Vector((co.x * 25, co.y * 25, co.z * 25))) > 0.25:
        c = nh.lerp(c, SPOT, 0.7)
    return c


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=140, ring=36)
    # dorsal and anal fins far back, opposite each other
    jf.midfin(mb, [(0.34, OUT.top(0.34) - 0.008), (0.48, OUT.top(0.48) - 0.008)],
              [(0.42, OUT.top(0.34) + 0.09), (0.54, OUT.top(0.48) + 0.03)], fin_col)
    jf.midfin(mb, [(0.3, OUT.bot(0.3) + 0.008), (0.46, OUT.bot(0.46) + 0.008)],
              [(0.4, OUT.bot(0.3) - 0.1), (0.52, OUT.bot(0.46) - 0.03)], fin_col)
    # rounded, slightly asymmetric tail
    base = [(0.57, 0.045), (0.59, 0.03), (0.61, 0.01), (0.62, -0.01), (0.62, -0.03)]
    edge = [(0.66, 0.12), (0.76, 0.115), (0.83, 0.04), (0.81, -0.05), (0.7, -0.1)]
    jf.midfin(mb, base, edge, fin_col, th0=0.018)
    jf.pairfin(mb, [(0.06, -0.47, -0.06), (0.06, -0.42, -0.065)], [(0.15, -0.36, -0.13), (0.12, -0.32, -0.12)], fin_col)
    jf.pairfin(mb, [(0.05, 0.0, -0.08), (0.05, 0.07, -0.075)], [(0.11, 0.1, -0.14), (0.09, 0.14, -0.12)], fin_col)
    # needle teeth along both jaws of the long snout
    rows = []
    for k in range(10):
        y = -0.93 + k * 0.035
        w = OUT.width(y) * 0.95
        for sx in (1, -1):
            rows.append([(sx * w, y, -0.002), (sx * w * 1.05, y - 0.004, -0.016)])
            rows.append([(sx * w, y + 0.017, -0.004), (sx * w * 1.05, y + 0.013, 0.01)])
    for a, b in rows:
        mb.add(kit.cone(Vector(a), Vector(b), 0.0035, sides=4), TOOTH)
    # mouth line
    for sx in (1, -1):
        pts = [(sx * (OUT.width(y) + 0.001), y, -0.004) for y in (-0.96, -0.85, -0.72, -0.6, -0.56)]
        mb.add(nh.tube(pts, [0.003] * len(pts), sides=4), RIM)
    fish.eyes(mb, -0.6, 0.015, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.6, 0.015), 0.016, (0.85, 0.7, 0.35))
    return kit.finish(mb, "AtractosteusSimplex", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "AtractosteusSimplex", **fish.PREVIEW)
