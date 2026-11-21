"""
Procedural Haidomyrmex cerberus (mid-Cretaceous hell ant, Burmese amber, Myanmar).

A haidomyrmecine "hell ant" worker about 5 millimetres long: a long head carrying a pair
of scythe-like mandibles that jut forward and sweep UP (not sideways, as in modern ants),
closing against a paddle-shaped, bristly horn on the front of the head; big compound eyes,
elbowed antennae, a slender mesosoma, a single-node waist, an oval gaster with a sting
and long legs. Glossy dark amber-brown with a darker gaster (colours from the amber
fossils are uncertain).
Faces -Y, pivot on the ground. Built with nh_ant.py.

Usage:
  blender --background --python tools/blender/haidomyrmex_cerberus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HellAnt.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ant  # noqa: E402

BODY = (0.36, 0.17, 0.07)
GASTER = (0.16, 0.08, 0.04)
LEG = (0.42, 0.22, 0.10)
JAW = (0.24, 0.11, 0.05)
HORN = (0.30, 0.15, 0.07)

PARAMS = dict(
    head_w=0.10, head_l=0.15, head_h=0.085, head_pitch=-6.0, head_z=0.09,
    eye_r=0.03, eye_y=-0.05,
    mandible=0.05, mandible_teeth=0,
    scape=0.16, funiculus=0.26, fun_segs=10, club_segs=0,
    meso_len=0.38, meso_h=0.12, meso_w=0.85,
    waist="node", pet_h=0.06, pet_w=0.04,
    gaster_l=0.22, gaster_w=0.13, gaster_h=0.12, gaster_bands=4,
    sting=True, legs=1.1,
    head_col=BODY, meso_col=BODY, waist_col=BODY, gaster_col=GASTER,
    leg_col=LEG, antenna_col=BODY, mandible_col=JAW,
    gloss=0.55,
)


def extra(ant):
    p, mb = ant.p, ant.mb
    w, l, h = p["head_w"], p["head_l"], p["head_h"]
    jaw = nh_ant.shade(JAW, p["gloss"])
    for sx in (-1, 1):
        pts = [ant.head_point(q) for q in ((sx * w * 0.32, -l * 0.82, -h * 0.45), (sx * w * 0.28, -l * 1.35, -h * 0.40),
                                           (sx * w * 0.20, -l * 1.75, -h * 0.05), (sx * w * 0.12, -l * 1.80, h * 0.55),
                                           (sx * w * 0.06, -l * 1.62, h * 0.95))]
        mb.add(nh.tube(pts, [0.022, 0.02, 0.017, 0.012, 0.0], sides=6, scale_xy=(0.7, 1.0)), jaw)
    # the paddle-like clypeal horn the jaws snap against, with trigger bristles
    root = ant.head_point((0, -l * 0.55, h * 0.75))
    tip = ant.head_point((0, -l * 1.05, h * 1.35))
    mb.add(nh.tube([root, tip], [0.018, 0.012], sides=6), nh_ant.shade(HORN, p["gloss"]))
    mb.add(nh.ellipsoid(tuple(tip), (0.03, 0.022, 0.012), subdivisions=2), nh_ant.shade(HORN, p["gloss"]))
    for k in range(5):
        a = ant.head_point((w * (-0.25 + 0.125 * k), -l * 0.95, h * 0.95))
        mb.add(nh.tube([a, a + Vector((0, -0.03, -0.015))], [0.003, 0.0], sides=3), nh_ant.shade(HORN, p["gloss"]))


if __name__ == "__main__":
    nh_ant.run(PARAMS, "HellAnt", extra=extra)
