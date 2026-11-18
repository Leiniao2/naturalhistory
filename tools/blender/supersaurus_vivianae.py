"""
Procedural Supersaurus vivianae (Late Jurassic Morrison Formation diplodocid sauropod,
Colorado and Wyoming) for map colonies.

One of the longest dinosaurs known, perhaps 33-35 m: a Diplodocus-like body plan pushed to
the extreme, with an enormous, very long neck carried a little higher than in Diplodocus,
a deep, bulky trunk, pillar legs and a long tail ending in a thin whiplash. A row of low
keratinous spines along the back. Painted rusty red-brown with pale buff bands across the
back, a darker spine and a cream belly (colour unknown). Built with nh_jur_quadruped.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/supersaurus_vivianae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Supersaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402

SPINE = (0.30, 0.18, 0.12)


def extras(ctx):
    sp = ctx.spine
    crisp = []
    n = 70
    for i in range(n):
        s = 0.1 + 0.72 * i / (n - 1)
        p, up = sp.top(s, inset=0.05)
        c, tan, hw, hh = sp.at(s)
        h = 0.02 + 0.22 * hh
        crisp.append((kit.cone(p, p + up * h, h * 0.45, sides=4), SPINE))
    return [], crisp


SPEC = qd.Spec(
    name="Supersaurus",
    paint=kit.paint(back=(0.40, 0.24, 0.16), flank=(0.60, 0.40, 0.28), belly=(0.86, 0.78, 0.62),
                    stripe=(0.80, 0.68, 0.48), freq=6.0, y_range=(-3.0, 4.6), stripe_amt=0.5, mottle_scale=6.0),
    hip_h=1.05, shoulder_h=1.0, body_len=1.4, body_hw=0.36, body_hh=0.4, belly_drop=0.08,
    tail_len=4.2, tail_droop=0.6, tail_r=0.7, tail_exp=1.8,
    neck=((0.0, -0.6, 0.3), (0.0, -1.35, 0.62), (0.0, -2.1, 0.85), (0.0, -2.75, 0.95)), neck_r=(0.24, 0.15, 0.1, 0.075),
    head_len=0.22, head_h=0.06, head_w=0.06, head_pitch=35, snout_taper=0.2, head_power=2.6,
    thigh_r=0.18, shin_r=0.12, foot_r=0.13, arm_r=0.15, forearm_r=0.105, hand_r=0.1,
    front_nails=1, hind_nails=3, voxel=0.024, max_tris=17000, stride=0.18,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Supersaurus", **qd.PREVIEW)
