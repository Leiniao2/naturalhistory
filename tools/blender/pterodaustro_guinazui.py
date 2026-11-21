"""
Procedural Pterodaustro guinazui (Early Cretaceous ctenochasmatid pterosaur, Lagarcito
Formation, Argentina).

A flamingo-like filter-feeding pterosaur with a 2.5-metre wingspan: a very long, slender
head whose jaws curve upwards towards the tip, the lower jaw lined with a dense comb of
about a thousand long, fine, bristle-like teeth for sieving water; a long neck, a small
furry body, broad membranous wings and short legs. Pink-tinged pale body and wing
membrane fading to rose at the wingtips, a dusky bill (pink colour conjectural, from its
flamingo-like diet).
Faces -Y, pivot at the body centre (Soar style).

Usage:
  blender --background --python tools/blender/pterodaustro_guinazui.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pterodaustro.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BODY = (0.90, 0.60, 0.58)
BELLY = (0.97, 0.90, 0.86)
WING = (0.86, 0.55, 0.52)
WING_TIP = (0.66, 0.26, 0.30)
BILL = (0.30, 0.24, 0.24)
BRISTLE = (0.95, 0.92, 0.85)


def body_paint(co, n):
    c = cc.countershade(n, BELLY, BODY, BODY)
    if co.y < -0.36:
        c = nh.lerp(c, BILL, nh.smoothstep(-0.40, -0.55, co.y))
    return cc.mottle(c, co, 0.06)


def wing_col(co, n):
    c = nh.lerp(WING, WING_TIP, nh.smoothstep(0.7, 1.5, abs(co.x)))
    if n.z < -0.3:
        c = nh.lerp(c, BELLY, 0.4)
    return cc.mottle(c, co, 0.08, 5.0)


def make():
    # tail stub -> body -> long neck -> long, up-curved bill
    axis = [(0.22, 0.0, 0.0, 0.0), (0.18, 0.0, 0.015, 0.015), (0.10, 0.0, 0.055, 0.05),
            (0.0, 0.0, 0.07, 0.06), (-0.08, 0.01, 0.055, 0.05), (-0.16, 0.035, 0.025, 0.025),
            (-0.26, 0.06, 0.022, 0.022), (-0.32, 0.07, 0.026, 0.03), (-0.40, 0.068, 0.016, 0.02),
            (-0.52, 0.068, 0.011, 0.013), (-0.62, 0.078, 0.008, 0.009), (-0.68, 0.098, 0.0, 0.0)]
    f = fl.Flier(name="Pterodaustro", axis=axis, paint=body_paint, eye=(0.022, -0.335, 0.085, 0.008),
                 eye_col=(0.10, 0.06, 0.04), disp=cc.fuzz_disp(0.003, 60.0))
    f.blobs.append(((0.06, -0.05, 0.02), (0.05, 0.05, 0.035), True))
    lead = [(0.05, -0.06, 0.02), (0.28, -0.10, 0.05), (0.48, -0.07, 0.06), (0.85, 0.0, 0.08), (1.3, 0.10, 0.12)]
    trail = [(0.05, 0.12, 0.0), (0.25, 0.17, 0.02), (0.48, 0.15, 0.04), (0.85, 0.12, 0.07), (1.3, 0.11, 0.12)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.012, nv=7, billow=0.015,
                           bone=((0.70, 0.45, 0.42), 0.02)))
    f.tubes.append(([(0.05, 0.10, -0.01), (0.07, 0.20, -0.02), (0.07, 0.28, -0.02)], [0.018, 0.011, 0.007], True))

    def crisp(mb, f):
        # the lower jaw: a long, thin, up-curved rod below the bill
        pts = cc.bezier_pts((0, -0.36, 0.045), (0, -0.58, 0.04), (0, -0.67, 0.09), 10)
        mb.add(nh.tube(pts, [0.013, 0.012, 0.011, 0.01, 0.009, 0.008, 0.007, 0.006, 0.004, 0.0], sides=7), BILL)
        # the comb of fine bristle teeth hanging from the lower jaw
        for i, p in enumerate(pts[1:-2]):
            for k in range(4):
                q = p + Vector((0, 0.008 * k, 0))
                for sx in (1, -1):
                    mb.add(cc.cone(q + Vector((sx * 0.004, 0, -0.004)), q + Vector((sx * 0.006, 0.003, -0.03)), 0.0018,
                                   sides=3), BRISTLE, smooth=False)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Pterodaustro")
