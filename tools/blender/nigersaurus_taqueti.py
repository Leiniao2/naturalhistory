"""
Procedural Nigersaurus taqueti (mid-Cretaceous rebbachisaurid sauropod, Elrhaz Formation, Niger).

A small, 9-metre sauropod built for grazing: a relatively short neck held low and angled
down, a light skull ending in a broad, straight-edged, shovel-like muzzle wider than the
rest of the head and lined with hundreds of small teeth, a deep body, pillar legs and a long whip-like tail. Grey-brown with darker
saddles, paler underside and a light muzzle (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/nigersaurus_taqueti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Nigersaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.38, 0.33, 0.28)
FLANK = (0.56, 0.50, 0.42)
BELLY = (0.80, 0.76, 0.66)
SADDLE = (0.24, 0.21, 0.18)
MUZZLE = (0.78, 0.72, 0.60)


def make():
    s = dn.DinoSpec(
        name="Nigersaurus",
        paint=None,
        hip_y=0.22, hip_z=0.42, body_len=0.50, torso_w=0.15, torso_h=0.16, belly=0.03, chest_dz=-0.02,
        tail_len=1.05, tail_r=0.5, tail_droop=-0.10,
        neck_len=0.40, neck_rise=0.02, neck_r=0.04, neck_s=-0.03,
        head_rows=[(0.0, 0.0, 0.032, 0.035), (-0.04, -0.012, 0.03, 0.032), (-0.08, -0.03, 0.034, 0.026),
                   (-0.115, -0.05, 0.05, 0.022), (-0.13, -0.06, 0.055, 0.02), (-0.135, -0.062, 0.0, 0.0)],
        head_len=0.135, head_h=0.035, head_w=0.032,
        leg_r=0.065, leg_type="column", leg_x=0.02, toes=3, toe_len=0.035, toe_r=0.02, claw=0.018, stride=0.05,
        fore="leg", fore_type="column", arm_r=0.055, fore_toes=0, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.008, eye_pos=(-0.035, 0.012, 0.85), eye_col=(0.35, 0.22, 0.10), scales=0.0015,
        voxel=0.009, max_tris=13000,
    )
    hb = s.head_base

    def extra(co, n, c):
        if co.y < hb.y - 0.09:
            return nh.lerp(c, MUZZLE, nh.smoothstep(hb.y - 0.09, hb.y - 0.12, co.y) * 0.8)
        return c
    s.paint = dn.make_paint(BACK, FLANK, BELLY, stripe=SADDLE, freq=12.0, stripe_amt=0.55, mottle=0.12,
                            extra=extra, y_range=(s.chest_y - 0.1, 1.5))
    def crisp(mb, s):
        # the row of tiny teeth across the front of the broad muzzle
        tip_y, tip_z = hb.y - 0.128, hb.z - 0.075
        for k in range(15):
            x = -0.048 + 0.096 * k / 14
            mb.add(cc.cone((x, tip_y, tip_z + 0.006), (x, tip_y - 0.004, tip_z - 0.008), 0.003, sides=4), cc.TOOTH, smooth=False)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Nigersaurus")
