"""
Procedural high-detail electric eel (Electrophorus electricus) for the map (Swim style).

A long, round-bodied knifefish: broad flattened head with a wide terminal mouth
and tiny eyes, no dorsal fin, small paddle pectorals, and one long undulating
anal fin running along the belly from just behind the throat to the tail tip.
Dark olive-grey above, an orange-red throat and chin and a warm underside on the
front of the body, rows of pale sensory pores on the head.

The body is a lofted shell fused into one seamless surface (nh_model.MeshBuilder.fuse),
given a fine skin grain and a mouth groove, then repainted procedurally. The rippling
anal fin, pectorals and eyes are crisp separate shells. The whole animal is bent into
a gentle swimming S-curve at the end.

Usage:
  blender --background --python tools/blender/electrophorus_electricus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ElectricEel.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector, Matrix, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

VOXEL = 0.0105

BACK = (0.33, 0.34, 0.24)       # dark olive-slate
FLANK = (0.60, 0.60, 0.46)      # lighter grey-olive
UNDER = (0.84, 0.58, 0.20)       # orange-yellow       # warm underside of the front half
THROAT = (0.86, 0.36, 0.10)      # orange-red chin and throat
PORE = (0.62, 0.60, 0.50)
LIP = (0.07, 0.06, 0.05)
FIN = (0.28, 0.28, 0.22)
FIN_EDGE = (0.56, 0.53, 0.44)
EYE = (0.03, 0.03, 0.04)
EYE_RING = (0.55, 0.45, 0.20)

Y_TIP, Y_END = -1.0, 1.0
Y_MOUTH_BACK = -0.905   # corner of the mouth
Y_FIN0 = -0.70          # anal fin starts just behind the throat


def _interp(table, y):
    """Smoothstep-blended piecewise interpolation through (y, value) points."""
    if y <= table[0][0]:
        return table[0][1]
    for (y0, v0), (y1, v1) in zip(table, table[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return table[-1][1]


HALF_W = [(-1.0, 0.012), (-0.985, 0.04), (-0.95, 0.058), (-0.9, 0.07), (-0.82, 0.076), (-0.6, 0.077),
          (-0.3, 0.073), (0.0, 0.066), (0.3, 0.054), (0.55, 0.040), (0.78, 0.024), (0.93, 0.010), (1.0, 0.002)]
HALF_TOP = [(-1.0, 0.010), (-0.985, 0.026), (-0.95, 0.040), (-0.9, 0.052), (-0.82, 0.064), (-0.6, 0.076),
            (-0.3, 0.080), (0.0, 0.078), (0.3, 0.070), (0.55, 0.058), (0.78, 0.040), (0.93, 0.018), (1.0, 0.003)]
HALF_BOT = [(-1.0, 0.010), (-0.985, 0.024), (-0.95, 0.036), (-0.9, 0.050), (-0.82, 0.066), (-0.6, 0.080),
            (-0.3, 0.085), (0.0, 0.082), (0.3, 0.072), (0.55, 0.058), (0.78, 0.040), (0.93, 0.018), (1.0, 0.003)]
CENTER_Z = [(-1.0, -0.008), (-0.9, 0.0), (1.0, 0.0)]


def w(y): return _interp(HALF_W, y)
def ht(y): return _interp(HALF_TOP, y)
def hb(y): return _interp(HALF_BOT, y)
def zc(y): return _interp(CENTER_Z, y)


def section(y, a):
    """Rounded-square cross-section (flatter on the head, round on the trunk)."""
    n = 2.0 + 0.8 * (1.0 - nh.smoothstep(-0.95, -0.75, y))
    c, s = math.cos(a), math.sin(a)
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    z = zc(y) + (ht(y) if s >= 0 else hb(y)) * math.copysign(abs(s) ** (2.0 / n), s)
    return Vector((x, y, z))


def loft(y0, y1, ny, na):
    bm = bmesh.new()
    ys = [y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(i / (ny - 1) * math.pi)) for i in range(ny)]
    rings = []
    for i, y in enumerate(ys):
        if i in (0, ny - 1):
            p = sum((section(y, k / na * math.tau) for k in range(na)), Vector()) / na
            rings.append([bm.verts.new(p)])
        else:
            rings.append([bm.verts.new(section(y, k / na * math.tau)) for k in range(na)])
    for a, b in zip(rings, rings[1:]):
        for k in range(na):
            j = (k + 1) % na
            if len(a) == 1:
                bm.faces.new([a[0], b[j], b[k]])
            elif len(b) == 1:
                bm.faces.new([a[k], a[j], b[0]])
            else:
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- surface detail

def mouth_z(y):
    """The lip line: a wide gape that rises slightly toward the snout (lower jaw juts a little)."""
    return zc(y) - 0.004 - 0.010 * nh.smoothstep(-0.92, -0.99, y)


def mouth_amount(p):
    """0..1 groove strength along the lip line on the front and sides of the snout."""
    if p.y > Y_MOUTH_BACK + 0.01:
        return 0.0
    d = abs(p.z - mouth_z(p.y))
    corner = 1.0 - nh.smoothstep(Y_MOUTH_BACK - 0.02, Y_MOUTH_BACK + 0.01, p.y)
    return (1.0 - nh.smoothstep(0.0015, 0.006, d)) * corner


PORES = []  # (position, radius) of the pale sensory pores on the head, set in build()


def make_pores():
    """Rows of pores along the top and sides of the head, like the real lateral-line canals."""
    pts = []
    for row, (frac, n_pores) in enumerate(((0.92, 9), (0.55, 11), (0.05, 10), (-0.45, 8))):
        for side in (-1, 1):
            for i in range(n_pores):
                y = -0.975 + i * (0.20 / n_pores) + (0.008 if row % 2 else 0.0)
                a = math.asin(max(-1.0, min(1.0, frac)))
                ang = a if side > 0 else math.pi - a
                y += noise.noise(Vector((i * 1.7, row * 3.1, side))) * 0.006
                if noise.noise(Vector((i * 2.3, row, side * 5.0))) > 0.35:
                    continue  # a few gaps so the rows don't read as a grid
                p = section(y, ang)
                pts.append((p, 0.0028 + 0.0008 * (row == 1)))
    return pts


def pore_amount(p):
    if p.y > -0.72:
        return 0.0
    best = 0.0
    for c, r in PORES:
        d = (p - c).length
        if d < r * 2:
            best = max(best, 1.0 - nh.smoothstep(r * 0.5, r * 1.6, d))
    return best


def skin_detail(bm):
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 70.0) * 0.0005 + noise.noise(p * 18.0 + Vector((2, 5, 1))) * 0.0010
        # faint myomere ripples along the trunk
        if p.y > -0.75:
            d += 0.0006 * math.sin(p.y * 160.0) * nh.smoothstep(0.5, 0.0, abs(p.z) / max(ht(p.y), 1e-3))
        d -= mouth_amount(p) * 0.006
        d -= pore_amount(p) * 0.0014
        v.co = p + v.normal * d


def body_color(p, n):
    y = p.y
    rel = (p.z - zc(y)) / max(ht(y) if p.z >= zc(y) else hb(y), 1e-3)   # -1 belly .. 1 back
    up = nh.smoothstep(-0.45, 0.95, rel)
    col = nh.lerp(FLANK, BACK, up)
    mott = noise.noise(p * 9.0 + Vector((1, 2, 3))) * 0.5 + 0.5
    col = nh.lerp(col, (col[0] * 0.8, col[1] * 0.8, col[2] * 0.78), mott * 0.35)
    # warm underside on the front of the body, fading out toward the tail
    front = 1.0 - nh.smoothstep(-0.45, -0.15, y)   # front third
    under = (1.0 - nh.smoothstep(-0.55, -0.15, rel)) * front
    col = nh.lerp(col, UNDER, under * 0.9)
    # orange-red chin and throat
    throat = (1.0 - nh.smoothstep(-0.65, -0.2, rel)) * (1.0 - nh.smoothstep(-0.80, -0.62, y))
    col = nh.lerp(col, THROAT, throat)
    # the lower jaw is orange right up to the lip; dark upper lip
    if y < Y_MOUTH_BACK + 0.02 and p.z < mouth_z(y):
        col = nh.lerp(col, THROAT, 0.7 * (1.0 - nh.smoothstep(-0.95, -0.9, y)))
    col = nh.lerp(col, LIP, mouth_amount(p))
    # sparse pale spots along the flanks
    if -0.7 < y < 0.8 and -0.5 < rel < 0.6:
        spot = noise.noise(Vector((p.x * 30.0, y * 26.0, p.z * 30.0)))
        col = nh.lerp(col, (0.44, 0.41, 0.33), nh.smoothstep(0.40, 0.55, spot) * 0.6)
    col = nh.lerp(col, PORE, pore_amount(p) * 0.9)
    return col


# ---------------------------------------------------------------- fins and eyes

def anal_fin():
    """Long rippling ribbon along the belly; taller toward the middle, wrapping the tail tip."""
    bm = bmesh.new()
    ny, nv = 220, 6
    thick = 0.0035
    rows_l, rows_r = [], []
    for i in range(ny):
        t = i / (ny - 1)
        y = Y_FIN0 + (Y_END + 0.012 - Y_FIN0) * t
        root = zc(min(y, Y_END)) - hb(min(y, Y_END)) * 0.75
        h = 0.075 * nh.smoothstep(0.0, 0.10, t) * (1.0 - 0.75 * nh.smoothstep(0.55, 1.0, t)) + 0.006
        ring_l, ring_r = [], []
        for k in range(nv):
            v = k / (nv - 1)
            # travelling wave: rays sway sideways more toward the free edge
            sway = 0.018 * v ** 1.5 * math.sin(y * 17.0 + 0.6) * (0.4 + 0.6 * nh.smoothstep(0.0, 0.2, t))
            z = root - h * v - 0.004 * v
            back = 0.010 * v  # rays rake backward a little
            p = Vector((sway, y + back, z))
            tk = thick * (1.0 - 0.6 * v)
            ring_l.append(bm.verts.new(p + Vector((-tk, 0, 0))))
            ring_r.append(bm.verts.new(p + Vector((tk, 0, 0))))
        rows_l.append(ring_l)
        rows_r.append(ring_r)
    for i in range(ny - 1):
        for k in range(nv - 1):
            bm.faces.new([rows_l[i][k], rows_l[i + 1][k], rows_l[i + 1][k + 1], rows_l[i][k + 1]])
            bm.faces.new([rows_r[i][k], rows_r[i][k + 1], rows_r[i + 1][k + 1], rows_r[i + 1][k]])
        bm.faces.new([rows_l[i][-1], rows_l[i + 1][-1], rows_r[i + 1][-1], rows_r[i][-1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def fin_color(co, n):
    root = zc(min(co.y, Y_END)) - hb(min(co.y, Y_END)) * 0.75
    v = max(0.0, root - co.z)
    edge = nh.smoothstep(0.045, 0.075, v) if co.y < 0.75 else nh.smoothstep(0.014, 0.03, v)
    rays = 0.5 + 0.5 * math.sin(co.y * 900.0)
    col = nh.lerp(FIN, (FIN[0] * 0.8, FIN[1] * 0.8, FIN[2] * 0.8), rays * 0.3)
    return nh.lerp(col, FIN_EDGE, edge * 0.85)


def pectoral(sign):
    """Small rounded paddle just behind the head, angled back and slightly down."""
    outline = []
    for k in range(14):
        a = k / 14 * math.tau
        outline.append((0.026 * math.cos(a) + 0.022, 0.018 * math.sin(a), 0.0))
    bm = nh.flat_panel(outline, thickness=0.0035)
    m = (Matrix.Translation(Vector((sign * w(-0.78) * 0.88, -0.775, zc(-0.78) - 0.018)))
         @ Matrix.Rotation(sign * math.radians(-55), 4, "Z")
         @ Matrix.Rotation(sign * math.radians(-25), 4, "Y")
         @ Matrix.Scale(-1 if sign < 0 else 1, 4, Vector((1, 0, 0))))
    nh.transform(bm, m)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def eye(sign):
    y = -0.935
    p = section(y, math.radians(30) if sign > 0 else math.radians(150))
    c = p + Vector((sign * -0.002, 0, 0))
    return nh.ellipsoid(center=c, radii=(0.0055, 0.0065, 0.0055), subdivisions=2)


def eye_color(sign):
    def fn(co, n):
        outward = n.x * sign
        return EYE if outward > 0.75 else EYE_RING
    return fn


# ---------------------------------------------------------------- pose

def bend(bm):
    """Gentle swimming S-curve in plan view; the head stays nearly straight."""
    for v in bm.verts:
        y = v.co.y
        env = nh.smoothstep(-0.95, 0.9, y)
        v.co.x += 0.21 * env * math.sin((y + 0.75) * 3.6)


def build():
    global PORES
    PORES = make_pores()
    parts = nh.MeshBuilder()
    parts.add(loft(Y_TIP, Y_END, 240, 44), (0.5, 0.5, 0.5))
    fused = parts.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    skin_detail(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, color=body_color)
    mb.add(anal_fin(), color=fin_color)
    for s in (-1, 1):
        mb.add(pectoral(s), color=fin_color)
        mb.add(eye(s), color=eye_color(s))
    bend(mb.bm)
    return mb.to_object("ElectricEel", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "ElectricEel", background=(0.10, 0.12, 0.08),
           views=((35, 25), (-90, 8), (150, 35), (0, 90), (20, -30)))
