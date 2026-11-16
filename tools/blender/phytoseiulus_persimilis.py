"""
Procedural predatory mite (Phytoseiulus persimilis) hunting on a leaf, for map colonies.

A green leaf lies on the ground; on it runs a single predatory mite (larger relative to the leaf
than the spider mites, so it reads at map scale) next to one of its oval, pinkish-orange eggs.
The mite is shiny, bright orange-red and pear-shaped - narrow at the front, broad and rounded
behind - with no spots or eyespots, a smooth dorsal shield with a few long pale setae, a small
gnathosoma with palps and long, slender, paler orange legs: the first pair reaching far
forward and held high like feelers, the others spread wide in a running stance. Its gloss is
baked into the vertex colours, since the map shader is diffuse only.

Fixed style, like the ladybird: faces -Y, pivot on the ground (lowest point of the leaf at
z = 0).

Usage:
  blender --background --python tools/blender/phytoseiulus_persimilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PredatoryMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

ORANGE = (0.93, 0.26, 0.05)      # bright orange-red
ORANGE_DARK = (0.50, 0.08, 0.02)
GLOSS = (1.0, 0.80, 0.62)
LEG = (0.98, 0.52, 0.20)
LEG_JOINT = (0.80, 0.30, 0.08)
CLAW = (0.45, 0.16, 0.05)
SETA = (1.0, 0.88, 0.72)
EGG = (1.0, 0.66, 0.42)
EGG_SHADE = (0.82, 0.40, 0.22)

LEAF = mite.Leaf(length=1.5, half_width=0.52, curl=0.08,
                 green=(0.22, 0.47, 0.12), light=(0.36, 0.60, 0.18))
HALF_LEN = 0.48


def profile(t):
    """Pear: narrow front, broad rounded rear."""
    p = 2.0 if t < 0 else 2.4
    k = max(0.0, 1.0 - abs(t) ** p) ** (1.0 / p)
    taper = 0.68 + 0.32 * nh.smoothstep(-0.9, 0.3, t)
    return 0.34 * k * taper, 0.24 * k * (0.8 + 0.2 * taper), 0.025 * math.cos(t * 1.4)


def predator():
    body = mite.Body(HALF_LEN, profile, center_z=0.30, belly=0.55)
    legs = [
        mite.Leg(t=-0.78, length=0.95, angle=72, lift=0.55, radius=0.032, taper=0.55, tip_size=0.022),
        mite.Leg(t=-0.55, length=0.70, angle=30, lift=0.32, radius=0.034, taper=0.5, tip_size=0.024),
        mite.Leg(t=-0.30, length=0.68, angle=-25, lift=0.30, radius=0.033, taper=0.5, tip_size=0.024,
                 phi=-0.5),
        mite.Leg(t=-0.08, length=0.80, angle=-58, lift=0.28, radius=0.033, taper=0.5, tip_size=0.024,
                 phi=-0.55),
    ]
    back = Vector((0, 1, -0.15))
    setae = [(t, phi, ln, None, back) for t, phi, ln in
             ((-0.7, 1.15, 0.16), (-0.4, 0.75, 0.22), (-0.05, 0.55, 0.26), (0.35, 0.65, 0.28),
              (0.72, 0.9, 0.24), (0.9, 1.4, 0.2))]
    spec = mite.Spec(
        body=body, body_color=mite.glossy(ORANGE, ORANGE_DARK, GLOSS, power=14, amount=0.85),
        legs=legs, leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(22, 18), gnatho_size=0.14,
        gnatho_colors=(ORANGE, LEG_JOINT, LEG), gnatho_kw=dict(palp_len=0.9, down=0.3),
        setae=setae, seta_color=SETA, seta_radius=0.006,
    )
    mb, _info = mite.build(spec)
    return mb


def build():
    mb = nh.MeshBuilder()
    mite.leaf_patch(mb, LEAF, nu=12, nv=18)
    h = LEAF.height
    at = Vector((0.0, 0.0, 0))
    mite.place(predator(), mb, (at.x, at.y, h(at.x, at.y)), yaw=-20, scale=0.5)
    x, y = 0.2, 0.36
    mb.add(nh.ellipsoid((x, y, h(x, y) + 0.045), (0.046, 0.062, 0.044), subdivisions=2),
           lambda co, n: nh.lerp(EGG_SHADE, EGG, nh.smoothstep(-0.5, 0.6, n.z)))
    obj = mb.to_object("PredatoryMite", roughness=0.3)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "PredatoryMite", ground=(0.33, 0.28, 0.20), views=((35, 35), (10, 70), (-90, 12)))
