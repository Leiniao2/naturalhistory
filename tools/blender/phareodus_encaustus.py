"""
Procedural Phareodus encaustus (early Eocene bonytongue, Green River lakes of Wyoming) for map
colonies. An osteoglossid, a relative of today's arowanas, about 50 cm long: a deep, flattened,
silvery-bronze body with large scales, a big upturned mouth with a jutting lower jaw full of
pointed teeth, very long pectoral fins, and the dorsal and anal fins set far back opposite each
other in front of a rounded tail. A fast ambush hunter of smaller fish such as Knightia.
Built with nh_jur_fish (nh_fish). Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/phareodus_encaustus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhareodusEncaustus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402
from mathutils import Vector  # noqa: E402

BACK = (0.24, 0.28, 0.22)
BRONZE = (0.68, 0.55, 0.32)
SILVER = (0.80, 0.80, 0.76)
BELLY = (0.93, 0.92, 0.88)
RIM = (0.30, 0.24, 0.14)
FIN = (0.50, 0.40, 0.26)
DARK = (0.12, 0.10, 0.08)
TOOTH = (0.93, 0.90, 0.82)

OUT = jf.Outline([(-0.63, 0.1, 0.07, 0.01), (-0.6, 0.12, -0.0, 0.025), (-0.52, 0.16, -0.09, 0.045),
                  (-0.38, 0.2, -0.17, 0.06), (-0.15, 0.22, -0.2, 0.065), (0.08, 0.2, -0.19, 0.058),
                  (0.25, 0.14, -0.13, 0.042), (0.36, 0.07, -0.065, 0.025), (0.42, 0.05, -0.045, 0.018),
                  (0.45, 0.05, -0.045, 0.014)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.005, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, SILVER, nh.smoothstep(-0.8, -0.3, z))
    c = nh.lerp(c, BRONZE, nh.smoothstep(-0.2, 0.4, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.55, 0.9, z))
    if co.y > -0.4:  # large cycloid scales: rounded rims in offset rows
        f = 26.0
        a = math.sin(co.y * f + (math.sin(co.z * f) > 0) * 1.6)
        b = math.sin(co.z * f)
        c = nh.lerp(RIM, c, 0.55 + 0.45 * nh.smoothstep(0.0, 0.35, min(abs(a), abs(b)) + 0.15))
    else:
        c = nh.lerp(c, BRONZE, 0.25)
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, DARK, v * 0.55)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=90, ring=32)
    # dorsal and anal fins far back, long-based, opposite each other
    jf.midfin(mb, [(0.06, OUT.top(0.06) - 0.01), (0.2, OUT.top(0.2) - 0.01), (0.34, OUT.top(0.34) - 0.008)],
              [(0.14, OUT.top(0.06) + 0.1), (0.27, OUT.top(0.2) + 0.09), (0.4, OUT.top(0.34) + 0.03)], fin_col)
    jf.midfin(mb, [(0.0, OUT.bot(0.0) + 0.01), (0.18, OUT.bot(0.18) + 0.01), (0.34, OUT.bot(0.34) + 0.008)],
              [(0.08, OUT.bot(0.0) - 0.1), (0.25, OUT.bot(0.18) - 0.1), (0.4, OUT.bot(0.34) - 0.03)], fin_col)
    # rounded tail
    base = [(0.42, 0.05), (0.44, 0.02), (0.45, 0.0), (0.44, -0.02), (0.42, -0.045)]
    edge = [(0.5, 0.17), (0.62, 0.13), (0.67, 0.0), (0.62, -0.13), (0.5, -0.17)]
    jf.midfin(mb, base, edge, fin_col, th0=0.016)
    # very long pectorals sweeping back along the belly
    jf.pairfin(mb, [(0.045, -0.43, -0.11), (0.045, -0.38, -0.13)], [(0.13, -0.12, -0.22), (0.12, -0.04, -0.26)], fin_col)
    jf.pairfin(mb, [(0.03, -0.1, -0.19), (0.03, -0.05, -0.19)], [(0.08, 0.04, -0.27), (0.07, 0.06, -0.25)], fin_col)
    # big upturned mouth: steep gape line, jutting lower jaw with teeth
    for sx in (1, -1):
        pts = []
        for k in range(6):
            t = k / 5
            y, z = -0.62 + t * 0.12, 0.09 - t * 0.12
            pts.append((sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) + 0.003), y, z))
        mb.add(nh.tube(pts, [0.009] * 6, sides=5), DARK)
        # gill cover
        pts = []
        for k in range(7):
            z = -0.15 + k * 0.045
            y = -0.4 + 0.035 * math.sin(k / 6 * math.pi)
            pts.append((sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) + 0.002), y, z))
        mb.add(nh.tube(pts, [0.005] * len(pts), sides=4), RIM)
        for k in range(4):
            y, z = -0.61 + k * 0.03, 0.08 - k * 0.03
            x = sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) * 0.8)
            mb.add(kit.cone(Vector((x, y, z)), Vector((x * 1.05, y - 0.012, z + 0.022)), 0.005, sides=4), TOOTH)
    fish.eyes(mb, -0.5, 0.1, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.5, 0.1), 0.028, (0.9, 0.78, 0.4))
    return kit.finish(mb, "PhareodusEncaustus", pivot="center", roughness=0.3)


if __name__ == "__main__":
    nh.run(build, "PhareodusEncaustus", **fish.PREVIEW)
