"""
Procedural Asian longhorned tick (Haemaphysalis longicornis), an adult female questing
on a grass blade, for map colonies.

A tall grass blade rises from a small tuft and bends forward; the tick clings to its
tip, nose raised, legs II-IV hooked round the blade's edges and the first pair of legs
held out forward and up. A small, plain, reddish-brown tick with no markings and no
eyes: a slightly darker, finely pitted scutum over the front of the oval body and
eleven festoons along the rear edge. Its mouthparts are the giveaway: short and broad,
the palps flaring out sideways from the capitulum into pointed lateral projections
(the "horns" of its name) around a short hypostome. Eight reddish-brown legs with paler
joints and paired claws. The tick is scaled up from life against the blade so it reads
on the map. Faces -Y, pivot on the ground (foot of the grass at z = 0).

Usage:
  blender --background --python tools/blender/haemaphysalis_longicornis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LonghornedTick.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_acari as acari  # noqa: E402
from mathutils import noise  # noqa: E402

BODY = (0.60, 0.33, 0.17)        # light reddish-brown
BELLY = (0.38, 0.20, 0.10)
MARGIN = (0.68, 0.42, 0.24)
SCUTUM = (0.45, 0.22, 0.10)
PIT = (0.30, 0.14, 0.07)
LEG = (0.50, 0.27, 0.13)
JOINT = (0.70, 0.50, 0.32)
MOUTH = (0.46, 0.23, 0.11)


def scutum_paint(xn, yn, t, co, n):
    c = acari.glossy(SCUTUM, nh.lerp(SCUTUM, (0, 0, 0), 0.4), n, 0.4)
    return nh.lerp(c, PIT, 0.6) if noise.noise(co * 90) > 0.4 else c


SPEC = acari.Spec(
    name="LonghornedTick", kind="tick",
    length=0.44, width=0.33, height=0.06, belly=0.022, egg=0.24, hump=0.15,
    body_color=BODY, belly_color=BELLY, margin_color=MARGIN, gloss=0.3,
    scutum=(-0.52, 0.50, 0.60, 0.1), scutum_color=SCUTUM, scutum_paint=scutum_paint,
    festoons=11, festoon_arc=1.0, festoon_color=(0.66, 0.40, 0.22),
    basis_len=0.05, basis_w=0.12, basis_h=0.04, hypo_len=0.05, palp_len=0.07, palp_w=0.021,
    palp_flare=0.034, mouth_color=MOUTH,
    leg_y=(-0.62, -0.42, -0.22, -0.02), leg_len=(0.33, 0.30, 0.32, 0.36), leg_r=0.0135,
    leg_color=LEG, leg_joint=JOINT,
    grip=0.045,
)


def build():
    mb = acari.questing_perch(SPEC, pitch=16)
    obj = mb.to_object("LonghornedTick", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "LonghornedTick", ground=(0.33, 0.30, 0.20), views=((35, 30), (0, 70), (-90, 10)))
