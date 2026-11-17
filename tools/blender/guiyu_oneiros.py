"""
Procedural Guiyu oneiros for the map: the oldest near-complete articulated bony fish
(osteichthyan), from the late Silurian (Ludlow, ~425 million years ago) Kuanti
Formation of Qujing, Yunnan, China. About 33 cm long.

Follows the published reconstruction (Zhu et al. 2009; Cui et al. 2019): a
streamlined, fusiform fish with a bony head about a quarter of its length, whose
lobe-finned-like skull is combined with placoderm-like features: behind the skull
roof a row of three median dorsal plates, the last carrying the stout, recurved
spine at the leading edge of the first dorsal fin, and large spines in front of the
pectoral and pelvic fins (the pelvic spines on a dermal pelvic girdle). Further
back a second dorsal fin and an anal fin, and a heterocercal tail whose scaled
body axis turns up into the upper lobe. The trunk is covered in thick rhombic
scales in oblique rows; the pectoral fins have a short fleshy, scaled lobe.

Built from nh_early_fish pieces: a smooth bony head shell painted with dermal-plate
sutures, tubercles and the mouth line; the trunk as separate rhombic scales over a
dark underlay; thin fin webs with fine rays; ridged spines and plates. Colours are
unknown: muted olive-brown above with a bronze sheen on the scales and a pale belly.

Usage:
  blender --background --python tools/blender/guiyu_oneiros.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Guiyu.fbx (map style Swim: pivot at the body
centre, facing -Y, dorsal fins up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402

NAME = "Guiyu"

BACK = (0.26, 0.25, 0.17)
FLANK = (0.52, 0.45, 0.30)
BELLY = (0.80, 0.75, 0.60)
BLOTCH = (0.20, 0.18, 0.12)
BONE = (0.50, 0.44, 0.32)
BONE_DARK = (0.30, 0.26, 0.19)
SUTURE = (0.12, 0.10, 0.07)
MOUTH = (0.10, 0.07, 0.06)
FIN = (0.42, 0.37, 0.26)
FIN_EDGE = (0.62, 0.57, 0.44)
RAY = (0.24, 0.20, 0.13)
SPINE = (0.66, 0.60, 0.46)
SPINE_RIDGE = (0.36, 0.31, 0.22)

PROF = ef.Profile([
    (-0.80, 0.010, 0.012, 0.012, -0.010),
    (-0.775, 0.050, 0.055, 0.045, -0.002),
    (-0.72, 0.090, 0.095, 0.075, 0.008),
    (-0.62, 0.122, 0.128, 0.105, 0.014),
    (-0.48, 0.140, 0.152, 0.128, 0.018),
    (-0.30, 0.136, 0.158, 0.134, 0.020),
    (-0.10, 0.118, 0.138, 0.118, 0.022),
    (0.10, 0.090, 0.108, 0.094, 0.030),
    (0.30, 0.058, 0.072, 0.062, 0.048),
    (0.42, 0.042, 0.052, 0.044, 0.070),
    (0.60, 0.024, 0.030, 0.024, 0.128),
    (0.80, 0.004, 0.006, 0.005, 0.215),
], power=lambda y: 2.5 if y < -0.5 else 2.15)

Y_HEAD = -0.455
EYE_Y = -0.665

HEAD_PLATES = [(-0.76, 0.0), (-0.69, 0.25), (-0.62, 0.0), (-0.55, 0.28), (-0.50, 0.0), (-0.66, 0.75),
               (-0.56, 0.95), (-0.72, 1.25), (-0.58, 1.45), (-0.50, 1.25), (-0.70, 2.1), (-0.55, 2.4)]


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.22


def head_color(co, n):
    u, v = PROF.rel(co)
    phi = ef.phi_of(PROF, co)
    c = nh.lerp(BONE, BONE_DARK, nh.smoothstep(0.0, 0.9, v) * 0.45)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    c = nh.lerp(c, BONE_DARK, 0.35 * nh.smoothstep(0.2, 0.6, ef.mottle(co, 40.0)))   # tubercles
    c = nh.lerp(c, SUTURE, 0.8 * ef.plates(HEAD_PLATES, co.y, phi, sphi=0.10, width=0.026))
    # mouth line, running back to below the eye
    if co.y < -0.58 and abs(u) > 0.45:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.004, 0.010, abs(co.z - mouth_z(co.y))))
    # gill-cover margin just in front of the back edge
    c = nh.lerp(c, SUTURE, 0.7 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.02 - 0.03 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.5)
    # lateral line scale row
    c = nh.lerp(c, BLOTCH, 0.5 * (1.0 - nh.smoothstep(0.03, 0.08, abs(v - 0.12))))
    return c


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # first dorsal fin behind its big spine (on the third median dorsal plate)
    ef.median_fin(mb, PROF, -0.27, -0.10, lambda u: 0.15 * (1 - u) ** 0.8 + 0.01, rays(5), sweep=0.7, cols=ef.ray_cols(5), rows=2)
    # second dorsal and anal fins
    ef.median_fin(mb, PROF, 0.20, 0.36, lambda u: 0.11 * math.sin(math.pi * (0.25 + 0.75 * u)) ** 0.7 + 0.008,
                  rays(5), sweep=0.8, cols=ef.ray_cols(5), rows=2)
    ef.median_fin(mb, PROF, 0.22, 0.36, lambda u: 0.09 * math.sin(math.pi * (0.25 + 0.75 * u)) ** 0.7 + 0.008,
                  rays(4), sign=-1, sweep=0.8, cols=ef.ray_cols(4), rows=2)
    # heterocercal tail: web below the upturned scaled axis, a narrow fringe above it
    axis, edge, axis_t, edge_t = [], [], [], []
    n = ef.ray_cols(9)
    for i in range(n):
        u = i / (n - 1)
        y = 0.38 + 0.42 * u
        axis.append((0.0, y, PROF.bot(y) + 0.006))
        L = 0.22 * math.sin(math.pi * min(1.0, u * 1.05) ** 0.75) ** 1.2 * (1 - 0.35 * u) + 0.004
        edge.append((0.0, y + 0.55 * L, PROF.bot(y) - L))
        axis_t.append((0.0, y, PROF.top(y) - 0.004))
        edge_t.append((0.0, y + 0.02, PROF.top(y) + 0.028 * math.sin(math.pi * u) + 0.003))
    ef.caudal_web(mb, axis, edge, rays(9), rows=3)
    ef.caudal_web(mb, axis_t[::3], edge_t[::3], ef.ray_color(FIN, RAY, FIN_EDGE, 1, rays=False), rows=1)

    for s in (1, -1):
        # pectoral fin: short fleshy scaled lobe with a fin web, spine in front
        root = Vector((s * PROF.W(-0.42) * 0.85, -0.42, PROF.CZ(-0.42) - PROF.HB(-0.42) * 0.55))
        tip = root + Vector((s * 0.15, 0.17, -0.08))
        ef.lobe(mb, root, root.lerp(tip, 0.5), 0.03, lambda t, co: nh.lerp(FLANK, BLOTCH, 0.3 * t), sides=8)
        ef.lobe_fringe(mb, root, tip, (-s * 0.5, 1.0, -0.2),
                       lambda t: 0.02 * math.sin(math.pi * t) + 0.005,
                       lambda t: 0.07 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 + 0.005, rays(4), cols=ef.ray_cols(4))
        ef.spine(mb, root + Vector((s * 0.0, -0.02, 0.01)), root + Vector((s * 0.16, 0.12, -0.09)), 0.013,
                 SPINE, SPINE_RIDGE, bend=(s * 0.005, 0.0, 0.01))
        # pelvic fin with its spine (dermal pelvic girdle)
        ef.paired_fin(mb, PROF, s, 0.02, 0.10, -1.05, lambda u: 0.09 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.9, ef.ray_color(FIN, RAY, FIN_EDGE, 1, rays=False), cols=5, rows=2)
        pr = PROF.point(0.01, -1.1)
        pr.x *= s
        ef.spine(mb, pr, pr + Vector((s * 0.05, 0.12, -0.06)), 0.009, SPINE, SPINE_RIDGE)


def dorsal_armour(mb):
    """Three median dorsal plates behind the skull; the last bears the first dorsal spine."""
    for i, (y, L, W) in enumerate(((-0.43, 0.055, 0.045), (-0.37, 0.06, 0.05), (-0.305, 0.07, 0.055))):
        z = PROF.top(y) - 0.006
        mb.add(nh.uv_ellipsoid((0.0, y, z), (W, L, 0.016), 10, 5),
               lambda co, n, y0=y: nh.lerp(BONE, SPINE_RIDGE, 0.6 * (0.5 + 0.5 * math.cos((co.x) * 260.0))
                                           * nh.smoothstep(0.3, 0.8, n.z)))
    base = Vector((0.0, -0.30, PROF.top(-0.30) + 0.002))
    ef.spine(mb, base, base + Vector((0.0, 0.11, 0.17)), 0.020, SPINE, SPINE_RIDGE, sides=8,
             bend=(0.0, -0.02, 0.012))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=15, na=26, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.80, 38, 19, scale_color, lift=0.004, fade_y=(0.55, 0.78))
    dorsal_armour(mb)
    fins(mb)
    ef.mouth_line(mb, PROF, -0.785, -0.60, mouth_z, MOUTH, grow=0.005)
    ef.surface_eye(mb, PROF, EYE_Y, 0.38, 0.034, (0.92, -0.25, 0.25), iris=(0.62, 0.50, 0.22))
    # nostrils
    for s in (1, -1):
        p = PROF.point(-0.755, 0.55)
        p.x *= s
        mb.add(nh.uv_ellipsoid(tuple(p), (0.006, 0.008, 0.006), 5, 3), MOUTH)
    obj = mb.to_object(NAME, roughness=0.45)
    vs = obj.data.vertices
    ys, zs = [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ef.PREVIEW)
