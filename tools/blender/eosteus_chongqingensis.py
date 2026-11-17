"""
Procedural Eosteus chongqingensis for the map: the oldest articulated bony fish
(osteichthyan) known, from the early Silurian (Telychian, about 436 million years
ago) Chongqing Lagerstaette at Yongdong, Xiushan County, Chongqing, China
(described by Zhu et al. 2026). The holotype is a near-complete fish only about
3 cm long.

Follows the published description of a stem bony fish (before the split into
ray-finned and lobe-finned fishes): a fusiform, generalised osteichthyan body with a
bony head and rhombic scales, a row of serial median dorsal plates along the back
behind the head, a single dorsal fin led by a fin spine, pectoral fin spines, an
anal fin spine, and a heterocercal tail whose upper lobe carries a row of ridge
scales (caudal fulcra). It had no fin rays (lepidotrichia), so the fins are drawn as
plain webs. Being so small, it is drawn with a relatively large head and eye.

Built from nh_early_fish pieces (bony head shell, rhombic scale lattice, fin webs,
ridged spines and plates). Colours are unknown: a muted grey-brown, paler below.

Usage:
  blender --background --python tools/blender/eosteus_chongqingensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eosteus.fbx (map style Swim: pivot at the
body centre, facing -Y, dorsal fin up). About 1.5 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Eosteus"

BACK = (0.30, 0.27, 0.24)
FLANK = (0.55, 0.50, 0.44)
BELLY = (0.82, 0.78, 0.70)
BLOTCH = (0.22, 0.20, 0.18)
BONE = (0.58, 0.53, 0.45)
BONE_DARK = (0.36, 0.32, 0.27)
SUTURE = (0.14, 0.12, 0.10)
MOUTH = (0.10, 0.07, 0.06)
FIN = (0.50, 0.46, 0.40)
FIN_EDGE = (0.70, 0.66, 0.58)
SPINE = (0.76, 0.70, 0.58)
SPINE_RIDGE = (0.42, 0.37, 0.30)
PLATE = (0.66, 0.60, 0.50)

# deep, compact spindle with a big head
PROF = ef.Profile([
    (-0.75, 0.012, 0.014, 0.014, -0.010),
    (-0.725, 0.062, 0.068, 0.058, -0.004),
    (-0.66, 0.110, 0.120, 0.100, 0.004),
    (-0.56, 0.142, 0.158, 0.135, 0.010),
    (-0.42, 0.155, 0.180, 0.155, 0.014),
    (-0.22, 0.142, 0.172, 0.150, 0.018),
    (0.00, 0.110, 0.135, 0.118, 0.026),
    (0.20, 0.070, 0.085, 0.074, 0.046),
    (0.32, 0.046, 0.056, 0.048, 0.072),
    (0.52, 0.022, 0.028, 0.022, 0.140),
    (0.75, 0.004, 0.006, 0.005, 0.240),
], power=lambda y: 2.4 if y < -0.45 else 2.15)

Y_HEAD = -0.40
EYE_Y = -0.615

HEAD_PLATES = [(-0.70, 0.0), (-0.62, 0.3), (-0.55, 0.0), (-0.48, 0.32), (-0.44, 0.0), (-0.60, 0.9),
               (-0.48, 1.0), (-0.64, 1.4), (-0.50, 1.6), (-0.60, 2.2), (-0.46, 2.4)]


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * (0.15 + 0.2 * nh.smoothstep(-0.74, -0.58, y))


def head_color(co, n):
    u, v = PROF.rel(co)
    phi = ef.phi_of(PROF, co)
    c = nh.lerp(BONE, BONE_DARK, nh.smoothstep(0.0, 0.9, v) * 0.5)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    c = nh.lerp(c, BONE_DARK, 0.3 * nh.smoothstep(0.2, 0.6, ef.mottle(co, 35.0)))
    c = nh.lerp(c, SUTURE, 0.75 * ef.plates(HEAD_PLATES, co.y, phi, sphi=0.11, width=0.026))
    c = nh.lerp(c, SUTURE, 0.7 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.02 - 0.03 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.3)
    return nh.lerp(c, BLOTCH, 0.4 * (1.0 - nh.smoothstep(0.03, 0.08, abs(v - 0.12))))


def plain(base=FIN, edge=FIN_EDGE):
    return ef.ray_color(base, base, edge, 1, rays=False, edge_amount=0.6)


def fins(mb):
    # single dorsal fin, led by its spine
    ef.median_fin(mb, PROF, -0.02, 0.17, lambda u: 0.16 * (1 - u) ** 0.8 + 0.008, plain(), sweep=0.7, cols=7, rows=2)
    b = Vector((0.0, -0.04, PROF.top(-0.04) - 0.004))
    ef.spine(mb, b, b + Vector((0.0, 0.10, 0.19)), 0.017, SPINE, SPINE_RIDGE, sides=6, bend=(0, -0.012, 0.0))
    # anal fin with its spine
    ef.median_fin(mb, PROF, 0.12, 0.27, lambda u: 0.11 * (1 - u) ** 0.8 + 0.008, plain(), sign=-1, sweep=0.8,
                  cols=6, rows=2)
    b = Vector((0.0, 0.10, PROF.bot(0.10) + 0.004))
    ef.spine(mb, b, b + Vector((0.0, 0.10, -0.13)), 0.013, SPINE, SPINE_RIDGE)
    # heterocercal tail, plain web (no fin rays)
    axis, edge = [], []
    for i in range(10):
        u = i / 9
        y = 0.30 + 0.45 * u
        axis.append((0.0, y, PROF.bot(y) + 0.005))
        L = 0.22 * math.sin(math.pi * min(1.0, u * 1.05) ** 0.75) ** 1.2 * (1 - 0.35 * u) + 0.004
        edge.append((0.0, y + 0.55 * L, PROF.bot(y) - L))
    ef.caudal_web(mb, axis, edge, plain(), rows=2)
    # caudal fulcra: a row of ridge scales along the top of the upper lobe
    for i in range(8):
        t = i / 8
        y = 0.40 + 0.33 * t
        p = Vector((0.0, y, PROF.top(y) - 0.002))
        d = Vector((0.0, 1.0, (PROF.top(y + 0.01) - PROF.top(y - 0.01)) / 0.02)).normalized()
        mb.add(nh.tube([p, p + d * 0.05 * (1 - 0.5 * t) + Vector((0, 0, 0.010 * (1 - t)))],
                       [0.008 * (1 - 0.5 * t), 0.0], sides=4, scale_xy=(0.6, 1.0)), SPINE, smooth=False)
    for s in (1, -1):
        # pectoral fins behind strong spines
        ef.paired_fin(mb, PROF, s, -0.36, -0.30, -0.75, lambda u: 0.14 * (1 - u) ** 0.6 + 0.02,
                      0.75, 0.35, 0.8, plain(), cols=5, rows=2)
        p = PROF.point(-0.37, -0.72, -0.004)
        p.x *= s
        ef.spine(mb, p, p + Vector((s * 0.15, 0.10, -0.06)), 0.014, SPINE, SPINE_RIDGE, bend=(0, -0.01, 0.01))
        # small pelvic fins
        ef.paired_fin(mb, PROF, s, 0.0, 0.05, -1.2, lambda u: 0.06 * (1 - u) ** 0.5 + 0.012,
                      0.5, 0.7, 0.9, plain(), cols=4, rows=1)


def dorsal_plates(mb):
    """Serial median dorsal plates from the skull roof back to the dorsal fin spine."""
    ys = [-0.375, -0.315, -0.255, -0.195, -0.135, -0.08]
    for i, y in enumerate(ys):
        z = PROF.top(y) - 0.004
        L, W = 0.036, 0.036 - 0.003 * i
        mb.add(nh.uv_ellipsoid((0.0, y, z), (W, L, 0.016), 8, 5),
               lambda co, n: nh.lerp(PLATE, SPINE_RIDGE, 0.55 * nh.smoothstep(0.75, 0.2, n.z)))
        # a low median keel on each plate
        mb.add(nh.tube([(0.0, y - L * 0.8, z + 0.012), (0.0, y + L * 0.9, z + 0.020)], [0.006, 0.0], sides=4,
                       scale_xy=(0.6, 1.0)), SPINE, smooth=False)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=14, na=24, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.75, 34, 18, scale_color, lift=0.004, fade_y=(0.45, 0.72))
    dorsal_plates(mb)
    fins(mb)
    ef.mouth_line(mb, PROF, -0.74, -0.58, mouth_z, MOUTH, grow=0.005)
    ef.surface_eye(mb, PROF, EYE_Y, 0.32, 0.045, (0.95, -0.25, 0.2), iris=(0.60, 0.54, 0.36))
    obj = mb.to_object(NAME, roughness=0.45)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
