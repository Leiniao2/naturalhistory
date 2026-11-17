"""
Procedural Protoceratops andrewsi (Late Cretaceous ceratopsian, Gobi Desert, Mongolia).

A sheep-sized, four-legged horned-dinosaur relative without real horns: a big head with a
deep parrot-like beak, a low bump over the nose and a broad bony frill sweeping back over the
neck; a stocky body and a tall, deep tail. Famous for the 'Fighting Dinosaurs' fossil locked
with a Velociraptor. Sandy-ochre with a darker back, pale belly and a frill edged in rust.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/protoceratops_andrewsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protoceratops.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.50, 0.38, 0.22)
FLANK = (0.70, 0.58, 0.38)
BELLY = (0.90, 0.84, 0.68)
FRILL = (0.74, 0.62, 0.42)
FRILL_EDGE = (0.55, 0.22, 0.12)
BEAK = (0.22, 0.20, 0.17)


def make():
    s = dn.DinoSpec(
        name="Protoceratops",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.35, 0.25, 0.14), freq=24.0, stripe_amt=0.4),
        hip_y=0.25, hip_z=0.40, body_len=0.55, torso_w=0.15, torso_h=0.16, belly=0.03, chest_dz=-0.04,
        tail_len=0.6, tail_r=0.65, tail_droop=-0.08, tail_flat=0.5,
        neck_len=0.08, neck_rise=0.06, neck_r=0.07, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.07, 0.08), (-0.08, -0.01, 0.07, 0.085), (-0.18, -0.03, 0.05, 0.07),
                   (-0.26, -0.06, 0.03, 0.045), (-0.30, -0.09, 0.0, 0.0)],
        head_len=0.30, head_h=0.08, head_w=0.07,
        leg_r=0.07, leg_type="column", toes=4, toe_len=0.05, toe_r=0.018, claw=0.012, stride=0.04,
        fore="leg", fore_type="bent", arm_r=0.045, fore_toes=4, shoulder_dy=0.05,
        eye_r=0.014, eye_pos=(-0.09, 0.03, 0.85), eye_col=(0.75, 0.45, 0.12), scales=0.002, voxel=0.009,
        max_tris=12000,
    )
    hb = s.head_base
    s.blobs.append(((0, hb.y - 0.19, hb.z + 0.04), (0.02, 0.04, 0.03), False))   # nasal bump

    def crisp(mb, s):
        # frill: a broad curved shield rising up and back from the rear of the skull
        lead, trail = [], []
        n = 11
        for i in range(n):
            a = math.pi * i / (n - 1)
            x = math.cos(a)
            lead.append((x * 0.065, hb.y - 0.02, hb.z + 0.03 + 0.03 * math.sin(a)))
            trail.append((x * 0.15, hb.y + 0.16 + 0.03 * math.sin(a), hb.z + 0.10 + 0.14 * math.sin(a)))

        def col(co, nn):
            d = (Vector(co) - Vector((0, hb.y - 0.02, hb.z + 0.03))).length
            return FRILL_EDGE if d > 0.20 else FRILL
        mb.add(cc.membrane(lead, trail, nv=6, thickness=0.02, normal_hint=Vector((0, 0.6, 0.8)).normalized()), col)
        mb.add(nh.ellipsoid((0, hb.y - 0.285, hb.z - 0.07), (0.022, 0.03, 0.04), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Protoceratops")
