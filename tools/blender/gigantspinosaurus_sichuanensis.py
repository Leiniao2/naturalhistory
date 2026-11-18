"""
Procedural Gigantspinosaurus sichuanensis (Late Jurassic Shangshaximiao Formation
stegosaur, Sichuan, China) for map colonies.

A low-slung stegosaur about 4-4.5 m long named for its enormous shoulder spines: a huge,
flattened spike swept back from each shoulder, nearly twice as long as the shoulder blade.
Two rows of small, low triangular plates run down the neck, back and tail, and the tail
ends in two pairs of spikes. Short legs, small low head with a beak. Painted dark olive with
pale ochre bands across the back and a cream belly; plates and spikes bone with dark tips.
Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gigantspinosaurus_sichuanensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gigantspinosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

BONE = (0.88, 0.80, 0.60)
TIP = (0.18, 0.13, 0.10)


def tip_color(p, ln):
    def fn(co, n):
        return nh.lerp(BONE, TIP, nh.smoothstep(0.4, 1.0, (co - p).length / ln))
    return fn


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # two rows of small triangular plates, tail base -> neck
    for i in range(14):
        s = 0.1 + 0.75 * i / 13
        p, up = sp.top(s, inset=0.1)
        hgt = 0.07 + 0.05 * (1 - abs(s - 0.5) * 2)
        for sx in (1, -1):
            base = p + Vector((sx * 0.035, 0, 0))
            crisp.append((kit.plate(base, hgt, hgt * 1.1, 0.012, up=up, lean=0.25, sx=sx * 0.3, shape="spike"),
                          tip_color(base, hgt * 1.1)))
    # two pairs of tail spikes
    for s in (0.04, 0.09):
        p, up = sp.top(s, inset=0.2)
        for sx in (1, -1):
            tip = p + (up * 0.5 + Vector((sx * 0.6, 0.5, 0))).normalized() * 0.2
            crisp.append((kit.cone(p, tip, 0.022, sides=6), tip_color(p, 0.2)))
    # the giant shoulder spines: long, flattened, swept back and out
    s = sp.s_at_y(-0.7)
    for sx in (1, -1):
        base = sp.side_pt(s, sx, height=0.25, inset=0.15)
        sx = 1 if base.x > 0 else -1  # side_pt's side vector follows the spine direction
        mid = base + Vector((sx * 0.2, 0.25, 0.08))
        tip = base + Vector((sx * 0.32, 0.62, 0.12))
        bm = nh.tube([base, mid, tip], [0.06, 0.04, 0.0], sides=8, scale_xy=None)
        crisp.append((bm, tip_color(base, 0.72)))
    return [], crisp


SPEC = qd.Spec(
    name="Gigantspinosaurus",
    paint=kit.paint(back=(0.24, 0.26, 0.16), flank=(0.42, 0.42, 0.26), belly=(0.86, 0.82, 0.64),
                    stripe=(0.72, 0.58, 0.30), freq=16.0, y_range=(-1.0, 1.6), stripe_amt=0.6),
    hip_h=0.72, shoulder_h=0.5, body_len=0.85, body_hw=0.27, body_hh=0.27, belly_drop=0.06,
    tail_len=1.5, tail_droop=0.2, tail_r=0.72,
    neck=((0.0, -0.16, -0.03), (0.0, -0.28, -0.07), (0.0, -0.36, -0.11)), neck_r=(0.14, 0.1, 0.07),
    head_len=0.24, head_h=0.07, head_w=0.06, head_pitch=12, snout_taper=0.5,
    thigh_r=0.12, shin_r=0.08, foot_r=0.085, arm_r=0.1, forearm_r=0.075, hand_r=0.07,
    front_nails=3, hind_nails=3, beak=(0.24, 0.21, 0.17), voxel=0.014,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Gigantspinosaurus", **qd.PREVIEW)
