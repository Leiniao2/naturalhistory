"""
Procedural Proterovaginoceras incognitum (Early-Middle Ordovician endocerid nautiloid, the
commonest cephalopod of the Baltoscandian "Vaginatum" limestones) for map colonies (Swim style).

A large, smooth endocerid: a long, slender, almost straight-sided conch with faint growth lines,
long chambers, and the endocerids' wide ventral siphuncle packed with stacked cone-shaped
deposits (a dark line along the belly) that kept the shell level. Colours are speculative: a
pale grey-cream shell with broad, soft, dark-brown transverse bands fading towards the apex.
A hooded head with large eyes and a crown of about twenty tentacles (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/proterovaginoceras_incognitum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProterovaginocerasIncognitum.fbx
Pivot at the body centre, tentacles forward (-Y), back up (+Z).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

SHELL = (0.80, 0.77, 0.68)
BELLY = (0.90, 0.88, 0.80)
BAND = (0.34, 0.24, 0.17)
SUTURE = (0.55, 0.50, 0.42)
FLESH = (0.48, 0.34, 0.30)
FLESH_LIGHT = (0.80, 0.66, 0.58)

LENGTH = 2.0
R_AP = 0.10
R_APEX = 0.022


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.6, 0.4, math.sin(a))
    col = nh.lerp(BELLY, SHELL, dorsal)
    band = nh.smoothstep(0.2, 0.9, math.sin(s * 22.0 * math.pi * 0.5 + 0.4 * math.cos(a)))
    col = nh.lerp(col, BAND, band * dorsal * 0.7 * (1.0 - 0.7 * s))
    col = tuple(x * (1.02 if info["ridge"] else 0.97) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.3)
    return col


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=190, sides=26, body_frac=0.20,
                     septum_spacing=0.9, siphuncle=-math.pi / 2, sinus=0.22, growth=0.005, bulge=0.04)
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=20, arm_len=2.0, arm_r=0.11,
                 hood=True, hood_col=(0.40, 0.28, 0.24), eye_r=0.27, spot=(0.30, 0.20, 0.18),
                 curl=0.25, spread=0.4, droop=0.4)
    obj = mb.to_object("ProterovaginocerasIncognitum", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ProterovaginocerasIncognitum", views=((35, 25), (-90, 8), (0, 90)))
