"""
Procedural Spriggina floundersi (Ediacaran segmented bilaterian) for map colonies.

A small, flat, elongate animal lying on the microbial mat: a horseshoe-shaped head shield at
the front whose two horns sweep back along the margins, then about forty pairs of narrow,
chevron-like segments that angle back toward the margins and taper to a pointed rear. The
segments of the left and right halves are offset by half a segment so they alternate across
the midline (glide symmetry, not mirror symmetry) - the odd arrangement that makes Spriggina
hard to place among living animals. Muted ochre-tan body with darker segment furrows, a
paler pinkish head shield with a darker rim.
Each half is a loft whose rows follow the chevron furrows (so every furrow is captured with
few triangles); the halves meet seamlessly on the midline, where the relief fades out.
Faces -Y, pivot at the body centre (Swim style), seen mostly from above.

Usage:
  blender --background --python tools/blender/spriggina_floundersi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Spriggina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SEGMENTS = 40          # segment pairs
HEAD_S = 4.0           # the head shield spans this many "segment" stations
Y_FRONT = -0.84        # front of the head shield (-Y)
Y_HEAD = -0.60         # head / trunk boundary on the midline
FINE_S = 22            # three rows per segment up to here, two (furrow, crest) behind
Y_BACK = 0.80          # pointed rear tip
W_MAX = 0.235          # half-width at the broadest point
SLANT = 0.62           # how far back (x half-width) a furrow reaches at the margin
HORN_S = 4.5           # head horns reach back along the margin to this segment
HORN_U = 0.64          # ... covering the margin outside this fraction of the half-width
UNDER_Z = -0.022
# columns across a half (0 = midline, 1 = margin); clustered toward the rim
COLS = (0.0, 0.09, 0.30, 0.50, 0.64, 0.80, 0.92, 1.0)

BODY = (0.70, 0.52, 0.34)       # ochre-tan segments
BODY_LIGHT = (0.84, 0.68, 0.50)
FURROW = (0.36, 0.23, 0.15)     # segment furrows
MIDLINE = (0.48, 0.32, 0.22)
HEAD = (0.86, 0.66, 0.56)       # paler, pinkish head shield
HEAD_RIM = (0.52, 0.34, 0.26)
UNDER = (0.55, 0.42, 0.32)


def yc(s):
    """Midline y of station s (s < 0: head, 0..SEGMENTS: trunk). Trunk segments shorten
    toward the rear."""
    if s <= 0.0:
        return Y_HEAD + (Y_HEAD - Y_FRONT) * s / HEAD_S
    t = s / SEGMENTS
    return Y_HEAD + (Y_BACK - Y_HEAD) * (1.25 * t - 0.25 * t * t)


def half_width(s):
    if s <= 0.0:
        # rounded front of the head shield
        t = (s + HEAD_S) / HEAD_S          # 0 at the front tip, 1 at the head's back
        return max(0.012, W_MAX * 1.02 * (1.0 - (1.0 - t) ** 2) ** 0.5)
    t = s / SEGMENTS
    w = W_MAX * (1.0 - 0.93 * t ** 1.7)
    # the head's horns flare a little proud of the first trunk segments
    w *= 1.0 + 0.04 * nh.smoothstep(HORN_S + 0.5, HORN_S - 1.0, s)
    return max(0.010, w)


def slant(s):
    """Furrows are straight across the front of the head and chevron-shaped in the trunk."""
    return SLANT * nh.smoothstep(-1.2, 0.3, s)


def head_mask(s, u):
    """1 on the horseshoe head shield (including its backswept horns), 0 on the trunk."""
    core = nh.smoothstep(0.35, -0.35, s)
    hu = HORN_U + (0.88 - HORN_U) * max(0.0, min(1.0, s / HORN_S))   # horns taper to a point
    horn = nh.smoothstep(hu - 0.07, hu + 0.07, u) * nh.smoothstep(HORN_S + 0.3, HORN_S - 0.3, s)
    return max(core, horn)


def phase(s, off):
    p = s + off
    return p - math.floor(p)


def height(s, u, off):
    w = half_width(s)
    t = max(0.0, s) / SEGMENTS
    h = (0.060 * (w / W_MAX) ** 0.8 + 0.008) * (1.0 - u ** 2.2) ** 0.6   # flat dome across
    m = head_mask(s, u)
    p = phase(s, off)
    crest = 0.5 - 0.5 * math.cos(p * math.tau)                # 0 in the furrow, 1 on the crest
    relief = nh.smoothstep(0.0, 0.18, u) * (1.0 - 0.5 * t)
    h += (1.0 - m) * relief * (0.016 * crest - 0.006)
    if s <= 0.0 or m > 0.0:
        # head shield: a touch higher, with a raised rim and a shallow furrow behind it
        h += 0.015 * m
        rim = max(nh.smoothstep(0.62, 0.80, u), nh.smoothstep(-HEAD_S * 0.45, -HEAD_S * 0.85, s))
        h += 0.012 * m * rim
        h -= 0.010 * 4.0 * m * (1.0 - m)
    return h


def color(s, u, off, co):
    t = max(0.0, s) / SEGMENTS
    p = phase(s, off)
    crest = 0.5 - 0.5 * math.cos(p * math.tau)
    c = nh.lerp(BODY_LIGHT, BODY, nh.smoothstep(0.1, 0.9, u))
    c = nh.lerp(c, FURROW, (1.0 - nh.smoothstep(0.15, 0.6, crest)) * 0.85 * nh.smoothstep(0.02, 0.1, u))
    c = nh.lerp(c, MIDLINE, nh.smoothstep(0.08, 0.0, u) * 0.6)
    c = nh.lerp(c, FURROW, nh.smoothstep(0.93, 1.0, u) * 0.35)          # darker margin
    m = head_mask(s, u)
    front = nh.smoothstep(-HEAD_S * 0.45, -HEAD_S * 0.85, s)       # 1 toward the front edge
    rim = max(nh.smoothstep(0.62, 0.80, u), front)
    hc = nh.lerp(HEAD, HEAD_RIM, rim * 0.6)
    c = nh.lerp(c, hc, m)
    c = nh.lerp(c, FURROW, min(1.0, 5.0 * m * (1.0 - m)) * 0.9)     # furrow around the shield
    c = nh.lerp(c, FURROW, nh.smoothstep(0.75, 1.0, t) * 0.2)
    k = 1.0 + 0.07 * noise.noise(co * 22.0)
    return tuple(min(1.0, x * k) for x in c)


def stations(off):
    """Row stations: dense across the rounded head, three per segment on the trunk (furrow,
    flank, crest), offset by `off` so they land on this half's furrows."""
    ss = []
    for i in range(12):
        t = i / 12
        ss.append(-HEAD_S + HEAD_S * (1.0 - math.cos(t * math.pi / 2)) ** 0.75)
    k = 0
    while True:
        s = k / 3.0 - off
        k += 1
        if s <= 0.05:
            continue
        if s >= FINE_S - off:
            break
        ss.append(s)
    k = 0
    while True:
        s = FINE_S - off + k / 2.0
        k += 1
        if s >= SEGMENTS - 0.1:
            break
        ss.append(s)
    ss.append(SEGMENTS)
    return ss


