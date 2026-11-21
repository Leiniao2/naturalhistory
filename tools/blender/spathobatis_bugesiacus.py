"""
Procedural Spathobatis bugesiacus (Late Jurassic guitarfish, France and Germany) for map colonies.

One of the earliest rays, about 1-1.5 m long, built like a living guitarfish: a flattened,
spade-shaped front made of the pointed snout and broad pectoral fins fused to the head,
eyes and spiracles on top, mouth and gill slits underneath, then a thick, shark-like rear
body with two dorsal fins and a small tail fin. It lay half-buried on sandy lagoon floors
and crushed shellfish and crustaceans. Painted sandy grey-brown with fine pale speckles
above and a white belly. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/spathobatis_bugesiacus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Spathobatis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.50, 0.42, 0.32)
DARK = (0.34, 0.28, 0.20)
BELLY = (0.94, 0.92, 0.88)
SPECK = (0.80, 0.74, 0.60)


def skin(co, n):
    c = nh.lerp(BELLY, TOP, nh.smoothstep(-0.35, 0.1, n.z))
    if n.z > 0:
        c = nh.lerp(c, DARK, 0.4 * nh.smoothstep(0.1, 0.5, noise.noise(co * 6)))
        c = nh.lerp(c, SPECK, 0.8 * nh.smoothstep(0.45, 0.6, noise.noise(co * 60)))
    return c


def disc_outline():
    """Plan view of the snout + pectoral disc (y from snout tip -1.0 back to 0.0)."""
    pts = []
    for i in range(25):
        t = i / 24
        y = -1.0 + 1.0 * t
        # pointed wedge snout widening into rounded pectorals, tapering at the back
        w = 0.36 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.8 * (0.55 + 0.45 * nh.smoothstep(0.1, 0.6, t))
        pts.append((w, y))
    return pts


def build():
    fused = []
    # flattened disc as a stack of thin lofted rows along Y
    outline = disc_outline()
    secs = []
    for x, y in outline:
        h = 0.012 + 0.035 * nh.smoothstep(-1.0, -0.4, y)
        secs.append(((0.0, y, 0.0), max(0.0, x), h))
    secs[0] = ((0.0, -1.0, 0.0), 0.0, 0.0)
    fused.append(kit.loft(secs, sides=20, power=2.6))
    # thick body and tail
    rows = [(0, -0.75, 0.01, 0.06, 0.04), (0, -0.45, 0.02, 0.11, 0.06), (0, -0.15, 0.02, 0.1, 0.06), (0, 0.15, 0.02, 0.07, 0.05),
            (0, 0.45, 0.02, 0.04, 0.035), (0, 0.7, 0.025, 0.022, 0.022), (0, 0.85, 0.03, 0.0, 0.0)]
    sp = kit.Spine(rows)
    fused.append(sp.mesh(sides=16))
    # pelvic fins
    for sx in (1, -1):
        fused.append(nh.ellipsoid((sx * 0.12, 0.08, -0.005), (0.07, 0.1, 0.01), subdivisions=2))
    body = kit.fuse_parts(fused, 0.009, 9000)
    mb = nh.MeshBuilder()
    mb.add(body, skin)
    # two dorsal fins and the tail fin
    for y0, h in ((0.3, 0.09), (0.52, 0.07)):
        mb.add(kit.blade([(y0, 0.03), (y0 + 0.05, 0.03 + h), (y0 + 0.1, 0.03 + h * 0.85), (y0 + 0.12, 0.02)], 0.01), TOP)
    mb.add(kit.blade([(0.68, 0.035), (0.86, 0.1), (0.9, 0.03), (0.84, -0.02), (0.72, 0.01)], 0.008), TOP)
    # eyes and spiracles on top
    for sx in (1, -1):
        e = Vector((sx * 0.05, -0.55, 0.055))
        mb.add(nh.ellipsoid(e, (0.014, 0.018, 0.012), subdivisions=2), (0.80, 0.70, 0.40))
        mb.add(nh.ellipsoid(e + Vector((sx * 0.003, -0.003, 0.009)), (0.007, 0.008, 0.005), subdivisions=1), (0.02, 0.02, 0.02))
        mb.add(nh.ellipsoid((sx * 0.055, -0.5, 0.055), (0.01, 0.008, 0.004), subdivisions=1), DARK)
        # gill slits underneath
        for k in range(5):
            mb.add(nh.ellipsoid((sx * (0.07 + k * 0.006), -0.42 + k * 0.03, -0.035), (0.016, 0.003, 0.002), subdivisions=1), (0.6, 0.55, 0.5))
    return kit.finish(mb, "Spathobatis", pivot="center", roughness=0.55)


if __name__ == "__main__":
    nh.run(build, "Spathobatis", background=(0.04, 0.10, 0.13), views=((35, 35), (-90, 5), (0, 80)))
