"""
Procedural Dimorphodon macronyx (Early Jurassic, Lyme Regis, Dorset) for map colonies.

An early pterosaur with an outsized, deep, puffin-like skull (lightened by big openings)
on a short neck, two kinds of teeth (long fangs in front, small blades behind), short,
broad wings and a long, stiff tail. Painted boldly: dark charcoal body and wings, a
yellow-and-red face and beak, pale throat. Built with nh_jur_flyer. Faces -Y, pivot at
the body centre.

Usage:
  blender --background --python tools/blender/dimorphodon_macronyx.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dimorphodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

DARK = (0.14, 0.13, 0.13)
YEL = (0.92, 0.72, 0.18)
RED = (0.78, 0.18, 0.10)
MEM = (0.26, 0.20, 0.18)


def face(co, n, c):
    if co.y < -0.2:
        k = nh.smoothstep(-0.2, -0.26, co.y)
        f = nh.lerp(YEL, RED, nh.smoothstep(-0.33, -0.4, co.y))
        c = nh.lerp(c, f, k)
    return c


def extras(spine):
    crisp = []
    for i in range(6):
        y = -0.33 - i * 0.017
        ln = 0.022 if i > 3 else 0.012
        for sx in (1, -1):
            b = Vector((sx * 0.013, y, 0.0))
            crisp.append((kit.cone(b, b + Vector((0, -0.004, -ln)), 0.0035, sides=4), kit.TOOTH))
    return [], crisp


SPEC = fl.Spec(
    name="Dimorphodon",
    rows=[(0, 0.6, 0.0, 0, 0), (0, 0.45, 0.0, 0.006, 0.006), (0, 0.25, 0.0, 0.009, 0.009), (0, 0.12, 0.0, 0.022, 0.022),
          (0, 0.04, 0.0, 0.045, 0.042), (0, -0.05, 0.005, 0.05, 0.046), (0, -0.12, 0.015, 0.032, 0.032),
          (0, -0.17, 0.03, 0.025, 0.028), (0, -0.21, 0.04, 0.03, 0.05), (0, -0.27, 0.035, 0.03, 0.058),
          (0, -0.34, 0.025, 0.024, 0.05), (0, -0.41, 0.012, 0.016, 0.03), (0, -0.45, 0.005, 0.008, 0.014), (0, -0.46, 0.003, 0, 0)],
    paint=kit.paint(back=DARK, flank=(0.22, 0.20, 0.19), belly=(0.70, 0.66, 0.60), extra=face),
    wing=[(0.03, -0.08), (0.17, -0.1), (0.27, -0.12), (0.5, -0.06), (0.68, 0.02), (0.48, 0.07), (0.26, 0.1), (0.11, 0.11), (0.03, 0.05)],
    wing_color=lambda co, n: nh.lerp((0.10, 0.09, 0.09), MEM, nh.smoothstep(-0.1, 0.0, co.y - abs(co.x) * 0.12)),
    arm=[(0.02, -0.07, 0.0), (0.17, -0.095, 0.0), (0.27, -0.115, 0.0), (0.5, -0.06, 0.0), (0.68, 0.02, 0.0)],
    arm_r=[0.02, 0.014, 0.012, 0.007, 0.002],
    legs=[(0.03, 0.04, -0.01), (0.07, 0.085, -0.02), (0.11, 0.115, -0.02)], leg_r=[0.014, 0.009, 0.006],
    eye=(0.022, -0.26, 0.06), eye_r=0.012, eye_color=(0.9, 0.85, 0.3),
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Dimorphodon", **fl.PREVIEW)
