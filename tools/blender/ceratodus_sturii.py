"""
Procedural Ceratodus sturii (Late Triassic lungfish, ~1 m) for map colonies.

A big lungfish of Triassic rivers and lakes, known mostly from its fan-shaped, ridged
tooth plates: a long, heavy body with large round scales, a blunt head, fleshy paddle-like
paired fins and a single fringe of fin running along the back, round the tail tip and
under the tail, like the living Australian lungfish. It could gulp air when the water went
stale. Painted olive-brown with dark spots. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Ceratodus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402
from mathutils import noise  # noqa: E402


BACK = (0.22, 0.22, 0.12)
FLANK = (0.46, 0.44, 0.26)
BELLY = (0.86, 0.80, 0.62)
SPOT = (0.14, 0.13, 0.08)
FIN = (0.44, 0.40, 0.26)

OUT = jf.Outline([(-0.80, 0.010, -0.040, 0.030), (-0.76, 0.050, -0.070, 0.060), (-0.66, 0.085, -0.090, 0.085),
                  (-0.48, 0.105, -0.100, 0.095), (-0.20, 0.110, -0.100, 0.092), (0.10, 0.095, -0.085, 0.074),
                  (0.36, 0.065, -0.060, 0.048), (0.56, 0.035, -0.035, 0.026), (0.70, 0.012, -0.012, 0.010),
                  (0.74, 0.002, -0.002, 0.003)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.004, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.1, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.9, z))
    if co.y > -0.62:   # big round scales
        a = math.sin(co.y * 45.0) * math.sin(co.z * 45.0 + co.y * 22.0)
        c = nh.lerp(c, tuple(x * 0.88 for x in c), nh.smoothstep(0.6, 0.95, abs(a)))
    m = nh.smoothstep(0.15, 0.45, noise.noise(co * 9.0))
    return nh.lerp(c, SPOT, 0.5 * m * nh.smoothstep(-0.3, 0.3, z))


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.18, 0.16, 0.10), v * 0.7)


def lobe_fin(mb, root, direction, length, width, sx):
    """Fleshy, leaf-shaped paired fin: a scaly central lobe fringed with fin rays."""
    from mathutils import Vector
    r = Vector(root)
    d = Vector(direction).normalized()
    side = Vector((sx, 0, 0))
    pts = [r + d * length * t for t in (0.0, 0.35, 0.7, 1.0)]
    mb.add(nh.tube(pts, [width * 0.5, width * 0.45, width * 0.3, 0.0], sides=8, scale_xy=(1.0, 0.45)), FLANK)
    base = [r + d * length * t for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
    for sign in (1, -1):
        edge = [p + Vector((0, 0, sign * width * (1.0 - abs(2 * t - 1) ** 2) * 0.9)) + side * 0.002
                for p, t in zip(base, (0.0, 0.25, 0.5, 0.75, 1.0))]
        fish.fin(mb, base, edge, fin_col, rows=2, th0=0.006, th1=0.002)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=150, ring=36)
    # one continuous fin fringe: back, around the pointed tail, belly
    top = [(y, OUT.top(y) - 0.006) for y in (-0.05, 0.15, 0.35, 0.55, 0.70)]
    jf.midfin(mb, top, [(y + 0.03, z + h) for (y, z), h in zip(top, (0.01, 0.07, 0.08, 0.07, 0.05))], fin_col)
    bot = [(y, OUT.bot(y) + 0.006) for y in (0.15, 0.35, 0.55, 0.70)]
    jf.midfin(mb, bot, [(y + 0.03, z - h) for (y, z), h in zip(bot, (0.01, 0.06, 0.06, 0.05))], fin_col)
    jf.midfin(mb, [(0.70, 0.012), (0.74, 0.0), (0.70, -0.012)], [(0.78, 0.05), (0.86, 0.0), (0.78, -0.045)], fin_col)
    for sx in (1, -1):
        lobe_fin(mb, (sx * 0.07, -0.50, -0.06), (sx * 0.5, 0.8, -0.35), 0.24, 0.06, sx)
        lobe_fin(mb, (sx * 0.05, 0.12, -0.07), (sx * 0.4, 0.85, -0.3), 0.18, 0.05, sx)
    fish.eyes(mb, -0.70, 0.03, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.70, 0.03), 0.014, (0.70, 0.60, 0.30))
    return kit.finish(mb, "Ceratodus", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Ceratodus", **fish.PREVIEW)
