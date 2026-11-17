"""
Procedural Lesothosaurus diagnosticus (Early Jurassic, ~200-190 Ma, upper Elliot
Formation, Lesotho and South Africa) for map colonies.

One of the earliest and most basal ornithischians, the beaked, plant-eating dinosaurs:
a small, lightly built biped about 1 m long, running on long, slender legs with short
arms and a long, stiff tail. The small, short head has big eyes, a horny beak at the
tip of the snout and a row of small leaf-shaped teeth for slicing plants. Painted
olive-brown with a darker back and tail bands and a pale belly (colour unknown).
Built with nh_jur_theropod (the biped body plan is the same). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lesothosaurus_diagnosticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lesothosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

BEAK = (0.22, 0.20, 0.16)
TOOTH = (0.86, 0.84, 0.74)


def markings(co, n, c):
    m = noise.noise((co.x * 24.0, co.y * 60.0, co.z * 24.0))
    return tuple(v * (1.0 + 0.1 * m) for v in c)


def beak(mb, ctx):
    # horny beak capping the tip of the snout, and the small predentary bone below it
    sp = ctx.spec
    top, bot, w = ctx.head_row(0.95)
    mb.add(nh.ellipsoid(ctx.head(0.97, z=(top + bot) * 0.5), (w * 0.95, sp.head_len * 0.08, (top - bot) * 0.55),
                        subdivisions=2), BEAK)
    mb.add(nh.ellipsoid(ctx.head(0.93, z=bot - sp.jaw_h * 0.7), (w * 0.7, sp.head_len * 0.07, sp.jaw_h * 0.4),
                        subdivisions=2), BEAK)


SPEC = th.Spec(
    name="Lesothosaurus",
    paint=kit.paint(back=(0.30, 0.30, 0.18), flank=(0.52, 0.48, 0.30), belly=(0.86, 0.82, 0.66),
                    stripe=(0.20, 0.18, 0.10), freq=22.0, y_range=(0.3, 2.0), extra=markings),
    body_len=0.42, body_hw=0.12, body_hh=0.16, tail_len=1.6, tail_lift=0.08,
    neck_len=0.3, neck_angle=38, neck_r=0.055, head_len=0.22, head_h=0.1, head_w=0.065, snout_taper=0.6,
    head_pitch=-6, jaw_h=0.035, jaw_open=4, teeth=7, tooth_len=0.009, tooth_color=TOOTH,
    thigh_r=0.09, shin_r=0.042, meta_r=0.027, toe_len=0.13, stride=0.16,
    arm_len=0.17, arm_r=0.024, fingers=4, finger_len=0.04,
    eye_r=0.024, voxel=0.01, max_tris=9000, detail=beak,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Lesothosaurus", **th.PREVIEW)
