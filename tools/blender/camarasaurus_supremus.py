"""
Procedural Camarasaurus supremus (Late Jurassic sauropod, Morrison Formation, western USA)
for map colonies.

The commonest sauropod of the Morrison Formation, up to about 18 m long: a shorter, deeper
body than Diplodocus, shoulders about as high as the hips, a thick neck held up at a slant,
a short, tall, boxy head with a blunt snout, big nostrils high in front of the eyes and
strong spoon-shaped teeth, and a fairly short, thick tail. Pillar legs, a single big thumb
claw on the hands. Painted grey-brown with a paler belly and faint darker bands (colour
unknown). Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/camarasaurus_supremus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Camarasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402

TOOTH = (0.92, 0.90, 0.80)


def extras(ctx):
    sp = ctx.spec
    fused = []
    # the arched nasal bulge in front of the eyes and a deep, rounded jowl
    fused.append((nh.ellipsoid(ctx.head(0.45, z=sp.head_h * 0.75), (sp.head_w * 0.75, sp.head_len * 0.22, sp.head_h * 0.45), subdivisions=2), (0.5,) * 3))
    fused.append((nh.ellipsoid(ctx.head(0.4, z=-sp.head_h * 0.45), (sp.head_w * 0.85, sp.head_len * 0.3, sp.head_h * 0.45), subdivisions=2), (0.5,) * 3))
    crisp = []
    for sx in (1, -1):
        for k in range(4):
            b = ctx.head(0.78 + k * 0.05, x=sx * sp.head_w * (0.62 - k * 0.07), z=-sp.head_h * 0.55)
            crisp.append((kit.cone(b, b + ctx.head_dir((0, -0.004, -sp.head_h * 0.35)), 0.009, sides=4), TOOTH))
        # nostrils high on the snout
        crisp.append((nh.ellipsoid(ctx.head(0.62, x=sx * sp.head_w * 0.35, z=sp.head_h * 1.08), (0.012, 0.018, 0.008), subdivisions=1), kit.PUPIL))
    return fused, crisp


SPEC = qd.Spec(
    name="Camarasaurus",
    paint=kit.paint(back=(0.38, 0.34, 0.28), flank=(0.56, 0.50, 0.40), belly=(0.84, 0.78, 0.66),
                    stripe=(0.28, 0.24, 0.20), freq=9.0, y_range=(-1.6, 2.2), stripe_amt=0.45, mottle_scale=6.0),
    hip_h=1.0, shoulder_h=1.02, body_len=1.05, body_hw=0.34, body_hh=0.38, belly_drop=0.08,
    tail_len=1.7, tail_droop=0.6, tail_r=0.72, tail_exp=1.3,
    neck=((0.0, -0.35, 0.22), (0.0, -0.68, 0.5), (0.0, -0.95, 0.75)), neck_r=(0.25, 0.17, 0.12),
    head_len=0.28, head_h=0.12, head_w=0.085, head_pitch=60, snout_taper=0.15, head_power=2.8,
    thigh_r=0.17, shin_r=0.12, foot_r=0.13, arm_r=0.15, forearm_r=0.11, hand_r=0.1,
    front_nails=1, hind_nails=3, voxel=0.02, max_tris=17000, stride=0.14,
    eye_r=0.022, extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Camarasaurus", **qd.PREVIEW)
