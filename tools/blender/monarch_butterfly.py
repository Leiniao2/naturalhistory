"""
Procedural monarch butterfly (Danaus plexippus) for map swarms.

Mid-flap, wings open in a shallow V. Each wing is a stack of concentric thin
slabs so the pattern stays crisp on both sides without a dense grid: a black
base, the bright orange field inset from it, bold black veins radiating from
the root, then the two rows of small white spots in the black border and the
orange spots near the forewing tip. Black body with white dots, clubbed
antennae, legs tucked under the thorax.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/monarch_butterfly.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MonarchButterfly.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

ORANGE = (0.98, 0.42, 0.04)
ORANGE_DEEP = (0.88, 0.30, 0.02)
BLACK = (0.035, 0.03, 0.03)
WHITE = (0.96, 0.95, 0.92)
BODY = (0.04, 0.035, 0.035)
EYE = (0.12, 0.11, 0.10)

# Slab thicknesses: each layer is a little thicker than the one below so it shows on both sides
T_BASE, T_ORANGE, T_VEIN, T_SPOT = 0.004, 0.0055, 0.007, 0.0085

# Right-wing outlines in wing space: x outward, y toward the tail (-y = forward)
FOREWING = [(0.030, -0.070), (0.110, -0.150), (0.230, -0.240), (0.360, -0.315), (0.480, -0.360),
            (0.545, -0.360), (0.575, -0.320), (0.565, -0.250), (0.535, -0.170), (0.495, -0.095),
            (0.445, -0.030), (0.385, 0.025), (0.300, 0.060), (0.190, 0.060), (0.090, 0.035),
            (0.035, 0.005)]
FORE_OUTER = (4, 12)           # outline indices of the outer margin (apex -> tornus)
FORE_ANCHOR = (0.07, -0.03)    # orange field is the outline pulled toward this point
FORE_INSET = 0.80

HINDWING = [(0.030, 0.000), (0.120, -0.025), (0.240, -0.020), (0.335, 0.025), (0.395, 0.095),
            (0.415, 0.175), (0.385, 0.255), (0.310, 0.315), (0.205, 0.345), (0.110, 0.320),
            (0.055, 0.250), (0.030, 0.130)]
HIND_OUTER = (3, 10)
HIND_ANCHOR = (0.07, 0.09)
HIND_INSET = 0.80


def v2(p):
    return Vector((p[0], p[1]))


def inset(outline, anchor, k):
    a = v2(anchor)
    return [tuple(a + (v2(p) - a) * k) for p in outline]


def resample(points, n):
    """n points evenly spaced along an open polyline."""
    pts = [v2(p) for p in points]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    out = []
    for k in range(n):
        d = total * (k + 0.5) / n
        for i, s in enumerate(seg):
            if d <= s or i == len(seg) - 1:
                t = min(d / s, 1.0) if s > 0 else 0.0
                out.append(pts[i].lerp(pts[i + 1], t))
                break
            d -= s
    return out


def slab(outline2d, thickness):
    return nh.flat_panel([(p[0], p[1], 0.0) for p in outline2d], thickness)


def disc(center, r, thickness, sides=7):
    return slab([(center[0] + math.cos(a) * r, center[1] + math.sin(a) * r)
                 for a in (i / sides * math.tau for i in range(sides))], thickness)


def ribbon(points, w0, w1, thickness):
    """Tapered flat strip along a 2D polyline (a wing vein)."""
    pts = [v2(p) for p in points]
    left, right = [], []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        w = w0 + (w1 - w0) * i / (len(pts) - 1)
        left.append(p + nrm * w)
        right.append(p - nrm * w)
    return slab([tuple(p) for p in left + right[::-1]], thickness)


def curve(a, b, bend, n=6):
    """Points from a to b bowed sideways by `bend` (fraction of the length)."""
    a, b = v2(a), v2(b)
    d = b - a
    nrm = Vector((-d.y, d.x))
    return [tuple(a + d * t + nrm * (bend * 4 * t * (1 - t))) for t in (i / (n - 1) for i in range(n))]


def build_wing(outline, outer, anchor, k, cell_end, veins, apex_spots=()):
    """Returns [(bmesh, colour)] for one right wing, in wing space.
    veins: (outline index, edge, t) - each vein runs from point t along the discal cell's
    front ('f') or back ('b') edge out to that margin point, like the real wing venation."""
    parts = [(slab(outline, T_BASE), BLACK)]
    field = inset(outline, anchor, k)
    parts.append((slab(field, T_ORANGE), lambda co, n: nh.lerp(ORANGE, ORANGE_DEEP,
                                                               max(0.0, 1.0 - co.length / 0.25))))
    root = v2(anchor) * 0.6 + v2(outline[0]) * 0.4
    cell = {"f": curve(root, cell_end, 0.10, 8), "b": curve(root, cell_end, -0.10, 8)}
    for edge in cell.values():
        parts.append((ribbon(edge, 0.0085, 0.0065, T_VEIN), BLACK))
    for idx, edge, t in veins:
        pts = cell[edge]
        base = v2(pts[min(int(t * (len(pts) - 1)), len(pts) - 1)])
        tip = v2(outline[idx])
        parts.append((ribbon(curve(base, tip, 0.02 if edge == "f" else -0.02), 0.0070, 0.0042, T_VEIN), BLACK))
    # white spots: two rows in the black border along the outer margin
    lo, hi = outer
    margin = outline[lo:hi + 1]
    margin_in = field[lo:hi + 1]
    for t, r, n in ((0.32, 0.0085, 16), (0.66, 0.0115, 12)):
        a = resample(margin, n)
        b = resample(margin_in, n)
        for pa, pb in zip(a, b):
            parts.append((disc(tuple(pa.lerp(pb, t)), r, T_SPOT), WHITE))
    for c, r, col in apex_spots:
        parts.append((disc(c, r, T_SPOT), col))
    return parts


def place(parts, mb, mirror, lift_deg, hinge, sweep_deg=0.0):
    """Moves wing-space parts onto the body: sweep about Z, raise about Y, mirror for the left wing."""
    m = (Matrix.Translation(Vector((hinge[0], hinge[1], hinge[2])))
         @ Matrix.Rotation(math.radians(-lift_deg), 4, "Y")
         @ Matrix.Rotation(math.radians(sweep_deg), 4, "Z"))
    if mirror:
        m = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ m
    for bm, col in parts:
        nh.transform(bm, m)
        if mirror:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        mb.add(bm, col)


def build_body(mb):
    mb.add(nh.uv_ellipsoid((0, -0.085, 0.005), (0.032, 0.030, 0.030), 14, 10), BODY)
    for x in (-0.022, 0.022):
        mb.add(nh.uv_ellipsoid((x, -0.098, 0.008), (0.016, 0.016, 0.018), 10, 8), EYE)
    mb.add(nh.uv_ellipsoid((0, -0.020, 0.008), (0.040, 0.065, 0.040), 16, 12), BODY)
    mb.add(nh.tube([(0, 0.030, 0.004), (0, 0.090, -0.004), (0, 0.160, -0.012), (0, 0.215, -0.020),
                    (0, 0.245, -0.024)], [0.034, 0.032, 0.026, 0.016, 0.0], sides=12), BODY)
    # white dots on head and thorax
    for p in ((0.012, -0.108, 0.022), (-0.012, -0.108, 0.022), (0.026, -0.075, 0.020),
              (-0.026, -0.075, 0.020), (0.036, -0.030, 0.012), (-0.036, -0.030, 0.012),
              (0.030, 0.005, 0.020), (-0.030, 0.005, 0.020), (0.0, -0.110, -0.012)):
        mb.add(nh.uv_ellipsoid(p, (0.0055, 0.0055, 0.0055), 6, 4), WHITE)
    # clubbed antennae
    for s in (-1, 1):
        pts = [(s * 0.010, -0.108, 0.022), (s * 0.040, -0.190, 0.060), (s * 0.072, -0.275, 0.098)]
        mb.add(nh.tube(pts, [0.0035, 0.003, 0.003], sides=5), BODY)
        mb.add(nh.uv_ellipsoid((s * 0.076, -0.285, 0.103), (0.008, 0.016, 0.008), 8, 6), BODY)
    # legs tucked under the thorax
    for s in (-1, 1):
        for y in (-0.050, -0.020, 0.012):
            pts = [(s * 0.018, y, -0.022), (s * 0.050, y - 0.004, -0.060), (s * 0.058, y + 0.040, -0.098)]
            mb.add(nh.tube(pts, [0.0045, 0.0035, 0.002], sides=4), BODY)
    # coiled proboscis
    mb.add(nh.tube([(0, -0.112, -0.012), (0, -0.122, -0.030), (0, -0.112, -0.040), (0, -0.104, -0.032)],
                   [0.003, 0.003, 0.003, 0.002], sides=4), BODY)


def build():
    mb = nh.MeshBuilder()
    build_body(mb)
    fore_veins = [(2, "f", 0.45), (3, "f", 0.75), (4, "f", 1.0), (5, "f", 1.0), (7, "b", 1.0),
                  (9, "b", 1.0), (10, "b", 0.7), (12, "b", 0.4), (13, "b", 0.15)]
    hind_veins = [(2, "f", 0.35), (3, "f", 0.7), (4, "f", 1.0), (5, "f", 1.0), (6, "b", 1.0),
                  (7, "b", 1.0), (8, "b", 0.75), (9, "b", 0.45), (10, "b", 0.2)]
    apex = [((0.468, -0.312), 0.015, ORANGE), ((0.505, -0.285), 0.013, ORANGE),
            ((0.532, -0.248), 0.012, ORANGE), ((0.432, -0.312), 0.010, ORANGE),
            ((0.500, -0.212), 0.009, WHITE)]
    for mirror in (False, True):
        place(build_wing(FOREWING, FORE_OUTER, FORE_ANCHOR, FORE_INSET, (0.30, -0.13), fore_veins, apex),
              mb, mirror, lift_deg=22, hinge=(0.025, -0.025, 0.020), sweep_deg=-4)
        place(build_wing(HINDWING, HIND_OUTER, HIND_ANCHOR, HIND_INSET, (0.21, 0.13), hind_veins),
              mb, mirror, lift_deg=16, hinge=(0.025, 0.005, 0.010), sweep_deg=2)
    return mb.to_object("MonarchButterfly", roughness=0.5)


if __name__ == "__main__":
    nh.run(build, "MonarchButterfly", views=((35, 30), (0, 75), (-90, 10)))
