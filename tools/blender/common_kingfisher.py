"""
Procedural low-poly common kingfisher (Alcedo atthis) perched on a short post.

Compact, chunky bird with a big head and a long black dagger bill; electric
blue-turquoise crown (barred with paler spots), back and folded wings, a bright
turquoise stripe down the back, orange-rufous underparts and cheek patch, white
throat and neck patch, a very short dark-blue tail and tiny red feet. It sits on
a brown stick that stands on the ground, so the whole prop rests at z = 0.

Usage:
  blender --background --python tools/blender/common_kingfisher.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CommonKingfisher.fbx
Faces -Y, pivot on the ground (foot of the post).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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


if __name__ == "__main__":
    nh.run(build, "CommonKingfisher", ground=(0.32, 0.45, 0.25), views=((35, 20), (-90, 8), (20, 65)))
