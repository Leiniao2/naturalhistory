"""
Procedural low-poly Paramecium caudatum (slipper animalcule) for colony instancing.

A slipper-shaped cell (blunt front, tapering rear) with a diagonal oral groove
running back to the mouth pocket, a fuzz of short cilia all over, two
star-shaped contractile vacuoles, a darker kidney-shaped macronucleus showing
through, and a few food vacuoles. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/paramecium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Paramecium.fbx
Faces -Y (front), long axis along Y, ~1.6 units long. Pivot at the body centre.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh
from mathutils import Vector, noise

import nh_model as nh

SEED = 11
LENGTH = 0.8            # half-length along Y
RADIUS = (0.25, 0.19)   # half-width (X) and half-height (Z) at the widest point
CILIA_COUNT = 700
CILIA_LENGTH = 0.028

# Palette
BODY = (0.80, 0.88, 0.66)        # pale translucent green-cream
BODY_RIM = (0.66, 0.78, 0.52)    # slightly deeper toward the ends
GROOVE = (0.52, 0.62, 0.38)      # oral groove shadow
NUCLEUS = (0.46, 0.42, 0.32)     # darker macronucleus seen through
CILIA_BASE = (0.85, 0.92, 0.75)
CILIA_TIP = (0.93, 0.97, 0.92)
VACUOLE = (0.62, 0.84, 0.96)     # clear blue contractile vacuole
FOOD = [(0.55, 0.62, 0.30), (0.62, 0.52, 0.30), (0.45, 0.55, 0.32)]

# Oral groove: runs diagonally from the front tip back to the mouth, on the upper flank so it
# reads from the map camera.
GROOVE_T = (-0.92, 0.05)        # t range along the body (-1 = front, +1 = rear)
GROOVE_PHI = (0.05, 1.3)     # angle around the body at the start / end (radians, atan2(z, x))
GROOVE_WIDTH = 0.26
MOUTH_T = 0.05

NUCLEUS_CENTER = (0.02, 0.08)   # (x, y) of the macronucleus, projected along Z
NUCLEUS_RADII = (0.13, 0.24)
VACUOLE_TS = (-0.5, 0.52)       # contractile vacuoles near each end, on the far upper flank
VACUOLE_PHI = 2.15


def profile(t):
    """Cross-section scale along the body: blunt front, tapering pointed rear."""
    if t < 0:  # superellipse: rounded, blunt front
        return (1.0 - min(1.0, -t) ** 3.4) ** (1 / 3.4) * (1.0 + 0.06 * -t)
    return (1.0 - min(1.0, t) ** 2.0) ** 0.5 * (1.0 - 0.38 * t * t)


def groove_phi(t):
    k = (t - GROOVE_T[0]) / (GROOVE_T[1] - GROOVE_T[0])
    return GROOVE_PHI[0] + (GROOVE_PHI[1] - GROOVE_PHI[0]) * k


def groove_amount(t, phi):
    """0..1 how deep in the oral groove a point at (t, phi) is."""
    if t < GROOVE_T[0] - 0.05 or t > GROOVE_T[1] + 0.08:
        return 0.0
    d = math.atan2(math.sin(phi - groove_phi(t)), math.cos(phi - groove_phi(t)))
    across = math.exp(-(d / GROOVE_WIDTH) ** 2)
    along = nh.smoothstep(GROOVE_T[0] - 0.05, GROOVE_T[0] + 0.25, t) * \
        (1.0 - nh.smoothstep(GROOVE_T[1] - 0.05, GROOVE_T[1] + 0.08, t))
    # deeper toward the mouth pocket
    return across * along * (0.55 + 0.45 * nh.smoothstep(GROOVE_T[0], GROOVE_T[1], t))


def body_point(x, y, z):
    """Maps a unit-sphere point to the slipper surface (before the groove indent)."""
    t = y
    f = profile(t)
    # gentle spiral twist so it doesn't look like a perfect egg
    twist = 0.25 * t
    cx, cz = math.cos(twist), math.sin(twist)
    rx, rz = x * cx - z * cz, x * cz + z * cx
    return Vector((rx * RADIUS[0] * f, t * LENGTH, rz * RADIUS[1] * f))


def make_body():
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=20, radius=1.0)
    # uv sphere poles are on Z; rotate so the poles lie on the long (Y) axis
    for v in bm.verts:
        n = v.co.normalized()
        x, y, z = n.x, n.z, -n.y
        t = y
        phi = math.atan2(z, x)
        p = body_point(x, y, z)
        g = groove_amount(t, phi)
        mouth = math.exp(-((t - MOUTH_T) / 0.1) ** 2) * math.exp(-(
            math.atan2(math.sin(phi - GROOVE_PHI[1]), math.cos(phi - GROOVE_PHI[1])) / 0.4) ** 2)
        radial = Vector((p.x, 0, p.z))
        indent = 0.035 * g + 0.05 * mouth
        if radial.length > 1e-6:
            p -= radial.normalized() * indent * min(1.0, radial.length / 0.1)
        # faint surface ripple (pellicle)
        p += radial.normalized() * noise.noise(Vector((x, y, z)) * 6.0) * 0.006 if radial.length > 1e-6 else Vector()
        v.co = p
    bm.normal_update()
    return bm


def body_color(co, normal):
    t = co.y / LENGTH
    phi = math.atan2(co.z, co.x)
    col = nh.lerp(BODY, BODY_RIM, nh.smoothstep(0.55, 0.95, abs(t)))
    # macronucleus seen through from above and below
    nx = (co.x - NUCLEUS_CENTER[0]) / NUCLEUS_RADII[0]
    ny = (co.y - NUCLEUS_CENTER[1]) / NUCLEUS_RADII[1]
    nd = math.sqrt(nx * nx + ny * ny)
    col = nh.lerp(col, NUCLEUS, (1.0 - nh.smoothstep(0.6, 1.0, nd)) * 0.95)
    # oral groove shadow
    g = groove_amount(t, phi)
    col = nh.lerp(col, GROOVE, min(1.0, g * 1.6))
    # mottled cytoplasm
    m = noise.noise(co * 9.0)
    col = tuple(c * (1.0 + 0.05 * m) for c in col)
    return col


def surface_at(t, phi):
    """Point and outward normal on the body surface at (t, phi), sampled numerically."""
    def pt(tt, pp):
        r = math.sqrt(max(0.0, 1.0 - tt * tt))
        x, z = math.cos(pp) * r, math.sin(pp) * r
        p = body_point(x, tt, z)
        g = groove_amount(tt, pp)
        radial = Vector((p.x, 0, p.z))
        if radial.length > 1e-6:
            p -= radial.normalized() * 0.035 * g * min(1.0, radial.length / 0.1)
        return p
    p = pt(t, phi)
    dt = pt(min(t + 0.01, 0.999), phi) - pt(max(t - 0.01, -0.999), phi)
    dp = pt(t, phi + 0.01) - pt(t, phi - 0.01)
    n = dp.cross(dt).normalized()
    if n.dot(Vector((p.x, p.y * 0.3, p.z))) < 0:
        n = -n
    return p, n


def make_cilia(rng):
    """Short, thin 3-sided cones all over the surface, swept slightly backwards."""
    bm = bmesh.new()
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(CILIA_COUNT):
        t = 1.0 - (i + 0.5) / CILIA_COUNT * 2.0
        t = max(-0.97, min(0.97, t))
        phi = golden * i + rng.uniform(-0.15, 0.15)
        p, n = surface_at(t, phi)
        g = groove_amount(t, phi)
        length = CILIA_LENGTH * rng.uniform(0.8, 1.2) * (1.5 if g > 0.3 else 1.0)  # longer oral cilia
        if t > 0.92:
            length *= 1.8  # caudal tuft (P. caudatum)
        sweep = Vector((0, 1, 0))
        d = (n + sweep * 0.6).normalized()
        side = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
        up = side.cross(d)
        r = 0.0045
        base = [bm.verts.new(p - n * 0.004 + (side * math.cos(a) + up * math.sin(a)) * r)
                for a in (0.0, math.tau / 3, 2 * math.tau / 3)]
        tip = bm.verts.new(p + d * length)
        for k in range(3):
            bm.faces.new([base[k], base[(k + 1) % 3], tip])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        # tips sit farther from the body axis than bases
        radial = math.hypot(co.x / RADIUS[0], co.z / RADIUS[1])
        return nh.lerp(CILIA_BASE, CILIA_TIP, nh.smoothstep(0.6, 1.1, radial))

    return bm, color


def make_contractile_vacuole(t, rng, mb):
    """Clear bubble with 6 radiating canals: the 'star' of the contractile vacuole (dorsal side)."""
    phi = VACUOLE_PHI + rng.uniform(-0.1, 0.1)
    p, n = surface_at(t, phi)
    mb.add(nh.ellipsoid(center=p - n * 0.012, radii=(0.03, 0.03, 0.02), subdivisions=2), VACUOLE)
    # canals along the surface
    tangent_a = Vector((0, 1, 0))
    tangent_a = (tangent_a - n * tangent_a.dot(n)).normalized()
    tangent_b = n.cross(tangent_a)
    for k in range(6):
        a = k / 6 * math.tau + rng.uniform(-0.15, 0.15)
        d = tangent_a * math.cos(a) + tangent_b * math.sin(a)
        pts, radii = [], []
        for s, r in ((0.02, 0.007), (0.05, 0.005), (0.08, 0.0)):
            q = p + d * s
            # project back onto the surface roughly
            qt = max(-0.98, min(0.98, q.y / LENGTH))
            qphi = math.atan2(q.z, q.x)
            sp, sn = surface_at(qt, qphi)
            pts.append(sp + sn * 0.002)
            radii.append(r)
        mb.add(nh.tube(pts, radii, sides=4), VACUOLE)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(make_body(), body_color)
    mb.add(*make_cilia(rng))

    for t in VACUOLE_TS:
        make_contractile_vacuole(t, rng, mb)

    # food vacuoles: small half-sunk spheres near the mouth and along the body
    for t, phi in ((0.18, 1.0), (0.32, 0.4), (-0.15, 2.6), (0.4, 1.8), (0.0, -0.6), (0.25, -1.6)):
        p, n = surface_at(t, phi)
        r = rng.uniform(0.035, 0.05)
        mb.add(nh.ellipsoid(center=p - n * r * 0.45, radii=(r, r, r), subdivisions=1), rng.choice(FOOD))

    return mb.to_object("Paramecium", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Paramecium", views=((35, 40), (-80, 15), (180, 60)))
