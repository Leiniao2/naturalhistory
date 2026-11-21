"""
Procedural emperor penguin (Aptenodytes forsteri, Pleistocene to today,
Antarctica) for map colonies.

The largest living penguin, about 1.1-1.3 m tall and 22-45 kg, which breeds on
the sea ice through the Antarctic winter and dives to over 500 m: blue-black
back, flippers and head, a white belly washed pale yellow on the breast, golden
ear patches on the sides of the neck and an orange-pink stripe on the long,
slightly curved bill. Shown swimming with its flippers spread. Built with
nh_pal_bird.py (Penguin). Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/aptenodytes_forsteri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AptenodytesForsteri.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_b2_quaternary_kit as kit  # noqa: E402,F401

import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Penguin(
    name="AptenodytesForsteri",
    length=1.5, girth=0.27, beak_len=0.17, flipper=0.45,
    back=(0.08, 0.09, 0.13), belly=(0.95, 0.94, 0.90), beak_col=(0.10, 0.09, 0.10),
)
GOLD = (0.98, 0.72, 0.15)


def paint(co, n, c):
    L, g = SPEC.length, SPEC.girth
    y0 = -L * 0.45   # head centre (before the object was re-centred, see below)
    return None


def build():
    obj = nb.build_penguin(SPEC)
    vs = obj.data.vertices
    ymin = min(v.co.y for v in vs)
    L, g = SPEC.length, SPEC.girth
    head_y = ymin + SPEC.beak_len + g * 0.5   # back of the bill = front of the head

    def marks(co, n, c):
        d = co.y - head_y
        # golden ear patch on each side behind the eye, fading into a yellow wash on the upper breast
        if 0.04 < d < 0.30 and abs(co.x) > g * 0.30 and -g * 0.25 < co.z < g * 0.30:
            k = nh.smoothstep(0.04, 0.10, d) * (1 - nh.smoothstep(0.20, 0.30, d))
            return nh.lerp(c, GOLD, 0.95 * k)
        if 0.15 < d < 0.55 and co.z < -g * 0.05 and sum(c) > 2.0:
            return nh.lerp(c, (1.0, 0.90, 0.60), 0.5 * (1 - nh.smoothstep(0.3, 0.55, d)))
        # orange stripe along the lower bill
        if co.y < head_y - 0.02 and co.z < -0.005 and co.y > ymin + 0.03:
            return (0.95, 0.50, 0.30)
        return None
    return kit.repaint(obj, marks)


if __name__ == "__main__":
    nh.run(build, SPEC.name, background=(0.05, 0.22, 0.32), views=((35, 25), (-90, 5), (0, 80)))
