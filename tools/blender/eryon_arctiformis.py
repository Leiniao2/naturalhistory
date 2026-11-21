"""
Procedural Eryon arctiformis (Late Jurassic polychelidan lobster, Solnhofen, Germany) for map colonies.

A flat, broad-bodied lobster about 10-15 cm long, a relative of today's blind deep-sea
lobsters: a wide, almost rectangular, flattened carapace with notched, saw-toothed side
margins and small eyes in notches at the front corners, a short, tapering abdomen tucked
behind it ending in a broad tail fan, and four pairs of slender legs ending in pincers, the
first pair long and thin with elongated claws. It crawled over the soft lagoon floor.
Painted sandy orange-brown with paler joints. Faces -Y, pivot at the body centre (Swim style,
like the other seabed crustaceans).

Usage:
  blender --background --python tools/blender/eryon_arctiformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eryon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.72, 0.46, 0.26)
DARK = (0.46, 0.26, 0.14)
LEG = (0.82, 0.62, 0.42)
PALE = (0.92, 0.82, 0.66)


def shell_col(co, n):
    c = nh.lerp(PALE, SHELL, nh.smoothstep(-0.5, 0.3, n.z))
    # dark rim and a faint midline groove
    rim = nh.smoothstep(0.18, 0.23, abs(co.x)) if co.y < 0.08 else 0.0
    c = nh.lerp(c, DARK, 0.6 * rim)
    if co.y > 0.08 and math.sin(co.y * 75) > 0.75:
        c = DARK
    return c


def build():
    fused = []
    # broad, flat carapace: superelliptic slab
    rows = [(0, -0.3, 0.02, 0.0, 0.0), (0, -0.29, 0.02, 0.2, 0.03), (0, -0.2, 0.025, 0.25, 0.045), (0, -0.05, 0.028, 0.26, 0.05),
            (0, 0.06, 0.025, 0.22, 0.045), (0, 0.1, 0.02, 0.1, 0.035), (0, 0.18, 0.012, 0.085, 0.03), (0, 0.27, 0.005, 0.065, 0.024),
            (0, 0.34, 0.0, 0.045, 0.018), (0, 0.38, -0.002, 0.0, 0.0)]
    spine = kit.Spine(rows, steps=3)
    fused.append(spine.mesh(sides=20, power=3.2))
    body = kit.fuse_parts(fused, 0.006, 6000)
    mb = nh.MeshBuilder()
    mb.add(body, shell_col)
    # saw-toothed carapace margins
    for sx in (1, -1):
        for i in range(9):
            y = -0.26 + i * 0.038
            c, tan, hw, hh = spine.at(spine.s_at_y(y))
            b = Vector((sx * (hw - 0.01), y, c.z))
            mb.add(kit.cone(b, b + Vector((sx * 0.03, -0.018, 0.0)), 0.009, sides=3), DARK, smooth=False)
        # eyes in notches at the front corners
        mb.add(nh.ellipsoid((sx * 0.17, -0.29, 0.04), (0.012, 0.012, 0.01), subdivisions=1), (0.1, 0.08, 0.06))
        # antennae (short) and antennules
        mb.add(kit.limb([(sx * 0.05, -0.29, 0.02), (sx * 0.08, -0.38, 0.02), (sx * 0.12, -0.46, 0.015)], [0.006, 0.004, 0.002], sides=4), LEG)
        mb.add(nh.flat_panel([(sx * 0.07, -0.3, 0.02), (sx * 0.13, -0.33, 0.02), (sx * 0.1, -0.36, 0.02)], thickness=0.006), SHELL)
    # tail fan
    mb.add(nh.flat_panel([(0, 0.34, 0.0), (0.06, 0.37, 0.0), (0.09, 0.44, -0.002), (0.03, 0.47, -0.002), (0, 0.45, 0.0),
                          (-0.03, 0.47, -0.002), (-0.09, 0.44, -0.002), (-0.06, 0.37, 0.0)], thickness=0.008), SHELL)
    # legs: first pair long with slender claws held forward, three shorter pairs with small pincers
    for sx in (1, -1):
        b = Vector((sx * 0.1, -0.2, -0.01))
        kn = b + Vector((sx * 0.14, -0.06, -0.01))
        wr = kn + Vector((sx * 0.02, -0.24, 0.0))
        mb.add(kit.limb([b, kn, wr], [0.014, 0.011, 0.01], sides=6), LEG)
        for ds in (0.015, -0.015):
            mb.add(nh.tube([wr, wr + Vector((sx * 0.01 + ds, -0.11, 0.0))], [0.007, 0.0015], sides=4), DARK)
        for k, y in enumerate((-0.12, -0.05, 0.02)):
            b = Vector((sx * 0.1, y, -0.015))
            kn = b + Vector((sx * 0.16, -0.01, 0.0))
            ft = kn + Vector((sx * 0.06, -0.03 + k * 0.015, -0.03))
            mb.add(kit.limb([b, kn, ft], [0.01, 0.008, 0.004], sides=5), LEG)
    return kit.finish(mb, "Eryon", pivot="center", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "Eryon", background=(0.04, 0.10, 0.13), views=((35, 35), (-90, 5), (0, 89)))
