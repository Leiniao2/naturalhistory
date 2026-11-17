"""
Procedural Stegosaurus stenops (Late Jurassic Morrison Formation) for map colonies.

The classic plated dinosaur: hips high above short forelimbs so the back arches up to a
peak over the hips; a short, low neck carrying a tiny, narrow head with a horny beak
near the ground; two staggered rows of broad, diamond-shaped plates from the neck to
the tail, tallest over the hips (flushed red with a dark rim); and four long spikes
splaying sideways at the end of the tail (the "thagomizer"). Olive-green with a pale
belly. Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/stegosaurus_stenops.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Stegosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402
from mathutils import Vector  # noqa: E402

PLATE = (0.74, 0.30, 0.14)
PLATE_RIM = (0.30, 0.16, 0.10)
SPIKE = (0.85, 0.80, 0.66)
SPIKE_TIP = (0.22, 0.18, 0.14)


def plate_color(base_z, height):
    def fn(co, n):
        k = nh.smoothstep(0.55, 1.0, (co.z - base_z) / max(1e-6, height))
        return nh.lerp(PLATE, PLATE_RIM, k)
    return fn


def extras(ctx):
    sp = ctx.spine
    crisp = []
    n = 17
    for i in range(n):
        s = 0.17 + 0.66 * i / (n - 1)
        p, up = sp.top(s, inset=0.08)
        # tallest over the hips (s ~ 0.48), small on the neck and tail
        hgt = 0.07 + 0.36 * math.exp(-((s - 0.5) / 0.18) ** 2)
        ln = 0.05 + hgt * 0.9
        sx = 1 if i % 2 else -1
        base = p + Vector((sx * 0.035, 0, 0))
        crisp.append((kit.plate(base, hgt, ln, 0.02, up=up, lean=0.18, sx=sx * 0.12), plate_color(base.z, hgt)))
    # thagomizer: two pairs of spikes near the tail tip
    for s, ln in ((0.05, 0.3), (0.1, 0.32)):
        for sx in (1, -1):
            p, up = sp.top(s, inset=0.2)
            tip = p + Vector((sx * ln * 0.85, ln * 0.35, ln * 0.4))

            def col(co, n, p=p, ln=ln):
                return nh.lerp(SPIKE, SPIKE_TIP, nh.smoothstep(0.5, 1.0, (co - p).length / ln))
            crisp.append((kit.cone(p, tip, 0.032, sides=6), col))
    return [], crisp


SPEC = qd.Spec(
    name="Stegosaurus",
    paint=kit.paint(back=(0.30, 0.34, 0.20), flank=(0.48, 0.50, 0.32), belly=(0.82, 0.78, 0.60),
                    spots=(0.22, 0.25, 0.15), spot_scale=9.0, spot_amt=0.45),
    hip_h=0.95, shoulder_h=0.5, body_len=0.95, body_hw=0.31, body_hh=0.34, belly_drop=0.06,
    tail_len=1.85, tail_droop=0.35, tail_r=0.7,
    neck=((0.0, -0.2, -0.05), (0.0, -0.36, -0.14), (0.0, -0.48, -0.22)), neck_r=(0.17, 0.11, 0.07),
    head_len=0.28, head_h=0.08, head_w=0.07, head_pitch=12, snout_taper=0.5,
    thigh_r=0.14, shin_r=0.09, foot_r=0.09, arm_r=0.11, forearm_r=0.08, hand_r=0.075,
    front_nails=3, hind_nails=3, beak=(0.25, 0.22, 0.18),
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Stegosaurus", **qd.PREVIEW)
