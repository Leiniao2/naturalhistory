"""
Procedural western honey bee worker (Apis mellifera) in flight, for map swarms.

Dark heart-shaped head with big oval compound eyes and elbowed antennae, a fuzzy
golden-brown thorax (short hair tufts break up the silhouette), and a tear-drop
abdomen banded amber, dark brown and pale hair like an Italian-type worker. Two
pairs of glassy wings raised mid-stroke, jointed legs, and orange pollen loads
packed on the hind legs.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/apis_mellifera.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HoneyBee.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

HEAD_COL = (0.08, 0.06, 0.045)
EYE = (0.04, 0.035, 0.035)
EYE_SHEEN = (0.20, 0.17, 0.14)
FACE_HAIR = (0.66, 0.54, 0.34)
FUZZ = (0.64, 0.46, 0.20)        # golden-tan thorax pile
FUZZ_LIGHT = (0.86, 0.72, 0.46)
FUZZ_DARK = (0.30, 0.19, 0.08)
AMBER = (0.80, 0.46, 0.13)
AMBER_DEEP = (0.58, 0.30, 0.09)
BAND_DARK = (0.15, 0.085, 0.04)
PALE_BAND = (0.88, 0.70, 0.40)
LEG = (0.20, 0.13, 0.07)
LEG_JOINT = (0.13, 0.085, 0.045)
POLLEN = (0.98, 0.58, 0.08)
MEMBRANE = (0.80, 0.82, 0.80)
VEIN = (0.42, 0.36, 0.28)

HEAD = Vector((0.0, -0.36, 0.02))
THORAX = Vector((0.0, -0.17, 0.04))
ABD_START = Vector((0.0, -0.05, 0.02))
ABD_LEN = 0.52


def fbm(p, octaves=3):
    """Fractal noise in roughly [-1, 1]."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * noise.noise(p * freq)
        norm += amp
        amp *= 0.5
        freq *= 2.1
    return total / norm


def fuzz_displace(bm, amount, scale, mask=None):
    """Pushes vertices along their normals by fine noise: a soft, matted pile instead of needles."""
    bm.normal_update()
    for v in bm.verts:
        k = mask(v.co) if mask else 1.0
        if k > 0.0:
            v.co += v.normal * amount * k * (0.5 + 0.5 * fbm(v.co * scale))


def fuzz_col(base, light, dark, scale=38.0):
    """Noisy pile colour: lighter tips, darker gaps."""
    def col(co, n):
        f = fbm(co * scale + Vector((3.1, 7.7, 1.3)))
        c = nh.lerp(base, light, max(0.0, f) * 1.4) if f > 0 else nh.lerp(base, dark, -f * 1.2)
        return nh.lerp(c, dark, max(0.0, -n.z) * 0.45)
    return col


# ---------------------------------------------------------------- body

def build_head(mb):
    # heart-shaped from the front: wide at the eyes, narrowing to the mouth
    def heart(n):
        return 1.0 - 0.18 * max(0.0, -n.z) * (1.0 - abs(n.x))

    head = nh.uv_ellipsoid(HEAD, (0.105, 0.065, 0.105), 16, 10, deform=heart)
    # a little matted fuzz on the crown and back of the head
    fuzz_displace(head, 0.010, 40.0, mask=lambda co: nh.smoothstep(0.02, 0.07, co.z - HEAD.z))
    crown = fuzz_col(nh.lerp(HEAD_COL, FUZZ, 0.45), FACE_HAIR, HEAD_COL)
    mb.add(head, lambda co, n: crown(co, n) if n.z > 0.45 else HEAD_COL)
    for s in (-1, 1):
        c = HEAD + Vector((s * 0.080, 0.004, 0.012))

        def eye_col(co, n):
            return nh.lerp(EYE, EYE_SHEEN, max(0.0, n.z) * 0.6 + max(0.0, -n.y) * 0.3)

        mb.add(nh.uv_ellipsoid(c, (0.040, 0.050, 0.085), 10, 8), eye_col)
    # pale hairy face patch and mandibles
    face = nh.uv_ellipsoid(HEAD + Vector((0, -0.045, 0.000)), (0.055, 0.025, 0.058), 12, 8)
    fuzz_displace(face, 0.008, 45.0)
    mb.add(face, fuzz_col(FACE_HAIR, FUZZ_LIGHT, HEAD_COL, 50.0))
    for s in (-1, 1):
        mb.add(nh.tube([HEAD + Vector((s * 0.030, -0.040, -0.080)), HEAD + Vector((s * 0.012, -0.060, -0.102))],
                       [0.011, 0.006], sides=5), HEAD_COL)
    # three ocelli on the crown
    for x, y in ((0.0, -0.01), (-0.022, 0.012), (0.022, 0.012)):
        mb.add(nh.uv_ellipsoid(HEAD + Vector((x, y, 0.104)), (0.009, 0.009, 0.007), 6, 4), EYE_SHEEN)
    # elbowed antennae: scape up and forward, flagellum bending down and out
    for s in (-1, 1):
        base = HEAD + Vector((s * 0.020, -0.055, 0.035))
        elbow = base + Vector((s * 0.025, -0.060, 0.080))
        tip = elbow + Vector((s * 0.080, -0.120, -0.010))
        mb.add(nh.tube([base, elbow], [0.009, 0.008], sides=5), HEAD_COL)
        mb.add(nh.tube([elbow, elbow.lerp(tip, 0.5) + Vector((0, -0.01, 0.02)), tip],
                       [0.008, 0.008, 0.006], sides=5), HEAD_COL)


