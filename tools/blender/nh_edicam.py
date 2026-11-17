"""
Shared helpers for the Ediacaran / Cambrian batch (tag "edicam") in tools/blender/.

Small building blocks reused by the per-species scripts (pteridinium_simplex.py,
marrella_splendens.py, ...):

  * mirror(bm, side)            reflect a shell across X for the left side
  * centre(obj) / ground(obj)   pivot at the bounding-box centre (Swim/Drift) or on z = 0 (Fixed)
  * segmented_trunk(...)        flattened, pinched-per-segment tube along Y
  * paddle(...)                 rounded flap outline (swimming flaps, gill blades, tail fans)
  * spike(...)                  tapered cone between two points
  * jointed_leg(...)            thin multi-segment arthropod/lobopod limb
  * frond_disc(...)             holdfast disc for sessile fronds
  * banded(...)                 colour function: light/dark bands along Y, paler underside
  * export(build, name, ...)    nh_model.run() with the batch's default seawater preview

All animals face -Y, Z up, colour in vertex colours (see nh_model.py).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SEA = (0.05, 0.22, 0.30)
SEABED = (0.55, 0.50, 0.40)


def mirror(bm, side):
    if side < 0:
        nh.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def centre(obj):
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


def ground(obj):
    """Pivot on the seabed: lowest vertex at z = 0, centred in X/Y."""
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    zmin = min(c.z for c in corners)
    obj.data.transform(Matrix.Translation((-mid.x, -mid.y, -zmin)))
    return obj


def segmented_trunk(y0, y1, segments, width_fn, z_fn=lambda y: 0.0, flat=0.5, sides=10,
                    pinch=0.88, tip=0.0):
    """Tube along +Y from y0 to y1; two rings per segment, the seam rings pinched.
    width_fn(t) gives the half-width for t in 0..1; flat scales the vertical radius."""
    pts, radii = [], []
    n = segments * 2
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        r = width_fn(t) * (pinch if i % 2 == 0 else 1.0)
        pts.append((0.0, y, z_fn(y)))
        radii.append(r)
    radii[0] = max(radii[0] * 0.6, 1e-4)
    radii[-1] = tip
    return nh.tube(pts, radii, sides=sides, scale_xy=(1.0, flat))


def paddle(length, width, n=10, taper=0.4, thickness=0.008, comb=0):
    """Rounded paddle in the XY plane from x = 0 (root) to x = length.
    taper: root width fraction; comb > 0 adds that many teeth along the rear (+Y) edge."""
    pts = []
    for i in range(n):
        a = i / n * math.tau
        u = math.cos(a) * 0.5 + 0.5
        w = math.sin(a) * width * (taper + (1 - taper) * u)
        if comb and math.sin(a) > 0:
            w *= 0.75 + 0.25 * (1 if (i % 2) else -1)
        pts.append((u * length, w, 0.0))
    return nh.flat_panel(pts, thickness=thickness)


def spike(base, tip, r=0.01, sides=5, mid=None):
    base, tip = Vector(base), Vector(tip)
    if mid is None:
        return nh.tube([base, base.lerp(tip, 0.5), tip], [r, r * 0.6, 0.0], sides=sides)
    return nh.tube([base, Vector(mid), tip], [r, r * 0.6, 0.0], sides=sides)


def jointed_leg(points, r0=0.012, r1=0.005, sides=5):
    n = len(points) - 1
    radii = [r0 + (r1 - r0) * i / n for i in range(n + 1)]
    return nh.tube([Vector(p) for p in points], radii, sides=sides)


def frond_disc(radius, height, rings=3, segments=20):
    """Low domed holdfast disc with concentric ridges, base at z = 0."""
    def deform(n):
        rr = math.hypot(n.x, n.y)
        return 1.0 + 0.06 * math.cos(rr * rings * math.pi)
    bm = nh.uv_ellipsoid((0, 0, 0), (radius, radius, height), segments=segments, rings=8, deform=deform)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.1
    return bm


def banded(light, dark, belly, y0, seg_len, amount=0.75, sharp=0.3):
    def color(co, n):
        t = ((co.y - y0) / seg_len) % 1.0
        band = 1.0 - nh.smoothstep(0.0, sharp, min(t, 1.0 - t))
        c = nh.lerp(light, dark, band * amount)
        return nh.lerp(belly, c, nh.smoothstep(-0.6, 0.1, n.z))
    return color


def export(build, name, fixed=False, views=None):
    bg = SEA
    if views is None:
        views = ((35, 28), (-90, 8), (0, 80)) if not fixed else ((35, 25), (-90, 6))
    if fixed:
        nh.run(build, name, background=bg, ground=SEABED, views=views)
    else:
        nh.run(build, name, background=bg, views=views)


def plate(y, half_w, half_len, height, z=0.0, segments=14, rings=7, bulge=1.6, edge_droop=0.5):
    """Flattened, dome-topped tergite / shield plate centred at (0, y, z): flat-ish
    underside, sides drooping a little (edge_droop) like an arthropod's pleurae."""
    def deform(n):
        return 1.0
    bm = nh.uv_ellipsoid((0, 0, 0), (half_w, half_len, height), segments=segments, rings=rings)
    for v in bm.verts:
        x = v.co.x / half_w if half_w else 0
        if v.co.z < 0:
            v.co.z *= 0.35
        v.co.z -= height * edge_droop * x * x
    nh.transform(bm, Matrix.Translation((0, y, z)))
    return bm


def plated_body(mb, plates, color_fn):
    """plates: list of (y, half_w, half_len, height[, z]). Each plate gets color_fn(index)."""
    for i, p in enumerate(plates):
        y, w, l, h = p[:4]
        z = p[4] if len(p) > 4 else 0.0
        c = color_fn(i)
        mb.add(plate(y, w, l, h, z), c)
