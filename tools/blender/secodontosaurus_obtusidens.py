"""
Procedural Secodontosaurus obtusidens (Early Permian sphenacodontid, ~2 m) for map colonies.

The "fox-faced" sail-back of the Texas red beds, a close relative of Dimetrodon: a long, low,
very narrow snout with blade-like teeth (good for snatching prey out of crevices and burrows),
a tall sail of skin carried on long neural spines along the back, a long tail and sprawling
legs. Greyish-tan body with darker cross-bands; the sail is reddish-orange with dark spines
and a pale rim.
Built with nh_per_tetra (sail added as crisp membrane + spines). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/secodontosaurus_obtusidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Secodontosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

SAIL = (0.72, 0.34, 0.16)
SAIL_RIM = (0.90, 0.78, 0.55)
SPINE = (0.30, 0.20, 0.14)
Y0, Y1 = -0.34, 0.30
TORSO = [
    (-0.42, 0.30, 0.07, 0.07),
    (-0.34, 0.30, 0.12, 0.11),
    (-0.15, 0.30, 0.14, 0.12),
    (0.05, 0.30, 0.13, 0.115),
    (0.22, 0.29, 0.11, 0.10),
    (0.34, 0.27, 0.08, 0.075),
    (0.60, 0.19, 0.045, 0.04),
    (0.90, 0.11, 0.022, 0.02),
    (1.12, 0.06, 0.006, 0.006),
    (1.16, 0.055, 0.0, 0.0),
]


def sail_h(y):
    t = (y - Y0) / (Y1 - Y0)
    return 0.42 * math.sin(math.pi * min(1.0, max(0.0, t)) ** 0.9)


def crisp(mb, spec):
    n = 16
    levels = (0.0, 0.15, 0.35, 0.6, 0.85, 0.93, 1.0)
    cols = (SPINE, SAIL, SAIL, SAIL, SAIL, SAIL_RIM, SAIL_RIM)
    ys = [Y0 + (Y1 - Y0) * i / n for i in range(n + 1)]
    bases = []
    for y in ys:
        z, hw, hh, _x = pt.rows_at(spec.torso, y)
        bases.append(z + hh - 0.01)

    def at(i, t):
        return V((0, ys[i], bases[i] + (sail_h(ys[i]) + 0.015) * t))
    for k in range(len(levels) - 1):
        lo = [at(i, levels[k]) for i in range(n + 1)]
        hi = [at(i, levels[k + 1]) for i in range(n + 1)]
        c0, c1, t0, t1 = cols[k], cols[k + 1], levels[k], levels[k + 1]

        def scol(co, nrm, c0=c0, c1=c1, t0=t0, t1=t1):
            j = min(range(n + 1), key=lambda i: abs(ys[i] - co.y))
            h = sail_h(ys[j]) + 0.015
            t = (co.z - bases[j]) / max(h, 1e-4)
            return nh.lerp(c0, c1, nh.smoothstep(t0, t1, t))
        for i in range(n):
            mb.add(pt.membrane([lo[i], lo[i + 1], hi[i + 1], hi[i]], 0.008), scol, smooth=False)
    for i in range(1, n):
        mb.add(nh.tube([at(i, 0) + V((0, 0, -0.01)), at(i, 1)], [0.007, 0.003], sides=5), SPINE)


SPEC = pt.Spec(
    name="Secodontosaurus",
    torso=TORSO,
    head=[
        (-0.40, 0.34, 0.065, 0.07),
        (-0.50, 0.34, 0.055, 0.065),
        (-0.62, 0.32, 0.035, 0.045),
        (-0.78, 0.30, 0.025, 0.033),
        (-0.88, 0.29, 0.018, 0.026),
        (-0.90, 0.288, 0.0, 0.0),
    ],
    jaw=[
        (-0.44, 0.265, 0.05, 0.022),
        (-0.66, 0.26, 0.025, 0.016),
        (-0.87, 0.262, 0.014, 0.012),
        (-0.895, 0.262, 0.0, 0.0),
    ],
    teeth=[(-0.89, -0.52, 16, 0.014, 0.0035, True)],
    fangs=[(0.022, -0.80, 0.28, 0.04, 0.007, 0.004)],
    fore=pt.Limb(y=-0.28, z=0.24, x=0.11, upper=0.13, lower=0.15, sprawl=0.75, r=0.04,
                 foot=(0.035, 0.045, 0.013), toe_len=0.04, toe_r=0.009),
    hind=pt.Limb(y=0.24, z=0.24, x=0.10, upper=0.14, lower=0.15, sprawl=0.65, r=0.046,
                 foot=(0.038, 0.052, 0.013), toe_len=0.045, toe_r=0.0095),
    eye=(0.05, -0.53, 0.37, 0.015), nostril=(0.015, -0.89, 0.30),
    back=(0.42, 0.36, 0.28), flank=(0.56, 0.49, 0.38), belly=(0.82, 0.76, 0.64), mark=(0.24, 0.18, 0.13),
    pattern="bands", pattern_freq=24.0, pattern_amount=0.6,
    crisp=crisp, voxel=0.0065, max_tris=10000, drop=0.04,
)

if __name__ == "__main__":
    pt.main(SPEC)
