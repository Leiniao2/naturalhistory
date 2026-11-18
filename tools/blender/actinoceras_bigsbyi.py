"""
Procedural Actinoceras bigsbyi (Middle-Late Ordovician actinocerid nautiloid, type species of
Actinoceras, from the limestones round Lake Huron) for map colonies (Swim style).

A big straight-shelled nautiloid, up to about a metre long: a heavy, fusiform conch that swells
behind the body chamber and tapers to both ends, with short chambers (closely spaced sutures)
and the actinocerids' broad, beaded central siphuncle stiffened by heavy deposits that weighted
the shell. Colours are speculative: a warm red-brown shell with dark zigzag bands across the back
and a pale belly. A muscular head with big eyes and a crown of a dozen thick, banded arms reaches
out of the aperture (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/actinoceras_bigsbyi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ActinocerasBigsbyi.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

SHELL = (0.62, 0.36, 0.22)
BELLY = (0.86, 0.76, 0.62)
BAND = (0.26, 0.12, 0.07)
SUTURE = (0.38, 0.22, 0.14)
SIPHUNCLE = (0.46, 0.28, 0.18)
FLESH = (0.56, 0.30, 0.24)
FLESH_LIGHT = (0.86, 0.62, 0.50)

LENGTH = 1.7
R_AP = 0.12
R_APEX = 0.03


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.5, 0.5, math.sin(a))
    col = nh.lerp(BELLY, SHELL, dorsal)
    # zigzag bands across the back
    zz = s * 34.0 + 0.9 * abs(math.sin(a * 3.0))
    band = nh.smoothstep(0.55, 0.85, math.sin(zz * math.pi))
    col = nh.lerp(col, BAND, band * dorsal * 0.8)
    col = tuple(x * (1.04 if info["ridge"] else 0.94) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.45)
    return col


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=170, sides=28, body_frac=0.22,
                     septum_spacing=0.30, siphuncle=0.0, sinus=0.25, growth=0.012, bulge=0.55)
    mb.add(bm, None)
    # the beaded central siphuncle shows through the old, worn apical end as a row of knobs
    for k in range(9):
        s = 0.80 + 0.022 * k
        y = s * LENGTH
        mb.add(nh.ellipsoid((0.0, y, 0.0), (0.028, 0.02, 0.028), subdivisions=2), SIPHUNCLE)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=12, arm_len=2.3, arm_r=0.16,
                 hood=True, hood_col=(0.44, 0.22, 0.16), eye_r=0.26, spot=(0.34, 0.16, 0.12),
                 curl=0.35, spread=0.5, droop=0.3)
    obj = mb.to_object("ActinocerasBigsbyi", roughness=0.5)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ActinocerasBigsbyi", views=((35, 25), (-90, 8), (0, 90)))
