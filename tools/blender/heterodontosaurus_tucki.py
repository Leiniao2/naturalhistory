"""
Procedural Heterodontosaurus tucki (Early Jurassic, upper Elliot and Clarens
Formations, South Africa) for map colonies.

A small, fast ornithischian about 1.2 m long with three kinds of teeth: a horny beak at
the front, a pair of long, curved canine-like tusks in each jaw, and chisel-like cheek
teeth for chopping tough plants. Long legs, strong five-fingered grasping hands with big
claws, a long tail, and (as in its relative Tianyulong) a crest of long bristles along
the back and tail. Painted chestnut-brown with pale bars across the back, a dark mask
and a cream belly; the bristles dark (colour unknown). Built with nh_jur_theropod.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/heterodontosaurus_tucki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Heterodontosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import Vector  # noqa: E402

BEAK = (0.18, 0.15, 0.12)
TUSK = (0.96, 0.93, 0.82)
BRISTLE = (0.16, 0.10, 0.07)


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # a crest of long filaments along the back and the top of the tail
    for i in range(34):
        s = 0.12 + 0.62 * i / 33
        p, up = sp.top(s, inset=0.1)
        ln = 0.07 + 0.06 * (1 - abs(s - 0.55) * 2.2)
        for dx in (-0.012, 0.012):
            b = p + Vector((dx, 0, 0))
            crisp.append((kit.cone(b, b + (up + Vector((dx * 8, 0.6, 0))).normalized() * ln, 0.004, sides=3), BRISTLE))
    return [], crisp


def details(mb, ctx):
    sp = ctx.spec
    top, bot, w = ctx.head_row(0.95)
    mb.add(nh.ellipsoid(ctx.head(0.97, z=(top + bot) * 0.5), (w * 0.95, sp.head_len * 0.08, (top - bot) * 0.55),
                        subdivisions=2), BEAK)
    mb.add(nh.ellipsoid(ctx.head(0.93, z=bot - sp.jaw_h * 0.7), (w * 0.7, sp.head_len * 0.07, sp.jaw_h * 0.4),
                        subdivisions=2), BEAK)
    # the tusks: a big lower canine rising in front of the upper one, and an upper one
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.78)
        b = ctx.head(0.8, x=sx * w * 0.9, z=-0.02)
        kit.teeth(mb, [(b, b + ctx.head_dir((sx * 0.004, -0.006, 0.055)), 0.01)], TUSK)
        b = ctx.head(0.74, x=sx * w * 0.92, z=0.005)
        kit.teeth(mb, [(b, b + ctx.head_dir((sx * 0.003, 0.004, -0.04)), 0.009)], TUSK)


def mask(co, n, c):
    return nh.lerp(c, (0.16, 0.10, 0.07), 0.35 * nh.smoothstep(-0.7, -0.8, co.y) * nh.smoothstep(-0.4, 0.3, n.z))


SPEC = th.Spec(
    name="Heterodontosaurus",
    paint=kit.paint(back=(0.36, 0.20, 0.11), flank=(0.56, 0.36, 0.20), belly=(0.90, 0.84, 0.70),
                    stripe=(0.85, 0.76, 0.58), freq=26.0, y_range=(-0.4, 1.6), stripe_amt=0.55, extra=mask),
    body_len=0.42, body_hw=0.12, body_hh=0.16, tail_len=1.55, tail_lift=0.05,
    neck_len=0.28, neck_angle=40, neck_r=0.055, head_len=0.22, head_h=0.11, head_w=0.065, snout_taper=0.55,
    head_pitch=-8, jaw_h=0.04, jaw_open=8, teeth=6, tooth_len=0.01,
    thigh_r=0.09, shin_r=0.042, meta_r=0.027, toe_len=0.13, stride=0.17,
    arm_len=0.24, arm_r=0.028, fingers=5, finger_len=0.06,
    eye_r=0.024, voxel=0.009, max_tris=10000, extras=extras, detail=details,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Heterodontosaurus", **th.PREVIEW)
