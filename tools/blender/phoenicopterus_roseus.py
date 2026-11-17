"""
Procedural low-poly greater flamingo (Phoenicopterus roseus) for map colonies.

A tall adult standing on both very long pink legs (backward-bending "knee" at the
ankle joint, webbed feet): a pale pink, boat-shaped body, folded wings with deep
pink-red coverts on top and the black flight feathers showing along the lower
edge and crossed over the tail, a long thin S-curved neck, a small head with a
yellow eye, and the thick, sharply bent bill - pale pink at the base with a black
tip.

Usage:
  blender --background --python tools/blender/phoenicopterus_roseus.py -- [--flight] [--render out.png]

Output: Assets/Resources/Models/Species/GreaterFlamingo.fbx
Faces -Y, pivot at the feet (ground). About 1.45 tall, 0.75 long (bill to tail).
--flight: GreaterFlamingoFlight.fbx, in flight (nh_flight): the long neck stretched straight out
ahead, the long legs trailing straight out behind, wings spread (deep pink-red coverts, black
flight feathers), pivot at the body centre.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flight  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

PINK_PALE = (0.96, 0.74, 0.76)   # body plumage
PINK_SHADE = (0.86, 0.60, 0.64)
PINK_NECK = (0.95, 0.66, 0.70)
COVERT = (0.92, 0.30, 0.40)      # deep pink-red wing coverts
COVERT_LIGHT = (0.96, 0.55, 0.60)
BLACK = (0.04, 0.04, 0.05)       # flight feathers
LEG = (0.94, 0.48, 0.55)
LEG_DARK = (0.80, 0.36, 0.44)
BILL = (0.96, 0.78, 0.78)
BILL_TIP = (0.05, 0.05, 0.06)
FACE = (0.98, 0.86, 0.84)        # bare pale skin at the bill base
EYE = (0.95, 0.80, 0.20)
PUPIL = (0.03, 0.02, 0.02)

BODY_Z = 0.86   # height of the body axis above the ground
HEAD_C = Vector((0.0, -0.285, 1.39))


def spline(points, radii, per=4):
    """Catmull-Rom resample of a polyline (and its radii) for a smooth, round curve."""
    pts = [Vector(p) for p in points]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    rx = [radii[0]] + list(radii) + [radii[-1]]
    out_p, out_r = [], []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out_p.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (3 * p1 - p0 - 3 * p2 + p3) * t3))
            out_r.append(rx[i] + (rx[i + 1] - rx[i]) * t)
    out_p.append(pts[-1])
    out_r.append(radii[-1])
    return out_p, out_r


def body_color(co, n):
    c = nh.lerp(PINK_PALE, PINK_SHADE, nh.smoothstep(0.1, -0.9, n.z) * 0.55)
    # slightly deeper pink on the breast
    return nh.lerp(c, PINK_NECK, nh.smoothstep(-0.08, -0.18, co.y) * 0.6)


def wing_color(side):
    """Folded wing: red coverts on top, black flight feathers along the lower edge and rear."""
    def fn(co, n):
        up = n.z
        rear = nh.smoothstep(0.08, 0.20, co.y)
        low = nh.smoothstep(0.05, -0.05, up) * nh.smoothstep(-0.08, 0.0, co.y)  # flight feather edge
        c = nh.lerp(COVERT_LIGHT, COVERT, nh.smoothstep(-0.12, 0.02, co.y))     # paler toward the shoulder
        c = nh.lerp(c, BLACK, max(rear, low))
        return nh.lerp(c, PINK_PALE, nh.smoothstep(-0.10, -0.17, co.y))        # shoulder blends into body
    return fn


def neck_color(co, n):
    return nh.lerp(PINK_NECK, PINK_PALE, 0.3 + 0.3 * max(0.0, n.z))


def bill_color(co, n):
    # bend point is where the bill turns down; everything well past it is black
    d = (co - HEAD_C).length
    c = BILL if d < 0.135 else BILL_TIP
    if d < 0.06:
        c = FACE
    return c


def build():
    mb = nh.MeshBuilder()

    # Plump, boat-shaped body: rounded breast at -Y, tapering to a short tail at +Y
    profile = [(-0.20, 0.0, 0.02), (-0.19, 0.04, 0.018), (-0.165, 0.072, 0.012), (-0.12, 0.092, 0.006),
               (-0.06, 0.102, 0.0), (0.0, 0.104, 0.0), (0.06, 0.10, 0.004), (0.12, 0.088, 0.012),
               (0.18, 0.066, 0.024), (0.23, 0.042, 0.034), (0.27, 0.02, 0.042), (0.29, 0.0, 0.046)]
    mb.add(nh.tube([(0, y, BODY_Z + dz) for y, _, dz in profile], [r for _, r, _ in profile],
                   sides=24, scale_xy=(0.82, 1.0)), body_color)

    # Folded wings along the flanks and back, primaries crossing over the tail
    for side in (-1, 1):
        wing = nh.ellipsoid((side * 0.052, 0.06, BODY_Z + 0.03), (0.05, 0.22, 0.06), subdivisions=4,
                            deform=lambda v: 1.0 - 0.18 * max(0.0, v.y) ** 2)
        mb.add(wing, wing_color(side))
        mb.add(nh.tube([(side * 0.04, 0.20, BODY_Z + 0.04), (side * 0.025, 0.30, BODY_Z + 0.05),
                        (side * 0.01, 0.37, BODY_Z + 0.045)], [0.032, 0.018, 0.0], sides=6,
                       scale_xy=(1.0, 0.45)), BLACK)
    # loose, drooping scapulars over the back in deep pink
    mb.add(nh.ellipsoid((0, 0.10, BODY_Z + 0.075), (0.06, 0.15, 0.03), subdivisions=2), COVERT_LIGHT)

    # Long thin S-curved neck: forward from the breast, back over itself, then forward to the head
    neck = [(0, -0.15, BODY_Z + 0.03), (0, -0.21, BODY_Z + 0.08), (0, -0.25, BODY_Z + 0.15),
            (0, -0.255, BODY_Z + 0.22), (0, -0.22, BODY_Z + 0.29), (0, -0.175, BODY_Z + 0.35),
            (0, -0.165, BODY_Z + 0.42), (0, -0.19, BODY_Z + 0.49), (0, -0.235, BODY_Z + 0.52),
            HEAD_C + Vector((0, 0.03, -0.005))]
    neck, nr = spline(neck, [0.055, 0.032, 0.025, 0.022, 0.021, 0.021, 0.021, 0.022, 0.024, 0.027])
    mb.add(nh.tube(neck, nr, sides=12, cap_start=False), neck_color)

    # Small head, a little longer than tall
    mb.add(nh.ellipsoid(HEAD_C, (0.031, 0.045, 0.034), subdivisions=3), PINK_PALE)
    for sx in (-1, 1):
        e = HEAD_C + Vector((sx * 0.026, -0.012, 0.008))
        mb.add(nh.ellipsoid(e, (0.008, 0.009, 0.009), subdivisions=1), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.004, -0.002, 0)), (0.005, 0.005, 0.005), subdivisions=1), PUPIL)

    # Thick bill, straight for a short way then bent sharply down
    bill = [HEAD_C + Vector(p) for p in ((0, -0.03, -0.004), (0, -0.07, -0.004), (0, -0.10, -0.008),
                                         (0, -0.118, -0.025), (0, -0.128, -0.05), (0, -0.13, -0.075),
                                         (0, -0.125, -0.092))]
    bill, br = spline(bill, [0.024, 0.022, 0.019, 0.016, 0.012, 0.009, 0.0], per=3)
    mb.add(nh.tube(bill, br, sides=10, scale_xy=(0.8, 1.0)), bill_color)

    # Very long pink legs: thigh hidden in the belly, the backward "knee" (ankle) halfway down
    for sx in (-1, 1):
        x = sx * 0.035
        leg = [(x, 0.03, BODY_Z - 0.05), (x * 1.05, 0.045, BODY_Z - 0.14), (x * 1.1, 0.06, 0.44),
               (x * 1.15, 0.03, 0.22), (x * 1.2, 0.0, 0.015)]
        mb.add(nh.tube(leg, [0.017, 0.012, 0.012, 0.0105, 0.0095], sides=6), LEG)
        mb.add(nh.ellipsoid((x * 1.1, 0.06, 0.44), (0.016, 0.017, 0.022), subdivisions=1), LEG_DARK)  # ankle joint
        # webbed foot: three forward toes joined by a web
        foot = Vector((x * 1.2, 0.0, 0.008))
        tips = []
        for ang in (-30, 0, 30):
            a = math.radians(ang)
            tip = foot + Vector((math.sin(a) * 0.075, -math.cos(a) * 0.075, -0.004))
            tips.append(tip)
            mb.add(nh.tube([foot, (foot + tip) / 2, tip], [0.008, 0.0065, 0.0], sides=4), LEG)
        web = [foot + Vector((0, 0, 0.002))] + [t * 0.85 + foot * 0.15 + Vector((0, 0, 0.002)) for t in tips]
        mb.add(nh.flat_panel(web, thickness=0.004), LEG)
        mb.add(nh.tube([foot, foot + Vector((0, 0.025, 0))], [0.006, 0.0], sides=4), LEG)

    obj = mb.to_object("GreaterFlamingo", roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


def flight_wing_color(t, c, top):
    """Spread wing: deep pink-red coverts over the inner wing, all the flight feathers black
    (secondaries along the trailing edge, the whole outer hand)."""
    hand = nh.smoothstep(0.52, 0.62, t)
    trailing = nh.smoothstep(0.42, 0.55, c)
    black = max(hand, trailing)
    cov = nh.lerp(COVERT, COVERT_LIGHT, nh.smoothstep(0.3, 0.0, t) * 0.5) if top else nh.lerp(COVERT, PINK_PALE, 0.25)
    return nh.lerp(cov, BLACK, black)


def build_flight():
    mb = nh.MeshBuilder()

    # The same boat-shaped body, level, its axis through the pivot
    profile = [(-0.20, 0.0, 0.02), (-0.19, 0.04, 0.018), (-0.165, 0.072, 0.012), (-0.12, 0.092, 0.006),
               (-0.06, 0.102, 0.0), (0.0, 0.104, 0.0), (0.06, 0.10, 0.004), (0.12, 0.088, 0.012),
               (0.18, 0.066, 0.024), (0.23, 0.042, 0.034), (0.27, 0.02, 0.042), (0.29, 0.0, 0.046)]
    mb.add(nh.tube([(0, y, dz - 0.01) for y, _, dz in profile], [r for _, r, _ in profile],
                   sides=24, scale_xy=(0.82, 1.0)), body_color)

    # Long thin neck stretched straight out ahead, drooping just a little
    head_c = Vector((0.0, -0.80, -0.02))
    neck = [(0, -0.15, 0.0), (0, -0.30, -0.01), (0, -0.45, -0.02), (0, -0.60, -0.025), (0, -0.72, -0.022),
            head_c + Vector((0, 0.03, -0.002))]
    neck, nr = spline(neck, [0.055, 0.026, 0.022, 0.021, 0.023, 0.027])
    mb.add(nh.tube(neck, nr, sides=12, cap_start=False), neck_color)

    mb.add(nh.ellipsoid(head_c, (0.031, 0.045, 0.034), subdivisions=3), PINK_PALE)
    for sx in (-1, 1):
        e = head_c + Vector((sx * 0.026, -0.012, 0.008))
        mb.add(nh.ellipsoid(e, (0.008, 0.009, 0.009), subdivisions=1), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.004, -0.002, 0)), (0.005, 0.005, 0.005), subdivisions=1), PUPIL)

    # The bent bill, pointing forward and down
    bill = [head_c + Vector(p) for p in ((0, -0.03, -0.004), (0, -0.07, -0.004), (0, -0.10, -0.008),
                                         (0, -0.118, -0.025), (0, -0.128, -0.05), (0, -0.13, -0.075),
                                         (0, -0.125, -0.092))]
    bill, br = spline(bill, [0.024, 0.022, 0.019, 0.016, 0.012, 0.009, 0.0], per=3)

    def flying_bill(co, n):
        return bill_color(co - head_c + HEAD_C, n)

    mb.add(nh.tube(bill, br, sides=10, scale_xy=(0.8, 1.0)), flying_bill)

    # Very long pink legs trailing straight out behind the tail, feet together
    for sx in (-1, 1):
        x = sx * 0.03
        leg = [(x, 0.05, -0.06), (x, 0.20, -0.06), (x, 0.42, -0.04), (x, 0.66, -0.02), (x, 0.80, -0.01)]
        mb.add(nh.tube(leg, [0.017, 0.012, 0.011, 0.0095, 0.006], sides=6), LEG)
        mb.add(nh.ellipsoid((x, 0.42, -0.04), (0.014, 0.018, 0.014), subdivisions=1), LEG_DARK)  # ankle joint
        mb.add(nh.tube([(x, 0.80, -0.01), (x * 1.6, 0.87, -0.008), (x * 1.8, 0.89, -0.006)],
                       [0.009, 0.006, 0.0], sides=4), LEG)  # folded toes

    # Wings spread, about 1.55 across: long, fairly narrow, pointed hand
    for side in (1, -1):
        mb.add(*nh_flight.make_wing(side, 0.78, flight_wing_color, root_x=0.05, y0=0.02, z0=0.02,
                                    leading=((0.0, -0.12), (0.45, -0.16), (0.8, -0.08), (1.0, 0.06)),
                                    chord=((0.0, 0.28), (0.45, 0.25), (0.8, 0.16), (1.0, 0.03)),
                                    thickness=((0.0, 0.06), (0.45, 0.03), (1.0, 0.006)),
                                    stations=18, chord_points=tuple(i / 10 for i in range(11))))

    return mb.to_object("GreaterFlamingoFlight", roughness=0.65)


if __name__ == "__main__":
    if "--flight" in sys.argv:
        nh.run(build_flight, "GreaterFlamingoFlight", views=((35, 25), (20, 70), (180, -35)))
    else:
        nh.run(build, "GreaterFlamingo", ground=(0.45, 0.52, 0.36), views=((40, 18), (-90, 5), (25, 65)))
