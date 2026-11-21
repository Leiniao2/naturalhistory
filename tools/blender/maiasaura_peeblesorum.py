"""
Procedural Maiasaura peeblesorum (Late Cretaceous hadrosaur, Montana) for map colonies.

A 9-metre duck-billed dinosaur, the "good mother lizard": a deep body walking mostly on
all fours, a long, broad, flat-ended bill, a small solid bony crest rising just in front
of the eyes, a thick neck and a deep, stiff tail. Olive-brown back with darker transverse
bands, buff flanks and a pale belly, a horn-coloured beak.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/maiasaura_peeblesorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Maiasaura.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.36, 0.22)
FLANK = (0.60, 0.55, 0.38)
BELLY = (0.88, 0.84, 0.70)
BAND = (0.22, 0.20, 0.13)
CREST = (0.55, 0.30, 0.16)
BILL = (0.32, 0.27, 0.20)


def make():
    s = dn.DinoSpec(
        name="Maiasaura",
        paint=None,
        hip_y=0.2, hip_z=0.56, body_len=0.62, torso_w=0.18, torso_h=0.22, belly=0.06, chest_dz=-0.10,
        tail_len=0.80, tail_r=0.6, tail_droop=-0.08, tail_flat=0.55,
        neck_len=0.20, neck_rise=0.06, neck_r=0.07, neck_s=0.03,
        head_len=0.28, head_h=0.065, head_w=0.055, snout_h=0.42, snout_w=1.05, snout_drop=0.08,
        leg_r=0.10, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.028, claw=0.01, stride=0.06,
        fore="leg", fore_type="bent", arm_r=0.045, fore_toes=3, shoulder_dy=0.06,
        eye_r=0.012, eye_col=(0.70, 0.45, 0.12), scales=0.002, voxel=0.011, max_tris=13000,
    )
    hb = s.head_base
    # the solid crest: a low knob of bone above and in front of the eyes
    s.blobs.append(((0, hb.y - 0.07, hb.z + 0.055), (0.038, 0.045, 0.042), False))

    def extra(co, n, c):
        if co.z > hb.z + 0.05 and hb.y - 0.11 < co.y < hb.y - 0.03 and abs(co.x) < 0.035:
            return nh.lerp(c, CREST, 0.8)
        return c
    s.paint = dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=28.0, stripe_amt=0.75, mottle=0.1,
                            extra=extra, y_range=(hb.y + 0.05, 1.0))

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.275, hb.z - 0.075), (0.058, 0.035, 0.014), subdivisions=2), BILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Maiasaura")
