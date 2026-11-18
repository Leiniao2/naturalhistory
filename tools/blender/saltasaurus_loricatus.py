"""
Procedural Saltasaurus loricatus (Late Cretaceous armoured titanosaur, Argentina).

A small, stocky sauropod about 12 metres long with a comparatively short, thick neck, a
broad body on stout legs and a medium tail; its back, flanks and tail are studded with
large oval bony plates set in a pebbly mosaic of small nodules. Sandy brown with darker
plates and a pale belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/saltasaurus_loricatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Saltasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_armour as ar  # noqa: E402

BACK = (0.46, 0.36, 0.24)
FLANK = (0.60, 0.50, 0.36)
BELLY = (0.84, 0.78, 0.64)
PLATE = (0.32, 0.24, 0.16)
NODULE = (0.40, 0.30, 0.20)


def make():
    s = dn.DinoSpec(
        name="Saltasaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, mottle=0.14,
                            extra=lambda co, n, c: nh.lerp(c, NODULE, 0.5 * cc.spots(co, 40.0, 0.35) * nh.smoothstep(0.2, 0.7, n.z))),
        hip_y=0.30, hip_z=0.40, body_len=0.50, torso_w=0.20, torso_h=0.19, belly=0.03, chest_dz=0.02,
        tail_len=0.70, tail_r=0.55, tail_droop=-0.12,
        neck_len=0.48, neck_rise=0.26, neck_r=0.055, neck_s=-0.02,
        head_len=0.12, head_h=0.035, head_w=0.034, snout_h=0.75, snout_w=0.85, snout_drop=0.02,
        leg_r=0.075, leg_type="column", leg_x=0.03, toes=3, toe_len=0.04, toe_r=0.022, claw=0.02, stride=0.04,
        fore="leg", fore_type="column", arm_r=0.065, fore_toes=0, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.008, eye_col=(0.3, 0.2, 0.1), scales=0.003, voxel=0.01, max_tris=12000,
    )

    def crisp(mb, s):
        ys = [s.chest_y + 0.04 + 0.075 * k for k in range(7)]
        ar.scutes(mb, s, ys, [-55, -25, 25, 55], 0.032, PLATE, height=0.15, keel=False)
        ar.scutes(mb, s, [y + 0.037 for y in ys[:-1]], [-75, -40, 0, 40, 75], 0.022, PLATE, height=0.1, keel=False)
        ys_t = [s.hip_y + 0.08 + 0.09 * k for k in range(4)]
        ar.scutes(mb, s, ys_t, [-30, 30], 0.022, PLATE, height=0.1, keel=False)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Saltasaurus")
