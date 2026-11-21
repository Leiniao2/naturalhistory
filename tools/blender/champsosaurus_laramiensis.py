"""
Procedural Champsosaurus laramiensis (Late Cretaceous choristodere, Lance Formation, North America).

A 1.5-metre, gharial-like aquatic reptile (not a crocodile): a skull very wide at the back,
where the huge jaw muscles flare out behind the eyes, ending in a long, very narrow snout
lined with small, sharp teeth; nostrils and eyes on top; a low, flattened body with small
sprawling limbs and webbed feet, and a long, deep, side-flattened swimming tail.
Olive-grey back with darker blotches and a pale belly (colours conjectural).
Swim style: faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/champsosaurus_laramiensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Champsosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402

BACK = (0.28, 0.30, 0.22)
FLANK = (0.46, 0.47, 0.36)
BELLY = (0.84, 0.82, 0.70)
BLOTCH = (0.16, 0.17, 0.12)


def make():
    s = dn.DinoSpec(
        name="Champsosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=BLOTCH, spot_scale=11.0, mottle=0.12),
        hip_y=0.18, hip_z=0.12, body_len=0.42, torso_w=0.10, torso_h=0.065, belly=0.0,
        tail_len=0.80, tail_r=0.9, tail_droop=-0.01, tail_flat=0.4,
        neck_len=0.08, neck_rise=0.01, neck_r=0.05, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.085, 0.04), (-0.05, -0.002, 0.07, 0.036), (-0.10, -0.006, 0.03, 0.024),
                   (-0.20, -0.012, 0.018, 0.016), (-0.30, -0.016, 0.015, 0.013), (-0.36, -0.018, 0.011, 0.01),
                   (-0.38, -0.018, 0.0, 0.0)],
        head_len=0.38, head_h=0.04, head_w=0.085,
        leg_type="sprawl", leg_r=0.03, toes=5, toe_len=0.04, toe_r=0.007, claw=0.006, stride=0.06,
        fore="leg", fore_type="sprawl", arm_r=0.024, fore_toes=5, shoulder_dy=0.04,
        eye_r=0.011, eye_pos=(-0.085, 0.03, 0.55), eye_col=(0.85, 0.70, 0.25), scales=0.002,
        voxel=0.007, max_tris=10000, pivot="centre",
    )
    hb = s.head_base

    def crisp(mb, s):
        teeth = []
        for k in range(12):
            y = hb.y - 0.12 - 0.021 * k
            teeth += [(sx * 0.013, y, hb.z - 0.012) for sx in (1, -1)]
        cc.teeth_row(mb, teeth, 0.01, 0.0025, down=True)
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.004, hb.y - 0.372, hb.z - 0.012), (0.003, 0.004, 0.003), subdivisions=1),
                   (0.06, 0.05, 0.04))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Champsosaurus", preview=tp.SWIM_VIEWS)
