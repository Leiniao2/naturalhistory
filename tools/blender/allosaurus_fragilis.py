"""
Procedural Allosaurus fragilis (Late Jurassic Morrison Formation theropod) for map colonies.

A large, lightly built predator: long, narrow skull with a low ridge along each side of
the snout and a short triangular horn in front of each eye (lacrimal horns, flushed
red here), slightly open jaws of serrated teeth, an S-curved neck, three-fingered arms
with big hooked claws, long tail held level. Tan-brown with dark transverse bands over
the back and tail and a cream belly. Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/allosaurus_fragilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Allosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import Vector  # noqa: E402

HORN = (0.70, 0.22, 0.12)


def extras(ctx):
    sp = ctx.spec
    fused = []
    for sx in (1, -1):
        # nasal ridges along the top edges of the snout
        for t in (0.42, 0.55, 0.68, 0.8):
            top, bot, w = ctx.head_row(t)
            fused.append((nh.ellipsoid(ctx.head(t, x=sx * w * 0.45, z=top - 0.004), (0.018, 0.035, 0.012), subdivisions=2), (0.5,) * 3))
    crisp = []
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.3)
        b = ctx.head(0.3, x=sx * w * 0.55, z=top - 0.01)
        crisp.append((kit.cone(b, b + ctx.head_dir((sx * 0.008, -0.03, 0.06)), 0.024, sides=5), HORN))
    return fused, crisp


def head_flush(co, n, c):
    return c


SPEC = th.Spec(
    name="Allosaurus",
    paint=kit.paint(back=(0.42, 0.30, 0.18), flank=(0.62, 0.48, 0.30), belly=(0.90, 0.82, 0.64),
                    stripe=(0.20, 0.13, 0.08), freq=22.0, y_range=(-0.75, 1.6)),
    body_len=0.62, body_hw=0.16, body_hh=0.25, tail_len=1.5,
    neck_len=0.4, neck_angle=42, head_len=0.5, head_h=0.2, head_w=0.095, snout_taper=0.5,
    arm_len=0.36, arm_r=0.045, fingers=3, finger_len=0.1,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Allosaurus", **th.PREVIEW)