def half(side, off):
    """One half of the body as a closed loft: each row is a loop (midline top -> margin ->
    underside -> midline underside) following a chevron furrow line."""
    bm = bmesh.new()
    vcol = {}
    loops = []
    for s in stations(off):
        w = half_width(s)
        y0 = yc(s)
        sl = slant(s)
        loop = []
        for u in COLS:
            x = side * u * w
            y = y0 + sl * w * u ** 1.25
            co = Vector((x, y, height(s, u, off)))
            v = bm.verts.new(co)
            vcol[v] = color(s, u, off, co)
            loop.append(v)
        for x, y in ((side * w * 0.97, y0 + sl * w), (0.0, y0)):
            v = bm.verts.new((x, y, UNDER_Z))
            vcol[v] = UNDER
            loop.append(v)
        loops.append(loop)
    n = len(loops[0])
    for a, b in zip(loops, loops[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def build():
    mb = nh.MeshBuilder()
    # right half (+X) furrows on whole segments, the left half offset by half a segment
    for side, off in ((1, 0.0), (-1, 0.5)):
        bm, vcol = half(side, off)
        nf.add_colored(mb, bm, vcol)
    # weld the two halves where their midline vertices coincide (the head)
    bmesh.ops.remove_doubles(mb.bm, verts=mb.bm.verts, dist=1e-5)
    inner = [f for f in mb.bm.faces if all(abs(v.co.x) < 1e-6 for v in f.verts)]
    bmesh.ops.delete(mb.bm, geom=inner, context="FACES_ONLY")   # the now-internal midline walls
    obj = mb.to_object("Spriggina", roughness=0.6)
    # pivot at the body centre: centre the thickness on z = 0
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Spriggina", background=(0.05, 0.14, 0.18), views=((30, 40), (0, 85), (-90, 12)))
