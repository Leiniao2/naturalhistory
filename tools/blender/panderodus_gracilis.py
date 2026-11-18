"""
Procedural Panderodus gracilis (Branson & Mehl, 1933) (Middle Ordovician-Silurian conodont, one
of the longest-lived and most widespread conodonts) for map colonies (Swim style).

A small, slender conodont a few centimetres long. Its soft body is known from Panderodus fossils
of the Silurian Waukesha beds: a dorsoventrally flattened, eel-like trunk with transverse muscle
blocks, a short head with big eyes and a fin round the tail. Its feeding apparatus was a pair of
rows of long, slender, fang-like cones, each with a deep groove along its side that may have
delivered venom - perhaps the oldest venomous vertebrate. Here: a wide, flattened, dark-backed
body (colour conjectural) and a crescent of pale fangs at the mouth. Built
with nh_ord_agnathan.build_conodont plus the fangs.

Usage:
  blender --background --python tools/blender/panderodus_gracilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PanderodusGracilis.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.ConodontSpec(
    name="PanderodusGracilis", length=1.7, depth=0.045, width=0.075, eye_r=0.05,
    body=(0.74, 0.62, 0.44), body_dark=(0.34, 0.20, 0.12), belly=(0.90, 0.84, 0.70),
    fin=(0.80, 0.70, 0.54), ray=(0.50, 0.36, 0.24), eye_rim=(0.12, 0.08, 0.06),
)
FANG = (0.97, 0.92, 0.80)


def build():
    """build_conodont() with a crescent of fang-like elements at the mouth, added to its MeshBuilder just before it becomes an object."""
    y0 = -SPEC.length / 2
    orig = nh.MeshBuilder.to_object

    def to_object(self, name, roughness=0.6):
        # fangs: a crescent of long slender cones protruding from the mouth
        for k in range(6):
            a = math.radians(-60 + 24 * k)
            base = Vector((math.sin(a) * 0.022, y0 + 0.012, -0.008 + math.cos(a) * 0.004))
            tip = base + Vector((math.sin(a) * 0.02, -0.10, -0.012 + 0.03 * (k % 2)))
            self.add(nh.tube([base, base.lerp(tip, 0.5) + Vector((0, 0, 0.006)), tip],
                             [0.010, 0.006, 0.0], sides=5), FANG)
        return orig(self, name, roughness)

    nh.MeshBuilder.to_object = to_object
    try:
        return ag.build_conodont(SPEC)
    finally:
        nh.MeshBuilder.to_object = orig


if __name__ == "__main__":
    nh.run(build, SPEC.name, **ag.PREVIEW)
