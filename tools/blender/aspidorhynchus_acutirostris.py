"""
Procedural Aspidorhynchus acutirostris (Late Jurassic aspidorhynchid fish, Solnhofen, Germany)
for map colonies.

A slim, fast predatory fish about 60 cm long, shaped like a garfish or needlefish: a very
long, pointed snout in which the upper jaw runs well past the shorter lower jaw, a long,
torpedo-shaped body covered with big, shiny ganoid scales (a row of deep scales along each
flank), dorsal and anal fins set far back near the forked tail. Painted steel-blue back,
silver flanks and a white belly. Built with nh_jur_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/aspidorhynchus_acutirostris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Aspidorhynchus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402

BACK = (0.16, 0.24, 0.32)
SILVER = (0.70, 0.74, 0.76)
BELLY = (0.94, 0.94, 0.90)
RIM = (0.30, 0.34, 0.38)
FIN = (0.30, 0.36, 0.40)

OUT = jf.Outline([(-1.0, 0.005, -0.0, 0.004), (-0.85, 0.012, -0.004, 0.008), (-0.7, 0.03, -0.02, 0.018), (-0.6, 0.06, -0.05, 0.035),
                  (-0.5, 0.085, -0.075, 0.05), (-0.3, 0.1, -0.09, 0.06), (0.0, 0.1, -0.09, 0.058), (0.3, 0.08, -0.07, 0.045),
                  (0.5, 0.045, -0.04, 0.025), (0.6, 0.03, -0.028, 0.016), (0.64, 0.03, -0.028, 0.014)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.005, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, SILVER, nh.smoothstep(-0.8, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.7, z))
    if co.y > -0.52:
        f = 40.0
        a = math.sin(co.y * f)
        b = math.sin(co.z * f * 1.4)
        c = nh.lerp(RIM, c, 0.75 + 0.25 * nh.smoothstep(0.04, 0.25, min(abs(a), abs(b))))
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.15, 0.20, 0.25), v * 0.7)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=160, ring=32)
    # lower jaw: shorter than the snout
    mb.add(nh.tube([(0, -0.5, -0.05), (0, -0.7, -0.03), (0, -0.82, -0.012)], [0.02, 0.01, 0.002], sides=8), SILVER)
    jf.midfin(mb, [(0.28, OUT.top(0.28) - 0.005), (0.42, OUT.top(0.42) - 0.005)], [(0.33, OUT.top(0.28) + 0.09), (0.46, OUT.top(0.42) + 0.02)], fin_col)
    jf.midfin(mb, [(0.3, OUT.bot(0.3) + 0.005), (0.44, OUT.bot(0.44) + 0.005)], [(0.35, OUT.bot(0.3) - 0.08), (0.48, OUT.bot(0.44) - 0.02)], fin_col)
    jf.midfin(mb, [(0.6, 0.03), (0.63, 0.0), (0.6, -0.028)], [(0.82, 0.2), (0.7, 0.0), (0.82, -0.19)], fin_col, th0=0.016)
    jf.pairfin(mb, [(0.05, -0.42, -0.06), (0.05, -0.36, -0.07)], [(0.14, -0.3, -0.12), (0.1, -0.28, -0.11)], fin_col)
    jf.pairfin(mb, [(0.04, 0.05, -0.08), (0.04, 0.1, -0.08)], [(0.08, 0.12, -0.13), (0.06, 0.15, -0.12)], fin_col)
    fish.eyes(mb, -0.55, 0.02, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.55, 0.02), 0.018, (0.85, 0.80, 0.55))
    return kit.finish(mb, "Aspidorhynchus", pivot="center", roughness=0.3)


if __name__ == "__main__":
    nh.run(build, "Aspidorhynchus", **fish.PREVIEW)
