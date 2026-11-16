"""
Procedural ear mite (Otodectes cynotis) for map colonies.

An oval, somewhat flattened, pearly-white mite with a smooth, faintly mottled cuticle and a
short, blunt, tan gnathosoma (chelicerae and palps) in front. Its legs are long for a mite
and light brown with darker joints: the two front pairs reach forward and end in short,
unjointed stalks (pedicels) carrying bell-shaped suckers it clings to the ear canal with; the
third pair trails backwards ending in a pair of long whip-like setae; the small fourth pair is
reduced (as in females). A pair of long setae trails from the rear and a few short ones sit on
the back.

Ground style (walks on its legs): faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/otodectes_cynotis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EarMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

WHITE = (0.97, 0.93, 0.85)
SHADE = (0.78, 0.72, 0.64)
MOTTLE = (0.84, 0.80, 0.72)
LEG = (0.80, 0.64, 0.44)
LEG_JOINT = (0.55, 0.40, 0.25)
MOUTH = (0.76, 0.58, 0.40)
CHELICERA = (0.58, 0.42, 0.28)
CLAW = (0.38, 0.26, 0.15)
SETA = (0.90, 0.86, 0.78)

HALF_LEN, WIDTH, HEIGHT = 0.45, 0.31, 0.17
BODY_Z = 0.20


def body_color(co, n):
    c = nh.lerp(SHADE, WHITE, nh.smoothstep(-0.7, 0.4, n.z))
    m = noise.noise(co * 8)
    c = nh.lerp(c, MOTTLE, max(0.0, m) * 0.8 * nh.smoothstep(-0.1, 0.4, n.z))
    # a soft pearly sheen on top
    c = nh.lerp(c, (1.0, 1.0, 0.98), 0.4 * max(0.0, n.dot(Vector((-0.4, -0.5, 0.75)).normalized())) ** 12)
    # slightly darker sclerotised rim where the legs join
    t = co.y / HALF_LEN
    c = nh.lerp(c, LEG, 0.25 * nh.smoothstep(0.1, -0.3, n.z) * nh.smoothstep(0.5, -0.2, t))
    return c


def build():
    body = mite.Body(HALF_LEN, mite.oval(WIDTH, HEIGHT, front=2.0, rear=2.3,
                                         dz=lambda t: 0.02 * math.cos(t * 1.5)),
                     center_z=BODY_Z, belly=0.55,
                     deform=lambda co, n: 0.002 * noise.noise(co * 20))
    legs = [
        mite.Leg(t=-0.66, length=0.50, angle=62, lift=0.24, radius=0.050, taper=0.45, tip="sucker",
                 tip_size=0.065, stalk=0.13),
        mite.Leg(t=-0.40, length=0.50, angle=28, lift=0.25, radius=0.050, taper=0.45, tip="sucker",
                 tip_size=0.065, stalk=0.13),
        mite.Leg(t=0.18, length=0.46, angle=-40, lift=0.20, radius=0.046, taper=0.45, tip="setae",
                 phi=-0.5),
        mite.Leg(t=0.45, length=0.24, angle=-62, lift=0.18, radius=0.040, taper=0.45, tip="claw",
                 tip_size=0.02, phi=-0.55, segments=4),
    ]
    down = Vector((0, 0, -0.4))
    setae = [
        (0.95, 0.45, 0.55, (0.25, 1.0, 0.15), down),     # long posterior setae
        (0.80, 0.05, 0.22, (0.8, 0.6, 0.1), down),
        (-0.15, 0.0, 0.16, (1.0, -0.2, 0.2), None),       # lateral
        (-0.55, 1.1, 0.10, None, Vector((0, 1, 0))),      # short dorsal setae
        (0.30, 1.2, 0.09, None, Vector((0, 1, 0))),
    ]
    spec = mite.Spec(
        body=body, body_color=body_color, legs=legs,
        leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(32, 26), gnatho_size=0.15,
        gnatho_colors=(MOUTH, CHELICERA, MOUTH), gnatho_kw=dict(palp_len=0.7, down=0.25),
        setae=setae, seta_color=SETA, seta_radius=0.0055, tip_setae=0.42,
    )
    mb, info = mite.build(spec)
    obj = mb.to_object("EarMite", roughness=0.45)
    nh.ground_to_zero(obj)
    zmax = max(v.co.z for v in obj.data.vertices)
    print(f"EarMite: hip z {info['hip_z']:.3f}, height {zmax:.3f}, mapHip ~ {info['hip_z'] / zmax:.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "EarMite", ground=(0.45, 0.32, 0.26), views=((35, 25), (-90, 8), (150, 55)))
