"""
Procedural low-poly mandarin duck drake (Aix galericulata), swimming.

Red bill with a pale tip, a broad white crescent sweeping back from above the
eye into a shaggy green-and-copper crest, a bright orange "whisker" ruff on the
face and neck, the two upright orange "sail" feathers on the back, a deep
purple-maroon breast with two bold white-and-black vertical bars, warm buff
flanks, a dark olive-brown back and a raised tail.

Usage:
  blender --background --python tools/blender/mandarin_duck.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MandarinDuck.fbx
Faces -Y, pivot at the WATERLINE (z = 0); only the keel sits below it. ~0.55 long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

MAROON = (0.34, 0.07, 0.22)
WHITE = (0.96, 0.96, 0.94)
BLACK = (0.03, 0.03, 0.04)
BUFF = (0.95, 0.66, 0.34)
BUFF_LIGHT = (0.98, 0.78, 0.50)
BUFF_DARK = (0.70, 0.44, 0.20)
ORANGE = (1.00, 0.48, 0.08)
ORANGE_PALE = (1.00, 0.72, 0.36)
OLIVE = (0.27, 0.24, 0.14)
OLIVE_DARK = (0.12, 0.11, 0.07)
GREEN = (0.06, 0.32, 0.20)
COPPER = (0.62, 0.30, 0.10)
FACE = (0.98, 0.86, 0.66)
BILL = (0.90, 0.08, 0.08)
NAIL = (0.99, 0.88, 0.78)
EYE = (0.05, 0.03, 0.02)
BLUE = (0.16, 0.22, 0.52)

BODY_C = Vector((0.0, 0.01, 0.032))
BODY_R = (0.098, 0.245, 0.068)
HEAD = Vector((0.0, -0.215, 0.165))
HEAD_R = (0.042, 0.054, 0.048)
CREST_C = HEAD + Vector((0.0, 0.05, -0.008))
CREST_R = (0.03, 0.085, 0.03)
CREST_TILT = -0.5  # radians about X: slopes down toward the back


def body_deform(v):
    """Radial multiplier on the unit sphere: flatter keel, fuller breast."""
    k = 1.0
    if v.z < 0:
        k *= 1.0 - 0.4 * (-v.z) ** 2
    if v.y < 0:
        k *= 1.0 + 0.07 * (-v.y)
    return k


def inside_body(p):
    v = Vector(((p.x - BODY_C.x) / BODY_R[0], (p.y - BODY_C.y) / BODY_R[1], (p.z - BODY_C.z) / BODY_R[2]))
    return v.length < body_deform(v.normalized()) if v.length > 1e-9 else True


def inside_head(p):
    d = p - HEAD
    if (d.x / HEAD_R[0]) ** 2 + (d.y / HEAD_R[1]) ** 2 + (d.z / HEAD_R[2]) ** 2 < 1.0:
        return True
    c = Matrix.Rotation(-CREST_TILT, 3, "X") @ (p - CREST_C)
    return (c.x / CREST_R[0]) ** 2 + (c.y / CREST_R[1]) ** 2 + (c.z / CREST_R[2]) ** 2 < 1.0


def surface_point(inside, origin, direction, max_dist=0.3):
    """Bisects along a ray from an interior origin to the surface of `inside`."""
    lo, hi = 0.0, max_dist
    direction = Vector(direction).normalized()
    for _ in range(24):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if inside(origin + direction * mid) else (lo, mid)
    return origin + direction * lo


def body_color(co, n):
    # warm buff flanks, lighter low down, with a faint darker scallop pattern
    t = nh.smoothstep(BODY_C.z + 0.04, BODY_C.z - 0.02, co.z)
    col = nh.lerp(BUFF, BUFF_LIGHT, t * 0.6)
    scallop = 0.5 + 0.5 * math.sin(co.y * 140.0 + math.sin(co.z * 90.0) * 2.0)
    col = nh.lerp(col, BUFF_DARK, scallop * 0.22)
    # dark olive-brown back on top
    col = nh.lerp(col, OLIVE, nh.smoothstep(0.78, 0.93, n.z))
    # deep maroon breast in front of the bars
    col = nh.lerp(col, MAROON, nh.smoothstep(-0.085, -0.10, co.y))
    # dark rump and raised tail coverts
    col = nh.lerp(col, OLIVE_DARK, nh.smoothstep(0.15, 0.21, co.y))
    # keel below the waterline
    return nh.lerp(col, BUFF_DARK, nh.smoothstep(0.004, -0.015, co.z) * 0.7)


def head_color(co, n):
    d = co - HEAD
    # crown and forehead: glossy green shading to copper toward the back
    crown = nh.lerp(GREEN, COPPER, nh.smoothstep(-0.01, 0.07, d.y))
    # face below the white band: pale in front of the eye, bright orange cheeks behind/below
    face = nh.lerp(ORANGE, FACE, nh.smoothstep(-0.025, -0.05, d.y) * nh.smoothstep(-0.03, 0.0, d.z))
    band_z = 0.008 - 0.3 * max(0.0, d.y + 0.02)  # the white band sits on this line; crown above, face below
    return crown if d.z > band_z else face


def make_sail(side):
    """Fan-shaped upright feather: straight leading edge, curved notched outer edge, dark trailing rim.
    Outline is (y_back, height) in the feather's own plane."""
    fan = [(0.0, 0.0), (0.055, 0.145), (0.075, 0.158), (0.1, 0.155), (0.12, 0.138),
           (0.116, 0.122), (0.128, 0.108), (0.126, 0.08), (0.1, 0.035), (0.045, 0.0)]
    # the same outline shifted back and slightly thinner: only its trailing edge shows past the fan
    rim = [(y + 0.009, h) for y, h in fan]
    shells = []
    for outline, col, thick in ((fan, ORANGE, 0.012), (rim, OLIVE_DARK, 0.008)):
        pts = [(h, y, 0.0) for y, h in outline]  # height along X for now
        bm = nh.flat_panel(pts, thick)
        nh.transform(bm, Matrix.Rotation(-math.pi / 2, 4, "Y"))  # X (height) -> Z
        nh.transform(bm, Matrix.Rotation(side * 0.22, 4, "Y"))   # lean outward
        nh.transform(bm, Matrix.Translation((side * 0.026, -0.005, 0.085)))
        shells.append((bm, col))
    return shells


