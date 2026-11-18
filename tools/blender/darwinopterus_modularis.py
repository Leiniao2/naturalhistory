"""
Procedural Darwinopterus modularis (Middle-Late Jurassic Tiaojishan Formation pterosaur,
Liaoning, China) for map colonies (Soar style).

A "transitional" pterosaur with a wingspan of about 0.9 m that mixes old and new: the long,
stiff tail and long fifth toe of the early long-tailed pterosaurs, but the long,
pointed skull on a long neck of the later pterodactyloids. The narrow jaws carry spaced,
sharp teeth, and adult males had a low bony crest along the top of the skull. Painted
warm brown with a paler belly, a rufous crest and darker membrane edges (colour unknown).
Built with nh_jur_flyer. Faces -Y, span along X, pivot at the body centre.

Usage:
  blender --background --python tools/blender/darwinopterus_modularis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Darwinopterus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

CREST = (0.72, 0.30, 0.14)
MEM = (0.46, 0.32, 0.22)
MEM_EDGE = (0.20, 0.13, 0.09)


def wing_color(co, n):
    k = nh.smoothstep(-0.02, 0.08, co.y + 0.12 - abs(co.x) * 0.14)
    return nh.lerp(MEM_EDGE, MEM, k)


def extras(spine):
    # low crest along the top of the long skull
    crisp = [(kit.blade([(-0.30, 0.03), (-0.36, 0.055), (-0.44, 0.05), (-0.52, 0.025), (-0.5, 0.012), (-0.3, 0.012)], 0.004), CREST)]
    for i in range(8):
        y = -0.40 - i * 0.02
        z = 0.004 - i * 0.0008
        for sx in (1, -1):
            b = Vector((sx * 0.008, y, z))
            crisp.append((kit.cone(b, b + Vector((sx * 0.002, -0.006, -0.012)), 0.0025, sides=4), kit.TOOTH))
    return [], crisp


SPEC = fl.Spec(
    name="Darwinopterus",
    rows=[(0, 0.65, 0.0, 0, 0), (0, 0.5, 0.0, 0.005, 0.005), (0, 0.3, 0.0, 0.007, 0.007), (0, 0.13, 0.0, 0.018, 0.018),
          (0, 0.05, 0.0, 0.04, 0.036), (0, -0.04, 0.004, 0.044, 0.04), (0, -0.11, 0.012, 0.028, 0.028),
          (0, -0.18, 0.024, 0.018, 0.02), (0, -0.25, 0.03, 0.017, 0.019), (0, -0.3, 0.026, 0.02, 0.024),
          (0, -0.36, 0.016, 0.014, 0.018), (0, -0.44, 0.008, 0.009, 0.011), (0, -0.52, 0.004, 0.005, 0.005),
          (0, -0.56, 0.002, 0, 0)],
    paint=kit.paint(back=(0.36, 0.25, 0.17), flank=(0.52, 0.40, 0.28), belly=(0.88, 0.80, 0.66)),
    wing=[(0.03, -0.08), (0.18, -0.1), (0.3, -0.13), (0.58, -0.07), (0.86, 0.02), (0.58, 0.07), (0.3, 0.1), (0.12, 0.12), (0.03, 0.06)],
    wing_color=wing_color,
    arm=[(0.02, -0.07, 0.0), (0.18, -0.095, 0.0), (0.3, -0.125, 0.0), (0.58, -0.07, 0.0), (0.86, 0.02, 0.0)],
    arm_r=[0.016, 0.012, 0.01, 0.005, 0.002],
    legs=[(0.03, 0.04, -0.01), (0.08, 0.09, -0.015), (0.12, 0.13, -0.015)], leg_r=[0.012, 0.008, 0.005],
    eye=(0.018, -0.3, 0.036), eye_r=0.01,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Darwinopterus", **fl.PREVIEW)
