"""
Procedural Lotosaurus adentus (Middle Triassic poposauroid pseudosuchian, ~2.5 m).

A toothless, sail-backed relative of crocodiles from Hunan, China: a short head ending in
a sharp horny beak (the name means "toothless"), a long neck, a deep body carrying a tall
sail of long spines over the back and hips, a long tail and upright legs. Built with
nh_tri_tetrapod; painted ochre with a rust-red, banded sail. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Lotosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


BEAK = (0.26, 0.22, 0.16)
SAIL = (0.62, 0.24, 0.12)
SAIL_DARK = (0.30, 0.12, 0.07)


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.460, 0.006, 0.010),
    (-0.97, 0.468, 0.018, 0.026),
    (-0.92, 0.480, 0.030, 0.040),
    (-0.86, 0.490, 0.040, 0.046),
    (-0.81, 0.488, 0.034, 0.040),
    (-0.74, 0.465, 0.034, 0.040),
    (-0.64, 0.440, 0.046, 0.054),
    (-0.52, 0.420, 0.080, 0.096),
    (-0.34, 0.420, 0.110, 0.122),
    (-0.14, 0.425, 0.112, 0.120),
    (0.04, 0.430, 0.094, 0.100),
    (0.18, 0.420, 0.062, 0.066),
    (0.38, 0.385, 0.038, 0.040, sway(0.38)),
    (0.62, 0.330, 0.022, 0.022, sway(0.62)),
    (0.86, 0.280, 0.010, 0.010, sway(0.86)),
    (1.00, 0.255, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.08, -0.42, 0.40), (0.11, -0.40, 0.24), (0.11, -0.44, 0.07), (0.11, -0.46, 0.014)],
               radii=[0.040, 0.030, 0.022, 0.018], toes=5, toe_len=0.035, toe_r=0.009, toe_spread=55,
               stride=10, claw_len=0.014)
HIND = tt.Limb(pts=[(0.085, 0.06, 0.44), (0.11, -0.02, 0.27), (0.11, 0.08, 0.08), (0.11, 0.04, 0.014)],
               radii=[0.060, 0.040, 0.027, 0.020], toes=4, toe_len=0.050, toe_r=0.011, toe_spread=50,
               stride=-10, claw_len=0.016)


def sail_h(y):
    """Sail height above the back: rising over the shoulders, tallest over the hips."""
    import math
    if y < -0.50 or y > 0.30:
        return 0.0
    t = (y + 0.50) / 0.80
    return 0.24 * math.sin(math.pi * t) ** 0.8


def sail(b, spec):
    pts = []
    n = 24
    for i in range(n + 1):
        y = -0.50 + 0.80 * i / n
        top = tt.Vector((0.0, y, 0.50 + sail_h(y)))
        pts.append(top)
    pts += [tt.Vector((0.0, 0.30, 0.47)), tt.Vector((0.0, -0.50, 0.47))]
    b.add(tt.panel(pts, 0.022), spec.flank)


def paint_extra(co, n, c, spec):
    c = nh.lerp(c, BEAK, nh.smoothstep(-0.94, -0.97, co.y))
    if co.z > 0.56 and -0.52 < co.y < 0.32:
        k = nh.smoothstep(0.56, 0.60, co.z)
        stripe = 0.5 + 0.5 * tt.math.sin(co.y * 70.0)
        sc = nh.lerp(SAIL, SAIL_DARK, nh.smoothstep(0.6, 0.9, stripe))
        c = nh.lerp(c, sc, k)
    return c


SPEC = tt.TetrapodSpec(
    name="Lotosaurus",
    axis=AXIS,
    blobs=[((0.07, 0.05, 0.42), (0.055, 0.12, 0.10), 25)],
    limbs=[FORE, HIND],
    voxel=0.009, max_tris=12000,
    mouth=(-0.995, -0.86, 0.456, 0.470, 0.003),
    eyes=(-0.855, 0.505, 0.0145, (0.80, 0.55, 0.12)),
    nostrils=(-0.95, 0.48),
    back=(0.44, 0.30, 0.14), flank=(0.70, 0.54, 0.30), belly=(0.92, 0.84, 0.64),
    paint_extra=paint_extra,
    pre=sail,
)

if __name__ == "__main__":
    tt.run(SPEC)
