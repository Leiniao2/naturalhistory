"""
Procedural Vegavis iaai (Late Cretaceous, ~68-66 Ma, Vega Island, Antarctica), swimming.

One of the oldest crown birds, a relative of ducks and geese (Anseriformes) that lived
alongside the last dinosaurs; its fossil larynx (syrinx) is the oldest known, so it
probably honked. A foot-propelled diver about 60 cm long, with a long, low, loon-like
body riding deep in the water, a longish neck, a small head and a slender, pointed bill,
and large webbed feet set far back. Plumage: dark grey-brown above with paler scalloping,
white throat and underparts (colours unknown).

Usage:
  blender --background --python tools/blender/vegavis_iaai.py -- [--flight] [--render out.png]

Output: Assets/Resources/Models/Species/Vegavis.fbx
Faces -Y, pivot at the WATERLINE (z = 0); only the keel sits below it. ~0.6 long.
--flight: VegavisFlight.fbx, in flight (nh_flight): neck stretched out, the big webbed feet
trailing behind the short tail as in a loon, narrow pointed wings spread (dark grey-brown above,
pale below), pivot at the body centre.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flight  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

DARK = (0.27, 0.25, 0.22)
GREY = (0.38, 0.36, 0.33)
PALE = (0.62, 0.60, 0.56)
WHITE = (0.93, 0.92, 0.89)
BILL = (0.16, 0.15, 0.14)
EYE = (0.45, 0.08, 0.06)
FEET = (0.30, 0.30, 0.32)
UNDERWING = (0.80, 0.79, 0.76)

BODY_C = Vector((0.0, 0.02, 0.02))
BODY_R = (0.085, 0.24, 0.06)
HEAD = Vector((0.0, -0.3, 0.165))
HEAD_R = (0.032, 0.045, 0.034)


def body_deform(v):
    k = 1.0
    if v.z < 0:
        k *= 1.0 - 0.35 * (-v.z) ** 2
    if v.y < 0:
        k *= 1.0 + 0.05 * (-v.y)
    return k


def body_color(co, n):
    # dark back with pale scallops, white flanks and breast at the waterline
    scallop = 0.5 + 0.5 * math.sin(co.y * 150.0) * math.sin(co.x * 160.0)
    top = nh.lerp(DARK, PALE, scallop * 0.35)
    # white below a line along the flank, the breast white higher up
    line = 0.45 - 0.35 * nh.smoothstep(0.05, -0.2, co.y)
    col = nh.lerp(top, WHITE, nh.smoothstep(line, line - 0.25, n.z))
    return nh.lerp(col, GREY, nh.smoothstep(0.1, -0.3, n.z) * nh.smoothstep(0.08, 0.2, co.y) * 0.5)


def neck_color(co, n):
    # dark hind neck, white throat and fore neck
    return nh.lerp(DARK, WHITE, nh.smoothstep(-0.1, -0.6, n.y - 0.5 * n.z))


def head_color(co, n):
    return nh.lerp(DARK, WHITE, nh.smoothstep(0.0, -0.5, n.z) * 0.9)


def add_head(mb, at):
    mb.add(nh.ellipsoid(at, HEAD_R, subdivisions=3), head_color)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(at + Vector((sx * 0.026, -0.018, 0.008)), (0.007, 0.007, 0.007), subdivisions=1), EYE)
    bill = [at + Vector((0, -0.035, -0.004)), at + Vector((0, -0.06, -0.008)), at + Vector((0, -0.085, -0.012))]
    mb.add(nh.tube(bill, [0.013, 0.008, 0.0], sides=6, scale_xy=(0.9, 0.7)), BILL)


def build():
    mb = nh.MeshBuilder()

    # Long, low body riding deep; the stern only slightly raised
    body = nh.uv_ellipsoid(BODY_C, BODY_R, segments=28, rings=18, deform=body_deform)
    for v in body.verts:
        if v.co.y > 0.12:
            v.co.z += (v.co.y - 0.12) ** 2 * 1.0
    mb.add(body, body_color)

    # Short tail
    mb.add(nh.tube([(0, 0.22, 0.05), (0, 0.27, 0.06), (0, 0.3, 0.065)], [0.03, 0.02, 0.0], sides=8,
                   scale_xy=(1.0, 0.4)), DARK)

    # Folded wings along the back
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.03, 0.08, 0.065), (0.03, 0.14, 0.016), subdivisions=3,
                            rotation=Matrix.Rotation(sx * 0.15, 3, "Y")),
               lambda co, n: nh.lerp(DARK, PALE, (0.5 + 0.5 * math.sin(co.y * 120.0)) * 0.3))

    # Longish neck rising from the breast, held in a gentle curve
    neck = [(0, -0.18, 0.03), (0, -0.23, 0.07), (0, -0.265, 0.115), (0, -0.285, 0.15)]
    mb.add(nh.tube(neck, [0.045, 0.034, 0.028, 0.027], sides=12, cap_start=False), neck_color)
    add_head(mb, HEAD)

    # Big webbed feet set far back, just under the water behind the body
    for sx in (-1, 1):
        ankle = Vector((sx * 0.05, 0.2, -0.02))
        mb.add(nh.tube([ankle + Vector((0, -0.03, 0.03)), ankle], [0.012, 0.01], sides=5), FEET)
        web = [(ankle.x, ankle.y, ankle.z), (ankle.x + sx * 0.04, ankle.y + 0.07, ankle.z - 0.005),
               (ankle.x, ankle.y + 0.085, ankle.z - 0.005), (ankle.x - sx * 0.03, ankle.y + 0.065, ankle.z - 0.005)]
        mb.add(nh.flat_panel(web, thickness=0.005), FEET, smooth=False)

    return mb.to_object("Vegavis", roughness=0.6)


def flight_wing_color(t, c, top):
    if not top:
        return nh.lerp(UNDERWING, GREY, nh.smoothstep(0.65, 0.95, t) * 0.6)
    col = nh.lerp(DARK, PALE, (0.5 + 0.5 * math.sin(t * 40.0) * math.sin(c * 12.0)) * 0.2)
    return nh.lerp(col, (0.12, 0.11, 0.10), nh.smoothstep(0.6, 0.75, t))  # darker primaries


def build_flight():
    mb = nh.MeshBuilder()

    body = nh.uv_ellipsoid(BODY_C, BODY_R, segments=28, rings=18, deform=body_deform)
    mb.add(body, body_color)
    mb.add(nh.tube([(0, 0.22, 0.03), (0, 0.27, 0.035), (0, 0.3, 0.035)], [0.03, 0.02, 0.0], sides=8,
                   scale_xy=(1.0, 0.4)), DARK)

    # Neck stretched forward, head level
    neck = [(0, -0.18, 0.025), (0, -0.25, 0.035), (0, -0.32, 0.045), (0, -0.355, 0.048)]
    mb.add(nh.tube(neck, [0.045, 0.032, 0.027, 0.027], sides=12, cap_start=False), neck_color)
    add_head(mb, Vector((0, -0.385, 0.05)))

    # Big webbed feet trailing behind the tail, loon-style
    for sx in (-1, 1):
        ankle = Vector((sx * 0.03, 0.27, 0.0))
        mb.add(nh.tube([Vector((sx * 0.035, 0.16, -0.02)), ankle], [0.013, 0.01], sides=5), FEET)
        web = [(ankle.x, ankle.y, ankle.z), (ankle.x + sx * 0.03, ankle.y + 0.08, ankle.z),
               (ankle.x, ankle.y + 0.095, ankle.z), (ankle.x - sx * 0.025, ankle.y + 0.075, ankle.z)]
        mb.add(nh.flat_panel(web, thickness=0.005), FEET, smooth=False)

    # Narrow, pointed wings, ~0.95 across
    for side in (1, -1):
        mb.add(*nh_flight.make_wing(side, 0.48, flight_wing_color, root_x=0.05, y0=0.0, z0=0.05,
                                    leading=((0.0, -0.08), (0.4, -0.09), (0.8, -0.02), (1.0, 0.1)),
                                    chord=((0.0, 0.16), (0.4, 0.14), (0.8, 0.08), (1.0, 0.012)),
                                    dihedral=((0.0, 0.0), (0.45, 0.02), (1.0, 0.0)),
                                    thickness=((0.0, 0.04), (0.45, 0.02), (1.0, 0.004))))

    nh.transform(mb.bm, Matrix.Translation(-BODY_C))
    return mb.to_object("VegavisFlight", roughness=0.6)


if __name__ == "__main__":
    if "--flight" in sys.argv:
        nh.run(build_flight, "VegavisFlight", views=((35, 25), (20, 70), (180, -35)))
    else:
        nh.run(build, "Vegavis", ground=(0.22, 0.40, 0.50), views=((40, 25), (-90, 5), (25, 65)))
