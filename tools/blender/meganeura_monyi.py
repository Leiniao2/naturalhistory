"""
Procedural Meganeura monyi (Carboniferous griffinfly) in level flight, for map colonies.

A giant dragonfly-like insect: huge compound eyes meeting on top of the head,
a boxy forward-tilted thorax, a long ringed abdomen with paired cerci, and four
long narrow wings held flat out. Each wing is a pale glassy membrane slab with
thicker dark vein ribbons on top (the dense longitudinal veins plus a ladder of
crossveins), so the venation stays crisp on both sides. Spiny legs are folded
forward into a catching basket under the thorax.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/meganeura_monyi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Meganeura.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.16, 0.13, 0.08)
BODY_DARK = (0.06, 0.05, 0.04)
STRIPE = (0.62, 0.52, 0.24)      # ochre markings
EYE = (0.10, 0.16, 0.14)
EYE_SHEEN = (0.30, 0.42, 0.36)
LEG = (0.09, 0.07, 0.05)
MEMBRANE = (0.72, 0.75, 0.70)
MEMBRANE_ROOT = (0.58, 0.46, 0.26)
VEIN = (0.16, 0.12, 0.08)

T_MEMBRANE, T_VEIN = 0.004, 0.0075

HEAD = Vector((0.0, -0.425, 0.035))
THORAX = Vector((0.0, -0.27, 0.03))
ABD_START = Vector((0.0, -0.15, 0.02))
ABD_LEN = 0.66


# ---------------------------------------------------------------- body

def build_head(mb):
    mb.add(nh.uv_ellipsoid(HEAD + Vector((0, 0.01, -0.01)), (0.050, 0.044, 0.044), 12, 8), BODY)
    # face / mandibles
    mb.add(nh.uv_ellipsoid(HEAD + Vector((0, -0.035, -0.03)), (0.028, 0.020, 0.022), 10, 6), STRIPE)
    for s in (-1, 1):
        mb.add(nh.tube([HEAD + Vector((s * 0.018, -0.040, -0.045)),
                        HEAD + Vector((s * 0.006, -0.058, -0.055))], [0.008, 0.0], sides=4), BODY_DARK)
    # compound eyes: big domes wrapping the sides, touching on top
    for s in (-1, 1):
        c = HEAD + Vector((s * 0.040, -0.004, 0.014))

        def eye_col(co, n):
            return nh.lerp(EYE, EYE_SHEEN, max(0.0, n.z) * 0.7 + max(0.0, -n.y) * 0.2)

        mb.add(nh.uv_ellipsoid(c, (0.048, 0.052, 0.052), 14, 10), eye_col)
    # short bristle antennae
    for s in (-1, 1):
        b = HEAD + Vector((s * 0.010, -0.040, 0.020))
        mb.add(nh.tube([b, b + Vector((s * 0.025, -0.035, 0.020))], [0.003, 0.0], sides=3), BODY_DARK)


def build_thorax(mb):
    # synthorax tilted back, deep and slightly boxy
    def boxy(n):
        return 1.0 + 0.10 * (abs(n.x) ** 4 + abs(n.z) ** 4)

    def col(co, n):
        c = nh.lerp(BODY, BODY_DARK, max(0.0, -n.z))
        # paired antehumeral stripes on top + oblique side stripes
        rel = co - THORAX
        if n.z > 0.3 and 0.012 < abs(rel.x) < 0.026:
            c = STRIPE
        if abs(n.x) > 0.6 and abs(rel.y * 0.7 + rel.z) < 0.010:
            c = STRIPE
        return c

    bm = nh.uv_ellipsoid((0, 0, 0), (0.068, 0.100, 0.075), 16, 12, deform=boxy)
    nh.transform(bm, Matrix.Translation(THORAX) @ Matrix.Rotation(math.radians(-18), 4, "X"))
    mb.add(bm, col)
    # neck and prothorax
    mb.add(nh.uv_ellipsoid(HEAD.lerp(THORAX, 0.5) + Vector((0, 0, -0.005)), (0.028, 0.030, 0.026), 8, 6),
           BODY_DARK)


def build_abdomen(mb):
    n_seg = 10
    steps = n_seg * 3
    pts, radii = [], []
    for i in range(steps + 1):
        t = i / steps
        pts.append(ABD_START + Vector((0.0, t * ABD_LEN, -0.03 * t * t)))
        phase = (t * n_seg) % 1.0
        pinch = 1.0 - 0.16 * (1.0 - min(phase, 1.0 - phase) * 2.0) ** 4
        # swollen base (segments 1-2), slender middle, slight club at the end
        r = 0.027 + 0.024 * max(0.0, 1.0 - t / 0.14) + 0.004 * nh.smoothstep(0.75, 0.95, t)
        radii.append(r * pinch)
    radii[-1] = 0.010

    def col(co, n):
        t = max(0.0, min(0.999, (co.y - ABD_START.y) / ABD_LEN))
        phase = (t * n_seg) % 1.0
        c = nh.lerp(BODY, BODY_DARK, max(0.0, -n.z) * 0.8)
        if phase < 0.11:  # narrow ochre ring at each segment base
            c = nh.lerp(c, STRIPE, 0.7)
        elif n.z > 0.75:  # dark dorsal carina
            c = BODY_DARK
        return c

    mb.add(nh.tube(pts, radii, sides=10, scale_xy=(1.0, 0.92)), col)
    end = pts[-1]
    for s in (-1, 1):
        mb.add(nh.tube([end + Vector((s * 0.006, -0.01, 0)), end + Vector((s * 0.022, 0.07, 0.004))],
                       [0.006, 0.0], sides=4), BODY_DARK)


def build_legs(mb):
    # folded forward under the thorax, tarsi pointing ahead (a catching basket)
    for pair in range(3):
        for s in (-1, 1):
            hip = THORAX + Vector((s * 0.026, -0.050 + pair * 0.040, -0.058))
            knee = hip + Vector((s * 0.050, -0.025 - pair * 0.012, -0.050))
            foot = knee + Vector((s * 0.008, -0.075 - pair * 0.010, -0.010))
            mb.add(nh.tube([hip, knee], [0.0075, 0.006], sides=4), LEG)
            mb.add(nh.tube([knee, foot], [0.0055, 0.0], sides=4), LEG)
            # spines along the tibia
            for k in (0.3, 0.6):
                p = knee.lerp(foot, k)
                mb.add(nh.tube([p, p + Vector((s * 0.008, 0.004, -0.014))], [0.0025, 0.0], sides=3), LEG)


# ---------------------------------------------------------------- wings

def v2(p):
    return Vector((p[0], p[1]))


def slab(outline2d, thickness):
    return nh.flat_panel([(p[0], p[1], 0.0) for p in outline2d], thickness)


def ribbon(points, w0, w1, thickness):
    """Tapered flat strip along a 2D polyline (a wing vein): just a top and a bottom sheet,
    no side walls, to keep the dense venation cheap."""
    pts = [v2(p) for p in points]
    bm = bmesh.new()
    rows = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        w = w0 + (w1 - w0) * i / max(len(pts) - 1, 1)
        l, r = p + nrm * w, p - nrm * w
        rows.append([bm.verts.new((q.x, q.y, z)) for q in (l, r) for z in (thickness / 2, -thickness / 2)])
    for (lt, lb, rt, rb), (lt2, lb2, rt2, rb2) in zip(rows, rows[1:]):
        bm.faces.new([lt, rt, rt2, lt2])
        bm.faces.new([lb, lb2, rb2, rb])
    return bm


def wing_edges(length, chord, base_chord, n=18):
    """Leading and trailing edges (x outward, -y forward) of a long narrow wing with a
    rounded tip; base_chord > chord widens the base behind (the hindwing's anal lobe)."""
    lead, trail = [], []
    for i in range(n + 1):
        t = math.sin(i / n * math.pi / 2)  # denser toward the tip
        x = 0.02 + t * length
        w = chord * (0.45 + 0.55 * nh.smoothstep(0.0, 0.30, t))
        w += (base_chord - chord) * max(0.0, 1.0 - t / 0.40) ** 2
        w *= math.sqrt(max(0.0, 1.0 - max(0.0, (t - 0.80) / 0.20) ** 2))
        lead.append((x, -w * 0.40 - 0.01 * t))
        trail.append((x, w * 0.60 - 0.01 * t))
    return lead, trail[:-1]


def build_wing(length, chord, base_chord, n_long, n_cross, seed):
    """[(bmesh, colour)] for one right wing in wing space (root at the origin)."""
    lead, trail = wing_edges(length, chord, base_chord)
    outline = lead + trail[::-1]

    def membrane_col(co, n):  # evaluated after placing: |x| is the distance out from the body
        return nh.lerp(MEMBRANE_ROOT, MEMBRANE, nh.smoothstep(0.03, 0.03 + length * 0.18, abs(co.x)))

    parts = [(slab(outline, T_MEMBRANE), membrane_col)]
    # costa: a heavier vein along the leading edge
    parts.append((ribbon(lead[:-2:2], 0.0050, 0.0030, T_VEIN), VEIN))
    # longitudinal veins fanning out from the root between the edges
    rails = [lead[:-2]]
    m = len(lead) - 2
    for k in range(1, n_long + 1):
        f = (k / (n_long + 1)) ** 1.15
        pts = [(a[0], a[1] + (b[1] - a[1]) * f) for a, b in zip(lead[:m], trail[:m])]
        rails.append(pts)
        parts.append((ribbon(pts[::2], 0.0028, 0.0016, T_VEIN), VEIN))
    # crossveins scattered between neighbouring veins
    import random
    rnd = random.Random(seed)
    for _ in range(n_cross):
        j = rnd.randrange(len(rails) - 1)
        i = rnd.randrange(2, m - 1)
        t = rnd.random()
        a = v2(rails[j][i]).lerp(v2(rails[j][i + 1]), t)
        b = v2(rails[j + 1][i]).lerp(v2(rails[j + 1][i + 1]), t)
        parts.append((ribbon([tuple(a), tuple(b)], 0.0014, 0.0014, T_VEIN), VEIN))
    return parts


def place(parts, mb, mirror, hinge, sweep_deg, dihedral_deg):
    m = (Matrix.Translation(Vector(hinge))
         @ Matrix.Rotation(math.radians(-dihedral_deg), 4, "Y")
         @ Matrix.Rotation(math.radians(sweep_deg), 4, "Z"))
    if mirror:
        m = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ m
    for bm, col in parts:
        nh.transform(bm, m)
        if mirror:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        mb.add(bm, col, smooth=False)


def build():
    mb = nh.MeshBuilder()
    build_head(mb)
    build_thorax(mb)
    build_abdomen(mb)
    build_legs(mb)
    fore = build_wing(0.80, 0.115, 0.115, 6, 22, 1)
    hind = build_wing(0.76, 0.120, 0.200, 6, 22, 2)
    for mirror in (False, True):
        place([(bm.copy(), c) for bm, c in fore], mb, mirror,
              hinge=(0.025, -0.300, 0.095), sweep_deg=-5, dihedral_deg=4)
        place([(bm.copy(), c) for bm, c in hind], mb, mirror,
              hinge=(0.025, -0.225, 0.090), sweep_deg=5, dihedral_deg=3)
    for bm, _ in fore + hind:
        bm.free()
    obj = mb.to_object("Meganeura", roughness=0.4)
    centre = Vector((0.0, (HEAD.y - 0.08 + ABD_START.y + ABD_LEN + 0.07) / 2, 0.03))
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Meganeura", background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
