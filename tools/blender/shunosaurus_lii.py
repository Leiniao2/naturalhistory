"""
Procedural Shunosaurus lii (Middle Jurassic Dashanpu sauropod, Sichuan, China) for map
colonies.

A comparatively small, short-necked sauropod about 9-10 m long, known from many complete
skeletons. Its tail ended in a bony club armed with short spikes, a weapon swung at
predators. Hips higher than the shoulders, neck held forward and slightly raised, small
head. Painted olive-grey with dark mottled blotches over the back, a pale belly and a
bone-coloured tail club (colour unknown). Built with nh_jur_quadruped. Faces -Y, pivot on
the ground.

Usage:
  blender --background --python tools/blender/shunosaurus_lii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Shunosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

CLUB = (0.62, 0.56, 0.44)
SPIKE = (0.86, 0.80, 0.64)


def extras(ctx):
    sp = ctx.spine
    fused, crisp = [], []
    # bony club at the tail tip (spine starts at the tail tip, s = 0)
    c, tan, hw, hh = sp.at(0.045)
    fused.append((nh.ellipsoid(c, (0.085, 0.15, 0.075), subdivisions=3), CLUB))
    for dx, dz, dy in ((1, 0.2, -0.03), (-1, 0.2, -0.03), (1, 0.6, 0.04), (-1, 0.6, 0.04), (0, 1, 0.0)):
        d = Vector((dx * 0.8, dy, dz)).normalized()
        b = c + Vector((dx * 0.06, dy, dz * 0.055))
        crisp.append((kit.cone(b, b + d * 0.11, 0.026, sides=6), SPIKE))
    return fused, crisp


def club_paint(base):
    def fn(co, n):
        c = base(co, n)
        return nh.lerp(c, CLUB, nh.smoothstep(1.32, 1.4, co.y))
    return fn


SPEC = qd.Spec(
    name="Shunosaurus",
    paint=club_paint(kit.paint(back=(0.30, 0.32, 0.22), flank=(0.48, 0.48, 0.36), belly=(0.84, 0.80, 0.66),
                               spots=(0.18, 0.19, 0.13), spot_scale=5.0, spot_amt=0.55)),
    hip_h=0.9, shoulder_h=0.8, body_len=0.95, body_hw=0.27, body_hh=0.3, belly_drop=0.05,
    tail_len=1.6, tail_droop=0.4, tail_r=0.75, tail_exp=0.9,
    neck=((0.0, -0.35, 0.1), (0.0, -0.75, 0.22), (0.0, -1.1, 0.28)), neck_r=(0.17, 0.11, 0.08),
    head_len=0.22, head_h=0.075, head_w=0.06, head_pitch=25, snout_taper=0.3,
    thigh_r=0.14, shin_r=0.095, foot_r=0.1, arm_r=0.11, forearm_r=0.08, hand_r=0.08,
    front_nails=1, hind_nails=3, voxel=0.016, max_tris=15000,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Shunosaurus", **qd.PREVIEW)
