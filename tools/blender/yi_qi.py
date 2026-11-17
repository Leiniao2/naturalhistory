"""
Procedural Yi qi (Middle-Late Jurassic scansoriopterygid theropod, Hebei, China) for map colonies.

A pigeon-sized feathered dinosaur that glided on bat-like membrane wings: the skin
stretched between its very long third finger and a long rod-like wrist bone (the
styliform element) unique among dinosaurs. Short, blunt head with a few forward teeth,
a body covered in dark filament-like feathers, a short tail and trailing legs. Dark
brown fuzz with a paler face, thin tan-brown membranes with the finger bones showing.
Built with nh_jur_flyer. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/yi_qi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/YiQi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

FUZZ = (0.20, 0.15, 0.12)
MEM = (0.55, 0.42, 0.30)
BONE = (0.24, 0.18, 0.14)

WRIST = (0.22, -0.1, 0.0)


def fuzz(co, n, c):
    m = noise.noise((co.x * 60, co.y * 120, co.z * 60))
    if co.y < -0.2:
        c = nh.lerp(c, (0.50, 0.40, 0.32), 0.5)
    return tuple(v * (1 + 0.2 * m) for v in c)


def extras(spine):
    fused, crisp = [], []
    # fingers and the styliform rod splaying from the wrist
    for tip in ((0.5, -0.12, 0.0), (0.42, 0.02, 0.0), (0.3, 0.12, 0.0)):
        for sx in (1, -1):
            a = Vector((sx * WRIST[0], WRIST[1], WRIST[2] + WRIST[0] * 0.08))
            b = Vector((sx * tip[0], tip[1], tip[2] + tip[0] * 0.08))
            crisp.append((nh.tube([a, b], [0.006, 0.0025], sides=5), BONE))
    # small forward teeth
    for sx in (1, -1):
        b = Vector((sx * 0.01, -0.33, 0.0))
        crisp.append((kit.cone(b, b + Vector((0, -0.006, -0.01)), 0.003, sides=4), kit.TOOTH))
    return fused, crisp


SPEC = fl.Spec(
    name="YiQi",
    rows=[(0, 0.26, 0.0, 0, 0), (0, 0.2, 0.0, 0.012, 0.012), (0, 0.1, 0.0, 0.035, 0.035),
          (0, 0.0, 0.0, 0.055, 0.05), (0, -0.1, 0.008, 0.05, 0.048), (0, -0.18, 0.02, 0.03, 0.03),
          (0, -0.23, 0.03, 0.036, 0.036), (0, -0.28, 0.028, 0.04, 0.038), (0, -0.33, 0.015, 0.022, 0.02), (0, -0.355, 0.01, 0, 0)],
    paint=kit.paint(back=FUZZ, flank=(0.30, 0.23, 0.18), belly=(0.55, 0.46, 0.38), extra=fuzz, mottle=0.0),
    wing=[(0.03, -0.09), (0.12, -0.1), (0.22, -0.1), (0.5, -0.12), (0.44, -0.03), (0.42, 0.02), (0.34, 0.07), (0.3, 0.12), (0.15, 0.08), (0.04, 0.05)],
    wing_color=lambda co, n: nh.lerp(MEM, (0.40, 0.30, 0.22), nh.smoothstep(0.2, 0.5, abs(co.x))),
    arm=[(0.02, -0.08, 0.0), (0.12, -0.1, 0.0), (0.22, -0.1, 0.0)], arm_r=[0.02, 0.012, 0.008],
    legs=[(0.03, 0.04, -0.015), (0.07, 0.11, -0.025), (0.09, 0.17, -0.025)], leg_r=[0.018, 0.01, 0.006],
    eye=(0.024, -0.285, 0.045), eye_r=0.012,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "YiQi", **fl.PREVIEW)
