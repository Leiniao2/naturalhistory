"""
Procedural Longisquama insignis (Middle-Late Triassic diapsid, ~15 cm body) for map
colonies.

A small, lizard-like reptile known from a single partial skeleton from the Madygen
Formation of Kyrgyzstan. It is famous for the row of long, hockey-stick-shaped
appendages growing from its back, each longer than the body, which are usually
reconstructed as a paired fan of plumes held up over the back for display. A short
head with large eyes, a slim body, slender clawed limbs for climbing and a long tail.
Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py) plus flat ribbon
plumes. Painted green-brown with a pale belly, the plumes orange with dark tips
(speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/longisquama_insignis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Longisquama.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

PLUME = (0.82, 0.46, 0.14)
PLUME_TIP = (0.18, 0.10, 0.06)
PLUME_BASE = (0.55, 0.40, 0.18)


def sway(y):
    s = max(0.0, (y - 0.0) / 0.95)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.160, 0.006, 0.006),
    (-0.95, 0.170, 0.030, 0.026),
    (-0.86, 0.185, 0.052, 0.045),
    (-0.76, 0.190, 0.062, 0.054),
    (-0.70, 0.185, 0.050, 0.045),
    (-0.60, 0.185, 0.070, 0.060),
    (-0.45, 0.190, 0.094, 0.074),
    (-0.25, 0.190, 0.094, 0.074),
    (-0.10, 0.185, 0.075, 0.060),
    (0.10, 0.160, 0.040, 0.035, sway(0.10)),
    (0.35, 0.130, 0.024, 0.021, sway(0.35)),
    (0.65, 0.090, 0.012, 0.011, sway(0.65)),
    (0.95, 0.060, 0.002, 0.002, sway(0.95)),
]

FORE = tt.Limb(pts=[(0.06, -0.55, 0.165), (0.15, -0.56, 0.135), (0.17, -0.60, 0.03), (0.17, -0.62, 0.008)],
               radii=[0.024, 0.019, 0.014, 0.011], toes=5, toe_len=0.05, toe_r=0.0055, toe_spread=80,
               toe_yaw=15, stride=14, claw_len=0.012)
HIND = tt.Limb(pts=[(0.06, -0.12, 0.165), (0.17, -0.08, 0.14), (0.19, 0.0, 0.03), (0.19, -0.03, 0.008)],
               radii=[0.030, 0.022, 0.016, 0.012], toes=5, toe_len=0.07, toe_r=0.006, toe_spread=80,
               toe_yaw=25, stride=-14, claw_len=0.012)


def plumes(mb, surf, spec):
    n = 7
    for i in range(n):
        t = i / (n - 1)
        y = -0.56 + 0.44 * t
        ln = 0.78 - 0.18 * abs(t - 0.4)
        lean = -0.08 + 0.30 * t          # front ones upright, rear ones lean back
        for sx in (1, -1):
            loc, nrm = surf.hit((sx * 0.018, y, 2.0), (0, 0, -1))
            if loc is None:
                continue
            pts, hw = [], []
            for k in range(9):
                u = k / 8
                # hockey-stick: straight shaft, the outer third widening and curving back
                pts.append(loc + Vector((sx * (0.05 * u + 0.08 * u * u), lean * u * ln + 0.18 * u ** 3 * ln,
                                         ln * u * (1.0 - 0.15 * u * u))))
                hw.append(0.008 + 0.030 * nh.smoothstep(0.35, 0.8, u) * (1.0 - 0.6 * nh.smoothstep(0.85, 1.0, u)))

            def col(co, _n, base=loc, l=ln):
                u = (co.z - base.z) / l
                c = nh.lerp(PLUME_BASE, PLUME, nh.smoothstep(0.1, 0.4, u))
                return nh.lerp(c, PLUME_TIP, nh.smoothstep(0.78, 0.9, u))
            mb.add(tt.ribbon(pts, hw, Vector((0, 1, 0)), 0.006), col)


SPEC = tt.TetrapodSpec(
    name="Longisquama",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.008, max_tris=8000,
    scale_bump=0.0012, scale_freq=70.0,
    mouth=(-0.995, -0.83, 0.155, 0.172, 0.003),
    eyes=(-0.82, 0.205, 0.022, (0.80, 0.55, 0.15)),
    back=(0.25, 0.30, 0.16), flank=(0.44, 0.48, 0.28), belly=(0.82, 0.80, 0.62),
    pattern=("bands", (0.14, 0.16, 0.09), 30.0, 0.6, 0.0, 1.0),
    post=plumes,
)

if __name__ == "__main__":
    tt.run(SPEC)
