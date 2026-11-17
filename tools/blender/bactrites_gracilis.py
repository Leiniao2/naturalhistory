"""
Procedural Bactrites gracilis (Devonian bactritid) for map colonies.

Bactritids were small, straight-shelled cephalopods, the ancestors of both the
ammonites and the coleoids (squid, belemnites). A slender orthocone about 10 cm long
with a small apical angle, a smooth shell crossed by fine growth lines, a slight
ventral sinus at the aperture, closely spaced chambers and a narrow marginal siphuncle
along the belly (the bactritid hallmark, unlike the central siphuncle of orthocerids).
Colours are speculative: a pale grey-buff shell with faint brown longitudinal streaks.
The animal peers out of the aperture with ten slender arms (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/bactrites_gracilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Bactrites.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

SHELL = (0.80, 0.76, 0.66)
BELLY = (0.90, 0.87, 0.80)
STREAK = (0.48, 0.34, 0.24)
SUTURE = (0.52, 0.44, 0.36)
FLESH = (0.60, 0.34, 0.32)
FLESH_LIGHT = (0.84, 0.62, 0.54)

LENGTH = 1.7
R_AP = 0.07
R_APEX = 0.006


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.55, 0.45, math.sin(a))
    col = nh.lerp(BELLY, SHELL, dorsal)
    # faint longitudinal streaks on the back
    streak = nh.smoothstep(0.6, 0.95, math.sin(a * 7.0 + 0.6))
    col = nh.lerp(col, STREAK, streak * 0.35 * dorsal * (1.0 - 0.5 * s))
    col = tuple(x * (1.03 if info["ridge"] else 0.95) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.4)
    col = nh.lerp(col, (0.60, 0.54, 0.46), nh.smoothstep(0.8, 1.0, s) * 0.4)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=120, sides=14, body_frac=0.3,
                     septum_spacing=0.6, siphuncle=-math.pi / 2, sinus=0.35,
                     growth=0.01, bulge=0.02)
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=10, arm_len=2.4, arm_r=0.12,
                 eye_r=0.25, spot=(0.46, 0.24, 0.20))
    obj = mb.to_object("Bactrites", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Bactrites", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
