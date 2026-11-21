"""
Procedural Haast's eagle (Hieraaetus moorei, Pleistocene to about 1400 AD,
South Island of New Zealand) for map colonies.

The largest eagle known, females up to about 15 kg with a wingspan of 2.6-3 m:
relatively short, broad wings for flying between forest trees, a long tail, and
huge feet with tiger-sized talons with which it killed moa many times its own
weight. A massive, deep hooked bill. Shown soaring; dark brown plumage with a
paler head and breast, following reconstructions based on its closest living
relatives (the little and booted eagles). Built with nh_neo_soar.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/hieraaetus_moorei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HieraaetusMoorei.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_b2_quaternary_kit as kit  # noqa: E402,F401

import nh_neo_soar as q  # noqa: E402

SPEC = q.Spec(
    name="HieraaetusMoorei",
    span=2.8, chord=0.60, tip_chord=0.42, fingers=6, finger_len=0.24,
    body=(0.17, 0.42, 0.15), neck_len=0.12, head_r=0.085, beak_len=0.13, beak_r=0.045, hook=1.0,
    tail=0.42, tail_w=0.22,
    plumage=(0.24, 0.16, 0.10), under=(0.62, 0.50, 0.38), wing_top=(0.20, 0.14, 0.09),
    head_col=(0.60, 0.48, 0.34), beak_col=(0.85, 0.75, 0.30),
)


def build():
    obj = q.build(SPEC)
    # huge yellow feet with black talons tucked under the tail
    mb = nh.MeshBuilder()
    for sx in (-1, 1):
        a = Vector((sx * 0.07, 0.30, -0.12))
        mb.add(nh.tube([tuple(a), tuple(a + Vector((0, 0.16, -0.03)))], [0.035, 0.03], sides=8), (0.85, 0.72, 0.22))
        for k in range(3):
            p = a + Vector((sx * 0.02 * (k - 1), 0.18, -0.04))
            mb.add(nh.tube([tuple(p), tuple(p + Vector((sx * 0.02 * (k - 1), 0.05, -0.04)))], [0.014, 0.0], sides=6),
                   (0.06, 0.05, 0.05))
    feet = mb.to_object("feet")
    import bpy
    bpy.ops.object.select_all(action="DESELECT")
    feet.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, views=((30, 35), (0, 75), (-90, 5)))
