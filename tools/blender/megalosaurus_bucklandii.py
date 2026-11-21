"""
Procedural Megalosaurus bucklandii (Middle Jurassic megalosaurid theropod, England) for map colonies.

The first dinosaur ever named (1824): a heavy, 6-7 m predator with a long, low, rather
narrow skull full of blade-like serrated teeth, a thick muscular neck, short but very
powerful arms with three big hooked claws, a deep chest and a long tail held level.
Painted dark olive-brown with blotchy darker mottling over the back and a dull buff
belly (colour unknown). Built with nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/megalosaurus_bucklandii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Megalosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402


def extras(ctx):
    fused = []
    # a low bony brow ridge over each eye and a thick, muscular neck base
    for sx in (1, -1):
        top, bot, w = ctx.head_row(0.24)
        fused.append((nh.ellipsoid(ctx.head(0.24, x=sx * w * 0.7, z=top - 0.006), (0.022, 0.05, 0.014), subdivisions=2), (0.5,) * 3))
    return fused, []


SPEC = th.Spec(
    name="Megalosaurus",
    paint=kit.paint(back=(0.36, 0.33, 0.20), flank=(0.56, 0.50, 0.32), belly=(0.86, 0.80, 0.62),
                    spots=(0.20, 0.18, 0.10), spot_scale=7.0, spot_amt=0.65, mottle=0.16),
    body_len=0.66, body_hw=0.19, body_hh=0.28, tail_len=1.4,
    neck_len=0.36, neck_angle=36, neck_r=0.1, head_len=0.52, head_h=0.18, head_w=0.095, snout_taper=0.45,
    jaw_open=14, teeth=12, tooth_len=0.04,
    thigh_r=0.17, shin_r=0.085, meta_r=0.05,
    arm_len=0.3, arm_r=0.055, fingers=3, finger_len=0.1,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Megalosaurus", **th.PREVIEW)
