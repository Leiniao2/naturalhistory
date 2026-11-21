"""
Procedural Tianyulong confuciusi (Late Jurassic heterodontosaurid, Liaoning, China) for map colonies.

A small, cat-sized plant-eating dinosaur about 70 cm long, famous because it was covered in
long, stiff, hollow bristles: a crest of filaments up to 6 cm long runs along its back and
over the top of its long tail, showing that fuzzy body coverings were not only for
meat-eaters. Short head with a horny beak and a pair of small fangs, long hind legs, grasping
hands. Painted chestnut with a grey-banded tail and dark bristles (colour unknown).
Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/tianyulong_confuciusi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tianyulong.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import Vector  # noqa: E402

BEAK = (0.15, 0.12, 0.10)
TUSK = (0.96, 0.93, 0.82)
BRISTLE = (0.30, 0.24, 0.20)
BRISTLE_TIP = (0.88, 0.84, 0.74)


def extras(ctx):
    sp = ctx.spine
    crisp = []
    # a dense mane of long bristles from the neck over the back to the tail tip, longest on the tail
    n = 70
    for i in range(n):
        s = 0.04 + 0.78 * i / (n - 1)
        p, up = sp.top(s, inset=0.12)
        ln = 0.09 + 0.1 * max(0.0, 1.0 - abs(s - 0.32) * 3.0)
        for dx in (-0.016, 0.0, 0.016):
            b = p + Vector((dx, 0, 0))
            d = (up + Vector((dx * 14, 0.45, 0))).normalized()
            col = BRISTLE_TIP if (i % 3 == 0) else BRISTLE
            crisp.append((kit.cone(b, b + d * ln * (1.0 if dx == 0 else 0.75), 0.008, sides=3), col))
    return [], crisp


def details(mb, ctx):
    sp = ctx.spec
    top, bot, w = ctx.head_row(0.95)
    mb.add(nh.ellipsoid(ctx.head(0.97, z=(top + bot) * 0.5), (w * 0.95, sp.head_len * 0.08, (top - bot) * 0.55), subdivisions=2), BEAK)
    mb.add(nh.ellipsoid(ctx.head(0.93, z=bot - sp.jaw_h * 0.7), (w * 0.7, sp.head_len * 0.07, sp.jaw_h * 0.4), subdivisions=2), BEAK)
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.78)
        b = ctx.head(0.8, x=sx * w * 0.9, z=-0.02)
        kit.teeth(mb, [(b, b + ctx.head_dir((sx * 0.004, -0.005, 0.04)), 0.008)], TUSK)


def tail_bands(co, n, c):
    if co.y > 0.25:
        import math
        k = 0.5 + 0.5 * math.sin(co.y * 14.0)
        c = nh.lerp(c, (0.55, 0.53, 0.50), 0.7 * nh.smoothstep(0.5, 0.75, k))
    return c


SPEC = th.Spec(
    name="Tianyulong",
    paint=kit.paint(back=(0.40, 0.18, 0.08), flank=(0.62, 0.34, 0.16), belly=(0.90, 0.82, 0.66), extra=tail_bands),
    body_len=0.4, body_hw=0.13, body_hh=0.17, tail_len=1.6, tail_lift=0.12,
    neck_len=0.26, neck_angle=42, neck_r=0.058, head_len=0.2, head_h=0.11, head_w=0.07, snout_taper=0.55,
    head_pitch=-8, jaw_h=0.04, jaw_open=6, teeth=5, tooth_len=0.008,
    thigh_r=0.095, shin_r=0.042, meta_r=0.027, toe_len=0.13, stride=0.16,
    arm_len=0.24, arm_r=0.028, fingers=5, finger_len=0.055,
    eye_r=0.026, voxel=0.009, max_tris=9000, extras=extras, detail=details,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Tianyulong", **th.PREVIEW)
