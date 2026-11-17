"""
Procedural Plectronoceras cambrense (Late Cambrian, China), the earliest known cephalopod.

A tiny shell, about 1 cm long: a short, broad, slightly curved horn (endogastric: the
underside of the curve is the belly), wide at the aperture and quickly narrowing to a
blunt apex. Its chambers were very closely spaced (septa only a fraction of a shell
radius apart), shown as dense sutures, with a ventral siphuncle. The animal looks out of
the aperture with a small head, two eyes and a ring of short arms (see nh_orthocone.py).
Colours are speculative: a pale buff shell with faint brownish growth bands.

Usage:
  blender --background --python tools/blender/plectronoceras_cambrense.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Plectronoceras.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 1.4 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

BUFF = (0.86, 0.78, 0.62)
BELLY = (0.92, 0.87, 0.76)
BAND = (0.58, 0.40, 0.26)
SUTURE = (0.50, 0.38, 0.28)
FLESH = (0.66, 0.40, 0.34)
FLESH_LIGHT = (0.88, 0.68, 0.58)

LENGTH = 1.0
R_AP = 0.26
R_APEX = 0.03
CURVE = 0.45  # how far the apex rises above the axis (endogastric curve)


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.6, 0.5, math.sin(a))
    col = nh.lerp(BELLY, BUFF, dorsal)
    band = nh.smoothstep(0.55, 0.9, math.sin(s * 34.0 + 0.4 * math.cos(a)))
    col = nh.lerp(col, BAND, band * 0.35 * (0.4 + 0.6 * dorsal))
    col = tuple(x * (1.03 if info["ridge"] else 0.95) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.6)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    # very closely spaced septa, the siphuncle along the belly
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=90, sides=16, body_frac=0.3,
                     septum_spacing=0.28, siphuncle=-math.pi / 2, sinus=0.15,
                     growth=0.012, bulge=0.04)
    # bend the horn: the apex curves up and back over the back
    for v in bm.verts:
        t = max(0.0, v.co.y) / LENGTH
        v.co.z += CURVE * t * t
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=10, arm_len=1.4, arm_r=0.12,
                 eye_r=0.26, spot=(0.50, 0.26, 0.22))
    obj = mb.to_object("Plectronoceras", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Plectronoceras", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
