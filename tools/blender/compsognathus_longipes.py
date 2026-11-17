"""
Procedural Compsognathus longipes (Late Jurassic Solnhofen theropod) for map colonies.

A turkey-sized, very lightly built predator: small, long and low skull with tiny teeth,
big eyes, long slender neck, long legs with a long shin and foot, short two-fingered arms
and a very long, thin tail making up more than half its length. Painted with a soft
fuzzy coat (protofeathers as in its relatives): warm rufous-brown back with darker tail
bands, a pale throat and belly, and a dark mask through the eye. Built with
nh_jur_theropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/compsognathus_longipes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Compsognathus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_theropod as th  # noqa: E402
from mathutils import noise  # noqa: E402

MASK = (0.14, 0.10, 0.08)


def markings(co, n, c):
    # dark mask band along the side of the head
    if co.y < -1.0 and co.z > 1.25 and abs(n.x) > 0.4:
        c = nh.lerp(c, MASK, 0.6)
    # fluffy streaks
    m = noise.noise((co.x * 30.0, co.y * 90.0, co.z * 30.0))
    return tuple(v * (1.0 + 0.12 * m) for v in c)


SPEC = th.Spec(
    name="Compsognathus",
    paint=kit.paint(back=(0.40, 0.22, 0.12), flank=(0.62, 0.40, 0.22), belly=(0.92, 0.86, 0.74),
                    stripe=(0.18, 0.10, 0.06), freq=30.0, y_range=(0.4, 2.2), extra=markings),
    body_len=0.42, body_hw=0.11, body_hh=0.16, tail_len=1.9, tail_lift=0.05,
    neck_len=0.42, neck_angle=40, neck_r=0.05, head_len=0.3, head_h=0.1, head_w=0.06, snout_taper=0.55,
    head_pitch=-4, jaw_h=0.035, jaw_open=6, teeth=8, tooth_len=0.012,
    thigh_r=0.09, shin_r=0.04, meta_r=0.026, toe_len=0.14, stride=0.16,
    arm_len=0.22, arm_r=0.025, fingers=2, finger_len=0.06,
    eye_r=0.022, voxel=0.01, max_tris=9000,
)

if __name__ == "__main__":
    nh.run(lambda: th.build(SPEC), "Compsognathus", **th.PREVIEW)
