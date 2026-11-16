"""
Procedural American house dust mite (Dermatophagoides farinae) for map colonies.

A plump, rounded-oval, creamy-white body with a soft translucent look: fine fingerprint-like
striae run over the cuticle (curving lengthwise down the back), a faint furrow divides the front
(propodosoma, with a slightly darker dorsal shield) from the rear, and darker food pellets show
through the middle of the back. In front sits a small tan gnathosoma with chelicerae and palps;
four pairs of short, stout, light-brown legs (two pairs reaching forward, two back) end in tiny
claws. A few long setae trail from the rear end and stick out from the flanks.

Ground style (walks on its eight legs): faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/dermatophagoides_farinae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HouseDustMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

CREAM = (0.94, 0.90, 0.80)
CREAM_SHADE = (0.80, 0.74, 0.62)
STRIA = (0.74, 0.68, 0.56)
SHIELD = (0.86, 0.78, 0.64)
GUT = (0.55, 0.45, 0.30)
LEG = (0.84, 0.70, 0.52)
LEG_JOINT = (0.62, 0.47, 0.32)
MOUTH = (0.80, 0.62, 0.46)
CHELICERA = (0.62, 0.44, 0.30)
CLAW = (0.40, 0.28, 0.16)
SETA = (0.92, 0.88, 0.78)

HALF_LEN, WIDTH, HEIGHT = 0.5, 0.37, 0.24
BODY_Z = 0.21
FURROW_T = -0.38


def stria(co):
    """0..1 fine ridged pattern: lines curving lengthwise down the back."""
    return 0.5 + 0.5 * math.sin(44.0 * (abs(co.x) + 0.35 * (co.y - 0.1) ** 2) + 0.8 * co.z)


def deform(co, n):
    t = co.y / HALF_LEN
    d = -0.022 * math.exp(-((t - FURROW_T) / 0.07) ** 2) * nh.smoothstep(0.05, 0.2, co.z - BODY_Z + 0.2)
    if t > FURROW_T + 0.1:
        d += 0.004 * (stria(co) - 0.5)
    return d + 0.002 * noise.noise(co * 25)


def body_color(co, n):
    t = co.y / HALF_LEN
    c = nh.lerp(CREAM_SHADE, CREAM, nh.smoothstep(-0.7, 0.3, n.z))
    top = nh.smoothstep(-0.2, 0.4, n.z)
    if t < FURROW_T:
        c = nh.lerp(c, SHIELD, 0.7 * top * nh.smoothstep(0.30, 0.18, abs(co.x)))
    else:
        c = nh.lerp(c, STRIA, 0.75 * stria(co) ** 2 * nh.smoothstep(-0.3, 0.2, n.z))
    c = nh.lerp(c, STRIA, 0.8 * math.exp(-((t - FURROW_T) / 0.06) ** 2) * top)
    # food pellets in the gut showing through the back
    g = nh.smoothstep(0.24, 0.08, math.hypot(co.x * 1.1, (co.y - 0.1) * 0.8))
    g *= 0.75 + 0.5 * noise.noise(co * 7)
    c = nh.lerp(c, GUT, min(1.0, max(0.0, 0.7 * g)) * top)
    return c


def build():
    body = mite.Body(HALF_LEN, mite.oval(WIDTH, HEIGHT, front=2.2, rear=2.4,
                                         dz=lambda t: 0.03 * math.cos(t * 1.4)),
                     center_z=BODY_Z, belly=0.6, deform=deform)
    legs = [
        mite.Leg(t=-0.70, length=0.30, angle=58, lift=0.18, radius=0.056, taper=0.45, tip_size=0.03),
        mite.Leg(t=-0.46, length=0.31, angle=24, lift=0.18, radius=0.056, taper=0.45, tip_size=0.03),
        mite.Leg(t=0.02, length=0.32, angle=-28, lift=0.16, radius=0.054, taper=0.45, tip_size=0.03,
                 phi=-0.55),
        mite.Leg(t=0.22, length=0.34, angle=-56, lift=0.15, radius=0.052, taper=0.45, tip_size=0.03,
                 phi=-0.6),
    ]
    back = Vector((0, 1, -0.05))
    setae = [
        # two pairs of long posterior setae trailing behind
        (0.93, 0.25, 0.72, (0.22, 1.0, 0.05), Vector((0, 0, -0.5))),
        (0.86, 0.75, 0.58, (0.35, 1.0, 0.25), Vector((0, 0, -0.5))),
        # lateral setae sticking out from the flanks
        (0.25, 0.05, 0.30, (1.0, 0.35, 0.10), Vector((0, 0.3, -0.3))),
        (-0.15, 0.10, 0.20, (1.0, -0.1, 0.25), None),
        # short scapular and dorsal setae
        (-0.52, 1.05, 0.16, (0.4, 0.5, 0.8), back),
        (0.05, 1.20, 0.10, None, back),
        (0.45, 1.10, 0.12, None, back),
    ]
    spec = mite.Spec(
        body=body, body_color=body_color, legs=legs,
        leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(40, 28), gnatho_size=0.17,
        gnatho_colors=(MOUTH, CHELICERA, MOUTH), gnatho_kw=dict(palp_len=0.85, down=0.35),
        setae=setae, seta_color=SETA, seta_radius=0.006,
    )
    mb, info = mite.build(spec)
    obj = mb.to_object("HouseDustMite", roughness=0.45)
    nh.ground_to_zero(obj)
    zmax = max(v.co.z for v in obj.data.vertices)
    print(f"HouseDustMite: hip z {info['hip_z']:.3f}, height {zmax:.3f}, mapHip ~ {info['hip_z'] / zmax:.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "HouseDustMite", ground=(0.33, 0.30, 0.28), views=((35, 25), (-90, 8), (150, 55)))
