"""
Procedural Pulmonoscorpius kirktonensis (giant Carboniferous scorpion, ~70 cm) for map colonies.

A big, heavy-bodied scorpion standing on eight splayed legs: a subquadrate
carapace (prosoma) with a median eye tubercle and lateral eye clusters at the
front corners, a broad mesosoma of seven overlapping tergites, and the five
lengthening segments of the metasoma curled high over the back, ending in a
swollen telson vesicle and a curved stinger pointing forward. Large pedipalps
reach forward with swollen chela hands and long fingers; small chelicerae sit
under the front edge. Very dark brown to black with a faint reddish tint on the
chelae and tail, the gloss baked into the vertex colours (diffuse map shader).
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/pulmonoscorpius_kirktonensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pulmonoscorpius.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.11, 0.075, 0.05)
BODY_DARK = (0.035, 0.028, 0.022)
RIM = (0.24, 0.15, 0.09)         # tergite hind margins, joints
CLAW = (0.20, 0.09, 0.05)        # reddish chelae
FINGER = (0.06, 0.04, 0.03)
LEG = (0.16, 0.11, 0.07)
LEG_TIP = (0.30, 0.20, 0.11)
STING = (0.30, 0.10, 0.05)
EYE = (0.55, 0.52, 0.42)
SHINE = (0.55, 0.50, 0.44)
LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()

BASE = 0.075                      # underside of the body above the ground


def glossy(base, dark=BODY_DARK, gloss=0.45):
    def color(co, n):
        c = nh.lerp(dark, base, nh.smoothstep(-0.5, 0.6, n.z))
        h = max(0.0, n.dot(LIGHT_DIR)) ** 16
        return nh.lerp(c, SHINE, h * gloss)
    return color


# ---------------------------------------------------------------- body

def build_prosoma(mb):
    c = Vector((0.0, -0.25, BASE + 0.035))

    def squarish(n):
        return (1.0 + 0.12 * (abs(n.x) ** 3 + abs(n.y) ** 3)) * (0.75 if n.z < 0 else 1.0)
    mb.add(nh.uv_ellipsoid(c, (0.125, 0.135, 0.050), 18, 10, deform=squarish), glossy(BODY))
    # median eye tubercle with the pair of median eyes
    t = c + Vector((0, -0.03, 0.050))
    mb.add(nh.uv_ellipsoid(t, (0.026, 0.030, 0.014), 8, 5), BODY_DARK)
    for s in (-1, 1):
        mb.add(nh.ellipsoid(t + Vector((s * 0.012, -0.004, 0.010)), (0.008,) * 3, 1), EYE)
        # lateral eye clusters at the front corners
        for k in range(3):
            mb.add(nh.ellipsoid(c + Vector((s * (0.095 - k * 0.010), -0.120 + k * 0.006, 0.020)),
                                (0.0055,) * 3, 1), EYE)
        # chelicerae under the front edge
        mb.add(nh.uv_ellipsoid(c + Vector((s * 0.025, -0.140, -0.015)), (0.022, 0.030, 0.018), 8, 5),
               CLAW)


MESO = [  # (y centre, half-width, half-length)
    (-0.095, 0.130, 0.040), (-0.030, 0.142, 0.042), (0.038, 0.150, 0.044), (0.108, 0.150, 0.045),
    (0.178, 0.145, 0.045), (0.246, 0.132, 0.044), (0.308, 0.105, 0.040),
]


def build_mesosoma(mb):
    for i, (y, w, l) in enumerate(MESO):
        c = Vector((0.0, y, BASE + 0.034 - i * 0.002))

        def col(co, n, c=c, l=l):
            g = glossy(BODY)(co, n)
            # paler hind margin of each tergite, a dark median line
            g = nh.lerp(g, RIM, 0.75 * nh.smoothstep(0.55, 0.95, (co.y - c.y) / l) * (n.z > 0.2))
            if abs(co.x) < 0.008 and n.z > 0.6:
                g = BODY_DARK
            return g

        def flat(n):
            return 0.7 if n.z < 0 else 1.0
        mb.add(nh.uv_ellipsoid(c, (w, l * 1.18, 0.046), 16, 8, deform=flat), col)
    # pale belly plates
    mb.add(nh.uv_ellipsoid((0, 0.10, BASE + 0.012), (0.11, 0.24, 0.02), 12, 6), RIM)


TAIL = [(0.30, 0.10), (0.40, 0.15), (0.47, 0.27), (0.46, 0.41), (0.38, 0.51), (0.26, 0.54),
        (0.15, 0.49), (0.10, 0.42)]   # (y, z) control points: back, up and curling forward


def tail_curve(steps=12):
    """Metasoma + telson path in the YZ plane (Catmull-Rom through TAIL)."""
    ctrl = [Vector((0.0, y, z)) for y, z in TAIL]
    ctrl = [ctrl[0] * 2 - ctrl[1]] + ctrl + [ctrl[-1] * 2 - ctrl[-2]]
    pts = []
    for i in range(1, len(ctrl) - 2):
        p0, p1, p2, p3 = ctrl[i - 1:i + 3]
        for k in range(steps):
            t = k / steps
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    pts.append(ctrl[-2])
    return pts


def build_metasoma(mb):
    path = tail_curve()
    lens = [0.10, 0.11, 0.12, 0.13, 0.15]   # segments lengthen toward the tip
    total = sum(lens)
    # cumulative arc length along the path
    acc = [0.0]
    for a, b in zip(path, path[1:]):
        acc.append(acc[-1] + (b - a).length)
    scale = acc[-1] * 0.80 / total          # leave ~20 % of the path for the telson

    def at(s):
        for i in range(1, len(acc)):
            if acc[i] >= s:
                t = (s - acc[i - 1]) / max(acc[i] - acc[i - 1], 1e-6)
                return path[i - 1].lerp(path[i], t)
        return path[-1]

    s0 = 0.0
    for i, L in enumerate(lens):
        L *= scale
        pts = [at(s0 + L * f) for f in (0.0, 0.15, 0.5, 0.85, 1.0)]
        r = 0.052 - i * 0.004
        radii = [r * 0.70, r * 0.95, r, r * 0.92, r * 0.70]
        mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.88)),
               lambda co, n: nh.lerp(glossy(BODY)(co, n), CLAW, 0.25))
        # joint ring
        mb.add(nh.tube([at(s0 + L * 0.98), at(s0 + L * 1.04)], [r * 0.6, r * 0.6], sides=6), RIM)
        s0 += L
    # telson: swollen vesicle plus a curved aculeus
    v0 = at(s0 + 0.01)
    rest = path[-1]
    fwd = (rest - v0).normalized()
    vc = v0 + fwd * 0.055
    vpts = [v0, v0 + fwd * 0.03, vc, v0 + fwd * 0.09]
    mb.add(nh.tube(vpts, [0.030, 0.046, 0.044, 0.024], sides=8), glossy(STING, BODY_DARK))
    down = Vector((0, 0.2, -1.0)).normalized()
    a0 = v0 + fwd * 0.085
    apts = [a0, a0 + fwd * 0.035 + down * 0.008, a0 + fwd * 0.060 + down * 0.030,
            a0 + fwd * 0.070 + down * 0.060]
    mb.add(nh.tube(apts, [0.020, 0.013, 0.007, 0.0], sides=6), BODY_DARK)


# ---------------------------------------------------------------- appendages

def jointed(mb, pts, radii, colors, sides=6):
    for i in range(len(pts) - 1):
        mb.add(nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=sides), colors[i])
        if 0 < i < len(pts) - 1:
            mb.add(nh.ellipsoid(pts[i], (radii[i] * 1.05,) * 3, 1), RIM)


def build_pedipalps(mb):
    for s in (-1, 1):
        root = Vector((s * 0.07, -0.36, BASE + 0.025))
        femur = root + Vector((s * 0.17, -0.07, 0.05))
        patella = femur + Vector((-s * 0.02, -0.17, 0.0))
        jointed(mb, [root, femur, patella], [0.026, 0.028, 0.032], [glossy(CLAW), glossy(CLAW)])
        # chela: swollen hand, then fixed and movable fingers
        hand_c = patella + Vector((-s * 0.035, -0.085, 0.0))
        hand_dir = (hand_c - patella).normalized()
        mb.add(nh.tube([patella, patella + hand_dir * 0.03, hand_c, hand_c + hand_dir * 0.065],
                       [0.034, 0.060, 0.064, 0.048], sides=10, scale_xy=(1.0, 0.75)), glossy(CLAW, gloss=0.6))
        base = hand_c + hand_dir * 0.06
        side = Vector((s, 0, 0))
        fixed = [base + side * -0.022, base + hand_dir * 0.06 - side * 0.032, base + hand_dir * 0.13 - side * 0.018]
        movable = [base + side * 0.022, base + hand_dir * 0.06 + side * 0.026, base + hand_dir * 0.125 - side * 0.006]
        mb.add(nh.tube(fixed, [0.022, 0.016, 0.0], sides=6), FINGER)
        mb.add(nh.tube(movable, [0.022, 0.015, 0.0], sides=6), FINGER)


def build_legs(mb):
    # (attach y, forward reach, splay) for legs I..IV
    legs = [(-0.32, -0.17, 0.34), (-0.27, -0.06, 0.39), (-0.22, 0.07, 0.39), (-0.16, 0.20, 0.37)]
    for s in (-1, 1):
        for y, reach, splay in legs:
            hip = Vector((s * 0.10, y, BASE + 0.015))
            knee = Vector((s * splay * 0.55, y + reach * 0.45, BASE + 0.10))
            ankle = Vector((s * splay * 0.88, y + reach * 0.85, BASE + 0.03))
            foot = Vector((s * splay, y + reach, 0.0))
            jointed(mb, [hip, knee, ankle, foot], [0.020, 0.018, 0.012, 0.004],
                    [glossy(LEG), glossy(LEG), LEG_TIP], sides=5)


def build():
    mb = nh.MeshBuilder()
    build_prosoma(mb)
    build_mesosoma(mb)
    build_metasoma(mb)
    build_pedipalps(mb)
    build_legs(mb)
    obj = mb.to_object("Pulmonoscorpius", roughness=0.4)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.3f}, hip {BASE + 0.015:.3f} -> mapHip {(BASE + 0.015) / max(zs):.2f}")
    return obj


if __name__ == "__main__":
    nh.run(build, "Pulmonoscorpius", ground=(0.30, 0.26, 0.18), views=((35, 30), (0, 75), (-90, 10)))
