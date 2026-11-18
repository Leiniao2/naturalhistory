"""
Procedural Borealopelta markmitchelli (Early Cretaceous nodosaurid, Alberta).

A 5.5-metre nodosaur with no tail club: a broad, low body covered in a mosaic of rounded
and keeled osteoderm plates, a narrow pear-shaped head, a neck armoured with half-rings,
and a pair of long, curved shoulder spikes jutting forward and out. Coloured as the
preserved pigments suggest: reddish-brown on top fading to a pale belly (countershading).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/borealopelta_markmitchelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Borealopelta.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_armour as ar  # noqa: E402

BACK = (0.42, 0.18, 0.10)
FLANK = (0.58, 0.34, 0.22)
BELLY = (0.84, 0.74, 0.58)
PLATE = (0.68, 0.46, 0.30)
SPIKE = (0.78, 0.64, 0.48)


def make():
    s = dn.DinoSpec(
        name="Borealopelta",
        paint=dn.make_paint(BACK, FLANK, BELLY, mottle=0.1),
        hip_y=0.28, hip_z=0.36, body_len=0.62, torso_w=0.28, torso_h=0.20, belly=0.0, chest_dz=-0.02,
        tail_len=0.70, tail_r=0.45, tail_droop=-0.06, tail_flat=1.3,
        neck_len=0.08, neck_rise=-0.02, neck_r=0.09, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.08, 0.065), (-0.05, -0.005, 0.08, 0.06), (-0.12, -0.02, 0.06, 0.045),
                   (-0.17, -0.04, 0.04, 0.032), (-0.19, -0.05, 0.0, 0.0)],
        head_len=0.19, head_h=0.065, head_w=0.08,
        leg_r=0.08, leg_type="column", leg_x=0.04, toes=4, toe_len=0.04, toe_r=0.02, claw=0.01, stride=0.04,
        fore="leg", fore_type="bent", arm_r=0.06, fore_toes=5, shoulder_dy=0.06,
        eye_r=0.012, eye_pos=(-0.07, 0.025, 0.85), eye_col=(0.65, 0.45, 0.15), scales=0.002, voxel=0.01,
        max_tris=12000,
    )
    hb = s.head_base

    def crisp(mb, s):
        ys = [s.chest_y + 0.02 + 0.06 * k for k in range(12)]
        ar.scutes(mb, s, ys, [-70, -50, -30, -10, 10, 30, 50, 70], 0.034, PLATE, height=0.3)
        ys_t = [s.hip_y + 0.06 + 0.07 * k for k in range(7)]
        ar.spikes(mb, s, ys_t, 75, 0.04, 0.016, PLATE, back=0.6)
        # neck half-rings
        for k in range(2):
            y = s.chest_y - 0.05 - 0.05 * k
            ar.scutes(mb, s, [y], [-50, -20, 20, 50], 0.022, PLATE, height=0.4)
        # the great shoulder spikes, curving forward and out
        for sx in (1, -1):
            p, n = ar.surface(s, s.chest_y + 0.06, 70 * sx, inset=0.01)
            mid = p + Vector((sx * 0.08, -0.06, 0.03))
            tip = p + Vector((sx * 0.14, -0.15, 0.04))
            mb.add(cc.curved_cone(p, mid, tip, 0.035, sides=8), SPIKE)
            p, n = ar.surface(s, s.chest_y + 0.14, 78 * sx, inset=0.01)
            mb.add(cc.cone(p, p + Vector((sx * 0.10, -0.04, 0.0)), 0.025, sides=7), SPIKE)
        mb.add(nh.ellipsoid((0, hb.y - 0.18, hb.z - 0.045), (0.035, 0.022, 0.018), subdivisions=2), (0.2, 0.15, 0.12))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Borealopelta")
