"""
Procedural green lacewing (Chrysopa pallens) in flight, for map swarms.

A delicate pale green insect: small head with big golden-copper compound eyes,
a row of tiny black spots on the face, long thread-like antennae swept forward,
a narrow thorax and a long slender abdomen. Four large oval wings are spread
flat, the forewings slightly longer and swept forward. Each wing is a pale
whitish-green membrane slab (the clear membrane, made a little opaque) with
thicker green vein ribbons on both sides: the costa with its ladder of costal
crossveins, the radial veins, the two step-like rows of gradate veins and the
forked veins running out to the margin. Thin pale legs hang under the thorax.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/chrysopa_pallens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GreenLacewing.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.46, 0.74, 0.26)
BODY_PALE = (0.70, 0.86, 0.42)
STRIPE = (0.86, 0.90, 0.52)      # pale yellow dorsal line
SPOT = (0.04, 0.04, 0.03)
EYE = (0.78, 0.50, 0.14)
EYE_SHEEN = (0.96, 0.78, 0.38)
ANTENNA = (0.62, 0.66, 0.36)
LEG = (0.62, 0.80, 0.42)
MEMBRANE = (0.82, 0.93, 0.76)    # glassy membrane, shown as a pale whitish green
VEIN = (0.36, 0.66, 0.22)
VEIN_DARK = (0.22, 0.46, 0.14)

T_MEMBRANE, T_VEIN = 0.003, 0.006

HEAD = Vector((0.0, -0.255, 0.012))
THORAX = Vector((0.0, -0.165, 0.010))
ABD_START = Vector((0.0, -0.10, 0.004))
ABD_LEN = 0.36


# ---------------------------------------------------------------- body

def build_head(mb):
    mb.add(nh.uv_ellipsoid(HEAD, (0.026, 0.026, 0.024), 10, 7), BODY_PALE)
    # small black facial spots
    for p in ((0.0, -0.022, 0.006), (0.010, -0.020, 0.012), (-0.010, -0.020, 0.012),
              (0.014, -0.016, -0.006), (-0.014, -0.016, -0.006), (0.006, -0.022, -0.012),
              (-0.006, -0.022, -0.012)):
        mb.add(nh.uv_ellipsoid(HEAD + Vector(p), (0.0042, 0.0042, 0.0042), 6, 4), SPOT)
    # mouthparts
    mb.add(nh.uv_ellipsoid(HEAD + Vector((0, -0.024, -0.014)), (0.010, 0.010, 0.008), 8, 6), BODY)
    # big hemispherical golden-copper eyes
    for s in (-1, 1):
        c = HEAD + Vector((s * 0.022, 0.0, 0.004))

        def eye_col(co, n, c=c):
            return nh.lerp(EYE, EYE_SHEEN, max(0.0, n.z) * 0.6 + max(0.0, -n.y) * 0.3)

        mb.add(nh.uv_ellipsoid(c, (0.017, 0.019, 0.019), 10, 7), eye_col)
    # long thread-like antennae, swept forward and out
    for s in (-1, 1):
        b = HEAD + Vector((s * 0.008, -0.018, 0.018))
        pts = [b, b + Vector((s * 0.03, -0.09, 0.035)), b + Vector((s * 0.075, -0.20, 0.05)),
               b + Vector((s * 0.12, -0.30, 0.045)), b + Vector((s * 0.15, -0.37, 0.03))]
        mb.add(nh.tube(pts, [0.0032, 0.0026, 0.0022, 0.0018, 0.0012], sides=4), ANTENNA)


def build_thorax(mb):
    def col(co, n):
        c = nh.lerp(BODY, BODY_PALE, max(0.0, -n.z) * 0.6)
        if n.z > 0.5 and abs(co.x) < 0.006:
            c = STRIPE
        return c

    # pronotum (narrow neck plate), then the deeper wing-bearing thorax
    mb.add(nh.uv_ellipsoid(HEAD.lerp(THORAX, 0.55), (0.019, 0.030, 0.018), 10, 8), col)
    mb.add(nh.uv_ellipsoid(THORAX + Vector((0, 0.02, 0.0)), (0.030, 0.060, 0.032), 14, 10), col)


def build_abdomen(mb):
    n_seg = 9
    steps = n_seg * 2
    pts, radii = [], []
    for i in range(steps + 1):
        t = i / steps
        pts.append(ABD_START + Vector((0.0, t * ABD_LEN, -0.02 * t * t)))
        phase = (t * n_seg) % 1.0
        pinch = 1.0 - 0.10 * (1.0 - min(phase, 1.0 - phase) * 2.0) ** 4
        r = 0.020 + 0.004 * math.sin(min(1.0, t / 0.6) * math.pi) - 0.010 * nh.smoothstep(0.7, 1.0, t)
        radii.append(r * pinch)
    radii[-1] = 0.004

    def col(co, n):
        c = nh.lerp(BODY, BODY_PALE, max(0.0, -n.z) * 0.7)
        if n.z > 0.6 and abs(co.x) < 0.005:
            c = STRIPE
        return c

    mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.9)), col)


def build_legs(mb):
    for pair in range(3):
        for s in (-1, 1):
            hip = THORAX + Vector((s * 0.016, -0.025 + pair * 0.03, -0.026))
            knee = hip + Vector((s * 0.040, -0.010 + pair * 0.018, -0.030))
            foot = knee + Vector((s * 0.010, 0.010 + pair * 0.025, -0.055))
            mb.add(nh.tube([hip, knee], [0.0042, 0.0034], sides=4), LEG)
            mb.add(nh.tube([knee, foot], [0.0030, 0.0015], sides=4), LEG)


# ---------------------------------------------------------------- wings

def v2(p):
    return Vector((p[0], p[1]))


def slab(outline2d, thickness):
    return nh.flat_panel([(p[0], p[1], 0.0) for p in outline2d], thickness)


def ribbon(points, w0, w1, thickness):
    """Tapered flat strip along a 2D polyline (a wing vein): a top and a bottom sheet only."""
    pts = []
    for p in points:
        if not pts or (v2(p) - pts[-1]).length > 1e-6:
            pts.append(v2(p))
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


def wing_edges(length, chord, n=24):
    """Leading and trailing edges (x outward, -y forward) of a broad oval lacewing wing."""
    lead, trail = [], []
    for i in range(n + 1):
        t = i / n
        x = 0.012 + t * length
        # narrow base, broadest a little past the middle, round tip
        w = chord * (0.30 + 0.70 * math.sin(min(1.0, t / 0.55) * math.pi / 2))
        w *= math.sqrt(max(0.0, 1.0 - max(0.0, (t - 0.62) / 0.38) ** 2.2))
        lead.append((x, -w * 0.38 - 0.03 * t * t))
        trail.append((x, w * 0.62 - 0.03 * t * t))
    return lead, trail


def lerp2(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def build_wing(length, chord, seed):
    """[(bmesh, colour)] for one right wing in wing space (root at the origin)."""
    lead, trail = wing_edges(length, chord)
    n = len(lead) - 1
    outline = lead + trail[::-1][1:-1]
    parts = [(slab(outline, T_MEMBRANE), MEMBRANE)]
    rnd = random.Random(seed)

    # vein rails between the leading edge (f=0) and the trailing edge (f=1)
    def rail(f, i0=0, i1=n):
        return [lerp2(lead[i], trail[i], f) for i in range(i0, i1 + 1)]

    costa = rail(0.0, 0, n - 1)
    sub = rail(0.10, 0, n - 3)
    radius = rail(0.20, 0, n - 2)
    parts.append((ribbon(costa, 0.0040, 0.0022, T_VEIN), VEIN))
    parts.append((ribbon(sub[::2] + sub[-1:], 0.0030, 0.0018, T_VEIN), VEIN))
    parts.append((ribbon(radius[::2] + radius[-1:], 0.0032, 0.0018, T_VEIN), VEIN))
    # ladder of costal crossveins between the costa and the subcosta
    for i in range(1, n - 3):
        for t in (0.0,):
            a = v2(costa[i]).lerp(v2(costa[i + 1]), t)
            b = v2(sub[i]).lerp(v2(sub[i + 1]), t)
            parts.append((ribbon([tuple(a), tuple(b)], 0.0012, 0.0012, T_VEIN), VEIN))
    # radial sector: veins branching off the radius and running back to the margin
    long_f = [0.36, 0.52, 0.68, 0.84]
    rails = [radius]
    for k, f in enumerate(long_f):
        i0 = 1 + k
        pts = [radius[i0]] + rail(f, i0 + 2, n - 1 - (k > 1))
        rails.append(pts)
        parts.append((ribbon(pts[:1] + pts[1::2] + pts[-1:], 0.0026, 0.0014, T_VEIN), VEIN))
    # cubitus along the hind part of the wing base
    cub = rail(0.92, 0, int(n * 0.55))
    parts.append((ribbon(cub[::2], 0.0026, 0.0014, T_VEIN), VEIN))
    # crossveins and two stepped rows of gradate veins between the longitudinal veins
    for j in range(len(long_f)):
        a_rail, b_rail = rails[j], rails[j + 1]
        for g in (0.45, 0.70):
            ia = min(int(len(a_rail) * g) + j, len(a_rail) - 2)
            ib = min(int(len(b_rail) * g) + j, len(b_rail) - 2)
            parts.append((ribbon([a_rail[ia], b_rail[ib]], 0.0013, 0.0013, T_VEIN), VEIN_DARK))
        for _ in range(3):
            t = rnd.uniform(0.15, 0.95)
            ia = min(int(len(a_rail) * t), len(a_rail) - 1)
            ib = min(int(len(b_rail) * t), len(b_rail) - 1)
            parts.append((ribbon([a_rail[ia], b_rail[ib]], 0.0011, 0.0011, T_VEIN), VEIN))
    # small forks running out to the hind margin and round the tip
    for i in range(3, n, 2):
        base = lerp2(lead[i], trail[i], 0.84 if i > n * 0.45 else 0.92)
        tip = trail[i]
        mid = lerp2(base, tip, 0.55)
        parts.append((ribbon([base, mid], 0.0011, 0.0011, T_VEIN), VEIN))
        for d in (-1, 1):
            end = (tip[0] + d * 0.011, tip[1])
            parts.append((ribbon([mid, end], 0.0010, 0.0008, T_VEIN), VEIN))
    for i in range(n - 4, n):
        base = lerp2(lead[i], trail[i], 0.3)
        parts.append((ribbon([radius[min(i, len(radius) - 1)], lead[i + 1]], 0.0011, 0.0009, T_VEIN), VEIN))
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
    fore = build_wing(0.56, 0.20, 1)
    hind = build_wing(0.50, 0.17, 2)
    for mirror in (False, True):
        place([(bm.copy(), c) for bm, c in fore], mb, mirror,
              hinge=(0.018, -0.180, 0.030), sweep_deg=-12, dihedral_deg=8)
        place([(bm.copy(), c) for bm, c in hind], mb, mirror,
              hinge=(0.018, -0.135, 0.026), sweep_deg=8, dihedral_deg=6)
    for bm, _ in fore + hind:
        bm.free()
    obj = mb.to_object("GreenLacewing", roughness=0.4)
    centre = Vector((0.0, (HEAD.y - 0.03 + ABD_START.y + ABD_LEN) / 2, 0.01))
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "GreenLacewing", background=(0.20, 0.28, 0.18), views=((35, 30), (0, 80), (-90, 8)))
