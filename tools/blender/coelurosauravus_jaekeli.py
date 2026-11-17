"""
Procedural Coelurosauravus jaekeli (Late Permian weigeltisaurid, ~40 cm) gliding, for map
colonies.

One of the earliest gliding vertebrates: a slim, lizard-like reptile with a long tail and a
pair of gliding "wings" - skin membranes stretched over some two dozen long, slender rods
of dermal bone fanning out from each flank (not ribs, as in modern Draco lizards). The
back of the skull carries a frill of spiky bony points. Shown in a glide with the wings
spread flat and the legs splayed. Brown body with darker banding; the membranes are
orange-brown with dark rods and dark trailing edges.
Built with nh_per_tetra. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/coelurosauravus_jaekeli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Coelurosauravus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402

ROD = (0.18, 0.12, 0.08)
WING = (0.70, 0.44, 0.22)
EDGE = (0.30, 0.18, 0.10)
FRILL = (0.42, 0.30, 0.18)
RODS = 14


def rod_end(sx, i):
    """Wing rods fan out from the flank, swept a little back; the wing is broadest mid-way."""
    t = i / (RODS - 1)
    y0 = -0.26 + 0.40 * t
    ang = math.radians(-12 + 52 * t)      # sweep back
    ln = 0.30 + 0.20 * math.sin(math.pi * (0.15 + 0.7 * t))
    base = V((sx * 0.055, y0, 0.012))
    return base, base + V((sx * ln * math.cos(ang), ln * math.sin(ang), 0.025))


def crisp(mb, spec):
    for sx in (1, -1):
        outline = []
        for i in range(RODS):
            outline.append(rod_end(sx, i)[1])
        base_pts = [rod_end(sx, i)[0] for i in range(RODS)][::-1]
        poly = outline + base_pts
        if sx < 0:
            poly = poly[::-1]

        def wcol(co, n, sx=sx):
            r = abs(co.x)
            return nh.lerp(WING, EDGE, nh.smoothstep(0.30, 0.48, r + 0.15 * max(0.0, co.y)))
        mb.add(pt.membrane(poly, 0.005), wcol, smooth=False)
        for i in range(RODS):
            a, b = rod_end(sx, i)
            mb.add(nh.tube([a + V((0, 0, 0.004)), b + V((0, 0, 0.004))], [0.004, 0.0015], sides=5), ROD)
    # spiky frill at the back of the skull
    for k in range(7):
        t = k / 6
        a = math.radians(-70 + 140 * t)
        base = V((0.035 * math.sin(a), -0.42 + 0.02 * math.cos(a), 0.025))
        tip = base + V((0.05 * math.sin(a), 0.045, 0.02 + 0.01 * math.cos(a)))
        mb.add(pt.cone(base, tip, 0.007), FRILL, smooth=False)


SPEC = pt.Spec(
    name="Coelurosauravus",
    torso=[
        (-0.40, 0.0, 0.040, 0.035),
        (-0.30, 0.0, 0.060, 0.045),
        (-0.10, 0.0, 0.068, 0.045),
        (0.10, 0.0, 0.060, 0.042),
        (0.20, 0.0, 0.040, 0.033),
        (0.45, 0.0, 0.022, 0.019),
        (0.80, 0.0, 0.010, 0.009),
        (1.00, 0.0, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.012, 0.045, 0.035),
        (-0.46, 0.012, 0.040, 0.030),
        (-0.54, 0.004, 0.026, 0.020),
        (-0.59, 0.0, 0.0, 0.0),
    ],
    fore=pt.Limb(y=-0.28, z=-0.01, x=0.045, upper=0.07, lower=0.07, sprawl=1.0, r=0.012, grounded=False,
                 foot=(0.012, 0.016, 0.005), toe_len=0.02, toe_r=0.003, claw=0.0),
    hind=pt.Limb(y=0.17, z=-0.01, x=0.04, upper=0.08, lower=0.08, sprawl=1.0, r=0.015, grounded=False,
                 foot=(0.013, 0.018, 0.005), toe_len=0.025, toe_r=0.0035, claw=0.0),
    eye=(0.032, -0.47, 0.022, 0.011),
    back=(0.32, 0.22, 0.14), flank=(0.44, 0.32, 0.20), belly=(0.80, 0.70, 0.54), mark=(0.15, 0.10, 0.06),
    pattern="bands", pattern_freq=30.0, pattern_amount=0.55,
    crisp=crisp, pivot="centre", voxel=0.0045, max_tris=5000,
    preview=dict(views=((35, 30), (0, 80), (-90, 8))),
)

if __name__ == "__main__":
    pt.main(SPEC)
