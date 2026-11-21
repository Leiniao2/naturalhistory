"""
Procedural Whiteia woodwardi (Early Triassic coelacanth, ~25 cm) for map colonies.

A coelacanth from the coastal seas of Madagascar, about 250 million years ago: a deep
body, a large head with a big mouth, two dorsal fins (the second on a fleshy lobe), fleshy
lobed pectoral, pelvic and anal fins, and the three-lobed coelacanth tail with a small
middle tuft. Painted steel blue with pale spots, like its living relative Latimeria.
Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Whiteia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402


from mathutils import Vector, noise  # noqa: E402

BACK = (0.12, 0.18, 0.28)
FLANK = (0.26, 0.36, 0.48)
BELLY = (0.62, 0.68, 0.74)
SPOT = (0.86, 0.88, 0.86)
FIN = (0.22, 0.30, 0.40)

OUT = jf.Outline([(-0.62, 0.000, -0.060, 0.020), (-0.58, 0.080, -0.110, 0.060), (-0.46, 0.160, -0.160, 0.095),
                  (-0.26, 0.200, -0.180, 0.100), (-0.02, 0.190, -0.170, 0.090), (0.20, 0.130, -0.120, 0.064),
                  (0.38, 0.070, -0.068, 0.036), (0.50, 0.040, -0.040, 0.022), (0.66, 0.012, -0.012, 0.010)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.004, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.8, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.9, z))
    return c


def spots(mb):
    """Irregular pale blotches on both flanks, as crisp flat discs on the skin."""
    import random
    rng = random.Random(7)
    for _ in range(26):
        y = rng.uniform(-0.38, 0.40)
        zt, zb = OUT.top(y), OUT.bot(y)
        z = zb + (zt - zb) * rng.uniform(0.15, 0.85)
        r = rng.uniform(0.012, 0.022) * (1.0 - 0.5 * max(0.0, y) / 0.4)
        for sx in (1, -1):
            x = fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z)
            mb.add(nh.ellipsoid((sx * x, y, z), (0.004, r, r * 0.8), subdivisions=2), SPOT)


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.10, 0.14, 0.20), v * 0.6)


def lobe(mb, root, tip):
    r, t = Vector(root), Vector(tip)
    mb.add(nh.tube([r, r.lerp(t, 0.5), t], [0.028, 0.022, 0.010], sides=8, scale_xy=(0.6, 1.0)), FLANK)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=90, ring=30)
    # first dorsal (rayed) and second dorsal on a lobe
    jf.midfin(mb, [(-0.20, OUT.top(-0.20) - 0.01), (-0.06, OUT.top(-0.06) - 0.01)],
              [(-0.10, OUT.top(-0.20) + 0.16), (-0.02, OUT.top(-0.06) + 0.04)], fin_col)
    lobe(mb, (0, 0.20, OUT.top(0.20) - 0.01), (0, 0.27, OUT.top(0.20) + 0.06))
    jf.midfin(mb, [(0.22, OUT.top(0.20) + 0.03), (0.28, OUT.top(0.20) + 0.06)],
              [(0.30, OUT.top(0.20) + 0.12), (0.34, OUT.top(0.20) + 0.08)], fin_col)
    lobe(mb, (0, 0.20, OUT.bot(0.20) + 0.01), (0, 0.27, OUT.bot(0.20) - 0.06))
    jf.midfin(mb, [(0.22, OUT.bot(0.20) - 0.03), (0.28, OUT.bot(0.20) - 0.06)],
              [(0.30, OUT.bot(0.20) - 0.12), (0.34, OUT.bot(0.20) - 0.08)], fin_col)
    # three-lobed tail: upper and lower lobes plus a small middle tuft
    jf.midfin(mb, [(0.40, OUT.top(0.40) - 0.004), (0.60, OUT.top(0.60) - 0.002)],
              [(0.56, 0.20), (0.70, 0.04)], fin_col)
    jf.midfin(mb, [(0.40, OUT.bot(0.40) + 0.004), (0.60, OUT.bot(0.60) + 0.002)],
              [(0.56, -0.20), (0.70, -0.04)], fin_col)
    jf.midfin(mb, [(0.64, 0.008), (0.66, 0.0), (0.64, -0.008)], [(0.76, 0.03), (0.80, 0.0), (0.76, -0.03)], fin_col)
    # lobed pectoral and pelvic fins
    for sx in (1, -1):
        for root, tip in (((sx * 0.07, -0.36, -0.06), (sx * 0.18, -0.24, -0.12)),
                          ((sx * 0.06, -0.02, -0.15), (sx * 0.12, 0.08, -0.22))):
            lobe(mb, root, tip)
            r, t = Vector(root), Vector(tip)
            d = (t - r)
            fish.fin(mb, [r.lerp(t, 0.4), t], [t + Vector((0, 0.03, 0.03)), t + d * 0.6], fin_col, rows=2,
                     th0=0.008, th1=0.003)
    for sx in (1, -1):   # gill cover line
        pts = [(sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.40, z) + 0.002), -0.40 + 0.03 * math.sin(k / 5 * math.pi), z)
               for k, z in enumerate([-0.14 + i * 0.05 for i in range(6)])]
        mb.add(nh.tube(pts, [0.005] * len(pts), sides=4), BACK)
    spots(mb)
    fish.eyes(mb, -0.49, 0.06, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.49, 0.06), 0.028, (0.55, 0.65, 0.55))
    return kit.finish(mb, "Whiteia", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Whiteia", **fish.PREVIEW)
