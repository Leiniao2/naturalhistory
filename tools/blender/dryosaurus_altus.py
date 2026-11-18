"""
Procedural Dryosaurus altus (Late Jurassic Morrison Formation ornithopod, western USA)
for map colonies.

A slender, fast-running plant-eater about 3 m long: long, powerful hind legs with very
long shins and three-toed feet built for sprinting, short arms with five small fingers,
a long stiffened tail held out as a counterbalance, and a short head with large eyes and
a toothless horny beak in front of its cheek teeth. Painted grey-green with pale buff
stripes along the flanks, a darker back and a cream belly (colour unknown). Built with
nh_jur_theropod (the biped body plan is the same). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dryosaurus_altus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dryosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402

BEAK = (0.20, 0.18, 0.14)
STRIPE = (0.82, 0.76, 0.56)


def stripes(co, n, c):
    # a pale lengthwise stripe along each flank, from the shoulder onto the tail
    band = nh.smoothstep(0.3, 0.12, abs(n.z - 0.2)) * nh.smoothstep(1.6, 0.8, co.y) * nh.smoothstep(-0.7, -0.4, co.y)
    band *= nh.smoothstep(0.6, 0.8, co.z)
    return nh.lerp(c, STRIPE, 0.75 * band)


def beak(mb, ctx):
    sp = ctx.spec
    top, bot, w = ctx.head_row(0.95)
    mb.add(nh.ellipsoid(ctx.head(0.97, z=(top + bot) * 0.5), (w * 0.95, sp.head_len * 0.09, (top - bot) * 0.55),
                        subdivisions=2), BEAK)
    mb.add(nh.ellipsoid(ctx.head(0.93, z=bot - sp.jaw_h * 0.7), (w * 0.7, sp.head_len * 0.08, sp.jaw_h * 0.4),
                        subdivisions=2), BEAK)


SPEC = th.Spec(
    name="Dryosaurus",
    paint=kit.paint(back=(0.24, 0.28, 0.20), flank=(0.42, 0.46, 0.34), belly=(0.86, 0.84, 0.70), extra=stripes,
                    stripe=(0.14, 0.17, 0.11), freq=18.0, y_range=(-0.5, 1.8), stripe_amt=0.6),
    body_len=0.48, body_hw=0.13, body_hh=0.18, tail_len=1.7, tail_lift=0.1,
    neck_len=0.34, neck_angle=40, neck_r=0.06, head_len=0.24, head_h=0.11, head_w=0.07, snout_taper=0.55,
    head_pitch=-8, jaw_h=0.04, jaw_open=4, teeth=6, tooth_len=0.008, tooth_color=(0.86, 0.84, 0.74),
    thigh_r=0.11, shin_r=0.045, meta_r=0.028, toe_len=0.14, stride=0.2,
    arm_len=0.2, arm_r=0.026, fingers=5, finger_len=0.035,
    eye_r=0.028, eye_color=(0.70, 0.50, 0.15), voxel=0.01, max_tris=10000, detail=beak,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Dryosaurus", **th.PREVIEW)
