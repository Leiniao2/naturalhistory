"""
Procedural human hair-follicle mite (Demodex folliculorum) for map colonies.

An elongated, worm-like, translucent milky-white mite: a short, wider front body (podosoma)
carrying four pairs of tiny stubby, telescoped legs crowded together in the front third, each
with a pair of minute claws, a small blunt gnathosoma with short palps at the front tip, and a
long, gently tapering rear body (opisthosoma) ringed by fine annuli and ending in a rounded tip.
A faint darker streak runs down the inside, and the body bends slightly as if wriggling.

Drift style: pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/demodex_folliculorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FollicleMite.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_mite as mite  # noqa: E402

BODY = (0.93, 0.89, 0.82)        # milky, translucent
BODY_SHADE = (0.78, 0.72, 0.64)
ANNULUS = (0.62, 0.54, 0.44)
PODOSOMA = (0.90, 0.84, 0.74)
STREAK = (0.66, 0.58, 0.46)      # gut / internal organs seen through
LEG = (0.88, 0.80, 0.68)
LEG_JOINT = (0.66, 0.56, 0.44)
CLAW = (0.42, 0.32, 0.22)
MOUTH = (0.85, 0.74, 0.62)

HALF_LEN = 0.8
WIDTH = 0.13
ANNULI_START = -0.32             # t where the ringed opisthosoma begins
ANNULUS_PERIOD = 0.05


def profile(t):
    w = WIDTH
    if t < -0.84:                                  # rounded front of the podosoma
        w *= math.sqrt(max(0.0, 1.0 - ((t + 0.84) / 0.16) ** 2))
    w *= 1.0 + 0.08 * math.exp(-((t + 0.6) / 0.25) ** 2)          # slightly swollen at the legs
    w *= 1.0 - 0.42 * nh.smoothstep(-0.3, 0.96, t)                 # long taper
    if t > 0.9:                                    # rounded rear tip
        w *= math.sqrt(max(0.0, 1.0 - ((t - 0.9) / 0.1) ** 2))
    return w, w * 0.88, 0.0


def annuli(co):
    """0..1, 1 in the grooves between the rings of the opisthosoma."""
    t = co.y / HALF_LEN
    on = nh.smoothstep(ANNULI_START, ANNULI_START + 0.08, t) * (1.0 - nh.smoothstep(0.9, 0.97, t))
    return on * (0.5 + 0.5 * math.cos(math.tau * co.y / ANNULUS_PERIOD)) ** 3


def deform(co, n):
    return -0.008 * annuli(co) + 0.0015 * noise.noise(co * 30)


def body_color(co, n):
    t = co.y / HALF_LEN
    c = nh.lerp(BODY_SHADE, BODY, nh.smoothstep(-0.7, 0.5, n.z))
    c = nh.lerp(c, PODOSOMA, 0.6 * (1.0 - nh.smoothstep(-0.45, -0.3, t)))
    # internal streak down the middle of the opisthosoma
    s = nh.smoothstep(0.06, 0.0, abs(co.x)) * nh.smoothstep(-0.4, -0.1, t) * (1.0 - nh.smoothstep(0.6, 0.85, t))
    c = nh.lerp(c, STREAK, 0.45 * s)
    c = nh.lerp(c, ANNULUS, 0.75 * annuli(co))
    return c


def bend(mb):
    """Slight S-shaped wriggle along the body (applied after building)."""
    for v in mb.bm.verts:
        t = v.co.y / HALF_LEN
        v.co.x += 0.06 * math.sin(t * 2.4 + 0.6) * nh.smoothstep(-0.5, 0.2, t)
        v.co.z += 0.05 * math.sin(t * 1.6 + 0.3) - 0.02


def build():
    body = mite.Body(HALF_LEN, profile, center_z=0.0, belly=0.85, deform=deform)
    legs = [mite.Leg(t=t, length=0.085, angle=a, stub=True, dip=42, radius=0.028, taper=0.45,
                     segments=3, tip="claw", tip_size=0.022, phi=-0.45, sides=6)
            for t, a in ((-0.80, 35), (-0.69, 15), (-0.58, -5), (-0.47, -22))]
    spec = mite.Spec(
        body=body, body_color=body_color, legs=legs,
        leg_color=LEG, leg_joint=LEG_JOINT, claw_color=CLAW,
        body_res=(12, 96, 0.85), gnatho_size=0.09,
        gnatho_colors=(MOUTH, MOUTH, LEG), gnatho_kw=dict(palp_len=0.55, chel_len=0.6, down=0.1),
    )
    mb, _info = mite.build(spec)
    bend(mb)
    obj = mb.to_object("FollicleMite", roughness=0.4)
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "FollicleMite", views=((35, 25), (-90, 8), (150, 55)))
