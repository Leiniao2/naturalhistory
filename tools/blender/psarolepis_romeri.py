"""
Procedural Psarolepis romeri for the map: an early bony fish (a "psarolepid" near the
base of the lobe-finned fishes) from the late Silurian to Early Devonian (about
418-397 million years ago) of Qujing, Yunnan, China.

Known from skulls, jaws, shoulder girdles, fin spines and scales rather than whole
bodies, so the body outline follows its articulated relative Guiyu. What sets it
apart is shown here: a strangely humped snout with the nostrils high up, small eyes
low on the head just above the upper jaw, the head covered in a porcelain-like
cosmine layer pocked with pores (which hides the bone sutures), tooth whorls at the
front of the lower jaw, a very large pectoral spine sweeping back from the shoulder
girdle in front of each pectoral fin, and a dorsal spine in front of a median fin
just behind the head, giving it a shark-like look. Pelvic fins with spines on a
dermal pelvic girdle, a second dorsal fin, an anal fin and a heterocercal tail; the
trunk carries thick rhombic cosmine-covered scales.

Built from nh_early_fish pieces (bony head shell, rhombic scale lattice, fin webs,
ridged spines). Colours are unknown: a cool grey-brown with a pale, glossy head.

Usage:
  blender --background --python tools/blender/psarolepis_romeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Psarolepis.fbx (map style Swim: pivot at the
body centre, facing -Y, dorsal fins up). About 1.55 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Psarolepis"

BACK = (0.20, 0.22, 0.22)
FLANK = (0.42, 0.42, 0.38)
BELLY = (0.78, 0.76, 0.68)
BLOTCH = (0.15, 0.16, 0.16)
COSMINE = (0.70, 0.66, 0.56)
COSMINE_TOP = (0.46, 0.44, 0.38)
PORE = (0.20, 0.18, 0.15)
MOUTH = (0.10, 0.07, 0.06)
TOOTH = (0.90, 0.86, 0.74)
FIN = (0.36, 0.36, 0.33)
FIN_EDGE = (0.58, 0.57, 0.52)
RAY = (0.20, 0.20, 0.18)
SPINE = (0.72, 0.68, 0.56)
SPINE_RIDGE = (0.38, 0.35, 0.28)

# humped snout: the head is tall at the front, the jaw line low
PROF = ef.Profile([
    (-0.78, 0.012, 0.030, 0.012, -0.040),
    (-0.765, 0.055, 0.115, 0.040, -0.040),
    (-0.72, 0.092, 0.162, 0.070, -0.030),
    (-0.64, 0.122, 0.168, 0.100, -0.015),
    (-0.52, 0.140, 0.165, 0.128, 0.006),
    (-0.36, 0.140, 0.162, 0.136, 0.016),
    (-0.14, 0.122, 0.142, 0.120, 0.020),
    (0.08, 0.092, 0.110, 0.096, 0.030),
    (0.28, 0.060, 0.074, 0.064, 0.048),
    (0.40, 0.043, 0.053, 0.045, 0.070),
    (0.58, 0.024, 0.030, 0.024, 0.128),
    (0.78, 0.004, 0.006, 0.005, 0.212),
], power=lambda y: 2.6 if y < -0.5 else 2.15)

Y_HEAD = -0.47
EYE_Y = -0.655


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.30


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(COSMINE, COSMINE_TOP, nh.smoothstep(0.1, 0.95, v) * 0.6)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.5)
    # pocked with pores: many small dark dots, no visible sutures
    pore = nh.smoothstep(0.12, 0.40, ef.mottle(co, 32.0, 2.0))
    c = nh.lerp(c, PORE, 0.55 * pore)
    if co.y < -0.57 and abs(u) > 0.4:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.004, 0.010, abs(co.z - mouth_z(co.y))))
    c = nh.lerp(c, PORE, 0.7 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.02 - 0.03 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)
    c = nh.lerp(c, BLOTCH, 0.45 * (1.0 - nh.smoothstep(0.03, 0.08, abs(v - 0.12))))
    return c


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    plain = ef.ray_color(FIN, RAY, FIN_EDGE, 1, rays=False)
    # first dorsal fin right behind the head, led by its spine
    ef.median_fin(mb, PROF, -0.40, -0.25, lambda u: 0.13 * (1 - u) ** 0.7 + 0.01, rays(4), sweep=0.8,
                  cols=ef.ray_cols(4), rows=2)
    base = Vector((0.0, -0.425, PROF.top(-0.425) - 0.004))
    ef.spine(mb, base, base + Vector((0.0, 0.13, 0.15)), 0.018, SPINE, SPINE_RIDGE, sides=8, bend=(0, -0.015, 0.01))
    # second dorsal and anal fins
    ef.median_fin(mb, PROF, 0.18, 0.34, lambda u: 0.11 * math.sin(math.pi * (0.25 + 0.75 * u)) ** 0.7 + 0.008,
                  rays(5), sweep=0.8, cols=ef.ray_cols(5), rows=2)
    ef.median_fin(mb, PROF, 0.20, 0.34, lambda u: 0.09 * math.sin(math.pi * (0.25 + 0.75 * u)) ** 0.7 + 0.008,
                  rays(4), sign=-1, sweep=0.8, cols=ef.ray_cols(4), rows=2)
    # heterocercal tail
    axis, edge, axis_t, edge_t = [], [], [], []
    n = ef.ray_cols(9)
    for i in range(n):
        u = i / (n - 1)
        y = 0.36 + 0.42 * u
        axis.append((0.0, y, PROF.bot(y) + 0.006))
        L = 0.21 * math.sin(math.pi * min(1.0, u * 1.05) ** 0.75) ** 1.2 * (1 - 0.35 * u) + 0.004
        edge.append((0.0, y + 0.55 * L, PROF.bot(y) - L))
        axis_t.append((0.0, y, PROF.top(y) - 0.004))
        edge_t.append((0.0, y + 0.02, PROF.top(y) + 0.028 * math.sin(math.pi * u) + 0.003))
    ef.caudal_web(mb, axis, edge, rays(9), rows=3)
    ef.caudal_web(mb, axis_t[::3], edge_t[::3], plain, rows=1)

    for s in (1, -1):
        # pectoral fin behind the huge shoulder-girdle spine
        root = Vector((s * PROF.W(-0.40) * 0.85, -0.40, PROF.CZ(-0.40) - PROF.HB(-0.40) * 0.55))
        tip = root + Vector((s * 0.14, 0.16, -0.08))
        ef.lobe(mb, root, root.lerp(tip, 0.5), 0.028, lambda t, co: nh.lerp(FLANK, BLOTCH, 0.3 * t), sides=8)
        ef.lobe_fringe(mb, root, tip, (-s * 0.5, 1.0, -0.2),
                       lambda t: 0.02 * math.sin(math.pi * t) + 0.005,
                       lambda t: 0.065 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 + 0.005, rays(4),
                       cols=ef.ray_cols(4))
        sb = Vector((s * PROF.W(-0.47) * 0.92, -0.47, PROF.CZ(-0.47) - PROF.HB(-0.47) * 0.35))
        ef.spine(mb, sb, sb + Vector((s * 0.20, 0.30, -0.10)), 0.024, SPINE, SPINE_RIDGE, sides=8,
                 bend=(s * 0.02, 0.0, 0.015))
        # pelvic fin and spine
        ef.paired_fin(mb, PROF, s, 0.0, 0.08, -1.05, lambda u: 0.08 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.9, plain, cols=5, rows=2)
        pr = PROF.point(-0.01, -1.1)
        pr.x *= s
        ef.spine(mb, pr, pr + Vector((s * 0.05, 0.11, -0.05)), 0.009, SPINE, SPINE_RIDGE)


def jaws(mb):
    """Parasymphysial tooth whorls: a few upturned teeth at the front of the lower jaw."""
    for s in (1, -1):
        for k in range(3):
            y = -0.755 + 0.012 * k
            z = mouth_z(y)
            x = s * (PROF.W(y) * 0.35 + 0.004)
            mb.add(nh.tube([(x, y, z - 0.006), (x, y - 0.003, z + 0.016 - 0.003 * k)], [0.0045, 0.0], sides=5), TOOTH)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=15, na=26, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 38, 19, scale_color, lift=0.004, fade_y=(0.53, 0.76))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.77, -0.60, mouth_z, MOUTH, grow=0.005)
    jaws(mb)
    ef.surface_eye(mb, PROF, EYE_Y, 0.05, 0.026, (0.95, -0.25, 0.1), iris=(0.55, 0.45, 0.22))
    # nostrils high on the humped snout, above the eyes
    for s in (1, -1):
        p = PROF.point(-0.70, 0.95)
        p.x *= s
        mb.add(nh.uv_ellipsoid(tuple(p), (0.007, 0.009, 0.006), 5, 3), MOUTH)
    obj = mb.to_object(NAME, roughness=0.4)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
