"""
Procedural Kryptobaatar dashzevegi (Late Cretaceous multituberculate, Djadokhta Formation,
Mongolia).

A mouse-sized multituberculate, the "rodents" of the dinosaur age: a short, broad head
with a blunt muzzle, big gnawing front incisors, round ears and dark eyes, a plump body on
short, sprawling legs with clawed feet for digging, and a long, tapering tail. Warm
grey-brown fur with a buff belly and a darker dorsal stripe (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kryptobaatar_dashzevegi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kryptobaatar.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

FUR = (0.32, 0.27, 0.22)
FUR_LIGHT = (0.55, 0.47, 0.37)
BELLY = (0.88, 0.80, 0.64)
STRIPE = (0.16, 0.13, 0.10)
NOSE = (0.40, 0.24, 0.22)
INCISOR = (0.90, 0.70, 0.35)


def make():
    s = dn.DinoSpec(
        name="Kryptobaatar",
        paint=dn.make_paint(FUR, FUR_LIGHT, BELLY, mottle=0.18,
                            extra=lambda co, n, c: nh.lerp(c, STRIPE, 0.7 * nh.smoothstep(0.85, 0.97, n.z))),
        hip_y=0.22, hip_z=0.20, body_len=0.48, torso_w=0.15, torso_h=0.14, belly=0.0, chest_dz=0.0,
        tail_len=0.75, tail_r=0.25, tail_droop=-0.08,
        neck_len=0.05, neck_rise=0.03, neck_r=0.09, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.10, 0.09), (-0.07, -0.01, 0.095, 0.08), (-0.14, -0.03, 0.06, 0.055),
                   (-0.18, -0.045, 0.035, 0.035), (-0.195, -0.05, 0.0, 0.0)],
        head_len=0.195, head_h=0.09, head_w=0.10,
        leg_type="sprawl", leg_r=0.045, toes=5, toe_len=0.035, toe_r=0.009, claw=0.014, stride=0.05,
        fore="leg", fore_type="sprawl", arm_r=0.04, fore_toes=5, shoulder_dy=0.06,
        eye_r=0.016, eye_pos=(-0.08, 0.03, 0.8), eye_col=(0.04, 0.03, 0.03),
        fuzz=0.006, scales=0.0, voxel=0.008, max_tris=9000,
    )
    hb = s.head_base

    def crisp(mb, s):
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.07, hb.y + 0.02, hb.z + 0.08), (0.03, 0.012, 0.032), subdivisions=2), NOSE)
            p = Vector((sx * 0.01, hb.y - 0.18, hb.z - 0.05))
            mb.add(cc.curved_cone(p, p + Vector((0, -0.01, -0.015)), p + Vector((0, -0.012, -0.03)), 0.008), INCISOR)
        mb.add(nh.ellipsoid((0, hb.y - 0.195, hb.z - 0.04), (0.016, 0.01, 0.012), subdivisions=2), NOSE)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Kryptobaatar")
