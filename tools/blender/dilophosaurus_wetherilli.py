"""
Procedural Dilophosaurus wetherilli (Early Jurassic Kayenta Formation theropod) for map colonies.

A slender, long-necked predator with a pair of thin, half-moon crests running side by side
along the top of the skull (barred red and cream here), a kinked upper jaw with a notch
behind the narrow snout tip, long legs, a long tail and four-fingered arms. Sandy yellow-
brown with dark stripes down the back and a pale belly. Built with nh_jur_theropod.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dilophosaurus_wetherilli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dilophosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
import bmesh  # noqa: E402

CREST = (0.78, 0.22, 0.12)
CREST_BAR = (0.92, 0.86, 0.72)


def crest_color(co, n):
    s = 0.5 + 0.5 * math.sin(co.y * 140.0)
    return CREST if s < 0.6 else CREST_BAR


def extras(ctx):
    crisp = []
    for sx in (1, -1):
        out = []
        samples = [(0.12, 0.0), (0.2, 0.1), (0.32, 0.15), (0.46, 0.155), (0.6, 0.12), (0.74, 0.06), (0.84, 0.0)]
        for t, z in samples:
            top, bot, w = ctx.head_row(t)
            p = ctx.head(t, z=top - 0.015 + z)
            out.append((p.y, p.z))
        top, bot, w = ctx.head_row(0.45)
        bm = kit.blade(out, 0.008, x=sx * w * 0.32)
        # lean each crest slightly outward
        for v in bm.verts:
            v.co.x += sx * max(0.0, v.co.z - out[0][1]) * 0.12
        crisp.append((bm, crest_color))
    return [], crisp


SPEC = th.Spec(
    name="Dilophosaurus",
    paint=kit.paint(back=(0.40, 0.31, 0.16), flank=(0.70, 0.58, 0.34), belly=(0.92, 0.86, 0.70),
                    stripe=(0.18, 0.13, 0.08), freq=26.0, y_range=(-0.8, 1.6), stripe_sharp=(0.55, 0.85)),
    body_len=0.55, body_hw=0.13, body_hh=0.2, tail_len=1.55,
    neck_len=0.5, neck_angle=46, neck_r=0.07, head_len=0.42, head_h=0.14, head_w=0.075, snout_taper=0.45,
    thigh_r=0.12, shin_r=0.06, meta_r=0.038, toe_len=0.15,
    tooth_len=0.03, teeth=11,
    arm_len=0.34, arm_r=0.038, fingers=4, finger_len=0.08,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Dilophosaurus", **th.PREVIEW)
