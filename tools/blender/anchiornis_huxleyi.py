"""
Procedural Anchiornis huxleyi (Late Jurassic Tiaojishan Formation paravian, Liaoning) for map colonies.

A crow-sized feathered dinosaur with four "wings": long pennaceous feathers on the arms
and also on the legs, plus a feathered tail. Its colours are known from fossil
melanosomes: grey body, white wing feathers with black tips giving a spangled edge, and a
rufous crest on the crown, with speckles on the face. Built with nh_jur_flyer, gliding
with all four wings spread. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/anchiornis_huxleyi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anchiornis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_flyer as fl  # noqa: E402
from mathutils import Vector  # noqa: E402

GREY = (0.32, 0.32, 0.33)
WHITE = (0.92, 0.92, 0.90)
BLACK = (0.06, 0.06, 0.07)
RUFOUS = (0.70, 0.30, 0.12)


TRAIL = [(0.0, 0.03), (0.12, 0.08), (0.3, 0.1), (0.45, 0.07), (0.56, 0.0)]


def trail_y(x):
    for (x0, y0), (x1, y1) in zip(TRAIL, TRAIL[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return TRAIL[-1][1]


def wing_color(co, n):
    """White feathers with black tips (a spangled trailing edge) on all four wings."""
    x = abs(co.x)
    if co.y > 0.09 and x < 0.3:  # hind (leg) wing
        return BLACK if co.y > 0.22 else WHITE
    if x > 0.5 or co.y > trail_y(x) - 0.03:
        return BLACK
    if math.sin(x * 120.0) > 0.9:
        return (0.6, 0.6, 0.6)
    return WHITE


def tail_color(co, n):
    return BLACK if co.y > 0.4 or math.sin(co.x * 110) > 0.8 else WHITE


def extras(spine):
    crisp = []
    # feathered tail fan
    crisp.append((nh.flat_panel([(0.0, 0.08, 0.0), (0.06, 0.15, 0.0), (0.07, 0.42, 0.0), (0.0, 0.46, 0.0),
                                 (-0.07, 0.42, 0.0), (-0.06, 0.15, 0.0)], thickness=0.004), tail_color))
    # rufous crest
    crisp.append((kit.blade([(-0.21, 0.04), (-0.19, 0.09), (-0.24, 0.075), (-0.27, 0.05)], 0.01), RUFOUS))
    return [], crisp


def body_extra(co, n, c):
    if -0.28 < co.y < -0.19 and n.z > 0.4:
        c = nh.lerp(c, RUFOUS, 0.7)
    return c


SPEC = fl.Spec(
    name="Anchiornis",
    rows=[(0, 0.4, 0.0, 0, 0), (0, 0.3, 0.0, 0.01, 0.01), (0, 0.12, 0.0, 0.025, 0.025),
          (0, 0.02, 0.0, 0.05, 0.05), (0, -0.08, 0.008, 0.048, 0.048), (0, -0.15, 0.025, 0.026, 0.028),
          (0, -0.2, 0.04, 0.03, 0.032), (0, -0.25, 0.042, 0.03, 0.03), (0, -0.3, 0.032, 0.017, 0.016), (0, -0.33, 0.026, 0, 0)],
    paint=kit.paint(back=GREY, flank=(0.42, 0.42, 0.42), belly=(0.70, 0.70, 0.68), extra=body_extra),
    wing=[(0.03, -0.08), (0.18, -0.1), (0.3, -0.1), (0.52, -0.06), (0.56, 0.0), (0.45, 0.07), (0.3, 0.1), (0.12, 0.08), (0.03, 0.03)],
    wing_color=wing_color,
    hind_wing=[(0.03, 0.05), (0.12, 0.1), (0.2, 0.16), (0.24, 0.26), (0.17, 0.3), (0.08, 0.22), (0.02, 0.12)],
    arm=[(0.02, -0.07, 0.0), (0.18, -0.095, 0.0), (0.3, -0.1, 0.0)], arm_r=[0.016, 0.01, 0.007],
    legs=[(0.03, 0.04, -0.01), (0.1, 0.12, -0.02), (0.15, 0.2, -0.02)], leg_r=[0.016, 0.009, 0.006],
    eye=(0.02, -0.245, 0.05), eye_r=0.01,
    extras=extras,
)

if __name__ == "__main__":
    nh.run(lambda: fl.build(SPEC), "Anchiornis", **fl.PREVIEW)
