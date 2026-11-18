"""
Procedural low-poly Telonema subtile, a telonemid: a small predatory flagellate close to the
common root of the SAR group (stramenopiles, alveolates, rhizarians) and the plants and algae.

An ovoid-to-pear-shaped cell, broad and a little flattened at the rear, tapering toward the front
where a small rounded "beak" (the cytostome region it engulfs prey with) juts out, its tip a
darker ring. Two long, unequal flagella spring from one side just behind the front: the longer
sweeps forward and out, fringed with fine stiff side hairs (mastigonemes), and the shorter,
smooth one trails back along the flank. Inside, a few dark olive food vacuoles (eaten bacteria)
bulge faintly through the rear half, and the round nucleus with its nucleolus shows near the
front. Pale greenish-cream, translucent-looking. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/telonema_subtile.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Telonema.fbx
About 1.6 units long from the hairy flagellum's tip to the trailing flagellum's tip, the cell
~0.56 wide. Faces -Y (beak first). Pivot at the centre of the bounds (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 4
LENGTH = 0.80          # cell length, front of the body to the rear (beak excluded)
RADIUS = 0.28          # widest radius
RINGS = 24
SIDES = 24
FLAG_T = 0.20          # where along the body the flagella leave
FLAG_PHI = 0.25        # and where round it (0 = +X side, pi/2 = top)
LONG_FLAG = 0.95
SHORT_FLAG = 0.70
HAIR_LEN = 0.045
HAIRS = 26             # hair pairs along the long flagellum

BODY = (0.86, 0.90, 0.74)
BODY_REAR = (0.80, 0.86, 0.66)
BODY_RIM = (0.93, 0.95, 0.84)
BEAK = (0.82, 0.86, 0.66)
MOUTH = (0.52, 0.58, 0.38)
NUCLEUS = (0.74, 0.79, 0.58)
NUCLEOLUS = (0.50, 0.56, 0.38)
VACUOLE = (0.40, 0.46, 0.20)
VACUOLE_CORE = (0.28, 0.32, 0.12)
FLAG = (0.92, 0.95, 0.84)
HAIR = (0.88, 0.92, 0.80)


def radius(t):
    """Pear profile: narrow front, widest well behind the middle, broad blunt rear."""
    t = min(max(t, 0.0), 1.0)
    front = math.sin(math.pi * 0.5 * min(1.0, t / 0.68)) ** 0.9
    rear = (1.0 - nh.smoothstep(0.68, 1.0, t) ** 2.2) ** 0.5 if t > 0.68 else 1.0
    return RADIUS * (0.22 + 0.78 * front) * rear if t > 0 else 0.0


def flatten(t):
    return 0.95 - 0.20 * nh.smoothstep(0.3, 1.0, t)


def axis(t):
    return Vector((0.0, -LENGTH / 2 + LENGTH * t, 0.0))


def surface(t, phi):
    r = radius(t)
    p = axis(t) + Vector((math.cos(phi) * r, 0, math.sin(phi) * r * flatten(t)))
    n = Vector((math.cos(phi), 0, math.sin(phi) / max(flatten(t), 0.1))).normalized()
    return p, n


def make_body():
    bm = bmesh.new()
    rings = []
    for i in range(RINGS + 1):
        u = i / RINGS
        t = 0.5 - 0.5 * math.cos(u * math.pi)  # denser at both ends
        if i == 0 or i == RINGS:
            rings.append([bm.verts.new(axis(t))])
            continue
        ring = []
        for k in range(SIDES):
            phi = k / SIDES * math.tau
            p, _n = surface(t, phi)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        t = (co.y + LENGTH / 2) / LENGTH
        c = nh.lerp(BODY, BODY_REAR, nh.smoothstep(0.4, 1.0, t))
        # a paler rim round the flanks hints at a translucent cell
        c = nh.lerp(c, BODY_RIM, (1.0 - abs(n.z)) ** 3 * 0.5)
        return tuple(k * (1.0 + 0.03 * noise.noise(co * 10.0)) for k in c)

    return bm, color


def flagellum(base, ctrl, n=20, r0=0.014):
    """Smooth curve from base through quadratic-ish control points; returns points and radii."""
    pts, radii = [], []
    for k in range(n + 1):
        u = k / n
        # Catmull-Rom-free: blend the control polyline with a cubic Bezier
        p0, p1, p2, p3 = base, ctrl[0], ctrl[1], ctrl[2]
        p = (p0 * (1 - u) ** 3 + p1 * 3 * u * (1 - u) ** 2 + p2 * 3 * u * u * (1 - u) + p3 * u ** 3)
        pts.append(p)
        radii.append(r0 * (1.0 - 0.55 * u) if k < n else 0.0)
    return pts, radii


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(*make_body())

    # the beak: a short rounded snout at the front, darkening to the cytostome at its tip
    b0, b1 = axis(0.0) + Vector((0, -0.03, 0.01)), axis(0.0) + Vector((0.0, -0.095, 0.02))

    def beak_col(co, n):
        return nh.lerp(BEAK, MOUTH, nh.smoothstep(b0.y - 0.04, b1.y - 0.01, co.y))

    mb.add(nh.tube([b0 + Vector((0, 0.10, 0)), b0 + Vector((0, 0.04, 0.003)), b0, b1],
                   [0.075, 0.062, 0.052, 0.036], sides=12), beak_col)
    mb.add(nh.ellipsoid(tuple(b1), (0.034, 0.016, 0.034), subdivisions=2), MOUTH)

    # nucleus near the front, bulging the surface a little on the upper side
    np_, nn = surface(0.34, math.radians(105))

    mb.add(nh.uv_ellipsoid(tuple(np_ - nn * 0.062), (0.085, 0.095, 0.078), segments=16, rings=10), NUCLEUS)
    mb.add(nh.uv_ellipsoid(tuple(np_ + nn * 0.0 + Vector((0.015, 0.01, 0))), (0.032, 0.032, 0.022),
                           segments=10, rings=6), NUCLEOLUS)

    # dark olive food vacuoles (eaten bacteria) in the rear half
    for t, phi, r in ((0.62, 1.9, 0.065), (0.74, 0.9, 0.060), (0.82, 2.7, 0.052), (0.56, 0.2, 0.048),
                      (0.88, 1.5, 0.045)):
        p, n = surface(t, phi)
        c = p - n * r * 0.62

        def vac_col(co, nrm, c=c, r=r):
            return nh.lerp(VACUOLE_CORE, VACUOLE, nh.smoothstep(0.0, r, (co - c).length * 1.1))

        mb.add(nh.uv_ellipsoid(tuple(c), (r, r * rng.uniform(0.9, 1.2), r * 0.9), segments=10, rings=7), vac_col)

    # two unequal flagella from the side just behind the front
    root, rn = surface(FLAG_T, FLAG_PHI)
    root = root - rn * 0.01
    # long hairy one: out and forward in a broad arc
    long_pts, long_r = flagellum(root, [root + Vector((0.30, -0.05, 0.06)),
                                        root + Vector((0.42, -0.50, 0.10)),
                                        root + Vector((0.18, -LONG_FLAG + 0.05, 0.04))], n=28, r0=0.015)
    mb.add(nh.tube(long_pts, long_r, sides=5), FLAG)
    # fine side hairs in two opposite rows, perpendicular to the flagellum
    for h in range(HAIRS):
        u = 0.08 + 0.84 * h / (HAIRS - 1)
        i = int(u * (len(long_pts) - 1))
        p, q = long_pts[i], long_pts[min(i + 1, len(long_pts) - 1)]
        d = (q - p).normalized()
        side = d.cross(Vector((0, 0, 1))).normalized()
        ln = HAIR_LEN * (1.0 - 0.4 * u)
        for s in (1, -1):
            tip = p + (side * s * 0.9 + Vector((0, 0, 0.35)) + d * 0.25).normalized() * ln
            mb.add(nh.tube([p, tip], [0.0045, 0.0], sides=3), HAIR)
    # shorter smooth one trailing back along the flank
    sroot = root + Vector((0.0, 0.03, -0.02))
    short_pts, short_r = flagellum(sroot, [sroot + Vector((0.18, 0.02, -0.02)),
                                           sroot + Vector((0.26, 0.40, -0.05)),
                                           sroot + Vector((0.16, SHORT_FLAG, -0.03))], n=22, r0=0.013)
    mb.add(nh.tube(short_pts, short_r, sides=5), FLAG)

    obj = mb.to_object("Telonema", roughness=0.35)
    vs = obj.data.vertices
    mid = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Telonema", views=((35, 35), (0, 85), (-90, 10)))
