"""
Procedural low-poly Redlichia (Cambrian redlichiid trilobite) for map colonies.

A lofted, three-lobed dorsal shell: a broad crescent cephalon with a raised
glabella, crescent eyes and long genal spines sweeping back; a tapering thorax
of many segments, each ending in a pointed pleural spine; a tiny pygidium; and
a pair of short antennae. Brownish-ochre with darker segment grooves.
Faces -Y, pivot at the body centre (Swim style), seen mostly from above.

Usage:
  blender --background --python tools/blender/redlichia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Redlichia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

SHELL = (0.58, 0.40, 0.20)      # ochre-brown
SHELL_LIGHT = (0.80, 0.62, 0.36)
AXIS = (0.42, 0.24, 0.12)       # axial lobe, darker and redder than the pleurae
GROOVE = (0.24, 0.14, 0.07)
EYE = (0.12, 0.10, 0.09)
UNDER = (0.42, 0.30, 0.18)

# Lengthwise layout along Y (front = -Y)
Y_FRONT = -0.62
Y_CEPH = -0.24      # cephalon / thorax boundary
Y_PYG = 0.50        # thorax / pygidium boundary
Y_BACK = 0.58
SEGMENTS = 15       # thoracic segments
COLS = 16           # across the shell (even, so the midline is a vertex column)


def half_width(y):
    if y < Y_CEPH:
        # crescent cephalon: rounded front, widest at the back
        t = (y - Y_CEPH) / (Y_FRONT - Y_CEPH)  # 0 at boundary, 1 at front tip
        return max(0.012, 0.40 * math.sqrt(max(0.0, 1.0 - t ** 2.2)))
    if y < Y_PYG:
        t = (y - Y_CEPH) / (Y_PYG - Y_CEPH)
        return 0.07 + 0.27 * (1.0 - t ** 1.9)  # near-parallel sides, tapering toward the tail
    t = (y - Y_PYG) / (Y_BACK - Y_PYG)
    return max(0.012, 0.07 * math.sqrt(max(0.0, 1.0 - t ** 2)))


def segment_phase(y):
    """0..1 position inside the current thoracic segment (None outside the thorax)."""
    if not (Y_CEPH <= y < Y_PYG):
        return None
    f = (y - Y_CEPH) / (Y_PYG - Y_CEPH) * SEGMENTS
    return f - math.floor(f)


def groove(y):
    """1 in the furrow between segments (and at the cephalon's back edge), 0 elsewhere."""
    p = segment_phase(y)
    if p is None:
        return math.exp(-((y - Y_PYG) / 0.012) ** 2)
    d = min(p, 1.0 - p)
    return math.exp(-(d / 0.11) ** 2)


def axis_width(y):
    if y < Y_CEPH:
        # glabella: tapers forward, stops short of the front border
        t = (y - Y_CEPH) / (Y_FRONT - Y_CEPH)
        return 0.11 * (1.0 - 0.55 * t) if t < 0.8 else 0.0
    return 0.085 * (half_width(y) / 0.31) ** 0.6 + 0.02


EYES = [(sx * 0.215, -0.40) for sx in (-1, 1)]


def height(x, y):
    w = half_width(y)
    u = min(1.0, abs(x) / w)
    h = 0.07 * (1.0 - u ** 2) ** 0.7                       # overall dome
    aw = axis_width(y)
    if aw > 0:
        h += 0.075 * math.exp(-(x / aw) ** 4)              # raised axial lobe / glabella
    if y < Y_CEPH:
        # flat border rim around the cephalon edge, eye lobes
        h += 0.012 * nh.smoothstep(0.82, 0.95, u)
        for ex, ey in EYES:
            d = math.hypot((x - ex) / 0.06, (y - ey) / 0.11)
            h += 0.025 * math.exp(-d ** 2)
    h -= 0.012 * groove(y) * (1.0 - 0.5 * u)               # segment furrows
    if aw > 0:
        # axial furrows: shallow troughs either side of the axis
        h -= 0.018 * math.exp(-((abs(x) - aw * 1.15) / 0.022) ** 2)
    return h


def shell_color(co, n):
    x, y = co.x, co.y
    w = half_width(y)
    u = min(1.0, abs(x) / max(w, 1e-3))
    c = nh.lerp(SHELL_LIGHT, SHELL, nh.smoothstep(0.0, 0.8, u))
    aw = axis_width(y)
    if aw > 0:
        c = nh.lerp(c, AXIS, math.exp(-(x / aw) ** 4))
        c = nh.lerp(c, GROOVE, 0.6 * math.exp(-((abs(x) - aw * 1.15) / 0.022) ** 2))  # axial furrows
    if y < Y_CEPH:
        c = nh.lerp(c, SHELL_LIGHT, nh.smoothstep(0.85, 0.97, u) * 0.7)
    c = nh.lerp(c, GROOVE, groove(y) * 0.7)
    if n.z < -0.3:
        c = UNDER
    return c


def rows():
    ys = []
    # cephalon: denser toward the rounded front
    for i in range(14):
        t = i / 14
        ys.append(Y_FRONT + (Y_CEPH - Y_FRONT) * (1 - math.cos(t * math.pi / 2)) ** 0.8)
    # thorax: 4 rows per segment so every furrow is captured
    seg = (Y_PYG - Y_CEPH) / SEGMENTS
    for s in range(SEGMENTS):
        for k in (0.0, 0.25, 0.5, 0.75):
            ys.append(Y_CEPH + seg * (s + k))
    for i in range(5):
        ys.append(Y_PYG + (Y_BACK - Y_PYG) * i / 4)
    return ys


def shell():
    """Lofted top surface + flat underside, joined around the outline."""
    bm = bmesh.new()
    ys = rows()
    top, bl, br = [], [], []
    for y in ys:
        w = half_width(y)
        row = []
        for j in range(COLS + 1):
            uu = -1.0 + 2.0 * j / COLS
            # cluster columns toward the edge so the rim and spines read crisply
            x = math.copysign(abs(uu) ** 0.85, uu) * w
            row.append(bm.verts.new((x, y, height(x, y))))
        top.append(row)
        bl.append(bm.verts.new((-w, y, -0.02)))
        br.append(bm.verts.new((w, y, -0.02)))
    n = len(ys)
    for i in range(n - 1):
        for j in range(COLS):
            bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
        bm.faces.new([bl[i], bl[i + 1], br[i + 1], br[i]])                   # underside strip
        bm.faces.new([bl[i], top[i][0], top[i + 1][0], bl[i + 1]])           # left wall
        bm.faces.new([br[i], br[i + 1], top[i + 1][COLS], top[i][COLS]])     # right wall
    bm.faces.new([bl[0]] + top[0] + [br[0]])
    bm.faces.new([br[-1]] + list(reversed(top[-1])) + [bl[-1]])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def spine(base, tip, r, bend=0.0):
    """Flattened, pointed spine from base to tip, with an optional sideways bow."""
    b, t = Vector(base), Vector(tip)
    mid = (b + t) / 2 + Vector((bend, 0, 0))
    pts = [b, b.lerp(mid, 0.6), mid, mid.lerp(t, 0.6), t]
    return nh.tube(pts, [r, r * 0.8, r * 0.6, r * 0.3, 0.0], sides=5, scale_xy=(1.0, 0.45))


def build():
    mb = nh.MeshBuilder()
    mb.add(shell(), shell_color)

    for sx in (-1, 1):
        # genal spines sweep back from the cephalon's rear corners past mid-thorax
        w = half_width(Y_CEPH - 0.01)
        mb.add(spine((sx * (w - 0.03), Y_CEPH - 0.04, 0.01),
                     (sx * (w + 0.04), Y_CEPH + 0.58, -0.005), 0.034, bend=sx * 0.05), SHELL)
        # pleural spines: one per thoracic segment, pointing back and out
        seg = (Y_PYG - Y_CEPH) / SEGMENTS
        for s in range(SEGMENTS):
            y = Y_CEPH + seg * (s + 0.5)
            w = half_width(y)
            length = 0.09 + 0.07 * (s / SEGMENTS)  # rear spines longer, sweeping back
            mb.add(spine((sx * (w - 0.02), y - seg * 0.35, 0.004),
                         (sx * (w + length * 0.35), y + length, -0.006), 0.019, bend=sx * 0.01), SHELL)
        # crescent eyes: a dark arc on each eye lobe
        ex, ey = EYES[0 if sx < 0 else 1]
        arc = []
        for k in range(7):
            a = math.radians(-70 + 140 * k / 6)
            x = ex + sx * 0.035 * math.cos(a)
            y = ey + 0.07 * math.sin(a)
            arc.append((x, y, height(x, y) + 0.008))
        mb.add(nh.tube(arc, [0.006, 0.011, 0.013, 0.013, 0.013, 0.011, 0.006], sides=5), EYE)
        # short antennae curving forward and out from under the front
        mb.add(nh.tube([(sx * 0.05, Y_FRONT + 0.04, -0.01), (sx * 0.10, Y_FRONT - 0.07, -0.005),
                        (sx * 0.17, Y_FRONT - 0.16, 0.0), (sx * 0.24, Y_FRONT - 0.21, 0.0)],
                       [0.01, 0.008, 0.006, 0.0], sides=4), GROOVE)

    # tiny pygidial spine pair
    for sx in (-1, 1):
        mb.add(spine((sx * 0.03, Y_BACK - 0.03, 0.0), (sx * 0.06, Y_BACK + 0.07, -0.005), 0.012), SHELL)

    obj = mb.to_object("Redlichia", roughness=0.55)
    # pivot at the body centre: centre the shell's thickness on z = 0
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Redlichia", views=((30, 40), (0, 85), (-90, 12)))
