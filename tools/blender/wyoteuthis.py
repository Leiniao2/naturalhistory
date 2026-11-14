"""
Procedural Wyoteuthis linsterorum for the map (Swim style).

A Late Jurassic belemnite (about 160 Ma, Sundance Formation, Wyoming): a squid-like
cephalopod with a muscular mantle, a pair of rhombic fins near the rear and ten
roughly equal hooked arms. Its internal guard was unusually short and fat (about
10 cm long and 6 cm across), so the back of the mantle ends in a blunt, barrel-like
point instead of the usual slender bullet. Colours are speculative: reddish-brown
chromatophores over a pale pinkish body, like living squid.

Mantle, head and funnel are fused into one surface (nh_model.MeshBuilder.fuse) and
repainted; the fins, arms (with pale hook rows) and big eyes are crisp shells.

Usage:
  blender --background --python tools/blender/wyoteuthis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Wyoteuthis.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector, Matrix, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

PALE = (0.86, 0.66, 0.56)
DORSAL = (0.52, 0.22, 0.15)
SPOT = (0.38, 0.13, 0.09)
FIN = (0.80, 0.56, 0.46)
FIN_EDGE = (0.55, 0.28, 0.20)
ARM = (0.74, 0.44, 0.34)
HOOK = (0.95, 0.90, 0.80)
EYE = (0.03, 0.03, 0.05)
IRIS = (0.50, 0.46, 0.36)

Y_COLLAR, Y_END = -0.36, 0.98


def _interp(table, y):
    if y <= table[0][0]:
        return table[0][1]
    for (y0, v0), (y1, v1) in zip(table, table[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return table[-1][1]


# mantle radius: full in front, tapering, then the fat guard makes a blunt barrel at the rear
MANTLE_R = [(-0.38, 0.150), (-0.30, 0.172), (-0.10, 0.185), (0.15, 0.172), (0.40, 0.145),
            (0.62, 0.125), (0.78, 0.115), (0.88, 0.095), (0.95, 0.055), (0.985, 0.012)]


def mr(y): return _interp(MANTLE_R, y)


def mantle():
    bm = bmesh.new()
    ny, na = 46, 28
    rings = []
    for i in range(ny):
        y = Y_COLLAR - 0.02 + (Y_END - Y_COLLAR + 0.02) * i / (ny - 1)
        r = mr(y)
        if i == ny - 1:
            rings.append([bm.verts.new((0, y, 0))])
            continue
        ring = []
        for k in range(na):
            a = k / na * math.tau
            # slightly flattened top-to-bottom, like a swimming squid
            ring.append(bm.verts.new((r * math.cos(a), y, r * 0.88 * math.sin(a))))
        rings.append(ring)
    bm.faces.new(list(reversed(rings[0])))
    for a, b in zip(rings, rings[1:]):
        for k in range(na):
            j = (k + 1) % na
            if len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def body_color(p, n):
    rel = p.z / max(abs(p.z) + math.hypot(p.x, 0.0) + 1e-3, 1e-3)  # rough -1..1 belly..back
    up = nh.smoothstep(-0.3, 0.7, rel)
    col = nh.lerp(PALE, DORSAL, up * 0.85)
    # chromatophore speckle, denser on the back
    sp = noise.noise(p * 26.0)
    col = nh.lerp(col, SPOT, nh.smoothstep(0.30, 0.50, sp) * (0.35 + 0.55 * up))
    big = noise.noise(p * 7.0 + Vector((4, 1, 9)))
    col = nh.lerp(col, (col[0] * 0.82, col[1] * 0.78, col[2] * 0.78), nh.smoothstep(0.0, 0.5, big) * up)
    # the blunt rear over the guard is a little paler and smoother
    col = nh.lerp(col, (0.80, 0.58, 0.48), nh.smoothstep(0.80, 0.96, p.y) * 0.5)
    # collar line where the mantle meets the head
    if Y_COLLAR - 0.03 < p.y < Y_COLLAR + 0.015:
        col = nh.lerp(col, SPOT, 0.5)
    return col


def fin(sign):
    """Rhombic fin on the side of the rear mantle."""
    pts = []
    root = [(0.0, 0.30), (0.0, 0.84)]
    outline = [(0.0, 0.84), (0.10, 0.78), (0.20, 0.64), (0.235, 0.56), (0.21, 0.48),
               (0.14, 0.40), (0.06, 0.33), (0.0, 0.30)]
    for u, y in outline:
        x = sign * (mr(y) * 0.80 + u)
        z = 0.012 * u / 0.235 - 0.01
        pts.append((x, y, z))
    if sign < 0:
        pts.reverse()
    bm = nh.flat_panel(pts, thickness=0.014)
    return bm


def fin_color(co, n):
    u = abs(co.x) - mr(co.y) * 0.8
    col = nh.lerp(FIN, FIN_EDGE, nh.smoothstep(0.12, 0.23, u))
    sp = noise.noise(co * 30.0)
    return nh.lerp(col, SPOT, nh.smoothstep(0.35, 0.55, sp) * 0.5 * nh.smoothstep(0.1, 0.0, u - 0.05))


ARM_BASE_Y = -0.62


def arm_path(k):
    """Ten arms in a ring, reaching forward and gathering toward the tips with a gentle curl."""
    a = k / 10 * math.tau + math.pi / 10
    ring = 0.085
    length = 0.42 + 0.03 * math.cos(a * 2.0)
    pts, radii = [], []
    n = 13
    for i in range(n):
        t = i / (n - 1)
        spread = ring * (1.0 + 0.9 * math.sin(t * math.pi * 0.85)) * (1.0 - 0.25 * t)
        curl = 0.05 * t * t
        x = math.cos(a) * spread + curl * math.cos(a + 1.2)
        z = math.sin(a) * spread * 0.9 + curl * math.sin(a + 1.2) - 0.02 * t
        y = ARM_BASE_Y + 0.06 - length * t
        pts.append((x, y, z))
        radii.append(0.030 * (1.0 - 0.85 * t) + 0.002)
    radii[-1] = 0.0
    return pts, radii, a


def arm_color(a):
    inward = Vector((-math.cos(a), 0.0, -math.sin(a)))

    def fn(co, n):
        q = Vector((co.x, 0.0, co.z))
        facing_in = n.dot(inward)
        col = ARM
        band = 0.5 + 0.5 * math.sin(co.y * 60.0)
        col = nh.lerp(col, (0.60, 0.30, 0.22), band * 0.35 * nh.smoothstep(0.0, -0.5, facing_in))
        # two rows of pale hooks on the inner face
        if facing_in > 0.35 and q.length > 0.0:
            hook = 0.5 + 0.5 * math.sin(co.y * 190.0)
            col = nh.lerp(col, HOOK, nh.smoothstep(0.55, 0.9, hook) * nh.smoothstep(0.35, 0.7, facing_in))
        return col
    return fn


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(mantle(), grey)
    # head: a little narrower than the mantle, with bulging eye sockets
    parts.add(nh.ellipsoid(center=(0, -0.48, 0.0), radii=(0.135, 0.17, 0.115), subdivisions=3), grey)
    for s in (-1, 1):
        parts.add(nh.ellipsoid(center=(s * 0.095, -0.47, 0.025), radii=(0.07, 0.08, 0.07), subdivisions=3), grey)
    parts.add(nh.ellipsoid(center=(0, -0.385, 0.0), radii=(0.14, 0.06, 0.12), subdivisions=3), grey)  # neck
    # funnel under the head
    parts.add(nh.tube([(0, -0.30, -0.10), (0, -0.42, -0.12), (0, -0.50, -0.105)], [0.04, 0.032, 0.022], sides=10), grey)
    # arm crown base
    parts.add(nh.ellipsoid(center=(0, -0.60, 0.0), radii=(0.10, 0.08, 0.09), subdivisions=3), grey)
    fused = parts.fuse(voxel=0.03, smooth=4, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(fused, color=body_color)
    for s in (-1, 1):
        mb.add(fin(s), color=fin_color, smooth=False)
        c = Vector((s * 0.148, -0.475, 0.035))
        mb.add(nh.ellipsoid(center=c, radii=(0.035, 0.05, 0.045), subdivisions=2),
               color=lambda co, n, s=s: EYE if n.x * s > 0.5 else IRIS)
    for k in range(10):
        pts, radii, a = arm_path(k)
        mb.add(nh.tube(pts, radii, sides=6, cap_start=False), color=arm_color(a))
    return mb.to_object("Wyoteuthis", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Wyoteuthis", background=(0.05, 0.16, 0.22),
           views=((35, 25), (-90, 8), (150, 35), (0, 90)))
