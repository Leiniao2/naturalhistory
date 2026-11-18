"""
Procedural Gargoyleosaurus parkpinorum (Late Jurassic Morrison Formation ankylosaur,
Wyoming) for map colonies.

One of the earliest true ankylosaurs, about 3-4 m long: a low, broad, barrel-shaped body
carried on short, splayed legs and covered from neck to tail in rows of keeled, conical
bony osteoderms, with a fringe of longer spikes along each flank and two rings of plates
over the neck. The short triangular head bears a small horn at each back corner. No tail
club yet: the tail is stiff and edged with small spikes. Painted dark brown-grey with
paler bone-coloured armour and a buff belly. Built with nh_jur_quadruped. Faces -Y, pivot
on the ground.

Usage:
  blender --background --python tools/blender/gargoyleosaurus_parkpinorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gargoyleosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

SCUTE = (0.74, 0.66, 0.50)
SPIKE = (0.84, 0.78, 0.62)
HORN = (0.30, 0.25, 0.20)


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # rows of keeled osteoderms over the back, from tail tip (s=0) to the neck
    for i in range(26):
        s = 0.08 + 0.8 * i / 25
        for h in (0.95, 0.7, 0.35):
            for sx in ((1, -1) if h < 0.9 else (1,)):
                p = sp.side_pt(s, sx, height=h, inset=0.05) if h < 0.9 else sp.top(s, inset=0.05)[0]
                c, tan, hw, hh = sp.at(s)
                n = (p - c).normalized()
                r = 0.024 + 0.04 * min(hw, 0.3)
                crisp.append((kit.cone(p - n * 0.005, p + n * r * 1.2, r, sides=5), SCUTE))
    # lateral spike fringe
    for i in range(16):
        s = 0.12 + 0.7 * i / 15
        for sx in (1, -1):
            p = sp.side_pt(s, sx, height=-0.1, inset=0.03)
            sx = 1 if p.x > 0 else -1
            c, tan, hw, hh = sp.at(s)
            ln = 0.06 + 0.07 * min(1.0, hw / 0.3)
            tip = p + Vector((sx * 1.0, 0.25, -0.05)).normalized() * ln
            crisp.append((kit.cone(p, tip, 0.022, sides=5), SPIKE))
    # horns at the back corners of the skull
    for sx in (1, -1):
        b = ctx.head(0.1, x=sx * ctx.spec.head_w * 0.8, z=ctx.spec.head_h * 0.2)
        crisp.append((kit.cone(b, b + ctx.head_dir((sx * 0.05, 0.03, 0.01)), 0.018, sides=5), HORN))
    return [], crisp


SPEC = qd.Spec(
    name="Gargoyleosaurus",
    paint=kit.paint(back=(0.36, 0.30, 0.22), flank=(0.50, 0.42, 0.30), belly=(0.80, 0.72, 0.54),
                    mottle=0.15),
    hip_h=0.34, shoulder_h=0.3, body_len=0.8, body_hw=0.3, body_hh=0.2, belly_drop=0.03,
    tail_len=0.9, tail_droop=0.12, tail_r=0.6,
    neck=((0.0, -0.12, -0.0), (0.0, -0.22, -0.02), (0.0, -0.3, -0.04)), neck_r=(0.15, 0.12, 0.1),
    head_len=0.22, head_h=0.085, head_w=0.12, head_pitch=10, snout_taper=0.5, head_power=2.3,
    thigh_r=0.1, shin_r=0.075, foot_r=0.08, arm_r=0.09, forearm_r=0.07, hand_r=0.07,
    front_nails=4, hind_nails=3, beak=(0.22, 0.19, 0.15), voxel=0.012, stride=0.08,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Gargoyleosaurus", **qd.PREVIEW)