def build_thorax(mb):
    # thorax, neck and petiole fused into one soft lump, then given a matted pile
    fb = nh.MeshBuilder()
    fb.add(nh.uv_ellipsoid(THORAX, (0.125, 0.140, 0.125), 16, 12), FUZZ)
    fb.add(nh.uv_ellipsoid(HEAD.lerp(THORAX, 0.55), (0.042, 0.042, 0.042), 8, 6), FUZZ)
    fb.add(nh.uv_ellipsoid(THORAX.lerp(ABD_START, 0.8), (0.035, 0.040, 0.035), 8, 6), FUZZ)
    body = fb.fuse(voxel=0.024, smooth=4)
    fuzz_displace(body, 0.011, 58.0)
    mb.add(body, fuzz_col(FUZZ, FUZZ_LIGHT, FUZZ_DARK))


def build_abdomen(mb):
    n_seg = 6
    steps = 36
    pts, radii = [], []
    for i in range(steps + 1):
        t = i / steps
        pts.append(ABD_START + Vector((0.0, t * ABD_LEN, -0.10 * t * t)))
        phase = (t * n_seg) % 1.0
        step = 1.0 - 0.07 * nh.smoothstep(0.75, 1.0, phase)  # overlapping tergite edges
        r = 0.150 * math.sin(math.pi * (0.14 + t * 0.86)) ** 0.7 * (1.0 - 0.30 * t)  # tapers to the tip
        radii.append(r * step)
    radii[0] = 0.04
    radii[-1] = 0.0
    abd = nh.tube(pts, radii, sides=14, scale_xy=(1.0, 0.92))
    # fuzzier toward the front, like the pile on the first tergites
    fuzz_displace(abd, 0.010, 42.0,
                  mask=lambda co: 0.35 + 0.65 * (1.0 - nh.smoothstep(0.05, 0.25, co.y - ABD_START.y)))
    pile = fuzz_col(PALE_BAND, FUZZ_LIGHT, AMBER_DEEP, 55.0)
    front = fuzz_col(FUZZ, FUZZ_LIGHT, FUZZ_DARK)

    def col(co, n):
        t = max(0.0, min(0.999, (co.y - ABD_START.y) / ABD_LEN))
        phase = (t * n_seg) % 1.0
        seg = int(t * n_seg)
        if t < 0.06:
            return front(co, n)
        amber = nh.lerp(AMBER, AMBER_DEEP, min(1.0, seg * 0.22))
        if phase < 0.18 and seg >= 1:
            c = pile(co, n)                      # pale hair band at the segment front
        elif phase < 0.70:
            c = nh.lerp(amber, BAND_DARK, 0.85 if seg >= 4 else 0.0)
        else:
            c = BAND_DARK                        # brown-black hind margin
        f = fbm(co * 60.0)
        c = nh.lerp(c, FUZZ_DARK if f < 0 else FUZZ_LIGHT, abs(f) * 0.18)
        return nh.lerp(c, BAND_DARK, max(0.0, -n.z) * 0.3)

    mb.add(abd, col)
    # sting tip
    end = pts[-1]
    mb.add(nh.tube([end + Vector((0, -0.03, 0.006)), end + Vector((0, 0.025, -0.008))], [0.008, 0.002], sides=4),
           BAND_DARK)


def leg(mb, points, radii, color=LEG):
    """Segmented leg: a slim tube per segment with darker rounded joints and a blunt foot."""
    for a, b, ra, rb in zip(points, points[1:], radii, radii[1:]):
        mb.add(nh.tube([a, b], [ra, rb], sides=5), color)
    for p, r in zip(points[1:], radii[1:]):
        mb.add(nh.uv_ellipsoid(p, (r * 1.25,) * 3, 5, 3), LEG_JOINT)


