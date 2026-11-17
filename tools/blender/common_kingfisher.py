"""
Procedural low-poly common kingfisher (Alcedo atthis) perched on a short post.

Compact, chunky bird with a big head and a long black dagger bill; electric
blue-turquoise crown (barred with paler spots), back and folded wings, a bright
turquoise stripe down the back, orange-rufous underparts and cheek patch, white
throat and neck patch, a very short dark-blue tail and tiny red feet. It sits on
a brown stick that stands on the ground, so the whole prop rests at z = 0.

Usage:
  blender --background --python tools/blender/common_kingfisher.py -- [--flight] [--render out.png]

Output: Assets/Resources/Models/Species/CommonKingfisher.fbx
Faces -Y, pivot on the ground (foot of the post).
--flight: CommonKingfisherFlight.fbx, in flight (nh_flight), with no post: body level, dagger bill
forward, short rounded wings spread (blue with turquoise-spotted coverts above, orange-buff
below), the turquoise back stripe and rump showing, feet tucked; pivot at the body centre.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flight  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

BLUE = (0.02, 0.32, 0.62)        # wing / crown blue
BLUE_DARK = (0.02, 0.16, 0.36)
TURQUOISE = (0.10, 0.75, 0.85)   # back stripe, crown spots
ORANGE = (0.92, 0.42, 0.10)
ORANGE_DEEP = (0.78, 0.30, 0.06)
WHITE = (0.96, 0.94, 0.88)
BILL = (0.06, 0.05, 0.05)
FEET = (0.90, 0.22, 0.15)
EYE = (0.02, 0.02, 0.02)
BARK = (0.36, 0.24, 0.14)
BARK_DARK = (0.22, 0.14, 0.08)

POST_TOP = 0.34
BODY_C = Vector((0.0, 0.03, POST_TOP + 0.15))
HEAD_C = Vector((0.0, -0.05, POST_TOP + 0.33))


def post():
    pts = [(0, 0.0, 0.0), (0.01, 0.0, 0.12), (0.0, 0.01, 0.24), (0.0, 0.0, POST_TOP)]
    bm = nh.tube(pts, [0.05, 0.042, 0.038, 0.036], sides=7)

    def color(co, n):
        k = noise.noise(Vector((co.x * 9, co.y * 9, co.z * 22)))
        return nh.lerp(BARK, BARK_DARK, 0.5 + 0.5 * k)
    return bm, color


def twig():
    # a short side twig with a leaf so the post reads as a branch, not a pole
    bm = nh.tube([(0.0, 0.0, 0.18), (0.07, -0.02, 0.23), (0.13, -0.03, 0.30)], [0.016, 0.011, 0.0], sides=5)
    return bm, BARK


def body_color(co, n):
    # orange underparts facing front/down, blue on the back and sides
    rel = co - BODY_C
    front = (-n.y * 0.75 - n.z * 0.65)
    belly = nh.smoothstep(0.05, 0.35, front)
    col = nh.lerp(BLUE, ORANGE, belly)
    # deeper orange low on the belly
    col = nh.lerp(col, ORANGE_DEEP, belly * nh.smoothstep(0.0, -0.1, rel.z) * 0.5)
    # turquoise stripe down the middle of the back
    stripe = nh.smoothstep(0.045, 0.0, abs(co.x)) * nh.smoothstep(0.0, 0.4, n.y + n.z * 0.4)
    return nh.lerp(col, TURQUOISE, stripe * (1 - belly))


def head_color(co, n):
    rel = co - HEAD_C
    side = abs(rel.x)
    col = BLUE
    # crown barring: pale turquoise spots on the top of the head
    if n.z > 0.15:
        spot = math.sin(rel.y * 190) * math.sin(rel.x * 170)
        if spot > 0.5:
            col = nh.lerp(BLUE, TURQUOISE, 0.65)
    # orange cheek patch running back from the bill base under the eye
    cheek = nh.smoothstep(0.04, 0.07, side) * nh.smoothstep(0.035, -0.005, rel.z) * nh.smoothstep(0.06, -0.02, rel.y)
    col = nh.lerp(col, ORANGE, cheek)
    # white patch on the side of the neck behind the cheek
    neck = nh.smoothstep(0.035, 0.065, side) * nh.smoothstep(0.01, -0.03, rel.z) * nh.smoothstep(0.015, 0.045, rel.y)
    col = nh.lerp(col, WHITE, neck)
    # white throat underneath
    throat = nh.smoothstep(-0.2, -0.6, n.z) * nh.smoothstep(0.03, -0.04, rel.y)
    col = nh.lerp(col, WHITE, throat)
    # thin blue moustache stripe between cheek and throat
    return col


def wing(side):
    # folded wing: a flattened ellipsoid lying along the flank, darker with spots near the shoulder
    rot = Matrix.Rotation(math.radians(-side * 8), 4, "Z") @ Matrix.Rotation(math.radians(-22), 4, "X")
    bm = nh.ellipsoid((0, 0, 0), (0.024, 0.13, 0.058), subdivisions=3)
    nh.transform(bm, rot)
    centre = BODY_C + Vector((side * 0.076, 0.06, 0.0))
    nh.transform(bm, Matrix.Translation(centre))

    def color(co, n):
        rel = co - centre
        col = nh.lerp(BLUE, BLUE_DARK, nh.smoothstep(0.0, 0.13, rel.y))
        # pale spots on the coverts
        if rel.y < 0.0 and math.sin(rel.y * 170) * math.sin(rel.z * 170) > 0.6:
            col = nh.lerp(col, TURQUOISE, 0.7)
        return col
    return bm, color


def build():
    mb = nh.MeshBuilder()
    mb.add(*post())
    mb.add(*twig())
    # leaf on the twig
    leaf = nh.flat_panel([(0.13, -0.03, 0.30), (0.17, -0.07, 0.33), (0.22, -0.06, 0.34), (0.18, -0.02, 0.31)], 0.006)
    mb.add(leaf, (0.30, 0.55, 0.20), smooth=False)

    # Body: chunky, tilted upright, belly forward
    body = nh.ellipsoid((0, 0, 0), (0.1, 0.13, 0.13), subdivisions=4)
    nh.transform(body, Matrix.Rotation(math.radians(-25), 4, "X"))
    nh.transform(body, Matrix.Translation(BODY_C))
    mb.add(body, body_color)

    # Big head sitting right on the body (kingfishers have hardly any neck)
    head = nh.ellipsoid(HEAD_C, (0.088, 0.1, 0.085), subdivisions=4)
    mb.add(head, head_color)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(HEAD_C + Vector((sx * 0.075, -0.035, 0.012)), (0.014, 0.016, 0.016), subdivisions=1), EYE)

    # Long dagger bill, slightly flattened side to side
    bill_pts = [HEAD_C + Vector(p) for p in ((0, -0.07, -0.008), (0, -0.14, -0.014), (0, -0.22, -0.022), (0, -0.29, -0.03))]
    mb.add(nh.tube(bill_pts, [0.028, 0.02, 0.011, 0.0], sides=6, scale_xy=(0.7, 1.0)), BILL)

    for sx in (-1, 1):
        mb.add(*wing(sx))

    # Very short tail poking out below the wingtips
    tail_pts = [BODY_C + Vector(p) for p in ((0, 0.09, -0.07), (0, 0.15, -0.13), (0, 0.19, -0.175), (0, 0.2, -0.19))]
    mb.add(nh.tube(tail_pts, [0.038, 0.034, 0.028, 0.0], sides=6, scale_xy=(1.0, 0.35)), BLUE_DARK)

    # Tiny red feet gripping the post top
    for sx in (-1, 1):
        mb.add(nh.tube([(sx * 0.03, 0.0, POST_TOP + 0.05), (sx * 0.032, -0.015, POST_TOP + 0.015),
                        (sx * 0.032, -0.045, POST_TOP + 0.005)], [0.014, 0.011, 0.0], sides=5), FEET)

    obj = mb.to_object("CommonKingfisher", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


UNDERWING = (0.90, 0.62, 0.38)


def flight_wing_color(t, c, top):
    """Short rounded wing: orange-buff below; above blue, with turquoise spots on the coverts near
    the leading edge and darker blue flight feathers toward the tip and trailing edge."""
    if not top:
        return nh.lerp(UNDERWING, BLUE_DARK, nh.smoothstep(0.7, 1.0, t) * nh.smoothstep(0.4, 0.8, c) * 0.6)
    col = nh.lerp(BLUE, BLUE_DARK, max(nh.smoothstep(0.55, 0.85, t), nh.smoothstep(0.55, 0.85, c)) * 0.8)
    coverts = (1 - nh.smoothstep(0.35, 0.5, c)) * (1 - nh.smoothstep(0.5, 0.65, t))
    if math.sin(t * 60) * math.sin(c * 40) > 0.45:
        col = nh.lerp(col, TURQUOISE, 0.75 * coverts)
    return col


def build_flight():
    mb = nh.MeshBuilder()
    # Chunky body, level (belly orange below, blue with the turquoise stripe above)
    body_c = Vector((0.0, 0.0, 0.0))

    def flight_body_color(co, n):
        belly = nh.smoothstep(0.1, -0.35, n.z)
        col = nh.lerp(BLUE, ORANGE, belly)
        col = nh.lerp(col, ORANGE_DEEP, belly * nh.smoothstep(-0.03, -0.09, co.z) * 0.5)
        stripe = nh.smoothstep(0.04, 0.0, abs(co.x)) * nh.smoothstep(0.3, 0.7, n.z)
        return nh.lerp(col, TURQUOISE, stripe * (1 - belly))

    mb.add(nh.ellipsoid(body_c, (0.095, 0.15, 0.09), subdivisions=4), flight_body_color)

    # The big head right in front of it, carried level, and the long dagger bill pointing ahead
    head = nh.MeshBuilder()
    head.add(nh.ellipsoid(HEAD_C, (0.088, 0.1, 0.085), subdivisions=4), head_color)
    for sx in (-1, 1):
        head.add(nh.ellipsoid(HEAD_C + Vector((sx * 0.075, -0.035, 0.012)), (0.014, 0.016, 0.016), subdivisions=1), EYE)
    bill_pts = [HEAD_C + Vector(p) for p in ((0, -0.07, -0.008), (0, -0.14, -0.01), (0, -0.22, -0.012), (0, -0.29, -0.014))]
    head.add(nh.tube(bill_pts, [0.028, 0.02, 0.011, 0.0], sides=6, scale_xy=(0.7, 1.0)), BILL)
    nh.transform(head.bm, Matrix.Translation(Vector((0, -0.19, 0.03)) - HEAD_C))
    mb.add(head.bm)

    # Very short dark-blue tail behind the turquoise rump
    mb.add(nh.tube([(0, 0.12, 0.01), (0, 0.19, 0.012), (0, 0.235, 0.012)], [0.04, 0.035, 0.0], sides=6,
                   scale_xy=(1.0, 0.3)), BLUE_DARK)

    # Tiny red feet tucked under the belly
    for sx in (-1, 1):
        mb.add(nh.tube([(sx * 0.03, 0.04, -0.075), (sx * 0.032, 0.09, -0.07), (sx * 0.033, 0.12, -0.065)],
                       [0.013, 0.011, 0.0], sides=5), FEET)

    # Short, rounded wings spread from the shoulders, ~0.9 across
    for side in (1, -1):
        mb.add(*nh_flight.make_wing(side, 0.45, flight_wing_color, root_x=0.06, y0=0.0, z0=0.035,
                                    leading=((0.0, -0.08), (0.45, -0.1), (0.8, -0.08), (1.0, -0.02)),
                                    chord=((0.0, 0.2), (0.45, 0.2), (0.8, 0.17), (1.0, 0.07)),
                                    dihedral=((0.0, 0.0), (0.45, 0.03), (1.0, 0.02)),
                                    thickness=((0.0, 0.05), (0.45, 0.025), (1.0, 0.006))))

    return mb.to_object("CommonKingfisherFlight", roughness=0.45)


if __name__ == "__main__":
    if "--flight" in sys.argv:
        nh.run(build_flight, "CommonKingfisherFlight", views=((35, 25), (20, 70), (180, -35)))
    else:
        nh.run(build, "CommonKingfisher", ground=(0.32, 0.45, 0.25), views=((35, 20), (-90, 8), (20, 65)))
