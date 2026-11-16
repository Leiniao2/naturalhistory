"""
Procedural lone star tick (Amblyomma americanum), an unfed adult female questing on a
grass blade, for map colonies.

A tall grass blade rises from a small tuft and bends forward; the tick clings to its
tip, nose raised, legs II-IV hooked round the blade's edges and the first pair of legs
held out forward and up. Female: a broad, flat, reddish-brown body; the finely pitted
brown scutum over its front tapers to a rounded point at the back, which carries the
single conspicuous silvery-white spot (the "lone star"); a pair of flat pale eyes sit
on the scutum's side margins. Eleven festoons scallop the rear edge. Long capitulum
(slender palps and hypostome, Amblyomma's long mouthparts) points forward; eight
reddish-brown legs with paler joints and paired claws. The tick is scaled up from life
against the blade so it reads on the map. Faces -Y, pivot on the ground (foot of the
grass at z = 0).

Usage:
  blender --background --python tools/blender/amblyomma_americanum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LoneStarTick.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_acari as acari  # noqa: E402
from mathutils import noise  # noqa: E402

BODY = (0.46, 0.21, 0.11)        # reddish-brown
BELLY = (0.28, 0.13, 0.07)
MARGIN = (0.55, 0.30, 0.17)
SCUTUM = (0.30, 0.15, 0.08)
PIT = (0.17, 0.08, 0.045)        # punctations on the scutum
SPOT = (0.96, 0.94, 0.86)        # the lone star
EYE = (0.86, 0.74, 0.46)
LEG = (0.34, 0.16, 0.085)
JOINT = (0.58, 0.40, 0.26)
MOUTH = (0.30, 0.15, 0.08)


def scutum_paint(xn, yn, t, co, n):
    c = acari.glossy(SCUTUM, acari.nh.lerp(SCUTUM, (0, 0, 0), 0.4), n, 0.45)
    pits = noise.noise(co * 90) > 0.38
    return nh.lerp(c, PIT, 0.7) if pits else c


SPEC = acari.Spec(
    name="LoneStarTick", kind="tick",
    length=0.50, width=0.40, height=0.06, belly=0.022, egg=0.18, hump=0.12,
    body_color=BODY, belly_color=BELLY, margin_color=MARGIN, gloss=0.3,
    scutum=(-0.50, 0.50, 0.64, 0.38), scutum_color=SCUTUM, scutum_paint=scutum_paint,
    spot=(SPOT, 0.095),
    eyes=(EYE, [(0.56, -0.62)]),
    festoons=11, festoon_arc=1.0, festoon_color=(0.54, 0.29, 0.16),
    basis_len=0.075, basis_w=0.10, basis_h=0.04, hypo_len=0.15, palp_len=0.16, palp_w=0.018,
    mouth_color=MOUTH,
    leg_y=(-0.62, -0.42, -0.22, -0.02), leg_len=(0.40, 0.36, 0.38, 0.43), leg_r=0.015,
    leg_color=LEG, leg_joint=JOINT, leg_tip=(0.40, 0.21, 0.11),
    grip=0.05,
)


def build():
    mb = acari.questing_perch(SPEC, pitch=16)
    obj = mb.to_object("LoneStarTick", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "LoneStarTick", ground=(0.33, 0.30, 0.20), views=((35, 30), (0, 70), (-90, 10)))
