"""
Procedural Icarosaurus siefkeri (Late Triassic kuehneosaurid, ~10 cm body) for map
colonies, gliding with its wings spread.

A small lizard-like gliding reptile from New Jersey, about 220 million years ago. Like the
living flying lizard Draco, its "wings" were skin membranes stretched over very long,
thin ribs sticking out sideways from its trunk, giving a wingspan of about 17 cm; it
glided from tree to tree and ate insects. Small pointed head, slender limbs and a long
tail. Built with the Jurassic flier/glider recipe (nh_jur_flyer.py): lizard body loft,
four short legs and a rounded rib-wing on each side, painted with dark rib struts.
Olive-brown body with pale speckles, orange-amber wings with dark ribs (speculative).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/icarosaurus_siefkeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Icarosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

MEM = (0.86, 0.52, 0.16)
MEM_EDGE = (0.95, 0.78, 0.40)
RIB = (0.22, 0.14, 0.08)
WING_ROOT_Y = -0.03    # centre of the rib fan on the body


def wing_color(co, n):
    ax = abs(co.x)
    a = math.atan2(co.y - WING_ROOT_Y, max(ax, 1e-4))
    k = abs(math.sin(a * 9.0))
    c = nh.lerp(MEM, MEM_EDGE, nh.smoothstep(0.30, 0.46, math.hypot(ax, co.y - WING_ROOT_Y)))
    return nh.lerp(c, RIB, 0.25 * (1.0 - nh.smoothstep(0.0, 0.25, k)) * nh.smoothstep(0.04, 0.08, ax))


def wing_outline():
    pts = [(0.05, -0.16)]
    for i in range(13):
        t = i / 12
        a = math.radians(-58 + 112 * t)
        r = 0.44 * (0.88 + 0.12 * math.sin(math.pi * t))
        pts.append((0.05 + r * math.cos(a), WING_ROOT_Y + r * math.sin(a) * 0.62))
    pts.append((0.05, 0.13))
    return pts


def extras(spine):
    fused = []
    crisp = []
    for sx in (1, -1):
        # forelegs reaching forward under the wing, hind legs back
        fused.append((kit.limb([(sx * 0.030, -0.22, -0.008), (sx * 0.075, -0.25, -0.018), (sx * 0.09, -0.30, -0.02)],
                               [0.011, 0.008, 0.006], sides=8), (0.5,) * 3))
        fused.append((kit.limb([(sx * 0.030, 0.16, -0.008), (sx * 0.085, 0.20, -0.02), (sx * 0.10, 0.27, -0.022)],
                               [0.013, 0.009, 0.006], sides=8), (0.5,) * 3))
        for tip in ((sx * 0.09, -0.30, -0.02), (sx * 0.10, 0.27, -0.022)):
            t = Vector(tip)
            for k in (-1, 0, 1):
                crisp.append((kit.cone(t, t + Vector((sx * 0.012 + k * 0.006, 0.004 if tip[1] > 0 else -0.014, -0.002)),
                                       0.0028, sides=4), kit.CLAW))
    # the elongated ribs that carry the membrane
    outline = wing_outline()[1:-1]
    for sx in (1, -1):
        for i in range(1, len(outline) - 1):
            ex, ey = outline[i]
            root = Vector((0.045, -0.12 + 0.22 * (i - 1) / (len(outline) - 3), 0.0))
            tip = Vector((ex * 0.97, ey * 0.97 + WING_ROOT_Y * 0.03, 0.0))
            pts = [root.lerp(tip, t) for t in (0.0, 0.5, 1.0)]
            pts = [Vector((sx * p.x, p.y, 0.004 + abs(p.x) * 0.05 + 0.0035)) for p in pts]
            crisp.append((nh.tube(pts, [0.0045, 0.003, 0.0012], sides=5), RIB))
    return fused, crisp


SPEC = fl.Spec(
    name="Icarosaurus",
    rows=[(0, 0.95, 0.0, 0, 0), (0, 0.80, 0.0, 0.004, 0.004), (0, 0.55, 0.0, 0.009, 0.008), (0, 0.30, 0.0, 0.017, 0.015),
          (0, 0.16, 0.0, 0.030, 0.024), (0, 0.02, 0.002, 0.048, 0.030), (0, -0.12, 0.004, 0.046, 0.030),
          (0, -0.24, 0.006, 0.032, 0.026), (0, -0.32, 0.010, 0.026, 0.024), (0, -0.38, 0.012, 0.030, 0.026),
          (0, -0.45, 0.010, 0.026, 0.021), (0, -0.52, 0.006, 0.016, 0.012), (0, -0.57, 0.003, 0.006, 0.005),
          (0, -0.585, 0.002, 0, 0)],
    paint=kit.paint(back=(0.28, 0.30, 0.16), flank=(0.42, 0.42, 0.24), belly=(0.82, 0.80, 0.62),
                    spots=(0.80, 0.78, 0.55), spot_scale=26.0, spot_amt=0.5),
    wing=wing_outline(),
    wing_color=wing_color,
    wing_z=0.004, wing_thick=0.006, dihedral=0.05,
    eye=(0.024, -0.43, 0.022), eye_r=0.010,
    voxel=0.005, max_tris=6000,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Icarosaurus", **fl.PREVIEW)
