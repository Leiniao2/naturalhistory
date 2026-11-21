"""
Procedural Mitrocystites mitra (Middle Ordovician mitrate stylophoran, Bohemia) for map
colonies (Fixed style).

One of the strangest echinoderms: no five-fold symmetry at all. A flattened, mitre-shaped
body (theca) a few centimetres long, flat underneath and gently domed on top, armoured with
large plates, bearing a single jointed appendage, the aulacophore, at its front: a stout,
ringed base, then a short stiff piece and a long tapering arm with a groove roofed by
little cover plates, used to gather food (some even argue the animal was an early
chordate relative). It lay on the soft sea floor with its arm curving down to the mud.
Pale ochre with darker sutures. Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/mitrocystites_mitra.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MitrocystitesMitra.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "MitrocystitesMitra"
PLATE = (0.82, 0.68, 0.44)
PLATE_DARK = (0.62, 0.48, 0.28)
SUTURE = (0.34, 0.24, 0.14)
ARM = (0.74, 0.60, 0.38)
ARM_DARK = (0.46, 0.34, 0.20)


def half_w(y):
    """Theca outline: narrow at the front (-Y), widest at the back, back edge with two
    short rounded points."""
    t = (y + 0.45) / 0.80            # 0 front .. 1 back
    if t < 0 or t > 1:
        return 0.0
    w = 0.16 + 0.22 * math.sin(min(1.0, t * 1.1) * math.pi / 2)
    w *= max(0.0, 1 - max(0.0, (t - 0.88) / 0.12) ** 2) ** 0.5
    return max(0.02, w)


def theca():
    bm = bmesh.new()
    ys = [-0.45 + 0.80 * i / 40 for i in range(41)]
    cols = 24
    top, bl, br = [], [], []
    for y in ys:
        w = half_w(y)
        row = []
        for j in range(cols + 1):
            u = -1 + 2 * j / cols
            x = u * w
            t = (y + 0.45) / 0.8
            h = 0.06 + 0.16 * (1 - u * u) ** 0.6 * math.sin(max(0.05, min(1.0, t * 1.05)) * math.pi) ** 0.5
            row.append(bm.verts.new((x, y, h)))
        top.append(row)
        bl.append(bm.verts.new((-w, y, 0.03)))
        br.append(bm.verts.new((w, y, 0.03)))
    for i in range(len(ys) - 1):
        for j in range(cols):
            bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
        bm.faces.new([bl[i], bl[i + 1], br[i + 1], br[i]])
        bm.faces.new([bl[i], top[i][0], top[i + 1][0], bl[i + 1]])
        bm.faces.new([br[i], br[i + 1], top[i + 1][cols], top[i][cols]])
    bm.faces.new([bl[0]] + top[0] + [br[0]])
    bm.faces.new([br[-1]] + list(reversed(top[-1])) + [bl[-1]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def theca_col(co, n):
    # a few big plates: a grid of rows and a median line, plus marginal frame plates
    w = half_w(co.y) or 1e-3
    u = co.x / w
    t = (co.y + 0.45) / 0.8
    c = PLATE
    rows = (0.18, 0.42, 0.66, 0.86)
    for r in rows:
        c = nh.lerp(c, SUTURE, 1 - nh.smoothstep(0.0, 0.015, abs(t - r)))
    c = nh.lerp(c, SUTURE, 1 - nh.smoothstep(0.0, 0.03, abs(u)))
    c = nh.lerp(c, SUTURE, 1 - nh.smoothstep(0.0, 0.03, abs(abs(u) - 0.55)))
    c = nh.lerp(c, PLATE_DARK, 0.5 * nh.smoothstep(0.75, 0.95, abs(u)))
    if n.z < -0.5:
        c = PLATE_DARK
    return c


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.85)
    mb.add(theca(), theca_col)
    # aulacophore: proximal ringed part, stylocone, then the long distal arm curving to the mud
    pts = [Vector((0, -0.40, 0.12)), Vector((0, -0.50, 0.13)), Vector((0, -0.58, 0.13))]
    radii = [0.085, 0.075, 0.06]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        mb.add(nh.tube([a, b], [radii[i], radii[i + 1]], sides=12),
               lambda co, n, a=a: nh.lerp(ARM, ARM_DARK, 0.6 * nh.smoothstep(0.7, 1.0, 0.5 + 0.5 * math.sin((co.y - a.y) * 120))))
    mb.add(nh.tube([Vector((0, -0.58, 0.13)), Vector((0, -0.68, 0.14))], [0.055, 0.04], sides=10), ARM_DARK)
    arm = [Vector((0, -0.68, 0.14)), Vector((0.03, -0.80, 0.12)), Vector((0.07, -0.92, 0.08)),
           Vector((0.10, -1.02, 0.05)), Vector((0.13, -1.10, 0.03))]
    mb.add(nh.tube(arm, [0.035, 0.03, 0.024, 0.016, 0.0], sides=8),
           lambda co, n: nh.lerp(ARM, ARM_DARK, 0.7 * nh.smoothstep(0.75, 1.0, 0.5 + 0.5 * math.sin(co.y * 160))))
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
