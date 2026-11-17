"""
Procedural Deinosuchus riograndensis (Late Cretaceous alligatoroid, Texas and the
southern USA).

A giant relative of alligators, perhaps 10-12 metres long, with a long, broad snout ending in
a bulbous tip, huge blunt teeth for crushing turtles and grabbing dinosaurs at the water's
edge, and rows of deeply pitted osteoderms down the back. Sprawling legs, a deep, flattened
swimming tail with a double crest of scutes. Dark olive-grey back, paler flanks, cream belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/deinosuchus_riograndensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Deinosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.20, 0.22, 0.17)
FLANK = (0.36, 0.37, 0.28)
BELLY = (0.82, 0.78, 0.62)
SCUTE = (0.14, 0.15, 0.12)


def make():
    s = dn.DinoSpec(
        name="Deinosuchus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.12, 0.13, 0.10), freq=28.0, stripe_amt=0.45, mottle=0.15),
        hip_y=0.25, hip_z=0.15, body_len=0.55, torso_w=0.17, torso_h=0.10, belly=0.0,
        tail_len=0.85, tail_r=0.85, tail_droop=-0.04, tail_flat=0.45,
        neck_len=0.10, neck_rise=0.01, neck_r=0.075, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.10, 0.055), (-0.10, -0.005, 0.085, 0.045), (-0.22, -0.012, 0.06, 0.03),
                   (-0.34, -0.015, 0.05, 0.024), (-0.42, -0.015, 0.058, 0.026), (-0.47, -0.017, 0.035, 0.018),
                   (-0.49, -0.018, 0.0, 0.0)],
        head_len=0.49, head_h=0.055, head_w=0.10, jaw=True, jaw_open=8, jaw_h=0.45, teeth=10, tooth_len=0.02,
        leg_type="sprawl", leg_r=0.045, toes=4, toe_len=0.06, toe_r=0.013, claw=0.015, stride=0.05,
        fore="leg", fore_type="sprawl", arm_r=0.035, fore_toes=5, shoulder_dy=0.05,
        eye_r=0.015, eye_pos=(-0.04, 0.045, 0.5), eye_col=(0.75, 0.62, 0.2), scales=0.003, voxel=0.01,
        max_tris=13000,
    )
    # double row of osteoderms down the back and the tail crests
    for k in range(16):
        y = s.chest_y + 0.02 + k * 0.05
        s.blobs.append(((0.04, y, s.hip_z + 0.085), (0.02, 0.02, 0.014), True))
    for k in range(10):
        c, r = dn.tail_point(s, 0.05 + 0.08 * k)
        s.blobs.append(((0.02, c.y, c.z + r * 0.9), (0.008, 0.02, 0.018 * (1 - k / 12)), True))
    s.paint = dn.make_paint(BACK, FLANK, BELLY, mottle=0.15,
                            extra=lambda co, n, c: nh.lerp(c, SCUTE, 0.6 * cc.spots(co, 30.0, 0.3) * nh.smoothstep(0.5, 0.9, n.z)))
    return s


if __name__ == "__main__":
    dn.run(make, "Deinosuchus")
