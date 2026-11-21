"""
Procedural snowy owl (Bubo scandiacus, Pleistocene to today; Arctic tundra,
and in the Ice Age across Europe) for map colonies.

A large, heavy owl about 55-70 cm long with a 1.3-1.5 m wingspan that hunts
lemmings and hares by day in the Arctic summer: broad, rounded wings, a big round
head with a flat facial disc, golden-yellow eyes and a small black hooked bill
nearly hidden in feathers, and thickly feathered feet. White plumage barred and
speckled with dark brown (heaviest in females). Built with nh_neo_soar.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/bubo_scandiacus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BuboScandiacus.fbx
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
    name="BuboScandiacus",
    span=2.2, chord=0.62, tip_chord=0.48, fingers=4, finger_len=0.12,
    body=(0.20, 0.36, 0.18), neck_len=0.04, head_r=0.15, beak_len=0.05, beak_r=0.03, hook=0.9,
    tail=0.24, tail_w=0.20,
    plumage=(0.94, 0.94, 0.92), under=(0.96, 0.96, 0.95), wing_top=(0.92, 0.91, 0.88),
    head_col=(0.96, 0.96, 0.95), beak_col=(0.08, 0.08, 0.08),
)


def build():
    obj = q.build(SPEC)
    vs = obj.data.vertices
    ymin = min(v.co.y for v in vs)

    def speckle(co, n, c):
        if c[0] < 0.3:  # bill, eyes
            return None
        k = noise.noise(Vector((co.x * 26, co.y * 14, co.z * 26)))
        head = co.y < ymin + 0.35
        if not head and k > (0.38 if n.z > 0 else 0.55):
            return (0.28, 0.22, 0.16)
        return None

    kit.repaint(obj, speckle)
    # big golden eyes in a flat face (the builder's eyes are small and brown)
    mb = nh.MeshBuilder()
    hc = Vector((0, -SPEC.body[1] * 0.8 - SPEC.neck_len, SPEC.body[2] * 0.30))
    for sx in (-1, 1):
        e = hc + Vector((sx * SPEC.head_r * 0.42, -SPEC.head_r * 0.82, SPEC.head_r * 0.22))
        mb.add(nh.ellipsoid(tuple(e), (0.042, 0.03, 0.042), subdivisions=2), (0.95, 0.75, 0.10))
        mb.add(nh.ellipsoid(tuple(e + Vector((0, -0.022, 0))), (0.022, 0.014, 0.022), subdivisions=2), (0.02, 0.02, 0.02))
    eyes = mb.to_object("eyes")
    import bpy
    bpy.ops.object.select_all(action="DESELECT")
    eyes.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, views=((30, 35), (0, 75), (-90, 5)))
