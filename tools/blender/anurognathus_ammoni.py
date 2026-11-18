"""
Procedural Anurognathus ammoni (Late Jurassic Solnhofen pterosaur, Bavaria) for map
colonies (Soar style).

A tiny, frog-faced pterosaur with a wingspan of about 35-50 cm: a very short, broad,
rounded head with a wide gape full of small peg-like teeth and large forward-facing eyes,
a compact body covered in fuzzy pycnofibres, broad wings and only a stub of a tail. It
probably hawked insects in the air at dusk, like a nightjar or a bat. Painted dusky grey-
brown with a paler throat and belly and dark wing membranes (colour unknown). Built with
nh_jur_flyer. Faces -Y, span along X, pivot at the body centre.

Usage:
  blender --background --python tools/blender/anurognathus_ammoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anurognathus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

MEM = (0.30, 0.25, 0.22)
MEM_EDGE = (0.14, 0.11, 0.10)


def wing_color(co, n):
    k = nh.smoothstep(-0.02, 0.1, co.y + 0.16 - abs(co.x) * 0.2)
    return nh.lerp(MEM_EDGE, MEM, k)


def fuzz(co, n, c):
    m = noise.noise(co * 120.0)
    return tuple(v * (1.0 + 0.18 * m) for v in c)


def extras(spine):
    crisp = []
    # small peg teeth along the wide gape
    for i in range(7):
        a = -0.6 + 1.2 * i / 6
        x = 0.03 * a
        y = -0.172 + 0.012 * a * a
        crisp.append((kit.cone(Vector((x, y, -0.002)), Vector((x, y - 0.002, -0.008)), 0.0018, sides=4), kit.TOOTH))
    return [], crisp


SPEC = fl.Spec(
    name="Anurognathus",
    rows=[(0, 0.13, 0.0, 0, 0), (0, 0.11, 0.0, 0.01, 0.01), (0, 0.07, 0.0, 0.03, 0.028), (0, 0.0, 0.0, 0.048, 0.042),
          (0, -0.07, 0.004, 0.044, 0.04), (0, -0.11, 0.01, 0.034, 0.032), (0, -0.135, 0.014, 0.04, 0.036),
          (0, -0.16, 0.012, 0.04, 0.03), (0, -0.175, 0.006, 0.03, 0.02), (0, -0.182, 0.004, 0, 0)],
    paint=kit.paint(back=(0.28, 0.24, 0.20), flank=(0.42, 0.36, 0.30), belly=(0.80, 0.74, 0.64), extra=fuzz),
    wing=[(0.03, -0.07), (0.14, -0.09), (0.24, -0.11), (0.42, -0.07), (0.6, 0.0), (0.46, 0.07), (0.28, 0.12), (0.12, 0.13), (0.03, 0.08)],
    wing_color=wing_color,
    arm=[(0.02, -0.06, 0.0), (0.14, -0.085, 0.0), (0.24, -0.105, 0.0), (0.42, -0.07, 0.0), (0.6, 0.0, 0.0)],
    arm_r=[0.014, 0.011, 0.009, 0.005, 0.002],
    legs=[(0.03, 0.03, -0.01), (0.07, 0.08, -0.014), (0.1, 0.12, -0.014)], leg_r=[0.011, 0.008, 0.005],
    eye=(0.026, -0.15, 0.024), eye_r=0.013, eye_color=(0.75, 0.45, 0.10),
    voxel=0.004, max_tris=6000,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Anurognathus", **fl.PREVIEW)
