"""
Procedural blue whale (Balaenoptera musculus, Pleistocene to today, all oceans)
for map colonies.

The largest animal that has ever lived, up to about 30 m long and 150-190
tonnes, a rorqual that lunges through swarms of krill with its throat pleats
ballooning, taking up to 4 tonnes of krill a day. A long, slender, streamlined
body, a broad, flat, U-shaped head with a central ridge leading to the
blowholes, a tiny dorsal fin far back, slim flippers and wide flukes. Mottled
blue-grey skin, paler below, with dozens of long throat grooves.

Reuses the cetacean loft from delphinus_delphis.py with rorqual proportions,
fins and colours. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/balaenoptera_musculus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BalaenopteraMusculus.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import delphinus_delphis as dd  # noqa: E402

BLUE = (0.36, 0.45, 0.56)
DARK = (0.22, 0.29, 0.38)
PALE = (0.62, 0.68, 0.74)
GROOVE = (0.20, 0.24, 0.30)

# long slender body; the head broad and flat on top, the throat deep
dd.HALF_W = [(-1.0, 0.03), (-0.97, 0.065), (-0.90, 0.095), (-0.78, 0.115), (-0.60, 0.125), (-0.40, 0.13),
             (-0.15, 0.125), (0.10, 0.105), (0.35, 0.075), (0.55, 0.045), (0.70, 0.028), (0.80, 0.024)]
dd.HALF_H_TOP = [(-1.0, 0.012), (-0.97, 0.025), (-0.90, 0.040), (-0.78, 0.060), (-0.62, 0.085), (-0.40, 0.11),
                 (-0.15, 0.115), (0.10, 0.105), (0.35, 0.08), (0.55, 0.06), (0.70, 0.04), (0.80, 0.026)]
dd.HALF_H_BOT = [(-1.0, 0.015), (-0.97, 0.035), (-0.90, 0.06), (-0.78, 0.09), (-0.62, 0.115), (-0.40, 0.12),
                 (-0.15, 0.11), (0.10, 0.09), (0.35, 0.065), (0.55, 0.045), (0.70, 0.032), (0.80, 0.025)]
dd.CENTER_Z = [(-1.0, -0.01), (-0.80, 0.0), (0.8, 0.0)]
dd.Y_MELON = -2.0


def dorsal():
    """Tiny, slightly hooked dorsal fin three-quarters of the way back."""
    base_z = lambda y: dd.zc(y) + dd.ht(y) - 0.015  # noqa: E731
    front, back = (0.38, base_z(0.38)), (0.50, base_z(0.50))
    apex = (0.50, dd.ht(0.47) + 0.05)
    notch = (0.49, base_z(0.49) + 0.015)
    pts = [front] + dd.curve(front, apex, 0.06, 6) + dd.curve(apex, notch, -0.1, 4) + [notch, back]
    pts += dd.curve(back, front, 0.0, 3)[1:]
    th = [0.035 for _p in pts]
    return dd.fin_slab(pts, th, lambda u, v: (Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))))


def flipper(sign):
    """Slim, pointed pectoral flipper."""
    droop, sweep = math.radians(30), 1.1
    def frame(u, v):
        x = sign * (dd.w(u) * 0.75 + v * math.cos(droop))
        z = dd.zc(u) - dd.hb(u) * 0.5 - v * math.sin(droop)
        return Vector((x, u + v * sweep, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    a, b = (-0.62, 0.0), (-0.56, 0.0)
    tip = (-0.60, 0.20)
    pts = [a] + dd.curve(a, tip, 0.08, 7) + dd.curve(tip, b, 0.06, 6) + [b]
    th = [0.03 - 0.015 * min(1.0, v / 0.2) for _u, v in pts]
    return dd.fin_slab(pts, th, frame)


def flukes():
    half = [(0.0, 0.76), (0.03, 0.79)] + dd.curve((0.03, 0.79), (0.26, 0.98), -0.08, 9) \
        + dd.curve((0.26, 0.98), (0.02, 0.95), -0.04, 8) + [(0.02, 0.95), (0.0, 0.93)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    th = [0.04 - 0.02 * min(1.0, abs(x) / 0.26) for x, _y in pts]
    return dd.fin_slab(pts, th, lambda u, v: (Vector((u, v, dd.zc(dd.Y_PED))), Vector((0.0, 0.0, 1.0))))


def body_color(p, n):
    y = p.y
    mott = noise.noise(p * 18.0)
    base = nh.lerp(BLUE, PALE, 0.5 * nh.smoothstep(0.2, 0.7, mott))
    base = nh.lerp(base, DARK, 0.4 * nh.smoothstep(0.0, -0.6, noise.noise(p * 7.0 + Vector((3, 1, 2)))))
    if dd.outside(p) > 0.008 or y > dd.Y_PED + 0.02:
        return nh.lerp(base, PALE, 0.5) if n.z < -0.3 else DARK
    r = dd.rel_z(p)
    col = nh.lerp(base, PALE, 0.6 * nh.smoothstep(-0.2, -0.8, r))
    # throat grooves: many long pale-dark furrows from the chin back to the navel
    if y < -0.10 and r < -0.30:
        xx = p.x / max(dd.w(y), 1e-3)
        g = 0.5 + 0.5 * math.cos(xx * 34.0)
        col = nh.lerp(col, GROOVE, 0.55 * nh.smoothstep(0.75, 0.95, g) * nh.smoothstep(-0.10, -0.25, y))
    # dark lip line
    col = nh.lerp(col, (0.10, 0.12, 0.16), 1.0 - nh.smoothstep(0.02, 0.07, abs(r + 0.25 + 0.0 * y)) if y < -0.72 else 0.0)
    return col


def details(mb):
    # splash-guard ridge and the paired blowholes on top of the head
    for k in range(10):
        y = -0.97 + k * 0.025
        mb.add(nh.ellipsoid((0, y, dd.zc(y) + dd.ht(y) - 0.002), (0.010, 0.014, 0.007), subdivisions=1), DARK)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.012, -0.72, dd.zc(-0.72) + dd.ht(-0.72)), (0.008, 0.016, 0.005), subdivisions=1),
               (0.05, 0.06, 0.08))


dd.dorsal, dd.flipper, dd.flukes, dd.body_color = dorsal, flipper, flukes, body_color


def build():
    obj = dd.build()
    import nh_b2_quaternary_kit  # noqa: F401  (keeps the batch's helpers on the path)
    import bpy
    mb = nh.MeshBuilder()
    details(mb)
    extra = mb.to_object("ridge")
    bpy.ops.object.select_all(action="DESELECT")
    extra.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    obj.name = "BalaenopteraMusculus"
    return obj


if __name__ == "__main__":
    nh.run(build, "BalaenopteraMusculus", background=(0.05, 0.18, 0.24), views=((35, 25), (-90, 4), (180, -40)))
