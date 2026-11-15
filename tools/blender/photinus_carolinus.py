"""
Procedural synchronous firefly (Photinus carolinus) in flight, lantern lit, for map swarms.

Slim, soft-bodied brownish-black beetle. The broad, flat pronotum shield hides
the head from above: pale yellow around the rim, a rosy-red flush on each side
and a black spot down the middle. In flight the leathery elytra (dark brown with
thin pale yellow edges) are raised up and out like a V, and the smoky,
lightly veined hind wings spread flat beneath them. The abdomen hangs below,
dark grey-brown with pinkish side margins, and ends in the creamy-yellow lantern
segments. The lantern is coloured above 1.0 (like the game's lava) so it stays
bright under the map's shading: Unity sees (1.45, 1.32, 0.50) there.
Small head with big dark eyes and long thread-like antennae, three pairs of
slender legs dangling.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/photinus_carolinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SynchronousFirefly.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

BLACK = (0.05, 0.045, 0.04)
BROWN = (0.15, 0.11, 0.08)        # elytra
BROWN_DARK = (0.08, 0.06, 0.05)
PALE = (0.92, 0.80, 0.42)         # elytral margins
SHIELD_YELLOW = (0.98, 0.84, 0.30)
SHIELD_RED = (0.88, 0.32, 0.26)
ABDOMEN = (0.16, 0.13, 0.12)
ABD_MARGIN = (0.70, 0.42, 0.36)
LANTERN_BASE = (1.0, 0.96, 0.55)  # painted colour, replaced by LANTERN after export prep
LANTERN = (1.45, 1.32, 0.50)      # > 1: stays bright under shading (target value in the FBX)
EYE = (0.10, 0.10, 0.11)
LEG = (0.12, 0.09, 0.07)
MEMBRANE = (0.50, 0.47, 0.45)
VEIN = (0.28, 0.24, 0.20)

PRONOTUM = Vector((0.0, -0.27, 0.03))
HEAD = Vector((0.0, -0.32, -0.005))
ABD_START = Vector((0.0, -0.14, 0.0))
ABD_LEN = 0.60
LANTERN_FROM = 0.66               # fraction of the abdomen length where the lantern segments start


# ---------------------------------------------------------------- body

def pronotum():
    """Flat, rounded shield reaching forward over the head."""
    def shape(n):
        return 1.0 + 0.12 * max(0.0, -n.y)   # a little longer at the front
    bm = nh.uv_ellipsoid(PRONOTUM, (0.14, 0.12, 0.03), segments=24, rings=12, deform=shape)
    for v in bm.verts:
        # squared-off hind edge: a half-disc shield rather than a full one
        v.co.y = min(v.co.y, PRONOTUM.y + 0.06 + 0.03 * (abs(v.co.x) / 0.14) ** 2)
        r = math.hypot((v.co.x - PRONOTUM.x) / 0.14, (v.co.y - PRONOTUM.y) / 0.13)
        if v.co.z > PRONOTUM.z:  # raised centre, flared flat rim
            v.co.z += 0.022 * max(0.0, 1.0 - r) ** 1.5

    def color(co, n):
        d = co - PRONOTUM
        r = math.hypot(d.x / 0.14, d.y / 0.13)
        # rosy-red patches either side of the middle, pale yellow rim
        col = nh.lerp(SHIELD_RED, SHIELD_YELLOW, nh.smoothstep(0.4, 0.7, r))
        # black spot down the middle, widest toward the back
        spot = nh.smoothstep(0.03, 0.02, abs(d.x) - 0.25 * max(0.0, d.y)) * nh.smoothstep(0.075, 0.05, abs(d.y - 0.015))
        col = nh.lerp(col, BLACK, spot)
        return nh.lerp(col, SHIELD_YELLOW, nh.smoothstep(0.0, -0.6, n.z) * 0.5)
    return bm, color


def abdomen():
    """Segmented abdomen; returns (dark part, lantern part) so the lantern can be lit separately."""
    n_seg = 7
    steps = 28
    pts, radii = [], []
    for i in range(steps + 1):
        t = i / steps
        pts.append(ABD_START + Vector((0.0, t * ABD_LEN, -0.05 * t * t)))
        phase = (t * n_seg) % 1.0
        step = 1.0 - 0.08 * nh.smoothstep(0.75, 1.0, phase)
        r = 0.088 * math.sin(math.pi * (0.2 + t * 0.8)) ** 0.5 * (1.0 - 0.25 * t)
        radii.append(max(r * step, 0.0))
    radii[-1] = 0.0
    cut = int(LANTERN_FROM * steps)
    front = nh.tube(pts[:cut + 2], radii[:cut + 2], sides=14, scale_xy=(1.0, 0.62))
    lantern = nh.tube(pts[cut:], [r * 1.02 for r in radii[cut:]], sides=14, scale_xy=(1.0, 0.62))

    def color(co, n):
        t = (co.y - ABD_START.y) / ABD_LEN
        phase = (t * n_seg) % 1.0
        col = nh.lerp(ABDOMEN, BROWN_DARK, nh.smoothstep(0.7, 0.95, phase))
        # pinkish lateral margins of each tergite
        return nh.lerp(col, ABD_MARGIN, nh.smoothstep(0.6, 0.9, abs(n.x)) * 0.6)
    return (front, color), (lantern, LANTERN_BASE)


def head(mb):
    mb.add(nh.uv_ellipsoid(HEAD, (0.062, 0.055, 0.05), 12, 8), BLACK)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(HEAD + Vector((s * 0.05, -0.012, 0.004)), (0.03, 0.036, 0.04), 10, 8), EYE)
        # long thread-like antennae sweeping forward and out
        base = HEAD + Vector((s * 0.022, -0.05, 0.02))
        pts = [base, base + Vector((s * 0.05, -0.12, 0.03)), base + Vector((s * 0.12, -0.24, 0.04)),
               base + Vector((s * 0.2, -0.33, 0.02))]
        mb.add(nh.tube(pts, [0.009, 0.008, 0.007, 0.004], sides=5), BLACK)
    # scutellum: small dark triangle behind the shield
    mb.add(nh.uv_ellipsoid((0, -0.15, 0.055), (0.05, 0.05, 0.03), 10, 6), BROWN_DARK)
    mb.add(nh.uv_ellipsoid((0, -0.19, 0.0), (0.085, 0.09, 0.07), 12, 8), BROWN_DARK)  # thorax underneath


def legs(mb):
    for s in (-1, 1):
        for k, y in enumerate((-0.26, -0.2, -0.13)):
            hip = Vector((s * 0.04, y, -0.05))
            knee = hip + Vector((s * 0.07, -0.01 + 0.02 * k, -0.035))
            foot = knee + Vector((s * 0.02, 0.05 + 0.03 * k, -0.08))
            mb.add(nh.tube([hip, knee], [0.009, 0.0075], sides=5), LEG)
            mb.add(nh.tube([knee, foot.lerp(knee, 0.3), foot], [0.0075, 0.006, 0.003], sides=5), LEG)


# ---------------------------------------------------------------- wings

def elytron(side):
    """Raised wing case: a long, curved, leathery shell with a pale outer edge, opened up and out."""
    L, W = 0.42, 0.075
    bm = nh.uv_ellipsoid((0, 0, 0), (W, L * 0.5, 0.018), segments=16, rings=12)
    for v in bm.verts:
        v.co.z -= 2.2 * v.co.x * v.co.x          # curved cross-section, convex upward
        v.co.y += L * 0.5                         # hinge at the front end
    tmp = nh.MeshBuilder()

    def color(co, n):
        edge = nh.smoothstep(0.75, 0.92, abs(co.x) / W)
        col = nh.lerp(BROWN, BROWN_DARK, nh.smoothstep(0.0, L, co.y) * 0.5)
        return nh.lerp(col, PALE, edge)
    tmp.add(bm, color)
    out = tmp.bm
    m = (Matrix.Translation((side * 0.05, -0.19, 0.07))
         @ Matrix.Rotation(math.radians(-side * 30), 4, "Z")      # swung outward
         @ Matrix.Rotation(math.radians(38), 4, "X")             # raised up
         @ Matrix.Rotation(math.radians(side * 18), 4, "Y"))    # outer edge tipped down
    nh.transform(out, m)
    return out


def ribbon(points, w, thickness):
    """Flat vein strip along a 2D polyline."""
    pts = [Vector((p[0], p[1])) for p in points]
    left, right = [], []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        left.append(p + nrm * w)
        right.append(p - nrm * w)
    return nh.flat_panel([(p.x, p.y, 0.0) for p in left + right[::-1]], thickness)


def hind_wing(mb, side):
    length, width = 0.50, 0.15
    lead, trail = [], []
    n = 12
    for i in range(n + 1):
        t = math.sin(i / n * math.pi / 2)
        x = 0.01 + t * length
        w = width * (0.4 + 0.6 * nh.smoothstep(0.0, 0.4, t))
        if t > 0.7:
            w *= math.sqrt(max(0.0, 1 - ((t - 0.7) / 0.3) ** 2))
        lead.append((x, -w * 0.3))
        trail.append((x, w * 0.7))
    outline = lead + trail[-2::-1]
    parts = [(nh.flat_panel([(x, y, 0) for x, y in outline], 0.004), MEMBRANE)]
    for vein in ([(0.02, -0.02), (0.25, -0.035), (0.45, -0.03)], [(0.03, 0.03), (0.22, 0.05), (0.40, 0.06)],
                 [(0.04, 0.07), (0.2, 0.1), (0.32, 0.12)]):
        parts.append((ribbon(vein, 0.004, 0.006), VEIN))
    m = (Matrix.Translation((0.05, -0.13, 0.05))
         @ Matrix.Rotation(math.radians(-12), 4, "Y")
         @ Matrix.Rotation(math.radians(22), 4, "Z"))
    if side < 0:
        m = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ m
    for bm, col in parts:
        nh.transform(bm, m)
        if side < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        mb.add(bm, col, smooth=False)


# ---------------------------------------------------------------- glow

def srgb_to_linear(c):
    return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92


def light_lantern(obj, vert_range):
    """Swaps the byte "Col" layer for a float one so the lantern can go above 1.0. The FBX exporter
    writes colours back in sRGB, so the stored value for the lantern is exactly LANTERN."""
    me = obj.data
    old = me.color_attributes["Col"]
    vals = [tuple(d.color) for d in old.data]
    me.color_attributes.remove(old)
    new = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    lit = tuple(srgb_to_linear(c) for c in LANTERN) + (1.0,)
    lo, hi = vert_range
    for loop, v in zip(me.loops, vals):
        new.data[loop.index].color = lit if lo <= loop.vertex_index < hi else v
    me.color_attributes.active_color = new
    me.color_attributes.render_color_index = me.color_attributes.active_color_index


def build():
    mb = nh.MeshBuilder()
    (front, front_col), (lantern, lantern_col) = abdomen()
    mb.add(front, front_col)
    lo = len(mb.bm.verts)
    mb.add(lantern, lantern_col)
    hi = len(mb.bm.verts)
    head(mb)
    mb.add(*pronotum())
    legs(mb)
    for side in (1, -1):
        hind_wing(mb, side)
        mb.add(elytron(side), None)
    obj = mb.to_object("SynchronousFirefly", roughness=0.5)
    light_lantern(obj, (lo, hi))
    centre = Vector((0.0, -0.05, 0.0))
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "SynchronousFirefly", background=(0.05, 0.08, 0.10), views=((35, 25), (0, 80), (-90, 8), (160, -25)))
