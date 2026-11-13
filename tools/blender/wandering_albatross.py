"""
Procedural low-poly wandering albatross (Diomedea exulans) in a gliding pose.

Very long, narrow wings (span ~3x body length) with a slight dihedral and a
gentle backward bend at the wrist; white body and head, white upper wing with
black flight feathers (trailing edge and tips), white underwing with dark tips,
a big pink hooked bill, short white tail, pale pink feet tucked under it.
Shown soaring above ocean tiles, so the top view is the one that matters.

Usage:
  blender --background --python tools/blender/wandering_albatross.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WanderingAlbatross.fbx
Faces -Y, pivot at the body centre (flier). Body ~1.2 long, wingspan ~3.2.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

WHITE = (0.95, 0.95, 0.93)
WHITE_SHADE = (0.80, 0.81, 0.82)  # soft grey on the belly and wing roots
BLACK = (0.05, 0.05, 0.06)
GREY = (0.45, 0.46, 0.48)
BILL = (0.95, 0.58, 0.55)
BILL_TIP = (0.98, 0.82, 0.60)
FEET = (0.88, 0.70, 0.72)
EYE = (0.03, 0.03, 0.04)

HALF_SPAN = 1.75
WING_STATIONS = 16
# chord positions (0 = leading edge, 1 = trailing edge) for the top and bottom surface
CHORD = (0.0, 0.12, 0.35, 0.6, 0.78, 0.9, 1.0)


def interp(keys, t):
    """Piecewise-smooth interpolation through (t, value) keyframes."""
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            s = nh.smoothstep(t0, t1, t) if t1 > t0 else 1.0
            return v0 + (v1 - v0) * s
    return keys[-1][1]


# Planform, in units of span fraction t (0 = root inside the body, 1 = tip).
# Wrist at ~0.45: leading edge pushes forward there, then sweeps back to the tip.
LEADING = [(0.0, -0.10), (0.45, -0.17), (0.8, -0.08), (1.0, 0.06)]
CHORD_LEN = [(0.0, 0.30), (0.45, 0.24), (0.8, 0.15), (1.0, 0.02)]
DIHEDRAL = [(0.0, 0.0), (0.45, 0.07), (0.8, 0.07), (1.0, 0.05)]
THICKNESS = [(0.0, 0.07), (0.45, 0.035), (1.0, 0.006)]


def airfoil(c):
    """0..1 thickness profile along the chord: blunt nose, thin trailing edge."""
    return min(1.0, 2.6 * math.sqrt(c) * (1.0 - c) ** 1.2)


def wing_color(t, c, top):
    if top:
        # black primaries toward the tip, black secondaries along the trailing edge
        tip = nh.smoothstep(0.55, 0.75, t)
        trailing = nh.smoothstep(0.62, 0.8, c) * (0.85 + 0.15 * t)
        inner_grey = nh.smoothstep(0.15, 0.5, t) * (1 - tip) * 0.25  # faint speckling on the coverts
        col = nh.lerp(WHITE, GREY, inner_grey)
        return nh.lerp(col, BLACK, max(tip, trailing))
    tip = nh.smoothstep(0.8, 0.95, t)
    trailing = nh.smoothstep(0.88, 1.0, c) * nh.smoothstep(0.2, 0.6, t)
    col = nh.lerp(WHITE, WHITE_SHADE, (1 - t) * 0.3)
    return nh.lerp(col, BLACK, max(tip, trailing * 0.8))


def make_wing(side):
    """One wing as a lofted airfoil; side = +1 (right, +X) or -1 (left)."""
    bm = bmesh.new()
    colors = {}
    rings = []
    for i in range(WING_STATIONS + 1):
        t = i / WING_STATIONS
        t = t ** 0.9  # a little denser toward the root
        x = 0.06 + t * (HALF_SPAN - 0.06)
        le = interp(LEADING, t)
        ch = interp(CHORD_LEN, t)
        z0 = interp(DIHEDRAL, t)
        th = interp(THICKNESS, t)
        ring = []
        if i == WING_STATIONS:
            v = bm.verts.new(Vector((side * x, le + ch * 0.5, z0)))
            colors[v] = wing_color(t, 0.5, True)
            rings.append([v])
            continue
        top = [(c, z0 + th * airfoil(c)) for c in CHORD]
        bottom = [(c, z0 - th * 0.35 * airfoil(c)) for c in reversed(CHORD[1:-1])]
        for k, (c, z) in enumerate(top + bottom):
            v = bm.verts.new(Vector((side * x, le + ch * c, z)))
            colors[v] = wing_color(t, c, k < len(top))
            ring.append(v)
        rings.append(ring)

    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            if len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    lookup = {tuple(round(c, 5) for c in v.co): col for v, col in colors.items()}
    return bm, (lambda co, nrm: lookup.get(tuple(round(c, 5) for c in co), WHITE))


def body_color(co, n):
    # white, with a soft grey shade on the underside
    return nh.lerp(WHITE, WHITE_SHADE, nh.smoothstep(0.2, -0.9, n.z) * 0.6)


def build():
    mb = nh.MeshBuilder()

    # Body: a stout torpedo, deepest just behind the wings, tapering to the tail
    body_y = [-0.34, -0.24, -0.1, 0.05, 0.2, 0.33, 0.44]
    body_r = [0.07, 0.115, 0.135, 0.135, 0.115, 0.08, 0.04]
    mb.add(nh.tube([(0, y, 0.0) for y in body_y], body_r, sides=12, scale_xy=(1.0, 0.92)), body_color)

    # Neck flowing into a big rounded head
    head_pts = [(0, -0.18, -0.01), (0, -0.30, 0.0), (0, -0.40, 0.03), (0, -0.48, 0.06), (0, -0.54, 0.07), (0, -0.585, 0.062), (0, -0.605, 0.05)]
    head_r = [0.1, 0.095, 0.085, 0.082, 0.075, 0.055, 0.0]
    mb.add(nh.tube(head_pts, head_r, sides=12, scale_xy=(0.92, 1.0)), body_color)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.062, -0.54, 0.09), (0.012, 0.014, 0.012), subdivisions=1), EYE)

    # Big pink bill with a hooked yellowish tip
    bill_pts = [(0, -0.575, 0.052), (0, -0.65, 0.042), (0, -0.72, 0.032), (0, -0.765, 0.026), (0, -0.79, -0.004)]
    bill_r = [0.042, 0.03, 0.024, 0.02, 0.0]
    tip_y = bill_pts[-2][1]

    def bill_color(co, n):
        return nh.lerp(BILL, BILL_TIP, nh.smoothstep(-0.70, tip_y, co.y) if co.y < -0.70 else 0.0)

    mb.add(nh.tube(bill_pts, bill_r, sides=6, scale_xy=(0.75, 1.0)), bill_color)

    # Short, slightly wedge-shaped tail
    tail = [(-0.04, 0.38, 0.01), (0.04, 0.38, 0.01), (0.068, 0.55, 0.0), (0.0, 0.575, 0.0), (-0.068, 0.55, 0.0)]

    def tail_color(co, n):
        return nh.lerp(WHITE, GREY, nh.smoothstep(0.50, 0.575, co.y) * 0.6)

    mb.add(nh.flat_panel(tail, thickness=0.015), tail_color, smooth=False)

    # Feet tucked back under the tail
    for sx in (-1, 1):
        mb.add(nh.tube([(sx * 0.04, 0.28, -0.08), (sx * 0.045, 0.42, -0.06), (sx * 0.05, 0.52, -0.045)],
                       [0.02, 0.022, 0.0], sides=5), FEET)

    for side in (1, -1):
        mb.add(*make_wing(side))

    return mb.to_object("WanderingAlbatross", roughness=0.7)


if __name__ == "__main__":
    nh.run(build, "WanderingAlbatross", views=((35, 25), (20, 70), (180, -35)))
