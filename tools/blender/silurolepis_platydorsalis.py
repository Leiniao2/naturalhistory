"""
Procedural Silurolepis platydorsalis for the map: the oldest known antiarch placoderm,
from the Late Silurian (Ludlow, about 423 million years ago) Kuanti Formation of Qujing,
Yunnan, China; a small fish around 10 cm long.

An early relative of Bothriolepis, with the antiarch plan already in place: a box of
bony plates round the head and the front of the body, eyes close together in a single
opening on top of the head, and plated pectoral appendages. Its trunk armour is low and
broad with an unusually flat back (hence "platydorsalis"), and the pectoral appendages
are short, stubby and unjointed, as in the other early (yunnanolepid) antiarchs. Behind
the box, a naked tapering tail with a dorsal fin.

Reuses the antiarch builder of bothriolepis_canadensis.py (imported, not edited) with
its own profile, appendages and colours.

Usage:
  blender --background --python tools/blender/silurolepis_platydorsalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SilurolepisPlatydorsalis.fbx (Swim: pivot at the
body centre, facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402
import bothriolepis_canadensis as bo  # noqa: E402

bo.NAME = "SilurolepisPlatydorsalis"
bo.ARMOUR = (0.56, 0.50, 0.38)
bo.ARMOUR_DARK = (0.34, 0.29, 0.21)
bo.TUBERCLE = (0.76, 0.70, 0.54)
bo.BACK = (0.22, 0.20, 0.16)
bo.FLANK = (0.40, 0.36, 0.28)
# broad and low, flat-topped armour (high superellipse power, low top)
bo.PROF = ef.Profile([
    (-0.80, 0.050, 0.025, 0.022, -0.030),
    (-0.77, 0.120, 0.050, 0.040, -0.030),
    (-0.68, 0.170, 0.070, 0.055, -0.028),
    (-0.56, 0.195, 0.090, 0.065, -0.026),
    (-0.40, 0.205, 0.100, 0.070, -0.025),
    (-0.24, 0.195, 0.098, 0.070, -0.025),
    (-0.10, 0.150, 0.085, 0.066, -0.020),
    (0.02, 0.085, 0.070, 0.055, -0.010),
    (0.20, 0.050, 0.050, 0.040, 0.000),
    (0.40, 0.030, 0.030, 0.024, 0.016),
    (0.60, 0.014, 0.014, 0.011, 0.040),
    (0.80, 0.002, 0.002, 0.002, 0.070),
], power=lambda y: 4.2 if y < -0.1 else 2.1)


def arm(mb, s):
    """Short, stubby, unjointed plated appendage pointing out and back."""
    P = bo.PROF
    root = Vector((s * P.W(-0.48) * 0.95, -0.48, P.CZ(-0.48) - 0.01))
    tip = root + Vector((s * 0.12, 0.16, -0.02))
    seg = lambda co, n: nh.lerp(bo.ARMOUR, bo.ARMOUR_DARK, 0.5 * (1 - n.z) * 0.5)  # noqa: E731
    mb.add(nh.tube([root, root.lerp(tip, 0.5), tip], [0.034, 0.030, 0.0], sides=7, scale_xy=(1.0, 0.55)), seg)
    for k in range(3):
        p = root.lerp(tip, 0.2 + 0.25 * k) + Vector((s * 0.024 * (1 - 0.2 * k), 0, 0))
        mb.add(nh.tube([p, p + Vector((s * 0.014, 0.010, 0))], [0.006, 0.0], sides=4), bo.ARMOUR_DARK)


bo.arm = arm

if __name__ == "__main__":
    nh.run(bo.build, bo.NAME, **df.PREVIEW)
