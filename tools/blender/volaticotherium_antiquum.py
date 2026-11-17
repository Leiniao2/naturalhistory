"""
Procedural Volaticotherium antiquum (Middle-Late Jurassic Daohugou beds, Inner Mongolia)
for map colonies.

A squirrel-sized eutriconodont mammal, the earliest known gliding mammal: a furry skin
membrane (patagium) stretched between its long front and hind limbs, preserved with hair
impressions, and a long, flattened tail used as a stabiliser. Pointed snout, large eyes,
small ears. Grey-brown fur, paler belly, a darker membrane edge. Built with nh_jur_flyer,
gliding with the membrane spread. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/volaticotherium_antiquum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Volaticotherium.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import noise  # noqa: E402

FUR = (0.40, 0.34, 0.27)
EDGE = (0.20, 0.16, 0.12)


def fur(co, n, c):
    m = noise.noise((co.x * 50, co.y * 120, co.z * 50))
    return tuple(v * (1 + 0.15 * m) for v in c)


def mem(co, n):
    k = nh.smoothstep(0.24, 0.32, abs(co.x))
    c = nh.lerp(FUR, EDGE, k)
    m = noise.noise((co.x * 50, co.y * 120, 0.0))
    return tuple(v * (1 + 0.12 * m) for v in c)


def extras(spine):
    fused = []
    for sx in (1, -1):
        fused.append((nh.ellipsoid((sx * 0.025, -0.2, 0.04), (0.012, 0.008, 0.016), subdivisions=1), (0.5,) * 3))  # ears
    return fused, []


SPEC = fl.Spec(
    name="Volaticotherium",
    rows=[(0, 0.55, 0.0, 0, 0), (0, 0.45, 0.0, 0.012, 0.006), (0, 0.25, 0.0, 0.02, 0.01), (0, 0.1, 0.0, 0.035, 0.025),
          (0, 0.0, 0.0, 0.06, 0.04), (0, -0.1, 0.004, 0.058, 0.04), (0, -0.17, 0.012, 0.04, 0.032),
          (0, -0.22, 0.016, 0.036, 0.03), (0, -0.27, 0.012, 0.022, 0.018), (0, -0.31, 0.006, 0.008, 0.007), (0, -0.32, 0.005, 0, 0)],
    paint=kit.paint(back=FUR, flank=(0.50, 0.43, 0.34), belly=(0.80, 0.74, 0.64), extra=fur, mottle=0.0),
    wing=[(0.04, -0.12), (0.2, -0.16), (0.3, -0.15), (0.3, -0.02), (0.28, 0.1), (0.24, 0.14), (0.1, 0.12), (0.04, 0.08)],
    wing_color=mem, wing_thick=0.008, dihedral=0.04,
    arm=[(0.03, -0.1, 0.0), (0.18, -0.15, 0.0), (0.3, -0.16, 0.0)], arm_r=[0.016, 0.01, 0.007],
    legs=[(0.03, 0.06, -0.005), (0.16, 0.11, 0.0), (0.26, 0.15, 0.0)], leg_r=[0.018, 0.011, 0.007],
    eye=(0.022, -0.23, 0.028), eye_r=0.01, eye_color=(0.08, 0.06, 0.05),
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Volaticotherium", **fl.PREVIEW)
