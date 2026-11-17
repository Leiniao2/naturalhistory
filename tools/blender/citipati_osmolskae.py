"""
Procedural Citipati osmolskae (Late Cretaceous oviraptorid, Gobi Desert, Mongolia).

An emu-sized feathered oviraptorosaur: long neck, a short deep head with a toothless parrot-
like beak and a tall rounded crest, feathered arms with clawed fingers (known from adults
fossilised brooding on their nests with arms spread over the eggs), long legs and a short
tail ending in a fan of feathers. Dark brown plumage, grey neck, a red-orange crest.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/citipati_osmolskae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Citipati.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.26, 0.18, 0.12)
FLANK = (0.40, 0.30, 0.21)
BELLY = (0.72, 0.64, 0.52)
NECK = (0.55, 0.55, 0.55)
CREST = (0.85, 0.32, 0.10)
BEAK = (0.86, 0.80, 0.62)
QUILL = (0.12, 0.09, 0.07)
QUILL_TIP = (0.90, 0.88, 0.82)
S = None


def extra(co, n, c):
    s = S
    hb = s.head_base
    if co.y < s.chest_y and co.z > s.chest_z + 0.05:
        c = nh.lerp(c, NECK, nh.smoothstep(s.chest_z + 0.05, s.chest_z + 0.2, co.z) * 0.8)
    if co.z > hb.z + s.head_h * 0.8:
        c = nh.lerp(c, CREST, nh.smoothstep(hb.z + s.head_h * 0.8, hb.z + s.head_h * 1.1, co.z))
    return c


def make():
    global S
    s = dn.DinoSpec(
        name="Citipati",
        paint=dn.make_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
        hip_y=0.25, hip_z=0.62, body_len=0.42, torso_w=0.13, torso_h=0.15, belly=0.02, chest_dz=0.03,
        tail_len=0.45, tail_r=0.6, tail_droop=0.02,
        neck_len=0.32, neck_rise=0.42, neck_r=0.04, neck_s=0.05,
        head_rows=[(0.0, 0.0, 0.045, 0.06), (-0.05, 0.0, 0.045, 0.065), (-0.10, -0.01, 0.035, 0.05),
                   (-0.14, -0.03, 0.022, 0.03), (-0.165, -0.05, 0.0, 0.0)],
        head_len=0.165, head_h=0.06, head_w=0.045,
        leg_r=0.06, knee_fwd=0.12, toes=3, toe_len=0.09, toe_r=0.016, claw=0.02, stride=0.05,
        arm_len=0.30, arm_r=0.022, fingers=3, finger_len=0.07, hand_claw=0.03,
        eye_r=0.013, eye_pos=(-0.06, 0.025, 0.9), eye_col=(0.80, 0.62, 0.20),
        fuzz=0.004, scales=0.0, voxel=0.009, max_tris=11000,
    )
    S = s
    hb = s.head_base
    # tall rounded crest over the snout and skull roof
    s.blobs.append(((0.0, hb.y - 0.06, hb.z + 0.075), (0.016, 0.065, 0.06), False))

    def crisp(mb, s):
        # horny beak over the snout tip and lower jaw
        mb.add(nh.ellipsoid((0, hb.y - 0.14, hb.z - 0.04), (0.022, 0.035, 0.03), subdivisions=2), BEAK)
        dn.arm_vanes(mb, s, lambda co, n: QUILL if co.y < s.chest_y + 0.12 else QUILL_TIP, length=0.16)
        dn.tail_fan(mb, s, lambda co, n: QUILL, u0=0.3, width=0.09)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Citipati")
