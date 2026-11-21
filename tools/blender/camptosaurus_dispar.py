"""
Procedural Camptosaurus dispar (Late Jurassic ornithopod, Morrison Formation, western USA)
for map colonies.

A bulky, beaked plant-eater about 5-7 m long, an early relative of Iguanodon: a long, low
head with a toothless horny beak in front and rows of grinding cheek teeth, a thick neck, a
heavy body carried high at the hips, strong arms with hoof-like fingers that let it browse
on all fours, and a long, deep tail. Painted olive-brown with pale vertical bars on the
flanks and a cream belly (colour unknown). Built with nh_jur_quadruped. Faces -Y, pivot on
the ground.

Usage:
  blender --background --python tools/blender/camptosaurus_dispar.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Camptosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402


def extras(ctx):
    sp = ctx.spec
    # deep cheeks behind the beak
    fused = [(nh.ellipsoid(ctx.head(0.3, z=-sp.head_h * 0.25), (sp.head_w * 1.0, sp.head_len * 0.25, sp.head_h * 0.6), subdivisions=2), (0.5,) * 3)]
    return fused, []


SPEC = qd.Spec(
    name="Camptosaurus",
    paint=kit.paint(back=(0.30, 0.30, 0.18), flank=(0.48, 0.46, 0.30), belly=(0.86, 0.82, 0.64),
                    stripe=(0.72, 0.68, 0.48), freq=16.0, y_range=(-0.9, 0.6), stripe_amt=0.55, stripe_sharp=(0.7, 0.95)),
    hip_h=1.0, shoulder_h=0.62, body_len=0.85, body_hw=0.26, body_hh=0.32, belly_drop=0.06,
    tail_len=1.9, tail_droop=0.25, tail_r=0.75, tail_exp=1.1,
    neck=((0.0, -0.22, 0.12), (0.0, -0.42, 0.18), (0.0, -0.58, 0.18)), neck_r=(0.16, 0.12, 0.1),
    head_len=0.42, head_h=0.13, head_w=0.09, head_pitch=22, snout_taper=0.45, head_power=2.3,
    thigh_r=0.17, shin_r=0.09, foot_r=0.085, arm_r=0.07, forearm_r=0.05, hand_r=0.05,
    front_nails=3, hind_nails=3, voxel=0.016, max_tris=14000, stride=0.16, knee_bend=0.12,
    eye_r=0.024, beak=(0.18, 0.15, 0.12), extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Camptosaurus", **qd.PREVIEW)
