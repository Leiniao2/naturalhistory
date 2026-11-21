"""
Procedural Dapedium politum (Early Jurassic dapediid fish, England and Germany) for map colonies.

A deep-bodied, almost disc-shaped ray-finned fish about 35 cm long, like a Jurassic
butterflyfish or bream: a nearly round outline, a small mouth with peg-like and button teeth
for crushing hard-shelled prey, a large eye, long low dorsal and anal fins running along the
back and belly, and a short tail stalk with a squarish tail fin. Its whole body was armoured
with thick, shiny, rhombic ganoid scales. Painted dark bronze with glossy, dark-rimmed
scales, a paler belly and dusky fins. Built with nh_jur_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/dapedium_politum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dapedium.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402

BACK = (0.18, 0.16, 0.12)
SCALE = (0.50, 0.40, 0.22)
BELLY = (0.80, 0.72, 0.52)
RIM = (0.10, 0.08, 0.05)
FIN = (0.22, 0.18, 0.12)

OUT = jf.Outline([(-0.5, 0.0, -0.04, 0.01), (-0.47, 0.08, -0.1, 0.05), (-0.38, 0.28, -0.26, 0.09), (-0.2, 0.42, -0.4, 0.11),
                  (0.0, 0.45, -0.43, 0.11), (0.18, 0.38, -0.36, 0.09), (0.32, 0.2, -0.18, 0.06), (0.42, 0.08, -0.07, 0.03),
                  (0.48, 0.06, -0.05, 0.02), (0.5, 0.06, -0.05, 0.018)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.01, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, SCALE, nh.smoothstep(-0.8, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.9, z))
    if co.y > -0.36:
        f = 30.0
        a = math.sin((co.y + co.z * 0.6) * f)
        b = math.sin((co.y - co.z * 0.6) * f)
        c = nh.lerp(RIM, c, nh.smoothstep(0.05, 0.3, min(abs(a), abs(b))))
    else:
        c = tuple(v * 0.8 for v in c)
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.10, 0.08, 0.06), v * 0.7)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=120, ring=44)
    # long low dorsal and anal fins
    jf.midfin(mb, [(-0.12, OUT.top(-0.12) - 0.01), (0.36, OUT.top(0.36) - 0.01)], [(-0.05, OUT.top(-0.12) + 0.07), (0.42, OUT.top(0.36) + 0.1)], fin_col)
    jf.midfin(mb, [(0.0, OUT.bot(0.0) + 0.01), (0.36, OUT.bot(0.36) + 0.01)], [(0.05, OUT.bot(0.0) - 0.06), (0.42, OUT.bot(0.36) - 0.09)], fin_col)
    jf.midfin(mb, [(0.47, 0.06), (0.49, 0.0), (0.5, -0.05)], [(0.68, 0.2), (0.66, 0.0), (0.68, -0.19)], fin_col, th0=0.02)
    jf.pairfin(mb, [(0.08, -0.3, -0.18), (0.08, -0.24, -0.2)], [(0.18, -0.18, -0.3), (0.14, -0.14, -0.28)], fin_col)
    jf.pairfin(mb, [(0.05, 0.05, -0.36), (0.05, 0.12, -0.33)], [(0.1, 0.16, -0.44), (0.08, 0.2, -0.4)], fin_col)
    for sx in (1, -1):
        pts = []
        for k in range(8):
            z = -0.22 + k * 0.055
            y = -0.34 + 0.03 * math.sin(k / 7 * math.pi)
            pts.append((sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) + 0.002), y, z))
        mb.add(nh.tube(pts, [0.006] * len(pts), sides=4), RIM)
    fish.eyes(mb, -0.4, 0.07, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.4, 0.07), 0.03, (0.85, 0.70, 0.35))
    return kit.finish(mb, "Dapedium", pivot="center", roughness=0.3)


if __name__ == "__main__":
    nh.run(build, "Dapedium", **fish.PREVIEW)
