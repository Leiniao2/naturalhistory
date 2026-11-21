"""
Procedural Deinocheirus mirificus (Late Cretaceous ornithomimosaur, Nemegt Formation, Mongolia).

An 11-metre, hump-backed giant ostrich-dinosaur: a tall sail-like hump over the hips, a
long neck, a long, low, toothless skull ending in a broad, flared duck-like bill, huge arms
with three long blunt-clawed fingers, heavy legs with broad, blunt toes for soft ground,
and a tail ending in a fan of feathers (a fused pygostyle). Feathered body, olive-brown
with paler flanks, a cream belly and dark arm and tail plumes (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/deinocheirus_mirificus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Deinocheirus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.33, 0.29, 0.20)
FLANK = (0.55, 0.49, 0.36)
BELLY = (0.88, 0.84, 0.72)
PLUME = (0.24, 0.20, 0.16)
BILL = (0.30, 0.26, 0.20)


def make():
    s = dn.DinoSpec(
        name="Deinocheirus",
        paint=dn.make_paint(BACK, FLANK, BELLY, mottle=0.1),
        hip_y=0.2, hip_z=0.58, body_len=0.46, torso_w=0.15, torso_h=0.19, belly=0.05, chest_dz=0.0,
        tail_len=0.62, tail_r=0.55, tail_droop=-0.05,
        neck_len=0.32, neck_rise=0.30, neck_r=0.05, neck_s=0.05,
        head_rows=[(0.0, 0.0, 0.04, 0.045), (-0.06, -0.005, 0.035, 0.04), (-0.13, -0.02, 0.025, 0.028),
                   (-0.20, -0.035, 0.03, 0.02), (-0.25, -0.045, 0.04, 0.016), (-0.27, -0.048, 0.0, 0.0)],
        head_len=0.27, head_h=0.045, head_w=0.04,
        leg_r=0.09, knee_fwd=0.11, ankle_back=0.05, toes=3, toe_len=0.08, toe_r=0.026, claw=0.012, stride=0.07,
        arm_len=0.42, arm_r=0.04, fingers=3, finger_len=0.14, hand_claw=0.07, finger_r=0.016, arm_x=0.05,
        hand_dir=(0, -0.5, -1.0), arm_lift=-0.06,
        eye_r=0.011, eye_pos=(-0.03, 0.015, 0.85), eye_col=(0.70, 0.50, 0.15), fuzz=0.005, scales=0.0,
        voxel=0.01, max_tris=14000,
    )
    # the tall neural-spine hump over the back and hips
    s.lofts.append(lambda: cc.limb([(0, s.chest_y + 0.06, s.hip_z + 0.05), (0, s.hip_y - 0.18, s.hip_z + 0.26),
                                    (0, s.hip_y + 0.02, s.hip_z + 0.22), (0, s.hip_y + 0.18, s.hip_z + 0.04)],
                                   [0.05, 0.06, 0.06, 0.04], flat=(0.7, 1.0)))
    s.blobs.append(((0, s.hip_y - 0.12, s.hip_z + 0.12), (0.10, 0.20, 0.12), False))
    hb = s.head_base

    def crisp(mb, s):
        dn.arm_vanes(mb, s, lambda co, n: PLUME, length=0.07, n=5, droop=0.3)
        # tail-tip fan of feathers
        c, r = dn.tail_point(s, 0.85)
        for k in range(7):
            a = (k - 3) * 0.28
            d = Vector((0.5 * a, 1.0, 0.25)).normalized()
            mb.add(cc.cone(c, c + d * 0.16, 0.022, sides=5), PLUME)
        # the broad, flared bill
        mb.add(nh.ellipsoid((0, hb.y - 0.245, hb.z - 0.05), (0.045, 0.035, 0.012), subdivisions=2), BILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Deinocheirus")
