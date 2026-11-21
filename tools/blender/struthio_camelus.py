"""
Procedural common ostrich (Struthio camelus, Pleistocene to today; Africa,
and during the Ice Age also Asia) for map colonies.

The largest living bird, up to 2.7 m tall and 150 kg, flightless and the fastest
runner on two legs (about 70 km/h): a big rounded body of loose black plumage
(males) with white wing and tail plumes, a long, nearly bare pinkish-grey neck, a
small flat head with huge eyes and a short broad bill, and long, bare, powerful
legs. Built with nh_neo_bigbird.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/struthio_camelus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/StruthioCamelus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_b2_quaternary_kit as kit  # noqa: E402,F401

import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="StruthioCamelus",
    hip=1.05, body=(0.27, 0.42, 0.30), body_tilt=8, leg_r=0.07,
    neck=((0, -0.34, 0.25), (0, -0.44, 0.75), (0, -0.50, 1.15)), neck_r=(0.10, 0.05, 0.045),
    head_r=0.06, beak_len=0.10, beak_h=0.045, hook=0.0, wing=0.30, tail=0.16,
    feather=(0.07, 0.06, 0.06), dark=(0.04, 0.04, 0.04), pale=(0.95, 0.93, 0.88),
    head_col=(0.82, 0.56, 0.50),
    beak_col=(0.78, 0.66, 0.52), leg_col=(0.84, 0.58, 0.52), eye_col=(0.25, 0.16, 0.08), stride=0.34, shag=0.025,
)


def paint(co, n, c):
    hip = SPEC.hip
    # bare pinkish neck and thighs, white plumes on the wing tips and tail
    if co.z > hip + SPEC.body[2] * 1.05 and co.y < -0.2:
        return SPEC.head_col
    if co.z < hip - SPEC.body[2] * 0.6:
        return SPEC.leg_col if sum(c) > 0.4 else c
    if co.y > SPEC.body[1] * 0.6 and co.z > hip - SPEC.body[2] * 0.3:
        return nh.lerp(c, SPEC.pale, 0.9)
    if abs(co.x) > SPEC.body[0] * 0.95 and co.y > 0.0 and co.z > hip - SPEC.body[2] * 0.5:
        return nh.lerp(c, SPEC.pale, 0.85)
    return None


def build():
    obj = q.build(SPEC)
    return kit.repaint(obj, paint)


if __name__ == "__main__":
    nh.run(build, SPEC.name, ground=(0.62, 0.55, 0.40))
