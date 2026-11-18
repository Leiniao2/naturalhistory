"""
Procedural Torvosaurus tanneri (Late Jurassic Morrison Formation megalosaurid, Colorado
and Utah) for map colonies.

One of the largest predators of its time, about 9-10 m long: a heavily built megalosaurid
with a long, low, deep-sided skull full of long serrated teeth, a thick muscular neck,
short but very powerful arms with big thumb claws, and a massive body on stout legs.
Painted dark umber with blackish transverse bands over the back and tail, a rust-red flush
on the snout and a cream belly. Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/torvosaurus_tanneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Torvosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402

RUST = (0.55, 0.20, 0.10)
BASE = kit.paint(back=(0.26, 0.19, 0.13), flank=(0.46, 0.34, 0.22), belly=(0.86, 0.78, 0.60),
                 stripe=(0.10, 0.07, 0.05), freq=20.0, y_range=(-0.7, 1.7), stripe_amt=0.75)


def paint(co, n):
    c = BASE(co, n)
    # rust-red flush over the snout and face
    return nh.lerp(c, RUST, 0.35 * nh.smoothstep(-1.15, -1.4, co.y) * nh.smoothstep(-0.2, 0.4, n.z))


def extras(ctx):
    fused = []
    # low rugose ridge over the snout and a heavy brow above each eye
    for t in (0.35, 0.5, 0.65, 0.8):
        top, bot, w = ctx.head_row(t)
        fused.append((nh.ellipsoid(ctx.head(t, z=top - 0.006), (0.02, 0.05, 0.014), subdivisions=2), (0.5,) * 3))
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.22)
        fused.append((nh.ellipsoid(ctx.head(0.22, x=sx * w * 0.7, z=top - 0.01), (0.03, 0.045, 0.018), subdivisions=2), (0.5,) * 3))
    return fused, []


SPEC = th.Spec(
    name="Torvosaurus",
    paint=paint,
    body_len=0.66, body_hw=0.2, body_hh=0.28, tail_len=1.45,
    neck_len=0.36, neck_angle=38, neck_r=0.105, head_len=0.56, head_h=0.2, head_w=0.11, snout_taper=0.38,
    head_pitch=-6, jaw_h=0.085, jaw_open=16, teeth=11, tooth_len=0.045,
    thigh_r=0.18, shin_r=0.09, meta_r=0.055, toe_len=0.18,
    arm_len=0.26, arm_r=0.06, fingers=3, finger_len=0.08,
    eye_color=(0.85, 0.45, 0.08), voxel=0.013,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Torvosaurus", **th.PREVIEW)
