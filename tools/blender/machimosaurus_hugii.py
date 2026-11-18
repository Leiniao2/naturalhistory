"""
Procedural Machimosaurus hugii (Late Jurassic teleosaurid crocodyliform, coastal seas of
Europe and North Africa) for map colonies.

The largest teleosaurid, about 7 m long: a heavy, gharial-to-crocodile-like marine
crocodyliform with a long but broad, robust snout full of short, blunt, conical teeth for
crushing hard-shelled prey such as turtles, a long, laterally flattened swimming tail,
short sprawling legs, and a back covered by two broad rows of thick, pitted bony scutes.
Painted olive-grey with darker bands and pale scute keels over a cream belly.
Built with nh_cre_dino (like Sarcosuchus). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/machimosaurus_hugii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Machimosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.26, 0.28, 0.22)
FLANK = (0.42, 0.44, 0.34)
BELLY = (0.84, 0.82, 0.66)
BAND = (0.15, 0.16, 0.12)
SCUTE = (0.44, 0.44, 0.34)


def make():
    s = dn.DinoSpec(
        name="Machimosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=14.0, stripe_amt=0.55, mottle=0.12,
                            extra=lambda co, n, c: nh.lerp(c, SCUTE, 0.55 * cc.spots(co, 26.0, 0.25) * nh.smoothstep(0.55, 0.9, n.z))),
        hip_y=0.25, hip_z=0.14, body_len=0.55, torso_w=0.15, torso_h=0.095, belly=0.0,
        tail_len=0.95, tail_r=0.85, tail_droop=-0.03, tail_flat=0.4,
        neck_len=0.09, neck_rise=0.01, neck_r=0.065, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.085, 0.05), (-0.08, -0.004, 0.07, 0.042), (-0.16, -0.008, 0.055, 0.034),
                   (-0.28, -0.012, 0.048, 0.03), (-0.38, -0.012, 0.045, 0.027), (-0.43, -0.012, 0.042, 0.025),
                   (-0.465, -0.014, 0.028, 0.018), (-0.48, -0.016, 0.0, 0.0)],
        head_len=0.48, head_h=0.05, head_w=0.085, jaw=True, jaw_open=8, jaw_h=0.45, teeth=11, tooth_len=0.012,
        leg_type="sprawl", leg_r=0.038, toes=4, toe_len=0.05, toe_r=0.012, claw=0.012, stride=-0.05,
        fore="leg", fore_type="sprawl", arm_r=0.03, fore_toes=5, shoulder_dy=0.05,
        eye_r=0.015, eye_pos=(-0.03, 0.045, 0.55), eye_col=(0.70, 0.66, 0.25), scales=0.003, voxel=0.0095,
        max_tris=13000,
    )
    # two broad rows of thick dorsal scutes from the neck to the tail
    for k in range(26):
        y = s.chest_y - 0.06 + k * 0.042
        f = max(0.0, (y - s.hip_y) / s.tail_len)
        for x in (0.032, 0.085):
            if f > 0.2 and x > 0.05:
                continue
            s.blobs.append(((x * (1 - 0.6 * f), y, s.hip_z + 0.085 - x * 0.35 - 0.06 * f), (0.03, 0.022, 0.016), True))
    return s


if __name__ == "__main__":
    dn.run(make, "Machimosaurus")
