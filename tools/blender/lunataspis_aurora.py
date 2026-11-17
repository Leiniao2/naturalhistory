"""
Procedural Lunataspis aurora (Late Ordovician, about 445 million years ago, the oldest
known horseshoe crab, from shallow-marine Konservat-Lagerstaetten in Manitoba, Canada;
about 4 cm long) for map colonies (Swim style).

A large crescent-shaped (lunate) prosomal shield with a low central cardiac lobe
flanked by weak ophthalmic ridges carrying small compound eyes; a shorter opisthosoma
of separate, freely movable segments with short lateral spines (unlike the fused
abdomen of living horseshoe crabs); and a long, keeled, lance-shaped telson. Walking
legs peek out under the shield. Olive-brown (colour conjectural).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/lunataspis_aurora.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LunataspisAurora.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402

SHELL = (0.40, 0.36, 0.22)
SHELL_LIGHT = (0.60, 0.55, 0.36)
DARK = (0.20, 0.17, 0.10)
UNDER = (0.55, 0.48, 0.32)
EYE = (0.06, 0.05, 0.04)

Y_FRONT, Y_PRO, Y_OP = -0.62, 0.0, 0.34
R = 0.62   # prosoma radius


def pro_half_width(y):
    """Crescent: a semicircle in front, its back edge cut by a shallow concave arc."""
    t = (y - Y_FRONT) / (Y_PRO + 0.18 - Y_FRONT)
    return max(0.02, R * math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2)))


def back_edge(x):
    """y of the shield's concave back margin at x (genal horns reach back at the sides)."""
    u = abs(x) / R
    return Y_PRO - 0.04 + 0.12 * u ** 2.5


def pro_height(x, y):
    w = pro_half_width(y)
    u = min(1.0, abs(x) / max(w, 1e-3))
    h = 0.09 * (1 - u ** 2) ** 0.8
    h += 0.035 * math.exp(-(x / 0.10) ** 4) * nh.smoothstep(-0.5, -0.2, y)     # cardiac lobe
    for sx in (-1, 1):
        h += 0.015 * math.exp(-((x - sx * 0.25) / 0.03) ** 2) * nh.smoothstep(-0.5, -0.25, y)  # ophthalmic ridges
    return h


def prosoma():
    bm = bmesh.new()
    cols = 28
    rows = 26
    grid = []
    for i in range(rows + 1):
        v = i / rows
        row = []
        for j in range(cols + 1):
            uu = -1 + 2 * j / cols
            x = uu * R * 0.999
            yb = back_edge(x)
            # front edge from the circle
            yf = Y_FRONT + 0.66 * (1 - math.sqrt(max(0.0, 1 - (x / R) ** 2)))
            y = yf + (yb - yf) * v
            if yb < yf:
                y = yf
            row.append(bm.verts.new((x, y, pro_height(x, y) * (1 - abs(uu) ** 6))))
        grid.append(row)
    for i in range(rows):
        for j in range(cols):
            bm.faces.new([grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]])
    # thin underside: duplicate flat
    bot = [[bm.verts.new((v.co.x, v.co.y, -0.02)) for v in row] for row in grid]
    for i in range(rows):
        for j in range(cols):
            bm.faces.new([bot[i][j + 1], bot[i][j], bot[i + 1][j], bot[i + 1][j + 1]])
    ring_t = [grid[0][j] for j in range(cols + 1)] + [grid[i][cols] for i in range(1, rows + 1)] + \
        [grid[rows][j] for j in range(cols - 1, -1, -1)] + [grid[i][0] for i in range(rows - 1, 0, -1)]
    ring_b = [bot[0][j] for j in range(cols + 1)] + [bot[i][cols] for i in range(1, rows + 1)] + \
        [bot[rows][j] for j in range(cols - 1, -1, -1)] + [bot[i][0] for i in range(rows - 1, 0, -1)]
    for k in range(len(ring_t)):
        a, b = ring_t[k], ring_t[(k + 1) % len(ring_t)]
        c, d = ring_b[(k + 1) % len(ring_b)], ring_b[k]
        if len({a, b, c, d}) == 4:
            try:
                bm.faces.new([a, b, c, d])
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def pro_color(co, n):
    if n.z < -0.3:
        return UNDER
    c = nh.lerp(SHELL_LIGHT, SHELL, nh.smoothstep(0.0, 0.5, abs(co.x)))
    c = nh.lerp(c, DARK, 0.5 * math.exp(-((abs(co.x) - 0.12) / 0.015) ** 2) * nh.smoothstep(-0.5, -0.2, co.y))
    edge = pro_half_width(co.y) - abs(co.x)
    return nh.lerp(c, SHELL_LIGHT, 0.6 * nh.smoothstep(0.05, 0.0, edge))


def build():
    mb = nh.MeshBuilder()
    mb.add(prosoma(), pro_color)
    # opisthosoma: free segments, tapering, short lateral spines
    n = 7
    for i in range(n):
        t = i / n
        y0 = Y_PRO - 0.02 + (Y_OP - Y_PRO) * t
        y1 = Y_PRO + (Y_OP - Y_PRO) * (t + 1 / n) + 0.01
        w = 0.24 * (1 - 0.55 * t)
        mb.add(nh.uv_ellipsoid(((0, (y0 + y1) / 2, 0.02)), (w, (y1 - y0) * 0.6, 0.045 * (1 - 0.3 * t)), 14, 6),
               lambda co, nn: UNDER if nn.z < -0.3 else nh.lerp(SHELL, SHELL_LIGHT, 0.4 * math.exp(-(co.x / 0.06) ** 2)))
        for sx in (-1, 1):
            mb.add(nh.tube([(sx * w * 0.9, (y0 + y1) / 2, 0.01), (sx * (w + 0.06), y1 + 0.03, 0.0)],
                           [0.014, 0.0], sides=4), SHELL)
    # telson: long, keeled, lance-shaped
    mb.add(nh.tube([(0, Y_OP, 0.01), (0, Y_OP + 0.15, 0.015), (0, Y_OP + 0.5, 0.0), (0, Y_OP + 0.72, -0.01)],
                   [0.04, 0.03, 0.015, 0.0], sides=6, scale_xy=(1.0, 0.7)), SHELL)
    # compound eyes on the ophthalmic ridges
    for sx in (-1, 1):
        y = -0.30
        mb.add(nh.ellipsoid((sx * 0.25, y, pro_height(0.25, y) + 0.005), (0.018, 0.035, 0.012), subdivisions=2), EYE)
        # short genal spines at the back corners
        mb.add(nh.tube([(sx * 0.57, 0.02, 0.0), (sx * 0.60, 0.12, -0.005), (sx * 0.61, 0.22, -0.01)],
                       [0.025, 0.015, 0.0], sides=5, scale_xy=(1.0, 0.5)), SHELL)
        # walking-leg tips peeking out at the back corners
        for k in range(3):
            y = -0.15 + 0.08 * k
            x = 0.30 + 0.05 * k
            mb.add(nh.tube([(sx * x, y, -0.02), (sx * (x + 0.1), y + 0.08, -0.04)], [0.015, 0.0], sides=4), UNDER)
    obj = mb.to_object("LunataspisAurora", roughness=0.45)
    vs = obj.data.vertices
    zs, ys = [v.co.z for v in vs], [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "LunataspisAurora", background=(0.05, 0.18, 0.22), views=((30, 40), (0, 85), (-90, 10)))
