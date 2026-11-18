"""
Procedural Styracosaurus albertensis (Late Cretaceous centrosaurine ceratopsian, Alberta).

A 5.5-metre horned dinosaur: a huge head with a deep parrot beak, one long upright nose
horn, small brow bumps, and a short frill crowned with six long spikes fanning up and back;
a bulky body on stout legs and a short tail. Olive-tan with darker dappling, a pale belly,
the frill edged in rust with dark spikes.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/styracosaurus_albertensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Styracosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.33, 0.22)
FLANK = (0.56, 0.50, 0.34)
BELLY = (0.86, 0.80, 0.64)
FRILL = (0.62, 0.48, 0.30)
FRILL_EDGE = (0.58, 0.20, 0.10)
HORN = (0.30, 0.25, 0.20)
BEAK = (0.18, 0.16, 0.14)


def make():
    s = dn.DinoSpec(
        name="Styracosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=(0.24, 0.22, 0.14), spot_scale=10.0),
        hip_y=0.28, hip_z=0.48, body_len=0.62, torso_w=0.20, torso_h=0.21, belly=0.04, chest_dz=-0.04,
        tail_len=0.50, tail_r=0.6, tail_droop=-0.10, tail_flat=0.6,
        neck_len=0.06, neck_rise=0.02, neck_r=0.10, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.09, 0.10), (-0.08, -0.01, 0.09, 0.105), (-0.18, -0.04, 0.065, 0.085),
                   (-0.27, -0.08, 0.04, 0.055), (-0.32, -0.12, 0.0, 0.0)],
        head_len=0.32, head_h=0.10, head_w=0.09,
        leg_r=0.09, leg_type="column", toes=4, toe_len=0.05, toe_r=0.022, claw=0.012, stride=0.04,
        fore="leg", fore_type="bent", arm_r=0.065, fore_toes=4, shoulder_dy=0.05,
        eye_r=0.014, eye_pos=(-0.10, 0.03, 0.85), eye_col=(0.75, 0.45, 0.12), scales=0.002, voxel=0.01,
        max_tris=13000,
    )
    hb = s.head_base

    def crisp(mb, s):
        # nose horn: long and upright, slightly curved back
        base = Vector((0, hb.y - 0.22, hb.z + 0.05))
        mb.add(cc.curved_cone(base, base + Vector((0, 0.0, 0.12)), base + Vector((0, 0.05, 0.22)), 0.03, sides=8), HORN)
        for sx in (1, -1):
            p = Vector((sx * 0.05, hb.y - 0.10, hb.z + 0.08))
            mb.add(cc.cone(p, p + Vector((sx * 0.01, 0.0, 0.03)), 0.014, sides=6), HORN)
        # short frill shield
        lead, trail = [], []
        n = 11
        for i in range(n):
            a = math.pi * i / (n - 1)
            x = math.cos(a)
            lead.append((x * 0.085, hb.y - 0.01, hb.z + 0.05 + 0.03 * math.sin(a)))
            trail.append((x * 0.17, hb.y + 0.11, hb.z + 0.13 + 0.10 * math.sin(a)))
        mb.add(cc.membrane(lead, trail, nv=5, thickness=0.022, normal_hint=Vector((0, 0.6, 0.8)).normalized()), FRILL)
        # six great spikes radiating from the frill edge, plus small knobs
        for k, a in enumerate((0.18, 0.30, 0.42, 0.58, 0.70, 0.82)):
            a *= math.pi
            p = Vector((math.cos(a) * 0.15, hb.y + 0.10, hb.z + 0.12 + 0.09 * math.sin(a)))
            d = Vector((math.cos(a) * 0.7, 0.55, math.sin(a) * 0.9)).normalized()
            ln = 0.22 if 1 <= k <= 4 else 0.15
            mb.add(cc.curved_cone(p, p + d * ln * 0.5, p + d * ln + Vector((0, 0.03, 0)), 0.022, sides=7), HORN)
        for a in (0.05, 0.95):
            a *= math.pi
            p = Vector((math.cos(a) * 0.17, hb.y + 0.10, hb.z + 0.13 + 0.05 * math.sin(a)))
            mb.add(nh.ellipsoid(tuple(p), (0.015, 0.015, 0.015), subdivisions=1), FRILL_EDGE)
        mb.add(nh.ellipsoid((0, hb.y - 0.305, hb.z - 0.10), (0.03, 0.04, 0.05), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Styracosaurus")
