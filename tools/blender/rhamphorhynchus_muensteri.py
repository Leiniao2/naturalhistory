"""
Procedural Rhamphorhynchus muensteri (Late Jurassic Solnhofen pterosaur) for map colonies.

A long-tailed "rhamphorhynchoid" pterosaur flying with its long, narrow wings spread: a
slender skull with a toothless beak tip and long, forward-raking interlocking teeth for
catching fish, a short neck, and a long stiff tail ending in a vertical, diamond-shaped
vane (red here). Grey-brown pycnofibre coat, pale throat, rust-brown membranes with a dark
leading edge. Built with nh_jur_flyer. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/rhamphorhynchus_muensteri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhamphorhynchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

VANE = (0.75, 0.20, 0.12)
MEM = (0.52, 0.30, 0.18)
MEM_EDGE = (0.22, 0.14, 0.10)


def wing_color(co, n):
    k = nh.smoothstep(-0.02, 0.08, co.y + 0.13 - abs(co.x) * 0.14)
    return nh.lerp(MEM_EDGE, MEM, k)


def extras(spine):
    crisp = [(kit.blade([(0.6, 0.0), (0.68, 0.05), (0.77, 0.0), (0.68, -0.03)], 0.004), VANE)]
    for i in range(7):
        y = -0.335 - i * 0.014
        for sx in (1, -1):
            b = Vector((sx * 0.011, y, 0.018 - i * 0.0012))
            crisp.append((kit.cone(b, b + Vector((sx * 0.004, -0.014, -0.016)), 0.003, sides=4), kit.TOOTH))
            b2 = Vector((sx * 0.009, y + 0.005, 0.004 - i * 0.0012))
            crisp.append((kit.cone(b2, b2 + Vector((sx * 0.004, -0.012, 0.014)), 0.0026, sides=4), kit.TOOTH))
    return [], crisp


SPEC = fl.Spec(
    name="Rhamphorhynchus",
    rows=[(0, 0.75, 0.0, 0, 0), (0, 0.6, 0.0, 0.005, 0.005), (0, 0.35, 0.0, 0.007, 0.007), (0, 0.15, 0.0, 0.02, 0.02),
          (0, 0.05, 0.0, 0.045, 0.04), (0, -0.05, 0.005, 0.05, 0.045), (0, -0.13, 0.012, 0.032, 0.032),
          (0, -0.19, 0.022, 0.02, 0.022), (0, -0.25, 0.03, 0.022, 0.024), (0, -0.29, 0.03, 0.026, 0.026),
          (0, -0.34, 0.016, 0.016, 0.016), (0, -0.41, 0.008, 0.01, 0.009), (0, -0.46, 0.004, 0.005, 0.004), (0, -0.48, 0.003, 0, 0)],
    paint=kit.paint(back=(0.36, 0.31, 0.26), flank=(0.50, 0.44, 0.36), belly=(0.86, 0.80, 0.70)),
    wing=[(0.03, -0.09), (0.2, -0.11), (0.33, -0.14), (0.62, -0.08), (0.92, 0.01), (0.62, 0.06), (0.32, 0.1), (0.12, 0.12), (0.03, 0.05)],
    wing_color=wing_color,
    arm=[(0.02, -0.08, 0.0), (0.2, -0.105, 0.0), (0.33, -0.135, 0.0), (0.62, -0.08, 0.0), (0.92, 0.01, 0.0)],
    arm_r=[0.018, 0.013, 0.011, 0.006, 0.002],
    legs=[(0.03, 0.04, -0.01), (0.08, 0.09, -0.015), (0.12, 0.125, -0.015)], leg_r=[0.013, 0.008, 0.005],
    eye=(0.02, -0.285, 0.04), eye_r=0.011,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Rhamphorhynchus", **fl.PREVIEW)
