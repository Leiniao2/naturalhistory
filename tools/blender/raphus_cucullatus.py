"""
Procedural dodo (Raphus cucullatus, Holocene of Mauritius, extinct by 1662)
for map colonies.

A flightless giant pigeon about 1 m tall and 10-18 kg, living on an island
without mammal predators: a stout, rounded body on short, thick yellow legs, tiny
useless wings, a curly tuft of tail feathers, and a big head with a bare face and
a long, heavy, hooked bill. Bluish-grey plumage, paler wings and tail tuft, a
greenish-yellow bill tip. Built with nh_pal_bird.py. Faces -Y, pivot on the
ground.

Usage:
  blender --background --python tools/blender/raphus_cucullatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RaphusCucullatus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_b2_quaternary_kit as kit  # noqa: E402,F401

import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Spec(
    name="RaphusCucullatus",
    body=(0.30, 0.40, 0.32), body_z=0.62, body_pitch=8,
    neck_len=0.22, neck_r=0.13, neck_lean=25, head_r=0.13,
    beak_len=0.30, beak_h=0.13, beak_w=0.09, beak_hook=0.10,
    leg_len=0.34, leg_r=0.05, thigh_r=0.12, toe_len=0.11,
    wing=0.10, tail=0.14,
    plumage=(0.50, 0.52, 0.55), back=(0.42, 0.44, 0.48), pale=(0.80, 0.78, 0.72), head_col=(0.55, 0.56, 0.58),
    wing_col=(0.78, 0.76, 0.70),
    beak_col=(0.80, 0.78, 0.55), leg_col=(0.85, 0.72, 0.25), eye_r=0.022, shaggy=0.8,
    voxel=0.012, max_tris=10000,
)


def tuft(co, n, c):
    # curly pale tail tuft and a darker, greenish hooked bill tip
    if co.y > SPEC.body[1] * 0.85 and co.z > SPEC.body_z - 0.05:
        return nh.lerp(c, (0.88, 0.86, 0.80), 0.8)
    return None


def build():
    obj = nb.build(SPEC)
    return kit.repaint(obj, tuft)


if __name__ == "__main__":
    nh.run(build, SPEC.name, ground=SPEC.ground)
