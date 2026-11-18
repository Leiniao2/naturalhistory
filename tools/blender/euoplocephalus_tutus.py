"""
Procedural Euoplocephalus tutus (Late Cretaceous ankylosaurid, Alberta).

A 5.5-metre armoured tank: a low, very broad body on short, splayed legs, a short, wide,
triangular skull with horn-like corners at the back, transverse bands of keeled osteoderms
across the neck, back and tail, a row of pointed spikes along each flank and a big two-lobed
bony club at the end of a stiff tail. Dark olive-brown hide, ochre armour with dark keels, a
pale belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/euoplocephalus_tutus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Euoplocephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_armour as ar  # noqa: E402

BACK = (0.30, 0.28, 0.18)
FLANK = (0.42, 0.38, 0.26)
BELLY = (0.74, 0.68, 0.52)
PLATE = (0.62, 0.50, 0.30)
KEEL = (0.26, 0.20, 0.14)
CLUB = (0.55, 0.45, 0.30)


def make():
    s = dn.DinoSpec(
        name="Euoplocephalus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.20, 0.18, 0.12), freq=14.0, stripe_amt=0.5),
        hip_y=0.28, hip_z=0.36, body_len=0.62, torso_w=0.30, torso_h=0.21, belly=0.0, chest_dz=-0.02,
        tail_len=0.70, tail_r=0.42, tail_droop=-0.05, tail_flat=1.5,
        neck_len=0.06, neck_rise=-0.02, neck_r=0.10, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.11, 0.07), (-0.05, -0.005, 0.11, 0.07), (-0.11, -0.02, 0.085, 0.055),
                   (-0.16, -0.04, 0.055, 0.04), (-0.18, -0.05, 0.0, 0.0)],
        head_len=0.18, head_h=0.07, head_w=0.11,
        leg_r=0.08, leg_type="column", leg_x=0.04, toes=4, toe_len=0.04, toe_r=0.02, claw=0.01, stride=0.04,
        fore="leg", fore_type="bent", arm_r=0.06, fore_toes=5, shoulder_dy=0.06,
        eye_r=0.012, eye_pos=(-0.07, 0.025, 0.85), eye_col=(0.65, 0.45, 0.15), scales=0.002, voxel=0.01,
        max_tris=12000,
    )
    # tail club: two big lateral knobs and a terminal one
    tip_c, _ = dn.tail_point(s, 0.9)
    s.blobs.append(((0.05, tip_c.y - 0.01, tip_c.z), (0.065, 0.075, 0.045), True))
    s.blobs.append(((0, tip_c.y + 0.05, tip_c.z), (0.04, 0.04, 0.035), False))
    hb = s.head_base

    def crisp(mb, s):
        # transverse bands of keeled plates over neck, back and the base of the tail
        ys = [s.chest_y - 0.02 + 0.075 * k for k in range(11)]
        ar.scutes(mb, s, ys, [-62, -38, -13, 13, 38, 62], 0.03, PLATE, height=0.5)
        ys_t = [s.hip_y + 0.08 + 0.08 * k for k in range(5)]
        ar.scutes(mb, s, ys_t, [-40, 0, 40], 0.022, PLATE, height=0.4)
        ar.spikes(mb, s, [s.chest_y + 0.06 + 0.12 * k for k in range(5)], 80, 0.08, 0.022, PLATE, back=0.5, up=-0.2)
        # horn-like corners at the back of the skull and the beak
        for sx in (1, -1):
            p = Vector((sx * 0.10, hb.y + 0.01, hb.z + 0.035))
            mb.add(cc.cone(p, p + Vector((sx * 0.04, 0.03, 0.01)), 0.018, sides=6), KEEL)
        mb.add(nh.ellipsoid((0, hb.y - 0.165, hb.z - 0.045), (0.045, 0.025, 0.02), subdivisions=2), (0.2, 0.18, 0.15))
    s.crisp = crisp
    # club painted bone-coloured
    club_y = tip_c.y - 0.08
    s.paint = dn.make_paint(BACK, FLANK, BELLY, stripe=(0.20, 0.18, 0.12), freq=14.0, stripe_amt=0.5,
                            extra=lambda co, n, c: nh.lerp(c, CLUB, nh.smoothstep(club_y, club_y + 0.04, co.y)))
    return s


if __name__ == "__main__":
    dn.run(make, "Euoplocephalus")
