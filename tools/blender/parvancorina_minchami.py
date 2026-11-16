"""
Procedural Parvancorina minchami (Ediacaran parvancorinomorph) for map colonies.

A small, low, shield-shaped animal lying on the microbial mat: a broad outline, nearly as wide
as long, broadest in the front third with a rounded front edge and a blunter, narrower rear.
On top stands the raised anchor-shaped ridge that identifies the genus - a curved transverse
ridge near the front, bowed forward, whose arms sweep back toward the sides, joined at its
centre by a midline ridge that runs back about two-thirds of the body and fades out. Fine
striations run obliquely back and out from the midline ridge toward the margin on both sides.
Muted, blotchy pinkish ochre skin; the ridge and striations are soft swellings and creases
shown by a slight shade change, not pale bars (a living animal, not a fossil cast).
One lofted shell (see nh_parvancorina.py). Faces -Y, pivot at the body centre (Swim style),
seen mostly from above.

Usage:
  blender --background --python tools/blender/parvancorina_minchami.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ParvancorinaMinchami.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_parvancorina as pv  # noqa: E402

W = 0.47           # half-width at the broadest point
T_WIDE = 0.34      # where along the body (0 front .. 1 rear) it is broadest


def half_width(t):
    if t < T_WIDE:
        # broadly rounded front
        return W * (1.0 - ((T_WIDE - t) / T_WIDE) ** 2) ** 0.5 + 0.01
    # shield sides converging toward a blunt rear
    q = (t - T_WIDE) / (1.0 - T_WIDE)
    return W * (1.0 - q ** 2.2) ** 0.5 * (1.0 - 0.3 * q) + 0.01


SHAPE = pv.Shape(
    name="ParvancorinaMinchami",
    y_front=-0.58, y_back=0.58,
    half_width=half_width,
    anchor=pv.arc_anchor(apex_y=-0.39, half_span=0.30, sweep=0.20, hook=125.0),
    ridge_end=0.36,
    dome=0.075, ridge_h=0.022, ridge_w=0.045,
    stripes=12, stripe_slant=0.45,
    rows=68, cols=30,
)


def build():
    return pv.build(SHAPE)


if __name__ == "__main__":
    nh.run(build, "ParvancorinaMinchami", background=(0.05, 0.14, 0.18),
           views=((30, 40), (0, 85), (-90, 12)))
