"""
Procedural Ceratosaurus nasicornis (Late Jurassic Morrison Formation theropod) for map colonies.

A heavy-headed predator with a blade-like horn on the nose, a low hornlet over each eye,
very long blade teeth, a single row of small bony osteoderms down the midline of the
neck, back and tail, short four-fingered arms and a deep, crocodile-like tail. Dark
grey-brown with ochre bands and a pale belly; the horns flushed red-orange. Built with
nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ceratosaurus_nasicornis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ceratosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402

HORN = (0.72, 0.30, 0.12)
SCUTE = (0.20, 0.17, 0.14)


def extras(ctx):
    fused, crisp = [], []
    # nasal horn: a thin blade standing on the snout
    out = []
    for t, z in ((0.6, 0.0), (0.65, 0.08), (0.69, 0.115), (0.73, 0.1), (0.80, 0.0)):
        top, bot, w = ctx.head_row(t)
        p = ctx.head(t, z=top - 0.012 + z)
        out.append((p.y, p.z))
    crisp.append((kit.blade(out, 0.022), HORN))
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.26)
        b = ctx.head(0.26, x=sx * w * 0.6, z=top - 0.012)
        crisp.append((kit.cone(b, b + ctx.head_dir((sx * 0.01, -0.035, 0.04)), 0.026, sides=5), HORN))
    # osteoderm row along the midline from the neck to mid-tail
    sp = ctx.spine
    n = 34
    for i in range(n):
        s = 0.18 + 0.75 * i / (n - 1)
        p, up = sp.top(s, inset=0.06)
        c, tan, hw, hh = sp.at(s)
        h = 0.02 + 0.012 * (1 - abs(s - 0.55) * 2)
        crisp.append((kit.cone(p, p + up * h, 0.016, sides=4), SCUTE))
    return fused, crisp


SPEC = th.Spec(
    name="Ceratosaurus",
    paint=kit.paint(back=(0.24, 0.21, 0.18), flank=(0.45, 0.37, 0.27), belly=(0.86, 0.78, 0.62),
                    stripe=(0.68, 0.48, 0.20), freq=20.0, y_range=(-0.7, 1.6), stripe_amt=0.6),
    body_len=0.6, body_hw=0.16, body_hh=0.25, tail_len=1.45,
    neck_len=0.38, neck_angle=40, neck_r=0.09, head_len=0.5, head_h=0.22, head_w=0.095, snout_taper=0.45,
    tooth_len=0.05, teeth=9,
    arm_len=0.26, arm_r=0.042, fingers=4, finger_len=0.06,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Ceratosaurus", **th.PREVIEW)
