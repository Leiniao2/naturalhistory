"""
Procedural Thoracopterus magnificus (Late Triassic gliding ray-finned fish, ~10 cm).

One of the oldest "flying fish", from the Alps of Austria and Italy, over 220 million years
before the modern ones: a small, slim, silvery fish with huge wing-like pectoral fins and a
second, smaller pair of pelvic "wings", and a deeply forked tail whose lower lobe is longer,
used to taxi over the surface before gliding. Painted blue-black above, silver below with
dusky fins. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Thoracopterus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402


BACK = (0.10, 0.16, 0.30)
FLANK = (0.66, 0.72, 0.78)
BELLY = (0.94, 0.95, 0.96)
FIN = (0.60, 0.66, 0.74)
FIN_EDGE = (0.18, 0.22, 0.32)

OUT = jf.Outline([(-0.50, -0.005, -0.020, 0.012), (-0.46, 0.030, -0.050, 0.035), (-0.36, 0.070, -0.070, 0.052),
                  (-0.20, 0.085, -0.080, 0.056), (0.00, 0.075, -0.070, 0.046), (0.20, 0.050, -0.048, 0.030),
                  (0.32, 0.032, -0.032, 0.018), (0.38, 0.026, -0.030, 0.014)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.004, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.6, 0.0, z))
    return nh.lerp(c, BACK, nh.smoothstep(0.25, 0.65, z))


def wing_col(u, v, co):
    c = nh.lerp(FIN, FIN_EDGE, nh.smoothstep(0.4, 1.0, v))
    rays = 0.5 + 0.5 * math.sin(u * 60.0)
    return nh.lerp(c, FIN_EDGE, 0.25 * rays)


def fin_col(u, v, co):
    return nh.lerp(FIN, FIN_EDGE, v * 0.7)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=70, ring=24)
    # huge pectoral "wings", spread out and swept back
    jf.pairfin(mb, [(0.04, -0.34, -0.02), (0.04, -0.30, -0.025), (0.04, -0.26, -0.03), (0.04, -0.23, -0.03)],
               [(0.36, -0.26, 0.03), (0.62, -0.12, 0.03), (0.58, 0.02, 0.02), (0.36, 0.06, 0.0)], wing_col,
               th0=0.010, th1=0.003)
    # smaller pelvic wings
    jf.pairfin(mb, [(0.03, 0.02, -0.05), (0.03, 0.05, -0.048), (0.03, 0.08, -0.045)],
               [(0.18, 0.06, -0.05), (0.26, 0.15, -0.05), (0.16, 0.20, -0.05)], wing_col, th0=0.008, th1=0.003)
    # small dorsal, deeply forked tail with the lower lobe longer
    jf.midfin(mb, [(0.12, OUT.top(0.12) - 0.004), (0.22, OUT.top(0.22) - 0.004)],
              [(0.18, OUT.top(0.12) + 0.05), (0.25, OUT.top(0.22) + 0.01)], fin_col, th0=0.010)
    jf.midfin(mb, [(0.36, 0.022), (0.37, -0.002), (0.36, -0.026)], [(0.62, 0.16), (0.44, -0.004), (0.70, -0.24)],
              fin_col, th0=0.010)
    fish.eyes(mb, -0.40, 0.02, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.40, 0.02), 0.026, (0.85, 0.85, 0.80))
    return kit.finish(mb, "Thoracopterus", pivot="center", roughness=0.3)


if __name__ == "__main__":
    nh.run(build, "Thoracopterus", **fish.PREVIEW)
