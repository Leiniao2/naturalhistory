"""
Procedural Proganochelys quenstedti (Late Triassic stem turtle, ~1 m) for map colonies.

One of the oldest turtles with a complete shell, from the Norian (about 210 million
years ago) of Germany and Thailand. Its high, domed carapace is made of many scutes and
edged with a row of spiky marginal plates; it could not pull its head in, so its neck
was guarded by bony spines, and its long tail ended in a club of fused osteoderms with
spikes. A toothless horny beak (though tiny teeth still lined its palate), sprawling,
stout clawed legs. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py)
plus a crisp domed shell with painted scute seams. Painted olive-brown shell, grey-brown
skin (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/proganochelys_quenstedti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Proganochelys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.36, 0.32, 0.18)
SHELL_DARK = (0.20, 0.17, 0.10)
SEAM = (0.12, 0.10, 0.07)
SPIKE = (0.50, 0.44, 0.30)
BEAK = (0.18, 0.15, 0.11)

SC = Vector((0.0, -0.07, 0.255))       # shell centre (rim height)
RX, RY, RZ = 0.40, 0.54, 0.24

AXIS = [
    (-1.00, 0.200, 0.010, 0.014),
    (-0.965, 0.210, 0.034, 0.034),
    (-0.89, 0.224, 0.054, 0.050),
    (-0.81, 0.230, 0.060, 0.052),
    (-0.73, 0.226, 0.054, 0.050),
    (-0.63, 0.232, 0.070, 0.062),
    (-0.50, 0.242, 0.180, 0.100),
    (0.00, 0.252, 0.250, 0.120),
    (0.38, 0.242, 0.180, 0.100),
    (0.52, 0.222, 0.060, 0.050),
    (0.72, 0.175, 0.034, 0.030),
    (0.86, 0.145, 0.042, 0.034),
    (0.95, 0.132, 0.005, 0.005),
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
    mb.add(tt.dome(SC, RX, RY, RZ, 0.06, power=2.1, segments=96, rings=40,
                   ridge=lambda x, y: 0.025 * math.exp(-(x / 0.05) ** 2)), shell_col)
    # spiky marginal plates around the rim
    for k in range(30):
        a = k / 30 * math.tau
        if -0.55 < math.sin(a) and abs(math.cos(a)) < 0.25 and math.sin(a) < -0.6:
            continue
        d = Vector((math.cos(a), math.sin(a), 0.0))
        base = SC + Vector((d.x * RX * 0.97, d.y * RY * 0.97, -0.005))
        if math.sin(a) < -0.85:      # leave the neck opening clear
            continue
        mb.add(tt.cone(base, base + Vector((d.x, d.y * 0.8, -0.15)).normalized() * 0.05, 0.02, sides=5), SPIKE)
    # neck spines and tail club spikes
    for y, sx, z in ((-0.80, 1, 0.27), (-0.74, 1, 0.27), (-0.68, 1, 0.28)):
        for s in (1, -1):
            base = Vector((s * 0.045, y, z))
            mb.add(tt.cone(base, base + Vector((s * 0.04, 0.01, 0.025)), 0.012, sides=5), SPIKE)
    for y in (0.60, 0.68, 0.76, 0.84, 0.90):
        loc, n = surf.hit((0.0, y, 2.0), (0, 0, -1))
        if loc is None:
            continue
        mb.add(tt.cone(loc - n * 0.004, loc + (n + Vector((0, 0.4, 0))).normalized() * 0.03, 0.011, sides=5), SPIKE)
        for s in (1, -1):
            loc2, n2 = surf.hit((s * 2.0, y, loc.z - 0.02), (-s, 0, 0))
            if loc2 is not None:
                mb.add(tt.cone(loc2 - n2 * 0.004, loc2 + n2 * 0.028, 0.010, sides=5), SPIKE)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.95, -0.985, co.y))


SPEC = tt.TetrapodSpec(
    name="Proganochelys",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=9000,
    mouth=(-0.995, -0.86, 0.196, 0.205, 0.004),
    eyes=(-0.86, 0.236, 0.014, (0.55, 0.40, 0.15)),
    back=(0.34, 0.31, 0.26), flank=(0.46, 0.42, 0.34), belly=(0.70, 0.64, 0.50),
    pattern=("spots", (0.24, 0.21, 0.17), 30.0, 0.5),
    paint_extra=paint_extra,
    post=shell,
)

if __name__ == "__main__":
    tt.run(SPEC)
