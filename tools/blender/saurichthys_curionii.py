"""
Procedural Saurichthys curionii (Middle Triassic ray-finned fish, ~50 cm) for map colonies.

A slim ambush hunter shaped like a modern garfish or barracuda, from Monte San Giorgio:
a long, needle-like beak of a snout (about a quarter of its length) lined with small
teeth, a slender body with rows of bony scutes, the dorsal and anal fins set far back
opposite each other for a sudden lunge, and a symmetrical forked tail. Painted grey-green
above, silver below. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Saurichthys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402


BACK = (0.20, 0.26, 0.22)
FLANK = (0.56, 0.60, 0.56)
BELLY = (0.90, 0.90, 0.86)
SCUTE = (0.14, 0.17, 0.15)
FIN = (0.36, 0.40, 0.34)

OUT = jf.Outline([(-0.95, 0.004, -0.004, 0.003), (-0.80, 0.010, -0.012, 0.008), (-0.65, 0.022, -0.024, 0.016),
                  (-0.56, 0.040, -0.038, 0.030), (-0.46, 0.058, -0.052, 0.040), (-0.25, 0.066, -0.060, 0.044),
                  (0.00, 0.066, -0.060, 0.042), (0.25, 0.056, -0.052, 0.034), (0.42, 0.040, -0.040, 0.024),
                  (0.54, 0.024, -0.024, 0.014), (0.60, 0.018, -0.018, 0.010), (0.63, 0.016, -0.016, 0.008)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.004, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.1, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.8, z))
    if co.y > -0.45:   # rows of scutes along the back, the midflank and the belly
        for zr in (0.85, 0.0, -0.8):
            if abs(z - zr) < 0.12:
                c = nh.lerp(c, SCUTE, 0.5 * (0.5 + 0.5 * math.sin(co.y * 120.0)))
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.20, 0.22, 0.18), v * 0.6)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=120, ring=24)
    jf.midfin(mb, [(0.30, OUT.top(0.30) - 0.005), (0.44, OUT.top(0.44) - 0.005)],
              [(0.38, OUT.top(0.30) + 0.09), (0.47, OUT.top(0.44) + 0.02)], fin_col)
    jf.midfin(mb, [(0.30, OUT.bot(0.30) + 0.005), (0.44, OUT.bot(0.44) + 0.005)],
              [(0.38, OUT.bot(0.30) - 0.09), (0.47, OUT.bot(0.44) - 0.02)], fin_col)
    jf.midfin(mb, [(0.60, 0.014), (0.62, 0.0), (0.60, -0.014)], [(0.82, 0.15), (0.70, 0.0), (0.82, -0.15)],
              fin_col, th0=0.012)
    jf.pairfin(mb, [(0.035, -0.42, -0.03), (0.035, -0.38, -0.035)], [(0.11, -0.30, -0.07), (0.08, -0.30, -0.06)], fin_col)
    for sx in (1, -1):   # mouth line along the beak
        pts = [(sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, -0.002) + 0.0015), y, -0.002)
               for y in (-0.93, -0.80, -0.68, -0.58, -0.52)]
        mb.add(nh.tube(pts, [0.0025] * len(pts), sides=4), SCUTE)
    fish.eyes(mb, -0.50, 0.015, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.50, 0.015), 0.016, (0.85, 0.75, 0.40))
    return kit.finish(mb, "Saurichthys", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Saurichthys", **fish.PREVIEW)
