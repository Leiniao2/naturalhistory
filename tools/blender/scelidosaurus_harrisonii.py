"""
Procedural Scelidosaurus harrisonii (Early Jurassic, Charmouth, Dorset) for map colonies.

One of the earliest armoured dinosaurs, about 4 m long: a low-slung, four-legged plant
eater with a small triangular head and beak, a longish neck and a long, stiff tail.
Parallel rows of oval, keeled bony scutes run along the neck, back, flanks and tail, with
a pair of three-pointed plates behind the head. Dark brown-grey skin, darker scutes with
pale keels, and a buff belly. Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/scelidosaurus_harrisonii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Scelidosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

SCUTE = (0.20, 0.17, 0.14)
KEEL = (0.75, 0.68, 0.52)


def scute_color(base, h):
    def fn(co, n):
        return nh.lerp(SCUTE, KEEL, nh.smoothstep(0.4, 1.0, (co - base).length / h))
    return fn


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # scute rows: (height on the flank, size)
    rows = ((0.95, 0.05), (0.7, 0.042), (0.35, 0.034), (-0.05, 0.026))
    n = 30
    for i in range(n):
        s = 0.06 + 0.82 * i / (n - 1)
        c, tan, hw, hh = sp.at(s)
        for j, (ht, sz) in enumerate(rows):
            if hw < 0.05 and j >= 2:
                continue
            k = sz * (0.6 + 0.5 * min(1.0, hw / 0.2))
            for sx in (1, -1):
                base = sp.side_pt(s, sx, height=ht, inset=0.05)
                out = (base - c).normalized()
                crisp.append((kit.cone(base, base + out * k, k * 0.7, sides=5), scute_color(base, k)))
    # three-pointed plates behind the head
    s = 0.93
    for sx in (1, -1):
        base = sp.side_pt(s, sx, height=0.7, inset=0.05)
        for d in ((0.03, 0.03, 0.06), (0.06, 0.02, 0.03), (0.0, 0.05, 0.05)):
            crisp.append((kit.cone(base, base + Vector((sx * d[0], d[1], d[2])), 0.02, sides=4), scute_color(base, 0.07)))
    return [], crisp


SPEC = qd.Spec(
    name="Scelidosaurus",
    paint=kit.paint(back=(0.26, 0.23, 0.19), flank=(0.40, 0.35, 0.28), belly=(0.78, 0.70, 0.52)),
    hip_h=0.62, shoulder_h=0.5, body_len=1.0, body_hw=0.22, body_hh=0.2, belly_drop=0.03,
    tail_len=1.9, tail_droop=0.18, tail_r=0.75,
    neck=((0.0, -0.18, 0.02), (0.0, -0.36, 0.04), (0.0, -0.5, 0.04)), neck_r=(0.12, 0.09, 0.07),
    head_len=0.22, head_h=0.07, head_w=0.075, head_pitch=14, snout_taper=0.55,
    thigh_r=0.1, shin_r=0.065, foot_r=0.065, arm_r=0.075, forearm_r=0.055, hand_r=0.055,
    front_nails=4, hind_nails=4, beak=(0.22, 0.20, 0.16), voxel=0.013, stride=0.14,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Scelidosaurus", **qd.PREVIEW)
