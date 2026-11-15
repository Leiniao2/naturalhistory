"""
Procedural Tyrian metaltail (Metallura tyrianthina), a male hovering, for map swarms.

Tiny Andean hummingbird held at a steep hover angle with its narrow, pointed
wings spread flat out to the sides (the bottom of a stroke). Dark bronze-green
body that shades to coppery bronze on the back, a glittering emerald gorget on
the throat, a small white spot behind the eye, and the short, straight black
bill. The slightly fanned, notched tail is the "metaltail": iridescent violet
to coppery purple. Little dark feet tucked under the belly.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/metallura_tyrianthina.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TyrianMetaltail.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

GREEN = (0.08, 0.24, 0.07)        # dark bronze-green plumage
BRONZE = (0.28, 0.25, 0.07)
BELLY = (0.10, 0.13, 0.06)
GORGET = (0.30, 1.00, 0.35)       # glittering emerald throat
GORGET_DEEP = (0.10, 0.80, 0.25)
SPOT = (0.95, 0.95, 0.92)
BILL = (0.04, 0.04, 0.04)
EYE = (0.02, 0.02, 0.02)
VIOLET = (0.45, 0.12, 0.62)       # tail
COPPER = (0.62, 0.22, 0.30)
TAIL_DARK = (0.18, 0.05, 0.22)
WING = (0.17, 0.15, 0.14)
WING_DARK = (0.09, 0.08, 0.08)
FEET = (0.08, 0.07, 0.06)

PITCH = math.radians(36)  # body raised head-up for hovering
TILT = Matrix.Rotation(-PITCH, 4, "X")

# body-frame positions (bird level, facing -Y); TILT turns them into the hover pose
BODY_C = Vector((0.0, 0.0, 0.0))
HEAD_C = Vector((0.0, -0.15, 0.035))
HEAD_R = 0.058


def body_shells():
    s = []
    s.append(nh.ellipsoid(BODY_C, (0.062, 0.12, 0.066), subdivisions=3))
    s.append(nh.ellipsoid((0, -0.085, 0.02), (0.052, 0.06, 0.056), subdivisions=2))
    s.append(nh.ellipsoid(HEAD_C, (HEAD_R, HEAD_R * 1.08, HEAD_R), subdivisions=3))
    # undertail coverts flowing into the tail base
    s.append(nh.tube([(0, 0.08, -0.01), (0, 0.13, -0.015), (0, 0.16, -0.02)], [0.04, 0.03, 0.02], sides=8))
    return s


def body_color(co, n):
    """co, n are in the body frame (before the hover tilt)."""
    d = co - HEAD_C
    sheen = 0.5 + 0.5 * noise.noise(co * 30.0)
    col = nh.lerp(GREEN, BRONZE, nh.smoothstep(-0.02, 0.12, co.y) * 0.7 + sheen * 0.15)
    col = nh.lerp(col, BELLY, nh.smoothstep(0.0, -0.8, n.z) * 0.6)
    # glittering gorget: throat and upper breast, under and in front of the head
    throat = nh.smoothstep(0.0, -0.45, n.z) * nh.smoothstep(-0.03, -0.09, co.y) * nh.smoothstep(0.04, -0.06, d.y + 0.0)
    throat = max(throat, nh.smoothstep(-0.25, -0.55, n.z) * nh.smoothstep(-0.03, -0.08, co.y))
    glitter = 0.6 + 0.4 * math.sin(co.x * 260.0) * math.sin(co.y * 240.0 + co.z * 150.0)
    return nh.lerp(col, nh.lerp(GORGET_DEEP, GORGET, glitter), throat)


def tail():
    """Slightly fanned, notched tail of broad violet-coppery feathers, held out behind."""
    shells = []
    root = Vector((0, 0.13, -0.012))
    for k, (a, L) in enumerate(((0.07, 0.2), (0.26, 0.215), (0.46, 0.225))):
        for sx in (-1, 1):
            ang = sx * a
            d = Vector((math.sin(ang), math.cos(ang), 0.12)).normalized()
            tip = root + d * L
            pts = [root + Vector((sx * 0.008 * k, 0, 0.002 * k)), root.lerp(tip, 0.45), root.lerp(tip, 0.85), tip]
            bm = nh.tube(pts, [0.022, 0.034, 0.03, 0.0], sides=6, scale_xy=(1.0, 0.16))
            shells.append(bm)
    return shells


def tail_color(co, n):
    s = (co - Vector((0, 0.13, -0.012))).length / 0.21
    col = nh.lerp(VIOLET, COPPER, 0.5 + 0.5 * math.sin(co.x * 80.0 + s * 5.0))
    return nh.lerp(col, TAIL_DARK, nh.smoothstep(0.7, 1.0, s) * 0.5)


def wing_outline(length=0.44, n=12):
    """Narrow, sickle-ish hummingbird wing: root at the origin, x outward, -y forward."""
    lead, trail = [], []
    for i in range(n + 1):
        t = i / n
        x = 0.005 + t * length
        lead.append((x, -0.03 - 0.012 * math.sin(math.pi * t)))
        w = 0.11 * (1 - 0.35 * t) * math.sqrt(max(0.0, 1 - max(0.0, (t - 0.75) / 0.25) ** 2))
        trail.append((x, -0.03 + max(w, 0.004)))
    trail[-1] = (lead[-1][0] + 0.01, lead[-1][1] + 0.01)
    return lead + trail[::-1]


def wing(side, hinge):
    pts = [(x, y, 0.0) for x, y in wing_outline()]
    bm = nh.flat_panel(pts, thickness=0.006)
    m = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-6), 4, "Z") @ Matrix.Rotation(math.radians(-6), 4, "Y")
    if side < 0:
        m = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ m
    nh.transform(bm, m)
    if side < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)

    def color(co, nrm):
        t = (abs(co.x) - abs(hinge.x)) / 0.44
        col = nh.lerp(WING, WING_DARK, nh.smoothstep(0.4, 1.0, t))
        # primary feather lines
        lines = nh.smoothstep(0.8, 0.95, math.sin(co.y * 160.0 - abs(co.x) * 60.0))
        return nh.lerp(col, WING_DARK, lines * 0.5)
    return bm, color


def build():
    parts = nh.MeshBuilder()
    for shell in body_shells():
        parts.add(shell, GREEN)
    body = parts.fuse(voxel=0.008, smooth=5, smooth_factor=0.5, max_tris=2400)

    tilted = nh.MeshBuilder()
    tilted.add(body, body_color)
    for shell in tail():
        tilted.add(shell, tail_color, smooth=False)
    # short, straight black bill
    tilted.add(nh.tube([HEAD_C + Vector((0, -0.045, -0.005)), HEAD_C + Vector((0, -0.09, -0.01)),
                        HEAD_C + Vector((0, -0.135, -0.014))], [0.011, 0.007, 0.002], sides=6), BILL)
    for sx in (-1, 1):
        eye = HEAD_C + Vector((sx * 0.045, -0.02, 0.016))
        tilted.add(nh.ellipsoid(eye, (0.012, 0.013, 0.012), subdivisions=1), EYE)
        tilted.add(nh.ellipsoid(HEAD_C + Vector((sx * 0.05, 0.016, 0.012)), (0.008, 0.009, 0.008),
                                subdivisions=1), SPOT)
        # tiny feet tucked under the belly
        tilted.add(nh.tube([(sx * 0.02, 0.02, -0.055), (sx * 0.022, 0.045, -0.075), (sx * 0.02, 0.06, -0.072)],
                           [0.008, 0.006, 0.0], sides=4), FEET)

    # tilt the bird into the hover pose
    mb = tilted
    nh.transform(mb.bm, TILT)

    # wings spread flat out to the sides from the shoulders
    shoulder = TILT @ Vector((0.045, -0.045, 0.045))
    for side in (1, -1):
        mb.add(*wing(side, Vector((shoulder.x, shoulder.y, shoulder.z))), smooth=False)
    return mb.to_object("TyrianMetaltail", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "TyrianMetaltail", background=(0.30, 0.40, 0.30), views=((35, 25), (0, 80), (-90, 8), (20, -10)))
