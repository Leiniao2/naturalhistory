"""
Procedural Collinsium ciliosum (early Cambrian luolishaniid lobopodian, Xiaoshiba, Yunnan).

A soft, annulated worm-like body ~8.5 cm long, its back bristling with 72 sharp spines in
transverse rows of up to five per segment (the middle ones longest). Six pairs of long,
slender front legs fringed with fine setae are raised up and forward like a feeding basket;
nine pairs of stout, clawed hind legs grip the seabed. Dark purplish-grey body, amber
spines with pale tips. Swim style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/collinsium_ciliosum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Collinsium.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.40, 0.32, 0.40)
DARK = (0.24, 0.18, 0.24)
BELLY = (0.62, 0.52, 0.56)
SPINE = (0.72, 0.48, 0.20)
SPINE_TIP = (0.95, 0.88, 0.70)
LEG = (0.56, 0.46, 0.52)
SETA = (0.86, 0.80, 0.76)
CLAW = (0.20, 0.14, 0.10)


def zline(y):
    # front end raised (feeding posture), rear on the bottom
    return 0.18 * nh.smoothstep(0.1, -0.6, y)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    for i in range(41):
        y = -0.7 + 1.4 * i / 40
        pts.append((0, y, zline(y)))
        radii.append(0.06 * (0.9 if i % 2 else 1.0) * (1 - 0.4 * max(0.0, (y - 0.4) / 0.3)))
    radii[0], radii[-1] = 0.035, 0.02
    mb.add(nh.tube(pts, radii, sides=10), ec.banded(BODY, DARK, BELLY, -0.7, 1.4 / 20, amount=0.5))
    mb.add(nh.uv_ellipsoid((0, -0.73, zline(-0.73) + 0.01), (0.04, 0.05, 0.035), segments=10, rings=6), BODY)
    # 15 leg-bearing segments: 6 setose front pairs, 9 clawed rear pairs
    for i in range(15):
        y = -0.62 + i * 0.085
        z = zline(y)
        for s in (-1, 1):
            if i < 6:
                b = Vector((s * 0.045, y, z - 0.02))
                tip = b + Vector((s * 0.09, -0.2, 0.18))
                mb.add(nh.tube(kit.curve(b, b + Vector((s * 0.06, -0.06, 0.04)), tip, 5),
                               [0.014, 0.012, 0.01, 0.008, 0.006, 0.0], sides=5), LEG)
                for q in range(1, 6):
                    p = Vector(b).lerp(tip, q / 6)
                    for side in (-1, 1):
                        mb.add(ec.spike(p, p + Vector((side * 0.025, 0.01, 0.0)), r=0.0025, sides=3), SETA, smooth=False)
            else:
                kit.lobopod(mb, (s * 0.045, y, z - 0.03), (s * 0.5, 0.05, -1), 0.1, 0.022, LEG, claw=CLAW, rings=3)
    # dorsal spines: 72 in rows of up to five across the back
    count = 0
    rows = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2]
    for r, k in enumerate(rows):
        y = -0.6 + r * 0.075
        z = zline(y)
        for j in range(k):
            if count >= 72:
                break
            off = (j - (k - 1) / 2)
            ln = 0.16 - 0.04 * abs(off)
            base = Vector((off * 0.022, y, z + 0.05))
            d = Vector((off * 0.35, 0.15, 1.0)).normalized()
            mb.add(ec.spike(base, base + d * ln, r=0.007, sides=4),
                   lambda co, n, b=base, ln=ln: nh.lerp(SPINE, SPINE_TIP, nh.smoothstep(0.5, 1.0, (co - b).length / ln)),
                   smooth=False)
            count += 1
    return ec.centre(mb.to_object("Collinsium", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Collinsium")
