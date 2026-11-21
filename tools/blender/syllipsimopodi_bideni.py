"""
Procedural Syllipsimopodi bideni for the map (Swim style).

The earliest known vampyropod (the octopus / vampire-squid line of coleoid cephalopods),
from the Early Carboniferous (Mississippian, about 328 Ma) Bear Gulch Limestone of
Montana, about 12 cm long. A squid-like animal: a slender muscular mantle ending in a
point, a pair of rounded fins near the tip, a broad internal gladius (shown as a pale
ridge down the middle of the back), a head with large eyes, and a crown of TEN arms
with rows of suckers - eight shorter arms and two elongated ones, the oldest known
example of that arrangement. Colours are speculative: reddish-brown chromatophore
speckles, paler underside, like living squid.

Mantle, head and funnel are fused into one surface (nh_model.MeshBuilder.fuse) and
repainted; fins, arms (with pale sucker rows) and eyes are crisp shells. Follows the
wyoteuthis.py convention.

Usage:
  blender --background --python tools/blender/syllipsimopodi_bideni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Syllipsimopodi.fbx
Pivot at the body centre, arms forward (-Y), back up (+Z).
"""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

PALE = (0.88, 0.70, 0.60)
DORSAL = (0.58, 0.24, 0.16)
SPOT = (0.40, 0.12, 0.08)
GLADIUS = (0.82, 0.62, 0.50)
FIN = (0.78, 0.50, 0.40)
FIN_EDGE = (0.52, 0.24, 0.17)
ARM = (0.72, 0.40, 0.30)
SUCKER = (0.96, 0.88, 0.78)
EYE = (0.03, 0.03, 0.05)
IRIS = (0.62, 0.55, 0.32)

Y_COLLAR, Y_END = -0.30, 0.78


