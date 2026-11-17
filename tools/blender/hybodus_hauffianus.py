"""
Procedural Hybodus hauffianus (Early Jurassic hybodont shark, Holzmaden, Germany) for map colonies.

A hybodont, a shark from an extinct side branch, about 2 m long and known from complete
skeletons in the Posidonia Shale: a blunt, rounded snout with the mouth near the front,
two tall dorsal fins each with a stout, grooved bony spine at its leading edge, broad
pectoral fins, and a strongly heterocercal tail with a long upper lobe. Males had hooked
head spines above the eyes. Grey-brown above with a pale belly. Built with nh_jur_fish
(nh_fish). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/hybodus_hauffianus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hybodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_fish as jf  # noqa: E402
from mathutils import Vector  # noqa: E402

BACK = (0.30, 0.29, 0.26)
FLANK = (0.48, 0.46, 0.41)
BELLY = (0.88, 0.86, 0.80)
FIN = (0.32, 0.30, 0.27)
SPINE = (0.82, 0.76, 0.62)

OUT = jf.Outline([(-0.9, 0.0, -0.02, 0.01), (-0.86, 0.05, -0.06, 0.06), (-0.75, 0.1, -0.1, 0.1), (-0.55, 0.13, -0.12, 0.13),
                  (-0.3, 0.135, -0.12, 0.13), (0.0, 0.11, -0.1, 0.1), (0.3, 0.07, -0.06, 0.06), (0.5, 0.05, -0.03, 0.035),
                  (0.7, 0.06, 0.0, 0.02), (0.95, 0.12, 0.08, 0.008)])


def skin(co):
    z = (co.z - (OUT.top(co.y) + OUT.bot(co.y)) * 0.5) / max(0.01, (OUT.top(co.y) - OUT.bot(co.y)) * 0.5)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.6, -0.1, z))
    return nh.lerp(c, BACK, nh.smoothstep(0.1, 0.7, z))


def fin_col(u, v, co):
    return nh.lerp(FIN, (0.2, 0.19, 0.17), v)


def build():
    mb = nh.MeshBuilder()
    OUT.body(mb, skin)
    # dorsal fins (with spines)
    for y0, y1, h in ((-0.32, -0.08, 0.2), (0.22, 0.42, 0.15)):
        base = [(y0 + (y1 - y0) * t, OUT.top(y0 + (y1 - y0) * t) - 0.01) for t in (0, 0.33, 0.66, 1)]
        edge = [(y0 + 0.08, OUT.top(y0) + h), (y0 + 0.13, OUT.top(y0) + h * 0.92), (y1, OUT.top(y1) + h * 0.45), (y1 + 0.06, OUT.top(y1) + 0.02)]
        jf.midfin(mb, base, edge, fin_col)
        b = Vector((0, y0, OUT.top(y0) - 0.01))
        mb.add(kit.cone(b, Vector((0, y0 + 0.07, OUT.top(y0) + h * 1.02)), 0.014, sides=6), SPINE, smooth=False)
    # heterocercal caudal: long upper lobe, smaller lower lobe
    base = [(0.55 + 0.4 * t, OUT.bot(0.55 + 0.4 * t) + 0.01) for t in (0, 0.33, 0.66, 1)]
    edge = [(0.68, -0.11), (0.76, -0.1), (0.9, 0.02), (1.08, 0.2)]
    jf.midfin(mb, base, edge, fin_col)
    jf.midfin(mb, [(0.62, OUT.top(0.62) - 0.01), (0.95, OUT.top(0.95) - 0.005)], [(0.75, OUT.top(0.75) + 0.05), (1.08, 0.2)], fin_col)
    # anal fin
    jf.midfin(mb, [(0.3, OUT.bot(0.3) + 0.01), (0.42, OUT.bot(0.42) + 0.01)], [(0.38, OUT.bot(0.3) - 0.07), (0.46, OUT.bot(0.42) - 0.03)], fin_col)
    # pectoral and pelvic fins
    jf.pairfin(mb, [(0.1, -0.55, -0.08), (0.1, -0.38, -0.08)], [(0.36, -0.36, -0.17), (0.3, -0.26, -0.15)], fin_col)
    jf.pairfin(mb, [(0.06, 0.08, -0.07), (0.05, 0.2, -0.06)], [(0.18, 0.2, -0.12), (0.12, 0.26, -0.1)], fin_col)
    # gill slits, eyes, mouth
    for i in range(5):
        y = -0.62 + i * 0.035
        for sx in (1, -1):
            x = fish.surface_x(OUT.top, OUT.bot, OUT.width, y, -0.03)
            mb.add(nh.tube([(sx * x, y, 0.03), (sx * x, y + 0.01, -0.07)], [0.004, 0.004], sides=4), (0.14, 0.13, 0.12))
    fish.eyes(mb, -0.74, 0.04, fish.surface_x(OUT.top, OUT.bot, OUT.width, -0.74, 0.04), 0.014, (0.7, 0.6, 0.3))
    for sx in (1, -1):
        mb.add(nh.tube([(0, -0.86, -0.05), (sx * 0.06, -0.8, -0.075)], [0.006, 0.005], sides=4), (0.15, 0.08, 0.08))
    return kit.finish(mb, "Hybodus", pivot="center", roughness=0.5)


if __name__ == "__main__":
    nh.run(build, "Hybodus", **fish.PREVIEW)
