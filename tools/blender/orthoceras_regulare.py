"""
Procedural Orthoceras regulare (Middle Ordovician orthocerid nautiloid) for map colonies.

A slender, straight, slowly tapering conch (about 20 cm long, apical angle of a few
degrees) with a smooth surface crossed by fine transverse growth lines, a long
phragmocone of closely spaced chambers (faint septal sutures) pierced by a narrow
central siphuncle, and a body chamber at the wide end. Colours are speculative but
follow preserved orthocerid colour patterns: a cream shell with reddish-brown
transverse bands on the back, fading to a pale belly (countershading). The animal
peers out of the aperture: a small head with two eyes, ten slender arms and the
funnel underneath (see nh_orthocone.py).

Usage:
  blender --background --python tools/blender/orthoceras_regulare.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Orthoceras.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_orthocone as oc  # noqa: E402

CREAM = (0.90, 0.80, 0.64)
BELLY = (0.94, 0.88, 0.76)
BAND = (0.55, 0.22, 0.12)       # reddish-brown
BAND_DARK = (0.40, 0.15, 0.09)
SUTURE = (0.58, 0.44, 0.32)
FLESH = (0.62, 0.32, 0.28)
FLESH_LIGHT = (0.86, 0.62, 0.52)

LENGTH = 1.75
R_AP = 0.085
R_APEX = 0.012


def paint(s, a, info):
    dorsal = nh.smoothstep(-0.55, 0.45, math.sin(a))
    col = nh.lerp(BELLY, CREAM, dorsal)
    # transverse bands, wider near the aperture, with a slight wave around the shell
    f = 30.0 * (1.0 + 0.7 * s)
    w = math.sin(s * f + 0.35 * math.cos(a * 2.0) + 1.3 + 1.2 * math.sin(s * 11.0))
    w2 = math.sin(s * f * 2.3 + 0.7)
    band = nh.smoothstep(0.35, 0.75, w) + 0.45 * nh.smoothstep(0.8, 0.95, w2) * (1 - nh.smoothstep(0.35, 0.75, w))
    col = nh.lerp(col, BAND, band * (0.12 + 0.78 * dorsal))
    # each band has a darker leading edge
    col = nh.lerp(col, BAND_DARK, nh.smoothstep(0.75, 0.95, w) * dorsal * 0.5)
    # fine growth lines
    col = tuple(x * (1.04 if info["ridge"] else 0.92) for x in col)
    col = nh.lerp(col, SUTURE, info["suture"] * 0.45)
    # the apex is older, worn and a little darker
    col = nh.lerp(col, (0.60, 0.48, 0.38), nh.smoothstep(0.8, 1.0, s) * 0.5)
    return tuple(min(1.0, x) for x in col)


def build():
    mb = nh.MeshBuilder()
    bm, r = oc.conch(LENGTH, R_AP, R_APEX, paint, rings=120, sides=16, body_frac=0.26,
                     septum_spacing=0.75, siphuncle=0.0, sinus=0.25,
                     growth=0.014, bulge=0.03)
    mb.add(bm, None)
    oc.soft_body(mb, 0.0, r * 0.98, FLESH, FLESH_LIGHT, arms=10, arm_len=2.6, arm_r=0.12,
                 eye_r=0.24, spot=(0.48, 0.22, 0.18))
    obj = mb.to_object("Orthoceras", roughness=0.45)
    oc.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Orthoceras", views=((35, 25), (-90, 8), (20, 10), (0, 90)))