def _interp(table, y):
    if y <= table[0][0]:
        return table[0][1]
    for (y0, v0), (y1, v1) in zip(table, table[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return table[-1][1]


# slender mantle tapering steadily to a point
MANTLE_R = [(-0.32, 0.105), (-0.24, 0.118), (-0.05, 0.122), (0.20, 0.108), (0.42, 0.085),
            (0.60, 0.058), (0.72, 0.030), (0.775, 0.006)]


def mr(y): return _interp(MANTLE_R, y)


def mantle():
    bm = bmesh.new()
    ny, na = 40, 24
    rings = []
    for i in range(ny):
        y = Y_COLLAR - 0.02 + (Y_END - Y_COLLAR + 0.02) * i / (ny - 1)
        r = mr(y)
        if i == ny - 1:
            rings.append([bm.verts.new((0, y, 0))])
            continue
        rings.append([bm.verts.new((r * math.cos(k / na * math.tau), y, r * 0.9 * math.sin(k / na * math.tau)))
                      for k in range(na)])
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
    r = max(math.hypot(p.x, p.z), 1e-3)
    up = nh.smoothstep(-0.3, 0.7, p.z / r)
    col = nh.lerp(PALE, DORSAL, up * 0.85)
    sp = noise.noise(p * 30.0)
    col = nh.lerp(col, SPOT, nh.smoothstep(0.28, 0.48, sp) * (0.3 + 0.6 * up))
    # the internal gladius: a pale ridge down the middle of the back of the mantle
    if p.y > Y_COLLAR and p.z > 0:
        g = nh.smoothstep(0.035, 0.012, abs(p.x)) * nh.smoothstep(0.74, 0.6, p.y)
        col = nh.lerp(col, GLADIUS, 0.8 * g)
    if Y_COLLAR - 0.025 < p.y < Y_COLLAR + 0.01:
        col = nh.lerp(col, SPOT, 0.5)
    return col


def fin(sign):
    """Rounded paddle fin near the mantle tip."""
    outline = [(0.0, 0.73), (0.06, 0.72), (0.12, 0.66), (0.14, 0.58), (0.12, 0.50), (0.07, 0.45), (0.0, 0.44)]
    pts = [(sign * (mr(y) * 0.8 + u), y, -0.005 + 0.01 * u / 0.14) for u, y in outline]
    if sign < 0:
        pts.reverse()
    return nh.flat_panel(pts, thickness=0.012)


def fin_color(co, n):
    u = abs(co.x) - mr(co.y) * 0.8
    col = nh.lerp(FIN, FIN_EDGE, nh.smoothstep(0.08, 0.14, u))
    return nh.lerp(col, SPOT, nh.smoothstep(0.35, 0.55, noise.noise(co * 32.0)) * 0.5)


ARM_BASE_Y = -0.52
LONG = (1, 6)   # the two elongated arms (ventro-lateral pair)


def arm_path(k):
    a = k / 10 * math.tau + math.pi / 10
    long = k in LONG
    ring = 0.065
    length = 0.62 if long else 0.30 + 0.02 * math.cos(a * 2.0)
    pts, radii = [], []
    n = 16 if long else 11
    for i in range(n):
        t = i / (n - 1)
        spread = ring * (1.0 + (0.6 if long else 1.0) * math.sin(t * math.pi * 0.85)) * (1.0 - 0.3 * t)
        curl = (0.03 if long else 0.045) * t * t
        x = math.cos(a) * spread + curl * math.cos(a + 1.2)
        z = math.sin(a) * spread * 0.9 + curl * math.sin(a + 1.2) - 0.02 * t
        pts.append((x, ARM_BASE_Y + 0.05 - length * t, z))
        if long:  # thin stalk, slightly broader sucker-bearing tip
            radii.append(0.020 * (1.0 - 0.6 * t) + 0.006 * nh.smoothstep(0.7, 0.9, t) * (1 - nh.smoothstep(0.95, 1.0, t)))
        else:
            radii.append(0.024 * (1.0 - 0.85 * t) + 0.002)
    radii[-1] = 0.0
    return pts, radii, a, long


def arm_color(a, long):
    inward = Vector((-math.cos(a), 0.0, -math.sin(a)))

    def fn(co, n):
        facing_in = n.dot(inward)
        col = nh.lerp(ARM, (0.56, 0.26, 0.18), 0.4 * nh.smoothstep(0.0, -0.6, facing_in))
        on = (co.y < ARM_BASE_Y - 0.40) if long else True
        if facing_in > 0.3 and on:
            s = 0.5 + 0.5 * math.sin(co.y * 170.0)
            col = nh.lerp(col, SUCKER, nh.smoothstep(0.5, 0.85, s) * nh.smoothstep(0.3, 0.65, facing_in))
        return col
    return fn


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(mantle(), grey)
    parts.add(nh.ellipsoid(center=(0, -0.40, 0.0), radii=(0.10, 0.13, 0.085), subdivisions=3), grey)
    for s in (-1, 1):
        parts.add(nh.ellipsoid(center=(s * 0.075, -0.40, 0.02), radii=(0.06, 0.07, 0.06), subdivisions=3), grey)
    parts.add(nh.ellipsoid(center=(0, -0.32, 0.0), radii=(0.10, 0.05, 0.085), subdivisions=3), grey)
    parts.add(nh.tube([(0, -0.25, -0.075), (0, -0.35, -0.09), (0, -0.42, -0.08)], [0.03, 0.024, 0.017], sides=10), grey)
    parts.add(nh.ellipsoid(center=(0, -0.50, 0.0), radii=(0.075, 0.06, 0.068), subdivisions=3), grey)
    fused = parts.fuse(voxel=0.022, smooth=4, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(fused, color=body_color)
    for s in (-1, 1):
        mb.add(fin(s), color=fin_color, smooth=False)
        c = Vector((s * 0.125, -0.405, 0.03))
        mb.add(nh.ellipsoid(center=c, radii=(0.036, 0.052, 0.047), subdivisions=2),
               color=lambda co, n, s=s: EYE if n.x * s > 0.55 else IRIS)
    for k in range(10):
        pts, radii, a, long = arm_path(k)
        mb.add(nh.tube(pts, radii, sides=6, cap_start=False), color=arm_color(a, long))
    obj = mb.to_object("Syllipsimopodi", roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, "Syllipsimopodi", background=(0.05, 0.16, 0.22),
           views=((35, 25), (-90, 8), (150, 35), (0, 90)))
