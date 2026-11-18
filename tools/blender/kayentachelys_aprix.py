"""
Procedural Kayentachelys aprix (Early Jurassic Kayenta Formation turtle, Arizona) for
map colonies.

One of the oldest turtles known from North America, a small, low-shelled freshwater
turtle. Its shell is low and smoothly domed, with neat scute seams and none of the spikes
of older turtles, and its short, toothless beak and still-primitive skull sit on a
neck that could not yet be pulled fully into the shell. Short, clawed, sprawling legs and a
short tail. Painted olive-brown with darker scute centres and a pale yellowish plastron;
olive-grey skin. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py), as
Proganochelys. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kayentachelys_aprix.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kayentachelys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.34, 0.33, 0.18)
SHELL_DARK = (0.18, 0.18, 0.09)
SEAM = (0.12, 0.10, 0.07)
SPIKE = (0.50, 0.44, 0.30)
BEAK = (0.18, 0.15, 0.11)

SC = Vector((0.0, -0.07, 0.235))       # shell centre (rim height)
RX, RY, RZ = 0.41, 0.55, 0.17

AXIS = [
    (-0.86, 0.200, 0.010, 0.014),
    (-0.825, 0.210, 0.034, 0.034),
    (-0.75, 0.224, 0.054, 0.050),
    (-0.69, 0.230, 0.060, 0.052),
    (-0.64, 0.228, 0.058, 0.052),
    (-0.58, 0.232, 0.072, 0.064),
    (-0.50, 0.242, 0.180, 0.100),
    (0.00, 0.252, 0.250, 0.120),
    (0.38, 0.242, 0.180, 0.100),
    (0.52, 0.222, 0.060, 0.050),
    (0.64, 0.185, 0.030, 0.026),
    (0.72, 0.165, 0.018, 0.016),
    (0.76, 0.155, 0.004, 0.004),
]

FORE = tt.Limb(pts=[(0.20, -0.38, 0.22), (0.33, -0.40, 0.15), (0.34, -0.45, 0.04), (0.34, -0.47, 0.013)],
               radii=[0.060, 0.050, 0.040, 0.035], toes=5, toe_len=0.03, toe_r=0.012, toe_spread=70,
               toe_yaw=15, stride=10, claw_len=0.02)
HIND = tt.Limb(pts=[(0.20, 0.30, 0.22), (0.32, 0.33, 0.15), (0.33, 0.38, 0.04), (0.33, 0.37, 0.013)],
               radii=[0.062, 0.052, 0.042, 0.036], toes=5, toe_len=0.03, toe_r=0.012, toe_spread=70,
               toe_yaw=25, stride=-10, claw_len=0.02)

# scute centres (plan view): vertebrals down the middle, costals either side, marginals on the rim
CENTRES = [(0.0, SC.y + RY * t) for t in (-0.62, -0.25, 0.1, 0.45, 0.78)]
CENTRES += [(s * RX * 0.52, SC.y + RY * t) for s in (1, -1) for t in (-0.45, -0.05, 0.35, 0.7)]
for k in range(28):
    a = k / 28 * math.tau
    CENTRES.append((math.cos(a) * RX * 0.92, SC.y + math.sin(a) * RY * 0.92))


def shell_col(co, n):
    e = tt.voronoi_edge(co, CENTRES, 0.032)
    c = nh.lerp(SHELL, SHELL_DARK, 0.5 * nh.smoothstep(0.3, 0.8, noise_k(co)))
    if co.z < SC.z - 0.01:
        c = nh.lerp(c, (0.70, 0.62, 0.42), 0.6)      # plastron
    return nh.lerp(c, SEAM, 0.85 * e)


def noise_k(co):
    from mathutils import noise
    return 0.5 + 0.5 * noise.noise(co * 9.0)


def shell(mb, surf, spec):
    mb.add(tt.dome(SC, RX, RY, RZ, 0.05, power=2.2, segments=96, rings=40,
                   ridge=lambda x, y: 0.012 * math.exp(-(x / 0.05) ** 2)), shell_col)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.81, -0.845, co.y))


SPEC = tt.TetrapodSpec(
    name="Kayentachelys",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=9000,
    mouth=(-0.855, -0.72, 0.196, 0.205, 0.004),
    eyes=(-0.72, 0.236, 0.014, (0.55, 0.40, 0.15)),
    back=(0.30, 0.31, 0.24), flank=(0.42, 0.43, 0.32), belly=(0.70, 0.66, 0.48),
    pattern=("spots", (0.24, 0.21, 0.17), 30.0, 0.5),
    paint_extra=paint_extra,
    post=shell,
)

if __name__ == "__main__":
    tt.run(SPEC)
