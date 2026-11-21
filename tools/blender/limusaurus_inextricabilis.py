"""
Procedural Limusaurus inextricabilis (Late Jurassic ceratosaur, Xinjiang, China) for map colonies.

A small, slender theropod about 1.7 m long that lost its teeth as it grew up: adults had a
short, deep, toothless horny beak and probably ate plants (they swallowed gizzard stones).
Long neck, small head with big eyes, long running legs and strangely tiny, stubby arms with
reduced fingers. Painted sandy grey with a darker back, faint bands on the tail and a pale
throat; the beak dark horn. Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/limusaurus_inextricabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Limusaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402

BEAK = (0.16, 0.14, 0.11)


def beak(mb, ctx):
    sp = ctx.spec
    for t, zf, s in ((0.86, 0.5, 1.0), (0.95, 0.45, 0.8)):
        top, bot, w = ctx.head_row(t)
        mb.add(nh.ellipsoid(ctx.head(t, z=(top + bot) * zf), (w * 1.02 * s, sp.head_len * 0.12, (top - bot) * 0.58 * s),
                            subdivisions=2), BEAK)
    top, bot, w = ctx.head_row(0.88)
    mb.add(nh.ellipsoid(ctx.head(0.88, z=-sp.jaw_h * 0.55), (w * 0.85, sp.head_len * 0.12, sp.jaw_h * 0.5),
                        subdivisions=2), BEAK)


SPEC = th.Spec(
    name="Limusaurus",
    paint=kit.paint(back=(0.36, 0.33, 0.26), flank=(0.60, 0.56, 0.46), belly=(0.90, 0.88, 0.80),
                    stripe=(0.26, 0.23, 0.18), freq=26.0, y_range=(0.2, 1.8), stripe_amt=0.6),
    body_len=0.46, body_hw=0.12, body_hh=0.17, tail_len=1.5, tail_lift=0.05,
    neck_len=0.5, neck_angle=50, neck_r=0.05, head_len=0.2, head_h=0.11, head_w=0.06, snout_taper=0.35,
    head_pitch=-12, jaw_h=0.045, jaw_open=3, teeth=0,
    thigh_r=0.1, shin_r=0.042, meta_r=0.026, toe_len=0.13, stride=0.18,
    arm_len=0.12, arm_r=0.022, fingers=2, finger_len=0.02,
    eye_r=0.028, eye_color=(0.85, 0.62, 0.15), voxel=0.009, max_tris=9000, detail=beak,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Limusaurus", **th.PREVIEW)
