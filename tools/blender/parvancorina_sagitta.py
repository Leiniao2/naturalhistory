"""
Procedural Parvancorina sagitta (Ediacaran parvancorinomorph, White Sea) for map colonies.

The narrower, arrow-shaped Parvancorina: an elongate outline, little more than half as wide as
long, with a bluntly pointed front, broadest a little ahead of mid-length and tapering to a
narrow rounded rear - an arrowhead in top view. Its anchor-shaped ridge is drawn out to
match: the transverse ridge near the front is a tight, forward-pointing arc whose arms sweep
well back along the flanks like the barbs of an arrowhead, and the midline ridge runs back
almost to the rear margin. Fine oblique striations flank the midline ridge. A slightly more
golden ochre-tan than P. minchami, with a pale ridge, darker troughs and a darker rim.
One lofted shell (see nh_parvancorina.py). Faces -Y, pivot at the body centre (Swim style),
seen mostly from above.

Usage:
  blender --background --python tools/blender/parvancorina_sagitta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ParvancorinaSagitta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_parvancorina as pv  # noqa: E402

W = 0.30           # half-width at the broadest point
T_WIDE = 0.42      # where along the body (0 front .. 1 rear) it is broadest


def half_width(t):
    if t < T_WIDE:
        # bluntly pointed, ogival front: the arrow's tip
        q = (T_WIDE - t) / T_WIDE
        return W * (1.0 - q ** 1.6) ** 0.75 + 0.008
    # long, gently converging flanks to a narrow rounded rear
    q = (t - T_WIDE) / (1.0 - T_WIDE)
    return W * (1.0 - q ** 2.4) ** 0.5 * (1.0 - 0.5 * q * q) + 0.008


SHAPE = pv.Shape(
    name="ParvancorinaSagitta",
    y_front=-0.70, y_back=0.70,
    half_width=half_width,
    anchor=pv.arc_anchor(apex_y=-0.47, half_span=0.17, sweep=0.30, hook=105.0),
    ridge_end=0.60,
    dome=0.07, ridge_h=0.032, ridge_w=0.025,
    stripes=16, stripe_slant=0.60,
    rows=76, cols=24,
    palette={
        "body": (0.76, 0.58, 0.38),
        "body_light": (0.88, 0.74, 0.54),
        "ridge": (0.93, 0.82, 0.62),
        "ridge_side": (0.48, 0.33, 0.20),
        "stripe": (0.56, 0.40, 0.26),
        "rim": (0.62, 0.45, 0.30),
    },
)


def build():
    return pv.build(SHAPE)


if __name__ == "__main__":
    nh.run(build, "ParvancorinaSagitta", background=(0.05, 0.14, 0.18),
           views=((30, 40), (0, 85), (-90, 12)))
