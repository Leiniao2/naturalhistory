"""
Procedural Shuyu zhejiangensis for the map: a small galeaspid (jawless armoured fish)
from the Silurian (Llandovery, about 438 million years ago) of Zhejiang, China, a few
centimetres long. Its finely preserved braincase, scanned in 3D, showed how the
galeaspid nose and brain were built and how the vertebrate head was assembled before
jaws evolved.

Reuses the galeaspid builder of yongdongaspis_littoralis.py (imported, not edited) with
Shuyu's own shield: a rounded, horseshoe-shaped head shield without long cornual
horns, only short blunt back corners; a narrow slit-like median dorsal opening on the
snout; small eyes set wide apart on top; the same scaly trunk with fin folds and
hypocercal tail. Darker grey-olive shield with pale tubercles (colours unknown).

Usage:
  blender --background --python tools/blender/shuyu_zhejiangensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ShuyuZhejiangensis.fbx (Swim: pivot at the body
centre, facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import yongdongaspis_littoralis as yd  # noqa: E402

yd.NAME = "ShuyuZhejiangensis"
yd.HALF_OUTLINE = [
    (0.00, -0.80), (0.07, -0.795), (0.14, -0.775), (0.20, -0.74), (0.25, -0.69), (0.29, -0.63),
    (0.32, -0.56), (0.338, -0.48), (0.345, -0.40), (0.342, -0.32), (0.332, -0.24), (0.318, -0.17),
    (0.300, -0.12),                                  # short blunt back corner
    (0.270, -0.13), (0.235, -0.165), (0.200, -0.21), (0.165, -0.245), (0.120, -0.262),
    (0.060, -0.266), (0.00, -0.262),
]
yd.DOME_H = 0.085
yd.EYE_Y, yd.EYE_X = -0.48, 0.175
yd.MDO_Y = -0.70
yd.SHIELD = (0.42, 0.42, 0.34)
yd.SHIELD_DARK = (0.24, 0.25, 0.20)
yd.TUBERCLE = (0.70, 0.70, 0.58)
yd.CANAL = (0.12, 0.12, 0.09)
yd.BACK = (0.18, 0.19, 0.15)
yd.FLANK = (0.38, 0.40, 0.32)
yd.FIN = (0.32, 0.34, 0.28)

def details(mb, poly):
    """Eyes on raised orbits, a narrow transverse slit for the median dorsal opening, pineal spot."""
    from mathutils import Vector
    for sg in (1, -1):
        p = Vector((sg * yd.EYE_X, yd.EYE_Y))
        z = yd.top_z(p, yd.edge_distance(p, poly))
        mb.add(nh.uv_ellipsoid((sg * yd.EYE_X, yd.EYE_Y, z - 0.004), (0.036, 0.040, 0.016), 10, 5),
               lambda co, n: nh.lerp(yd.SHIELD_DARK, yd.TUBERCLE, 0.4 * n.z))
        ef.eye(mb, (sg * yd.EYE_X, yd.EYE_Y, z + 0.004), (sg * 0.45, -0.15, 0.88), 0.024, iris=(0.55, 0.48, 0.28))
    p = Vector((0.0, yd.MDO_Y))
    z = yd.top_z(p, yd.edge_distance(p, poly))
    mb.add(nh.uv_ellipsoid((0.0, yd.MDO_Y, z - 0.002), (0.050, 0.012, 0.006), 10, 4), yd.OPENING)
    p = Vector((0.0, -0.52))
    mb.add(nh.uv_ellipsoid((0.0, -0.52, yd.top_z(p, yd.edge_distance(p, poly)) - 0.001), (0.010, 0.012, 0.004), 6, 3),
           yd.CANAL)


yd.shield_details = details

if __name__ == "__main__":
    nh.run(yd.build, yd.NAME, **ef.PREVIEW)
