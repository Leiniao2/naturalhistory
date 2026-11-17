"""
Procedural Lepidotes gigas (Early Jurassic ginglymodian fish, Europe) for map colonies.

A heavily armoured ray-finned fish, relative of today's gars, up to about 1 m long:
a deep, spindle-shaped body covered in thick, shiny, rhombic ganoid scales set in
diagonal rows, a small mouth with rows of button-like crushing teeth for snails and
shellfish, a single dorsal fin set far back opposite the anal fin, and a nearly
symmetrical tail fin. Bronze-olive scales with dark rims, pale belly and dusky fins.
Built with nh_jur_fish (nh_fish). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/lepidotes_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lepidotes.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402

BACK = (0.30, 0.30, 0.16)
SCALE = (0.62, 0.50, 0.24)
BELLY = (0.88, 0.82, 0.62)
RIM = (0.18, 0.15, 0.08)
FIN = (0.30, 0.26, 0.18)

OUT = jf.Outline([(-0.75, -0.01, -0.03, 0.01), (-0.72, 0.04, -0.07, 0.05), (-0.6, 0.13, -0.13, 0.1), (-0.4, 0.21, -0.19, 0.12),
                  (-0.15, 0.23, -0.21, 0.12), (0.1, 0.2, -0.18, 0.1), (0.35, 0.12, -0.1, 0.06), (0.5, 0.07, -0.055, 0.035),
                  (0.6, 0.06, -0.045, 0.025), (0.63, 0.06, -0.045, 0.02)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.01, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, SCALE, nh.smoothstep(-0.7, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.9, z))
    if co.y > -0.55:  # rhombic ganoid scales in diagonal rows (head behind the gill cover is bare)
        f = 34.0
        a = math.sin((co.y + co.z) * f)
        b = math.sin((co.y - co.z) * f)
        edge = min(abs(a), abs(b))
        c = nh.lerp(RIM, c, nh.smoothstep(0.05, 0.3, edge))
    else:
        c = tuple(v * 0.85 for v in c)
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.18, 0.16, 0.12), v * 0.7)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=140, ring=48)
    # dorsal far back, opposite the anal fin
    jf.midfin(mb, [(0.1, OUT.top(0.1) - 0.01), (0.3, OUT.top(0.3) - 0.01)], [(0.15, OUT.top(0.1) + 0.12), (0.34, OUT.top(0.3) + 0.03)], fin_col)
    jf.midfin(mb, [(0.12, OUT.bot(0.12) + 0.01), (0.3, OUT.bot(0.3) + 0.01)], [(0.2, OUT.bot(0.12) - 0.1), (0.34, OUT.bot(0.3) - 0.03)], fin_col)
    # near-symmetrical caudal
    jf.midfin(mb, [(0.58, 0.05), (0.6, 0.0), (0.62, -0.04)], [(0.85, 0.24), (0.76, 0.0), (0.84, -0.22)], fin_col, th0=0.02)
    jf.pairfin(mb, [(0.08, -0.5, -0.1), (0.08, -0.4, -0.11)], [(0.2, -0.36, -0.2), (0.15, -0.3, -0.18)], fin_col)
    jf.pairfin(mb, [(0.06, -0.05, -0.17), (0.06, 0.05, -0.16)], [(0.12, 0.06, -0.25), (0.1, 0.12, -0.22)], fin_col)
    # gill cover line
    for sx in (1, -1):
        pts = []
        for k in range(7):
            z = -0.15 + k * 0.045
            y = -0.55 + 0.03 * math.sin(k / 6 * math.pi)
            pts.append((sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) + 0.002), y, z))
        mb.add(nh.tube(pts, [0.006] * len(pts), sides=4), RIM)
    fish.eyes(mb, -0.64, 0.04, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.64, 0.04), 0.022, (0.85, 0.75, 0.4))
    return kit.finish(mb, "Lepidotes", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Lepidotes", **fish.PREVIEW)
