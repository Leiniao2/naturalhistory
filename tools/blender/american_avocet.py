"""
Procedural low-poly American avocet (Recurvirostra americana) in breeding plumage.

An elegant wader on very long blue-grey legs: slim white body, bold black-and-
white back (black scapular stripes, white wing patch, black primaries), a
cinnamon head and neck, and a long, thin, sharply upcurved black bill.

Usage:
  blender --background --python tools/blender/american_avocet.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmericanAvocet.fbx
Faces -Y, pivot at the feet (ground). About 0.75 long (bill to tail), 0.75 tall.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

WHITE = (0.94, 0.94, 0.92)
WHITE_SHADE = (0.78, 0.79, 0.80)
BLACK = (0.05, 0.05, 0.06)
CINNAMON = (0.80, 0.42, 0.18)
CINNAMON_PALE = (0.92, 0.66, 0.45)
LEG = (0.48, 0.60, 0.72)
BILL = (0.06, 0.06, 0.07)
EYE = (0.12, 0.03, 0.02)

BODY_Z = 0.44  # height of the body axis above the ground


def body_color(co, n):
    col = nh.lerp(WHITE, WHITE_SHADE, nh.smoothstep(0.1, -0.9, n.z) * 0.5)
    # cinnamon wash creeping down from the neck onto the upper breast
    front = nh.smoothstep(-0.10, -0.20, co.y) * nh.smoothstep(BODY_Z - 0.02, BODY_Z + 0.06, co.z)
    return nh.lerp(col, CINNAMON_PALE, front * 0.8)


def wing_color(side):
    """Folded wing seen from above: black scapular stripe along the inner edge,
    white wing patch on the outside, black primaries at the rear."""
    def fn(co, n):
        across = (co.x * side - 0.035) / 0.07  # 0 = inner edge, 1 = outer edge
        primaries = nh.smoothstep(0.09, 0.15, co.y)
        outer = nh.smoothstep(0.75, 0.95, across) * nh.smoothstep(-0.02, 0.06, co.y)  # black outer coverts
        stripe = 1.0 - nh.smoothstep(0.35, 0.5, across)
        stripe *= nh.smoothstep(0.0, 0.4, n.z)  # only on top
        lower = nh.smoothstep(0.1, -0.5, n.z)  # underside of the wing stays pale
        col = nh.lerp(WHITE, BLACK, max(stripe, primaries, outer))
        return nh.lerp(col, WHITE_SHADE, lower * (1 - primaries))
    return fn


def neck_color(co, n):
    # cinnamon head and neck, fading to white low on the breast
    return nh.lerp(CINNAMON_PALE, CINNAMON, nh.smoothstep(BODY_Z + 0.04, BODY_Z + 0.16, co.z))


def build():
    mb = nh.MeshBuilder()

    # Slim boat-shaped body: breast at -Y, tapering into a short tail at +Y
    # (y, radius, axis height): plump breast, deepest belly mid-body, slim tail
    profile = [(-0.185, 0.0, 0.03), (-0.175, 0.03, 0.025), (-0.155, 0.052, 0.018), (-0.12, 0.068, 0.01),
               (-0.07, 0.078, 0.0), (-0.01, 0.081, -0.004), (0.05, 0.079, -0.004), (0.11, 0.071, 0.0),
               (0.17, 0.056, 0.01), (0.22, 0.038, 0.022), (0.26, 0.022, 0.032), (0.29, 0.0, 0.04)]
    mb.add(nh.tube([(0, y, BODY_Z + dz) for y, _, dz in profile], [r for _, r, _ in profile],
                   sides=16, scale_xy=(0.85, 1.0)), body_color)

    # Folded wings lying along the back, crossing slightly over the tail
    for side in (-1, 1):
        wing = nh.ellipsoid((side * 0.05, 0.08, BODY_Z + 0.04), (0.05, 0.20, 0.035), subdivisions=3,
                            deform=lambda v: 1.0 - 0.15 * max(0.0, v.y) ** 2)
        mb.add(wing, wing_color(side))
        # wing tips extending past the tail
        mb.add(nh.tube([(side * 0.04, 0.22, BODY_Z + 0.05), (side * 0.025, 0.31, BODY_Z + 0.055),
                        (side * 0.012, 0.36, BODY_Z + 0.055)], [0.028, 0.016, 0.0], sides=6,
                       scale_xy=(1.0, 0.45)), BLACK)

    # Slender S-curved neck rising from the breast to the head
    neck = [(0, -0.13, BODY_Z + 0.02), (0, -0.165, BODY_Z + 0.065), (0, -0.185, BODY_Z + 0.12),
            (0, -0.195, BODY_Z + 0.18), (0, -0.21, BODY_Z + 0.235), (0, -0.23, BODY_Z + 0.27)]
    mb.add(nh.tube(neck, [0.05, 0.032, 0.022, 0.02, 0.021, 0.025], sides=10, cap_start=False), neck_color)

    # Small rounded head, a little longer than tall
    hc = Vector((0, -0.245, BODY_Z + 0.285))
    mb.add(nh.ellipsoid(hc, (0.032, 0.047, 0.034), subdivisions=3), CINNAMON)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.026, -0.255, BODY_Z + 0.295), (0.008, 0.009, 0.008), subdivisions=1), EYE)

    # Long, thin, sharply upcurved bill
    bill = []
    for i in range(7):
        t = i / 6
        y = -0.28 - 0.24 * t
        z = BODY_Z + 0.275 - 0.01 * t + 0.075 * t ** 2.4
        bill.append((0, y, z))
    mb.add(nh.tube(bill, [0.011, 0.009, 0.007, 0.0055, 0.0045, 0.003, 0.0], sides=5, scale_xy=(0.8, 1.0)), BILL)

    # Very long legs: thigh hidden in the belly, backward-bending "knee" (ankle), long shin
    for sx in (-1, 1):
        x = sx * 0.028
        leg = [(x, 0.04, BODY_Z - 0.04), (x * 1.1, 0.05, BODY_Z - 0.12), (x * 1.2, 0.075, 0.22),
               (x * 1.25, 0.04, 0.10), (x * 1.3, 0.01, 0.012)]
        mb.add(nh.tube(leg, [0.013, 0.009, 0.0095, 0.0075, 0.007], sides=5), LEG)
        # three forward toes and one small hind toe
        foot = Vector((x * 1.3, 0.01, 0.008))
        for ang in (-28, 0, 28):
            a = math.radians(ang)
            tip = foot + Vector((math.sin(a) * 0.06, -math.cos(a) * 0.06, -0.004))
            mb.add(nh.tube([foot, (foot + tip) / 2, tip], [0.006, 0.005, 0.0], sides=4), LEG)
        mb.add(nh.tube([foot, foot + Vector((0, 0.025, 0))], [0.005, 0.0], sides=4), LEG)

    obj = mb.to_object("AmericanAvocet", roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "AmericanAvocet", ground=(0.45, 0.52, 0.36), views=((40, 22), (-90, 5), (25, 65)))
