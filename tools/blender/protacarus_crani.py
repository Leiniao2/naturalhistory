"""
Procedural Protacarus crani (Early Devonian mite, Rhynie chert, Scotland) for map colonies.

One of the oldest known mites, under half a millimetre long, a soil-dwelling relative of
today's primitive endeostigmatid mites that lived among the first land plants. A soft,
egg-shaped, slightly flattened body with a shallow furrow behind the front shield, a small
gnathosoma with chelicerae and palps in front, four pairs of fairly long, slender legs with
tiny claws, and a scatter of fine bristles. Modelled amber to rust-brown with darker leg
joints. Built with nh_mite.py.

Ground style: faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/protacarus_crani.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protacarus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

BODY = (0.66, 0.34, 0.16)
BODY_DARK = (0.36, 0.16, 0.08)
SHIELD = (0.50, 0.24, 0.10)
LEG = (0.78, 0.52, 0.30)
LEG_JOINT = (0.44, 0.24, 0.12)
MOUTH = (0.70, 0.42, 0.24)
CHELICERA = (0.40, 0.20, 0.10)
CLAW = (0.20, 0.10, 0.05)
SETA = (0.92, 0.82, 0.66)

HALF_LEN, WIDTH, HEIGHT = 0.5, 0.33, 0.21
BODY_Z = 0.24
FURROW_T = -0.34
GLOSSY = mite.glossy(BODY, BODY_DARK, (0.95, 0.80, 0.62), amount=0.5)


def deform(co, n):
    t = co.y / HALF_LEN
    d = -0.02 * math.exp(-((t - FURROW_T) / 0.07) ** 2) * nh.smoothstep(0.05, 0.2, co.z - BODY_Z + 0.2)
    return d + 0.003 * noise.noise(co * 18)


def body_color(co, n):
    t = co.y / HALF_LEN
    c = GLOSSY(co, n)
    top = nh.smoothstep(-0.2, 0.4, n.z)
    if t < FURROW_T:
        c = nh.lerp(c, SHIELD, 0.6 * top)
    c = nh.lerp(c, BODY_DARK, 0.7 * math.exp(-((t - FURROW_T) / 0.06) ** 2) * top)
    m = noise.noise(co * 9 + Vector((2.0, 1.0, 0.5)))
    c = nh.lerp(c, BODY_DARK, 0.35 * nh.smoothstep(0.2, 0.5, m) * top)
    return c


def build():
    body = mite.Body(HALF_LEN, mite.oval(WIDTH, HEIGHT, front=1.8, rear=2.2,
                                         dz=lambda t: 0.02 * math.cos(t * 1.4)),
                     center_z=BODY_Z, belly=0.6, deform=deform)
    legs = [
        mite.Leg(t=-0.72, length=0.48, angle=60, lift=0.22, radius=0.042, taper=0.4, tip_size=0.028),
        mite.Leg(t=-0.48, length=0.42, angle=26, lift=0.20, radius=0.042, taper=0.4, tip_size=0.028),
        mite.Leg(t=0.0, length=0.42, angle=-26, lift=0.19, radius=0.040, taper=0.4, tip_size=0.028, phi=-0.55),
        mite.Leg(t=0.22, length=0.48, angle=-56, lift=0.18, radius=0.040, taper=0.4, tip_size=0.028, phi=-0.6),
    ]
    back = Vector((0, 1, -0.05))
    setae = [
        (0.92, 0.30, 0.40, (0.25, 1.0, 0.1), Vector((0, 0, -0.4))),
        (0.85, 0.70, 0.32, (0.4, 1.0, 0.25), None),
        (0.20, 0.20, 0.22, (1.0, 0.3, 0.2), None),
        (-0.55, 1.05, 0.18, (0.4, 0.4, 0.8), back),
        (0.0, 1.15, 0.14, None, back),
        (0.45, 1.10, 0.14, None, back),
    ]
    spec = mite.Spec(
        body=body, body_color=body_color, legs=legs,
        leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(36, 24), gnatho_size=0.16,
        gnatho_colors=(MOUTH, CHELICERA, MOUTH), gnatho_kw=dict(palp_len=1.0, down=0.3),
        setae=setae, seta_color=SETA, seta_radius=0.006,
    )
    mb, info = mite.build(spec)
    obj = mb.to_object("Protacarus", roughness=0.45)
    nh.ground_to_zero(obj)
    zmax = max(v.co.z for v in obj.data.vertices)
    print(f"Protacarus: hip z {info['hip_z']:.3f}, height {zmax:.3f}, mapHip ~ {info['hip_z'] / zmax:.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "Protacarus", ground=(0.30, 0.27, 0.19), views=((35, 25), (-90, 8), (150, 55)))
