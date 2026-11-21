"""
Procedural Massospondylus carinatus (Early Jurassic sauropodomorph, southern Africa) for map colonies.

An early relative of the giant sauropods, 4-6 m long, that walked on its hind legs: a long,
slender neck, a small head with leaf-shaped teeth and a short snout, sturdy arms with grasping
five-fingered hands armed with a huge, curved thumb claw, a bulky gut and a long tail.
Painted warm tan with darker brown blotches along the back and a cream belly (colour unknown).
Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/massospondylus_carinatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Massospondylus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import Vector  # noqa: E402


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # the big thumb claws, hooked inward and down
    for sx in (1, -1):
        sh = sp.side_pt(sp.s_at_y(-ctx.spec.body_len * 0.92), sx, height=-0.25, inset=0.25)
        el = sh + Vector((sx * 0.03, ctx.spec.arm_len * 0.15, -ctx.spec.arm_len * 0.5))
        wr = el + Vector((0.0, -ctx.spec.arm_len * 0.45, -ctx.spec.arm_len * 0.12))
        b = wr + Vector((-sx * 0.012, -0.01, -0.005))
        crisp.append((kit.cone(b, b + Vector((-sx * 0.025, -0.05, -0.035)), 0.013, sides=6), (0.14, 0.12, 0.10)))
    # gut: a deep belly
    fused = [(nh.ellipsoid((0, -0.3, 0.86), (0.17, 0.3, 0.2), subdivisions=2), (0.5,) * 3)]
    return fused, crisp


SPEC = th.Spec(
    name="Massospondylus",
    paint=kit.paint(back=(0.42, 0.28, 0.16), flank=(0.66, 0.50, 0.32), belly=(0.92, 0.86, 0.70),
                    spots=(0.28, 0.17, 0.09), spot_scale=6.0, spot_amt=0.55),
    body_len=0.6, body_hw=0.16, body_hh=0.22, tail_len=1.5, tail_lift=0.0,
    neck_len=0.72, neck_angle=30, neck_r=0.06, head_len=0.18, head_h=0.09, head_w=0.055, snout_taper=0.4,
    head_pitch=-14, jaw_h=0.035, jaw_open=5, teeth=7, tooth_len=0.01, tooth_color=(0.9, 0.88, 0.78),
    thigh_r=0.15, shin_r=0.07, meta_r=0.04, toe_len=0.15, stride=0.12,
    arm_len=0.4, arm_r=0.04, fingers=4, finger_len=0.06,
    eye_r=0.02, voxel=0.011, max_tris=12000, extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Massospondylus", **th.PREVIEW)
