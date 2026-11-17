"""
Procedural Sinosauropteryx prima (Early Cretaceous compsognathid, Yixian Formation, China).

The first non-avian dinosaur found with feathers: a small, long-legged hunter with a short
head, a fuzzy coat of simple filaments and an extremely long tail. Its colours are known
from fossil melanosomes: rufous-brown above, pale below (countershading), a dark 'bandit
mask' across the eyes, and a tail ringed with alternating ginger and white bands.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sinosauropteryx_prima.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sinosauropteryx.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.52, 0.24, 0.10)
FLANK = (0.70, 0.40, 0.20)
BELLY = (0.93, 0.88, 0.80)
MASK = (0.16, 0.08, 0.05)
WHITE = (0.94, 0.92, 0.86)

S = None


def extra(co, n, c):
    s = S
    # banded tail: whole-circumference rings behind the hips
    if co.y > s.hip_y + 0.12:
        b = 0.5 + 0.5 * math.sin((co.y - s.hip_y) * 30.0)
        c = nh.lerp(c, WHITE, nh.smoothstep(0.55, 0.7, b) * 0.9)
        c = nh.lerp(c, BACK, nh.smoothstep(0.45, 0.3, b) * 0.5)
    # bandit mask across the eye
    hb = s.head_base
    if co.y < hb.y + 0.01 and co.z > hb.z - s.head_h * 0.1:
        f = nh.smoothstep(hb.y + 0.01, hb.y - 0.02, co.y) * (1 - nh.smoothstep(hb.y - 0.07, hb.y - 0.10, co.y))
        c = nh.lerp(c, MASK, 0.9 * f * nh.smoothstep(0.75, 0.3, n.z))
    return c


def make():
    global S
    s = dn.DinoSpec(
        name="Sinosauropteryx",
        paint=dn.make_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
        hip_y=0.05, hip_z=0.36, body_len=0.32, torso_w=0.065, torso_h=0.08, belly=0.015,
        tail_len=1.25, tail_r=0.65, tail_droop=0.02,
        neck_len=0.16, neck_rise=0.13, neck_r=0.03, neck_s=0.025,
        head_len=0.15, head_h=0.035, head_w=0.03, snout_h=0.5, snout_w=0.45, snout_drop=0.005,
        leg_r=0.035, knee_fwd=0.07, toes=3, toe_len=0.05, toe_r=0.009, claw=0.012, stride=0.04,
        arm_len=0.12, arm_r=0.012, fingers=3, finger_len=0.03, hand_claw=0.012,
        eye_r=0.012, eye_col=(0.30, 0.20, 0.10), fuzz=0.004, scales=0.0, voxel=0.0075, max_tris=9000,
    )
    S = s
    return s


if __name__ == "__main__":
    dn.run(make, "Sinosauropteryx")
