"""
Procedural Diplodocus carnegii (Late Jurassic Morrison Formation sauropod) for map colonies.

A long, low sauropod: hips higher than the shoulders, a very long neck held out nearly
level, a small, long, low head with peg teeth at the front of a square muzzle, and an even
longer tail tapering into a thin whiplash. A row of low keratinous spines runs along the
midline of the back and tail. Pillar legs with elephantine feet (one big thumb claw on the
hands, three claws on the feet). Grey-brown with darker bands across the back and a pale
belly. Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/diplodocus_carnegii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Diplodocus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402

SPINE = (0.28, 0.24, 0.20)


def extras(ctx):
    sp = ctx.spine
    crisp = []
    n = 60
    for i in range(n):
        s = 0.12 + 0.68 * i / (n - 1)
        p, up = sp.top(s, inset=0.05)
        c, tan, hw, hh = sp.at(s)
        h = 0.02 + 0.25 * hh
        crisp.append((kit.cone(p, p + up * h, h * 0.45, sides=4), SPINE))
    return [], crisp


SPEC = qd.Spec(
    name="Diplodocus",
    paint=kit.paint(back=(0.36, 0.34, 0.30), flank=(0.52, 0.49, 0.42), belly=(0.82, 0.78, 0.68),
                    stripe=(0.22, 0.21, 0.18), freq=7.0, y_range=(-2.6, 4.0), stripe_amt=0.55, mottle_scale=6.0),
    hip_h=1.0, shoulder_h=0.88, body_len=1.25, body_hw=0.3, body_hh=0.34, belly_drop=0.06,
    tail_len=3.8, tail_droop=0.55, tail_r=0.7, tail_exp=1.7,
    neck=((0.0, -0.55, 0.14), (0.0, -1.2, 0.26), (0.0, -1.8, 0.3), (0.0, -2.25, 0.27)), neck_r=(0.2, 0.13, 0.09, 0.07),
    head_len=0.2, head_h=0.055, head_w=0.055, head_pitch=22, snout_taper=0.2, head_power=2.6,
    thigh_r=0.15, shin_r=0.1, foot_r=0.11, arm_r=0.12, forearm_r=0.085, hand_r=0.085,
    front_nails=1, hind_nails=3, voxel=0.02, max_tris=17000, stride=0.16,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Diplodocus", **qd.PREVIEW)
