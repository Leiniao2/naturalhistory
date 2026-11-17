"""
Procedural Edmontosaurus regalis (Late Cretaceous saurolophine hadrosaur, western North America).

One of the largest duck-billed dinosaurs, about 12 metres long: a long, low, flat-topped head
with a wide spoon-shaped beak and hundreds of grinding teeth behind it, no bony crest but a
fleshy comb on top of the head (known from a mummified E. regalis), a heavy body and deep
tail, walking on all fours. Grey-green back with darker blotches, pale belly, a red comb.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/edmontosaurus_regalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Edmontosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.33, 0.30)
FLANK = (0.48, 0.50, 0.44)
BELLY = (0.84, 0.82, 0.72)
BLOTCH = (0.18, 0.20, 0.18)
COMB = (0.70, 0.16, 0.10)
BILL = (0.28, 0.25, 0.22)


def make():
    s = dn.DinoSpec(
        name="Edmontosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=BLOTCH, spot_scale=8.0),
        hip_y=0.2, hip_z=0.58, body_len=0.64, torso_w=0.17, torso_h=0.21, belly=0.05, chest_dz=-0.08,
        tail_len=0.85, tail_r=0.6, tail_droop=-0.05, tail_flat=0.6,
        neck_len=0.22, neck_rise=0.10, neck_r=0.06, neck_s=0.03,
        head_len=0.32, head_h=0.06, head_w=0.05, snout_h=0.45, snout_w=1.0, snout_drop=0.07,
        leg_r=0.095, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.026, claw=0.01, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.042, fore_toes=3, shoulder_dy=0.06,
        eye_r=0.012, eye_col=(0.75, 0.5, 0.15), scales=0.002, voxel=0.011, max_tris=13000,
    )
    hb = s.head_base
    s.blobs.append(((0, hb.y - 0.02, hb.z + 0.06), (0.012, 0.06, 0.03), False))   # fleshy comb

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.31, hb.z - 0.065), (0.055, 0.035, 0.012), subdivisions=2), BILL)
    s.paint = dn.make_paint(BACK, FLANK, BELLY, spot=BLOTCH, spot_scale=8.0,
                            extra=lambda co, n, c: COMB if (co.z > hb.z + 0.045 and hb.y - 0.09 < co.y < hb.y + 0.05 and abs(co.x) < 0.02) else c)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Edmontosaurus")
