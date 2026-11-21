"""
Procedural Undina penicillata (Late Jurassic coelacanth, Solnhofen, Germany) for map colonies.

A Jurassic coelacanth about 50 cm long, a relative of the living Latimeria: a stout,
deep-bellied body with large rounded scales, a big head with a wide mouth, fleshy,
limb-like lobed pectoral, pelvic, second dorsal and anal fins on short stalks, a spiny
first dorsal fin, and the coelacanths' distinctive three-lobed tail with a small extra lobe
sticking out of the middle. Painted dark steel-blue with pale blotches (like the living
coelacanth) and a lighter belly. Built with nh_jur_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/undina_penicillata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Undina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402
from mathutils import noise, Vector  # noqa: E402

BACK = (0.14, 0.18, 0.26)
FLANK = (0.24, 0.30, 0.40)
BELLY = (0.56, 0.60, 0.64)
BLOTCH = (0.78, 0.80, 0.80)
FIN = (0.18, 0.22, 0.30)

OUT = jf.Outline([(-0.72, 0.02, -0.06, 0.03), (-0.68, 0.09, -0.12, 0.08), (-0.55, 0.16, -0.17, 0.12), (-0.4, 0.2, -0.2, 0.13),
                  (-0.15, 0.21, -0.21, 0.13), (0.1, 0.17, -0.17, 0.1), (0.3, 0.11, -0.11, 0.07), (0.45, 0.07, -0.07, 0.045),
                  (0.6, 0.05, -0.05, 0.03), (0.68, 0.04, -0.04, 0.02)])


def skin(co):
    zt, zb = OUT.top(co.y), OUT.bot(co.y)
    z = (co.z - (zt + zb) * 0.5) / max(0.01, (zt - zb) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.8, -0.2, z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.3, 0.9, z))
    blot = nh.smoothstep(0.3, 0.5, noise.noise(Vector((co.x * 3.0, co.y, co.z)) * 16.0))
    c = nh.lerp(c, BLOTCH, 0.55 * blot * nh.smoothstep(-0.6, 0.0, z))
    # round scales
    s = math.sin(co.y * 60) * math.sin(co.z * 60)
    c = tuple(v * (0.9 + 0.1 * s) for v in c)
    return c


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.10, 0.12, 0.18), v * 0.6)


def lobe_fin(mb, base, tip, r, blade_len, blade_w, color):
    """A fleshy, scaled stalk ending in a fan of fin rays (a lobed fin)."""
    b, t = Vector(base), Vector(tip)
    mb.add(nh.tube([b, b.lerp(t, 0.5), t], [r, r * 0.8, r * 0.5], sides=8), FLANK)
    d = (t - b).normalized()
    side = d.cross(Vector((1, 0, 0)))
    if side.length < 1e-3:
        side = Vector((0, 0, 1))
    side.normalize()
    out = [t + side * blade_w * 0.3, t + d * blade_len * 0.6 + side * blade_w * 0.5, t + d * blade_len,
           t + d * blade_len * 0.6 - side * blade_w * 0.5, t - side * blade_w * 0.3]
    fish.fin(mb, [tuple(out[0]), tuple(t), tuple(out[4])], [tuple(out[1]), tuple(out[2]), tuple(out[3])], color, rows=3, th0=0.012, th1=0.004)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin, stations=120, ring=40)
    # spiny first dorsal
    jf.midfin(mb, [(-0.22, OUT.top(-0.22) - 0.01), (-0.08, OUT.top(-0.08) - 0.01)], [(-0.16, OUT.top(-0.22) + 0.13), (-0.04, OUT.top(-0.08) + 0.03)], fin_col)
    # lobed second dorsal and anal fins
    lobe_fin(mb, (0, 0.22, OUT.top(0.22) - 0.02), (0, 0.29, OUT.top(0.22) + 0.06), 0.022, 0.12, 0.08, fin_col)
    lobe_fin(mb, (0, 0.22, OUT.bot(0.22) + 0.02), (0, 0.29, OUT.bot(0.22) - 0.06), 0.022, 0.12, 0.08, fin_col)
    # three-lobed tail: upper and lower fans plus the small central lobe
    jf.midfin(mb, [(0.45, 0.065), (0.6, 0.045)], [(0.55, 0.22), (0.75, 0.13)], fin_col, th0=0.018)
    jf.midfin(mb, [(0.45, -0.065), (0.6, -0.045)], [(0.55, -0.22), (0.75, -0.13)], fin_col, th0=0.018)
    mb.add(nh.tube([(0, 0.66, 0.0), (0, 0.8, 0.0)], [0.02, 0.008], sides=6), FLANK)
    jf.midfin(mb, [(0.78, 0.008), (0.8, -0.008)], [(0.88, 0.04), (0.88, -0.04)], fin_col, th0=0.01)
    # lobed pectoral and pelvic fins
    for sx in (1, -1):
        lobe_fin(mb, (sx * 0.1, -0.38, -0.08), (sx * 0.17, -0.3, -0.13), 0.022, 0.12, 0.07, fin_col)
        lobe_fin(mb, (sx * 0.07, 0.0, -0.18), (sx * 0.12, 0.07, -0.24), 0.02, 0.1, 0.06, fin_col)
        pts = []
        for k in range(8):
            z = -0.15 + k * 0.042
            y = -0.47 + 0.03 * math.sin(k / 7 * math.pi)
            pts.append((sx * (fish.surface_x(OUT.top, OUT.bot, OUT.width, y, z) + 0.002), y, z))
        mb.add(nh.tube(pts, [0.006] * len(pts), sides=4), (0.08, 0.10, 0.14))
    fish.eyes(mb, -0.6, 0.05, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.6, 0.05), 0.026, (0.55, 0.80, 0.75))
    return kit.finish(mb, "Undina", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Undina", **fish.PREVIEW)
