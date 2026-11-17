"""
Procedural Guanlong wucaii (Late Jurassic Shishugou Formation proceratosaurid tyrannosauroid)
for map colonies.

An early, small relative of Tyrannosaurus about 3 m long, with a tall, thin, fan-shaped
crest running along the midline of the snout from the nostrils to the eyes (its name
means "crowned dragon"), long three-fingered arms, slender legs and a long tail. Painted
with a short fuzzy coat: chestnut-brown back, buff flanks with dark speckles, a pale
belly and an orange crest. Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/guanlong_wucaii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Guanlong.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import noise  # noqa: E402

CREST = (0.86, 0.46, 0.14)
CREST_EDGE = (0.55, 0.16, 0.08)


def extras(ctx):
    out = []
    # fan-shaped crest, tallest above the eye-snout midpoint
    for t, z in ((0.18, 0.0), (0.24, 0.07), (0.34, 0.14), (0.46, 0.17), (0.58, 0.15), (0.7, 0.10), (0.82, 0.05), (0.9, 0.0)):
        top, bot, w = ctx.head_row(t)
        p = ctx.head(t, z=top - 0.015 + z)
        out.append((p.y, p.z))
    zb = min(z for _, z in out)

    def col(co, n):
        return nh.lerp(CREST, CREST_EDGE, nh.smoothstep(0.08, 0.16, co.z - zb))
    return [], [(kit.blade(out, 0.012), col)]


def fuzz(co, n, c):
    m = noise.noise((co.x * 30.0, co.y * 80.0, co.z * 30.0))
    return tuple(v * (1.0 + 0.14 * m) for v in c)


SPEC = th.Spec(
    name="Guanlong",
    paint=kit.paint(back=(0.36, 0.20, 0.11), flank=(0.66, 0.50, 0.32), belly=(0.92, 0.86, 0.72),
                    spots=(0.22, 0.13, 0.08), spot_scale=22.0, spot_amt=0.55, extra=fuzz),
    body_len=0.5, body_hw=0.12, body_hh=0.19, tail_len=1.6,
    neck_len=0.42, neck_angle=40, neck_r=0.065, head_len=0.42, head_h=0.14, head_w=0.075, snout_taper=0.5,
    thigh_r=0.11, shin_r=0.055, meta_r=0.034, toe_len=0.15,
    teeth=10, tooth_len=0.025,
    arm_len=0.42, arm_r=0.035, fingers=3, finger_len=0.1,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Guanlong", **th.PREVIEW)
