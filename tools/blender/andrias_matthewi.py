"""
Procedural Andrias matthewi (Matthew's giant salamander, Miocene to Pliocene of
North America, Nebraska to Florida) for map colonies (Swim style).

A cryptobranchid giant salamander about 2.3 m long, a close relative of the living
Chinese and Japanese giant salamanders: a very flat, broad, rounded head with a wide
mouth and tiny lidless eyes far forward on top, a long, flattened body with loose,
wrinkled skin folds running along both flanks (they breathe partly through the skin),
short, stubby, splayed legs with blunt toes and a tail compressed into a deep
paddle with a fin-like keel. Mottled olive-brown with darker blotches, paler below.
Built with the shared tetrapod recipe (nh_tri_tetrapod.py), like
mastodonsaurus_giganteus.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/andrias_matthewi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AndriasMatthewi.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.08 * s * s


# (y, z, half-width, half-height[, x]) snout -> tail tip
AXIS = [
    (-1.00, 0.000, 0.060, 0.020),
    (-0.97, 0.000, 0.120, 0.030),
    (-0.90, 0.002, 0.160, 0.040),
    (-0.80, 0.004, 0.175, 0.048),
    (-0.70, 0.006, 0.165, 0.052),
    (-0.62, 0.006, 0.130, 0.055),   # neck
    (-0.50, 0.006, 0.140, 0.062),
    (-0.30, 0.006, 0.150, 0.066),
    (-0.10, 0.006, 0.150, 0.066),
    (0.08, 0.006, 0.130, 0.062),
    (0.20, 0.006, 0.090, 0.066, sway(0.20)),
    (0.40, 0.008, 0.055, 0.085, sway(0.40)),
    (0.62, 0.010, 0.035, 0.085, sway(0.62)),
    (0.85, 0.010, 0.018, 0.060, sway(0.85)),
    (1.00, 0.010, 0.004, 0.012, sway(1.00)),
]

# loose, wrinkled skin folds along the flanks, from behind the head to the hips
FOLDS = []
for i in range(9):
    y = -0.55 + i * 0.075
    FOLDS.append(((0.150, y, -0.012), (0.028, 0.045, 0.018)))

FORE = tt.Limb(pts=[(0.13, -0.47, -0.02), (0.21, -0.45, -0.04), (0.24, -0.50, -0.055), (0.25, -0.52, -0.058)],
               radii=[0.036, 0.030, 0.025, 0.022], toes=4, toe_len=0.035, toe_r=0.011, toe_spread=70,
               toe_yaw=30, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.11, 0.05, -0.02), (0.20, 0.08, -0.04), (0.23, 0.13, -0.055), (0.24, 0.15, -0.058)],
               radii=[0.040, 0.032, 0.026, 0.023], toes=5, toe_len=0.04, toe_r=0.011, toe_spread=75,
               toe_yaw=60, toe_drop=0.0, claws=False)


def wrinkles(co, n, c, spec):
    # fine vertical creases on the skin folds and flanks, darker tubercles on the head
    if -0.6 < co.y < 0.12 and abs(n.x) > 0.4:
        k = abs(math.sin(co.y * 120.0 + 3.0 * math.sin(co.z * 40.0)))
        c = tt.nh.lerp(c, (0.16, 0.14, 0.08), 0.35 * (1.0 - tt.nh.smoothstep(0.0, 0.3, k)))
    return c


SPEC = tt.TetrapodSpec(
    name="AndriasMatthewi",
    axis=AXIS, power=2.3,
    blobs=FOLDS,
    limbs=[FORE, HIND],
    voxel=0.0085, max_tris=10000,
    pivot="centre",
    scale_bump=0.003, scale_freq=30.0,
    mouth=(-1.0, -0.74, -0.004, -0.006, 0.006), mouth_min_x=0.2,
    eyes=(-0.88, 0.035, 0.009, (0.55, 0.45, 0.20), 0.085),
    back=(0.26, 0.23, 0.13), flank=(0.38, 0.33, 0.20), belly=(0.58, 0.52, 0.38),
    pattern=("spots", (0.14, 0.12, 0.07), 9.0, 0.7),
    paint_extra=wrinkles,
)

if __name__ == "__main__":
    tt.run(SPEC)
