"""
Procedural Kentrosaurus aethiopicus (Late Jurassic Tendaguru Formation stegosaur, Tanzania)
for map colonies.

A smaller, spikier African cousin of Stegosaurus, about 4.5 m long: pairs of narrow plates
over the neck and shoulders turn into pairs of long, sharp spikes along the hips and tail,
and a long spike juts back from each shoulder. High hips, short forelimbs, small low head
with a beak. Ochre-tan with dark brown bands over the back and a pale belly; the plates and
spikes bone-coloured with dark tips. Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kentrosaurus_aethiopicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kentrosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

BONE = (0.86, 0.78, 0.60)
TIP = (0.20, 0.15, 0.11)


def tip_color(p, ln):
    def fn(co, n):
        return nh.lerp(BONE, TIP, nh.smoothstep(0.45, 1.0, (co - p).length / ln))
    return fn


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # neck and shoulder plates (pairs), s high = toward the head
    for i, s in enumerate((0.86, 0.82, 0.78, 0.74, 0.70, 0.66, 0.62)):
        p, up = sp.top(s, inset=0.1)
        hgt = 0.1 + 0.03 * i
        for sx in (1, -1):
            base = p + Vector((sx * 0.04, 0, 0))
            crisp.append((kit.plate(base, hgt, hgt * 0.7, 0.014, up=up, lean=0.15, sx=sx * 0.35, shape="spike"),
                          tip_color(base, hgt * 1.1)))
    # spikes from the hips to the tail tip, longest at the tail base
    for i, s in enumerate((0.56, 0.5, 0.44, 0.38, 0.32, 0.26, 0.2, 0.14, 0.08, 0.03)):
        p, up = sp.top(s, inset=0.15)
        ln = 0.18 + 0.12 * math.exp(-((s - 0.32) / 0.15) ** 2)
        for sx in (1, -1):
            base = p + Vector((sx * 0.04, 0, 0))
            tip = base + (up * 0.75 + Vector((sx * 0.35, 0.55, 0))).normalized() * ln
            crisp.append((kit.cone(base, tip, 0.024, sides=6), tip_color(base, ln)))
    # shoulder spikes pointing back and out
    s = sp.s_at_y(-0.78)
    for sx in (1, -1):
        base = sp.side_pt(s, sx, height=0.1, inset=0.15)
        tip = base + Vector((sx * 0.22, 0.35, 0.06))
        crisp.append((kit.cone(base, tip, 0.04, sides=6), tip_color(base, 0.42)))
    return [], crisp


SPEC = qd.Spec(
    name="Kentrosaurus",
    paint=kit.paint(back=(0.42, 0.30, 0.16), flank=(0.66, 0.52, 0.30), belly=(0.88, 0.82, 0.64),
                    stripe=(0.24, 0.15, 0.08), freq=18.0, y_range=(-1.2, 2.2), stripe_amt=0.75),
    hip_h=0.9, shoulder_h=0.5, body_len=0.85, body_hw=0.24, body_hh=0.28, belly_drop=0.05,
    tail_len=1.7, tail_droop=0.25, tail_r=0.7,
    neck=((0.0, -0.2, -0.04), (0.0, -0.36, -0.12), (0.0, -0.48, -0.2)), neck_r=(0.14, 0.095, 0.065),
    head_len=0.26, head_h=0.07, head_w=0.06, head_pitch=12, snout_taper=0.5,
    thigh_r=0.12, shin_r=0.075, foot_r=0.08, arm_r=0.095, forearm_r=0.07, hand_r=0.065,
    front_nails=3, hind_nails=3, beak=(0.25, 0.22, 0.18), voxel=0.014,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Kentrosaurus", **qd.PREVIEW)
