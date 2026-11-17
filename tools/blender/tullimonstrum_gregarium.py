"""
Procedural Tullimonstrum gregarium, the "Tully monster" (Late Carboniferous of Mazon Creek,
Illinois, a soft-bodied swimming animal of uncertain affinity, up to about 35 cm long) for
map colonies (Swim style).

A segmented, torpedo-shaped soft body; in front a long, slender, flexible proboscis ending in
a small claw lined with tiny teeth; just behind the proboscis a stiff transverse bar sticking
out to both sides with an eye at each end; at the back a rhomboid tail fin spread
horizontally. Grey-brown with darker segment bands. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/tullimonstrum_gregarium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tullimonstrum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_arthropod as ar  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Tullimonstrum"
BODY = (0.44, 0.38, 0.32)
BAND = (0.30, 0.25, 0.21)
BELLY = (0.70, 0.64, 0.56)
BAR = (0.38, 0.33, 0.28)
FIN = (0.34, 0.29, 0.25)
EYE = (0.05, 0.05, 0.06)
TOOTH = (0.88, 0.85, 0.76)


def build():
    parts = []
    # trunk: tapering torpedo along Y, a little flattened
    pts, radii = [], []
    for i in range(16):
        t = i / 15
        y = -0.26 + t * 0.72
        r = 0.07 * math.sin(math.pi * (0.12 + 0.88 * t) ** 0.8) + 0.01
        pts.append((0, y, 0))
        radii.append(r)
    parts.append((nh.tube(pts, radii, sides=16, scale_xy=(1.0, 0.8)), BODY))
    # proboscis: slender, gently drooping
    prob = [(0, -0.24, 0.0), (0, -0.36, -0.01), (0, -0.48, -0.03), (0, -0.58, -0.06), (0, -0.64, -0.09)]
    parts.append((nh.tube(prob, [0.03, 0.014, 0.012, 0.011, 0.012], sides=8), BODY))
    # eye bar
    parts.append((nh.tube([(-0.2, -0.17, 0.055), (0, -0.17, 0.04), (0.2, -0.17, 0.055)], [0.013, 0.016, 0.013],
                          sides=8), BAR))
    # tail fin: rhomboid, horizontal
    parts.append((cf.panel([(0, 0.36, 0), (0.12, 0.47, 0), (0, 0.66, 0), (-0.12, 0.47, 0)], (0, 0, 1), 0.016), FIN))
    fused = ar.fuse_parts(parts, voxel=0.006, max_tris=5000)
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            co = l.vert.co
            if -0.15 < co.y < 0.38 and abs(co.x) < 0.09:
                c = BODY
                if ((co.y + 0.15) / 0.04) % 1.0 < 0.3:
                    c = BAND
                c = nh.lerp(c, BELLY, nh.smoothstep(-0.01, -0.05, co.z))
                l[col] = (*c, 1.0)
    details = []
    for sx in (-1, 1):
        details.append(ar.eye((sx * 0.215, -0.17, 0.057), 0.024, (sx, -0.2, 0.2), iris=EYE, pupil=(0.2, 0.18, 0.12)))
        # claw: two little jaws at the tip of the proboscis
        base = Vector((0, -0.64, -0.09))
        tip = base + Vector((sx * 0.025, -0.05, -0.01))
        details.append((nh.tube([base, base + Vector((sx * 0.03, -0.025, 0)), tip], [0.01, 0.008, 0.002], sides=5), BAR))
        for k in range(3):
            p = base.lerp(tip, 0.4 + 0.2 * k)
            details.append((nh.tube([p, p + Vector((-sx * 0.012, -0.002, 0))], [0.003, 0.0], sides=3), TOOTH))
    return ar.finish(fused, details, NAME, ground=False)


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.06, 0.18, 0.24), views=((35, 30), (-90, 8), (0, 80)))