def build_legs(mb):
    for s in (-1, 1):
        # front legs tucked forward under the head
        hip = THORAX + Vector((s * 0.040, -0.075, -0.095))
        pts = [hip, hip + Vector((s * 0.045, -0.025, -0.045)), hip + Vector((s * 0.040, -0.085, -0.040)),
               hip + Vector((s * 0.030, -0.120, -0.060))]
        leg(mb, pts, [0.011, 0.0085, 0.007, 0.0055])
        # middle legs folded under the thorax
        hip = THORAX + Vector((s * 0.050, -0.010, -0.105))
        pts = [hip, hip + Vector((s * 0.065, 0.010, -0.040)), hip + Vector((s * 0.050, 0.080, -0.075)),
               hip + Vector((s * 0.040, 0.130, -0.085))]
        leg(mb, pts, [0.011, 0.0085, 0.007, 0.0055])
        # hind legs trailing back under the abdomen, pollen basket on the tibia
        hip = THORAX + Vector((s * 0.055, 0.050, -0.100))
        knee = hip + Vector((s * 0.070, 0.050, -0.045))
        ankle = knee + Vector((s * 0.025, 0.165, -0.060))
        foot = ankle + Vector((s * 0.005, 0.085, -0.010))
        leg(mb, [hip, knee, ankle, foot], [0.012, 0.010, 0.012, 0.006])
        basket = knee.lerp(ankle, 0.62) + Vector((s * 0.014, 0, 0.004))
        mb.add(nh.uv_ellipsoid(basket, (0.032, 0.046, 0.032), 10, 7,
                               deform=lambda n: 1.0 + 0.06 * math.sin(n.x * 9 + n.y * 7)), POLLEN)


# ---------------------------------------------------------------- wings

def v2(p):
    return Vector((p[0], p[1]))


def ribbon(points, w, thickness):
    """Flat vein strip (top and bottom sheets only)."""
    pts = [v2(p) for p in points]
    bm = bmesh.new()
    rows = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        l, r = p + nrm * w, p - nrm * w
        rows.append([bm.verts.new((q.x, q.y, z)) for q in (l, r) for z in (thickness / 2, -thickness / 2)])
    for (lt, lb, rt, rb), (lt2, lb2, rt2, rb2) in zip(rows, rows[1:]):
        bm.faces.new([lt, rt, rt2, lt2])
        bm.faces.new([lb, lb2, rb2, rb])
    return bm


def wing_outline(length, width, n=12):
    """Rounded oval wing, root at the origin, x outward, -y forward (leading edge fairly straight)."""
    lead, trail = [], []
    for i in range(n + 1):
        t = math.sin(i / n * math.pi / 2)
        x = 0.01 + t * length
        w = width * (0.35 + 0.65 * nh.smoothstep(0.0, 0.45, t)) * math.sqrt(max(0.0, 1 - ((t - 0.7) / 0.3) ** 2)
                                                                            if t > 0.7 else 1.0)
        lead.append((x, -w * 0.30))
        trail.append((x, w * 0.70))
    return lead + trail[-2::-1]


def build_wing(length, width, veins):
    outline = wing_outline(length, width)
    parts = [(nh.flat_panel([(x, y, 0) for x, y in outline], 0.004), MEMBRANE)]
    for pts in veins:
        parts.append((ribbon([(x * length, y * width) for x, y in pts], 0.0026, 0.006), VEIN))
    return parts


FORE_VEINS = [  # leading edge, radial and cubital veins, one closing crossvein
    [(0.02, -0.08), (0.30, -0.22), (0.62, -0.26)],
    [(0.04, 0.02), (0.35, -0.06), (0.62, -0.10)],
    [(0.05, 0.12), (0.32, 0.14), (0.55, 0.12)],
    [(0.55, -0.10), (0.55, 0.12)],
]
HIND_VEINS = [
    [(0.02, -0.06), (0.40, -0.20), (0.72, -0.22)],
    [(0.05, 0.12), (0.40, 0.10), (0.65, 0.18)],
]


def place(parts, mb, mirror, hinge, sweep_deg, lift_deg):
    m = (Matrix.Translation(Vector(hinge))
         @ Matrix.Rotation(math.radians(-lift_deg), 4, "Y")
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
    for mirror in (False, True):
        place(build_wing(0.50, 0.17, FORE_VEINS), mb, mirror,
              hinge=(0.06, -0.19, 0.13), sweep_deg=28, lift_deg=32)
        place(build_wing(0.34, 0.12, HIND_VEINS), mb, mirror,
              hinge=(0.06, -0.12, 0.12), sweep_deg=40, lift_deg=26)
    obj = mb.to_object("HoneyBee", roughness=0.5)
    centre = Vector((0.0, -0.08, 0.02))
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "HoneyBee", background=(0.22, 0.32, 0.20), views=((35, 25), (0, 80), (-90, 8), (180, 15)))