def build():
    mb = nh.MeshBuilder()

    # Long, low body; the stern sweeps up into the raised tail
    body = nh.uv_ellipsoid(BODY_C, BODY_R, segments=28, rings=18, deform=body_deform)
    for v in body.verts:
        if v.co.y > 0.1:
            v.co.z += (v.co.y - 0.1) ** 2 * 2.2
    mb.add(body, body_color)

    # Raised, pointed tail
    mb.add(nh.tube([(0, 0.2, 0.07), (0, 0.26, 0.1), (0, 0.31, 0.13)], [0.035, 0.022, 0.0], sides=8,
                   scale_xy=(1.0, 0.4)), OLIVE_DARK)

    # Slim folded wings on the back, dark olive with a blue speculum at the rear
    for sx in (-1, 1):
        def wing_col(co, n):
            return nh.lerp(OLIVE, BLUE, nh.smoothstep(0.12, 0.16, co.y) * nh.smoothstep(0.4, -0.1, n.z))
        mb.add(nh.ellipsoid((sx * 0.03, 0.1, 0.086), (0.03, 0.125, 0.018), subdivisions=3,
                            rotation=Matrix.Rotation(sx * 0.15, 3, "Y")), wing_col)

    # Two bold white bars edged in black on each side of the breast, hugging the body surface
    for sx in (-1, 1):
        for y0 in (-0.118, -0.092):
            for col, rad, out in ((BLACK, 0.017, -0.007), (WHITE, 0.0115, 0.002)):
                pts = []
                for k in range(7):
                    z = -0.002 + 0.092 * k / 6
                    p = surface_point(inside_body, Vector((0, y0, z)), (sx, 0, 0))
                    pts.append(p + Vector((sx * out, 0, 0)))
                radii = [rad * (0.5 if k in (0, 6) else 1.0) for k in range(7)]
                mb.add(nh.tube(pts, radii, sides=6, scale_xy=(0.35, 1.0)), col)

    # The orange sails
    for sx in (-1, 1):
        for bm, col in make_sail(sx):
            mb.add(bm, col, smooth=False)

    # Neck: maroon low, orange ruff high
    neck = [(0, -0.14, 0.05), (0, -0.175, 0.09), (0, -0.195, 0.125), (0, -0.207, 0.15)]
    mb.add(nh.tube(neck, [0.055, 0.045, 0.04, 0.038], sides=12, cap_start=False),
           lambda co, n: nh.lerp(MAROON, ORANGE, nh.smoothstep(0.08, 0.13, co.z)))

    # Head and the swept-back crest
    mb.add(nh.ellipsoid(HEAD, HEAD_R, subdivisions=3), head_color)
    crest = nh.ellipsoid((0, 0, 0), CREST_R, subdivisions=3, deform=lambda v: 1.0 - 0.3 * max(0.0, v.y))
    nh.transform(crest, Matrix.Rotation(CREST_TILT, 4, "X"))
    nh.transform(crest, Matrix.Translation(CREST_C))
    mb.add(crest, lambda co, n: nh.lerp(GREEN, COPPER, nh.smoothstep(0.0, 0.08, (co - HEAD).y)))

    # Shaggy tufts at the back of the crest
    for k in range(5):
        a = (k - 2) * 0.35
        base = CREST_C + Vector((math.sin(a) * 0.015, 0.05, -0.02 + 0.006 * abs(k - 2)))
        tip = base + Vector((math.sin(a) * 0.03, 0.05, -0.035))
        mb.add(nh.tube([base, (base + tip) / 2, tip], [0.012, 0.008, 0.0], sides=4), COPPER)

    # Broad white crescent: a separate shell laid on the head/crest surface, from above the eye
    # sweeping back and widening into the crest
    for sx in (-1, 1):
        path = [(-0.035, 0.024), (-0.012, 0.022), (0.015, 0.012), (0.045, -0.002), (0.075, -0.018), (0.1, -0.032)]
        widths = [0.006, 0.012, 0.016, 0.018, 0.015, 0.0]
        pts = []
        for dy, dz in path:
            origin = HEAD + Vector((0, dy * 0.6, dz * 0.5))
            p = surface_point(inside_head, origin, (sx, 0, 0.15))
            pts.append(p + Vector((sx * 0.001, 0, 0)))
        mb.add(nh.tube(pts, widths, sides=6, scale_xy=(0.3, 1.0)), WHITE)

    # Orange "whisker" ruff: streaks fanning back and down from the cheeks onto the neck
    for sx in (-1, 1):
        for k in range(12):
            t = k / 11
            origin = HEAD + Vector((0, -0.02 + 0.045 * t, -0.008 - 0.022 * t))
            base = surface_point(inside_head, origin, (sx, 0, -0.25))
            tip = base + Vector((sx * 0.014, 0.022 + 0.01 * t, -0.032 - 0.01 * t))
            mb.add(nh.tube([base, (base * 0.4 + tip * 0.6), tip], [0.009, 0.007, 0.0], sides=4),
                   lambda co, n: nh.lerp(ORANGE, ORANGE_PALE, nh.smoothstep(HEAD.z - 0.03, HEAD.z - 0.07, co.z) * 0.6))

    # Eyes, just in front of / below the start of the white band
    for sx in (-1, 1):
        p = surface_point(inside_head, HEAD + Vector((0, -0.02, 0.004)), (sx, -0.25, 0))
        mb.add(nh.ellipsoid(p, (0.009, 0.009, 0.009), subdivisions=1), EYE)

    # Red bill with a pale nail at the tip
    bill = [HEAD + Vector((0, -0.045, -0.006)), HEAD + Vector((0, -0.07, -0.013)), HEAD + Vector((0, -0.088, -0.02))]
    mb.add(nh.tube(bill, [0.017, 0.012, 0.007], sides=6, scale_xy=(1.0, 0.7)), BILL)
    mb.add(nh.ellipsoid(HEAD + Vector((0, -0.09, -0.02)), (0.008, 0.006, 0.005), subdivisions=1), NAIL)

    return mb.to_object("MandarinDuck", roughness=0.55)


if __name__ == "__main__":
    nh.run(build, "MandarinDuck", ground=(0.22, 0.42, 0.50), views=((40, 25), (-90, 5), (25, 65)))
