"""
Procedural blacklegged (deer) tick (Ixodes scapularis), an unfed adult female questing
on a grass blade, for map colonies.

A tall grass blade rises from a small tuft and bends forward; the tick clings to its
tip, nose raised, legs II-IV hooked round the blade's edges and the first pair of legs
held out forward and up to snag a passing host. Female: a glossy, dark brown-black
scutum covers the front third of an orange-red, egg-shaped body (alloscutum) with a
paler margin; long, slender capitulum (club-shaped palps either side of the hypostome)
pointing forward; eight black legs with paired claws. Like all Ixodes it has no eyes
and no festoons. The tick is scaled up from life against the blade so it reads on the
map. Faces -Y, pivot on the ground (foot of the grass at z = 0).

Usage:
  blender --background --python tools/blender/ixodes_scapularis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BlackleggedTick.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_acari as acari  # noqa: E402

BODY = (0.66, 0.20, 0.07)        # orange-red alloscutum
BELLY = (0.36, 0.10, 0.04)
MARGIN = (0.78, 0.34, 0.14)
SCUTUM = (0.065, 0.040, 0.030)   # dark brown-black
LEG = (0.05, 0.035, 0.03)
MOUTH = (0.10, 0.06, 0.045)

SPEC = acari.Spec(
    name="BlackleggedTick", kind="tick",
    length=0.48, width=0.36, height=0.075, belly=0.025, egg=0.26, hump=0.2,
    body_color=BODY, belly_color=BELLY, margin_color=MARGIN, gloss=0.35,
    scutum=(-0.56, 0.48, 0.60, 0.15), scutum_color=SCUTUM,
    basis_len=0.075, basis_w=0.09, basis_h=0.04, hypo_len=0.13, palp_len=0.14, palp_w=0.017,
    mouth_color=MOUTH,
    leg_y=(-0.62, -0.42, -0.22, -0.02), leg_len=(0.40, 0.36, 0.38, 0.42), leg_r=0.0145,
    leg_color=LEG, leg_joint=(0.09, 0.06, 0.05),
    grip=0.05,
)


def build():
    mb = acari.questing_perch(SPEC, pitch=16)
    obj = mb.to_object("BlackleggedTick", roughness=0.4)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "BlackleggedTick", ground=(0.33, 0.30, 0.20), views=((35, 30), (0, 70), (-90, 10)))
