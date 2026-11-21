"""
Shared body-plan helpers for the batch-2 Ediacaran species (bradgatia_linfordensis.py,
mawsonites_spriggi.py, thectardis_avalonensis.py, ...). Builds on nh_model.py.

  * grid(rows, ...)              quad grid from rows of (co, rgb); closed rings, fan caps
  * lathe(nv, nu, shape, color)  surface of revolution: shape(u, v) -> (r, z)
  * polar_disc(R, height, color) low disc heightfield over a flat base (discs, trilobozoans)
  * blade(...)                   a lens-section leaf growing up +Z, front face -Y (fronds)
  * rangeo(s, v, ...)            rangeomorph branching pattern (primary furrows, secondaries)
  * place(bm, x, y, yaw, lean)   rotate / move a shell
  * mat(mb, radius, seed)        microbial-mat patch to root sessile animals on
  * finish(mb, name, fixed)      MeshBuilder -> object, pivot on z = 0 (Fixed) or centred
  * export(build, name, ...)     nh.run with a seawater preview

All animals face -Y, Z up, colour in vertex colours (see nh_model.py).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402

MAT = (0.40, 0.38, 0.27)
MAT_LIGHT = (0.55, 0.51, 0.38)
SAND = (0.66, 0.60, 0.46)
SEA_BG = (0.05, 0.14, 0.18)
GROUND = (0.50, 0.48, 0.38)


def grid(rows, closed=True, cap_start=True, cap_end=True):
    """rows: list of lists of (co, rgb). Returns (bm, {vert: rgb})."""
    bm = bmesh.new()
    vcol = {}
    R = []
    for row in rows:
        r = []
        for co, c in row:
            v = bm.verts.new(Vector(co))
            vcol[v] = c
            r.append(v)
        R.append(r)
    n = len(R[0])
    for a, b in zip(R, R[1:]):
        for k in range(n if closed else n - 1):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    for ring, cap in ((R[0], cap_start), (R[-1], cap_end)):
        if not cap:
            continue
        cen = sum((v.co for v in ring), Vector()) / n
        cv = bm.verts.new(cen)
        vcol[cv] = vcol[ring[0]]
        for k in range(n):
            bm.faces.new([ring[k], ring[(k + 1) % n], cv])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def lathe(nv, nu, shape, color, cap_start=True, cap_end=True):
    """Surface of revolution. shape(u, v) -> (r, z) with u in [0, 1) round the axis (u = 0 at
    -Y, the front) and v in [0, 1] along the profile; color(u, v, co) -> rgb."""
    rows = []
    for i in range(nv + 1):
        v = i / nv
        row = []
        for k in range(nu):
            u = k / nu
            th = -math.pi / 2 + u * math.tau
            r, z = shape(u, v)
            co = Vector((r * math.cos(th), r * math.sin(th), z))
            row.append((co, color(u, v, co)))
        rows.append(row)
    return grid(rows, True, cap_start, cap_end)


def polar_disc(R, height, color, rings=24, segs=72, base_inset=0.96, base_color=None):
    """Disc of radius R: top surface z = height(r, th) (r as a fraction of R, th in radians from
    -Y), a short wall down to a flat base at z = 0. color(r, th, co) -> rgb."""
    rows = []
    for i in range(rings + 1):
        r = max(0.004, (i / rings) ** 0.85)
        row = []
        for k in range(segs):
            th = -math.pi / 2 + k / segs * math.tau
            co = Vector((r * R * math.cos(th), r * R * math.sin(th), height(r, th)))
            row.append((co, color(r, th, co)))
        rows.append(row)
    last = rows[-1]
    bc = base_color or tuple(c * 0.8 for c in last[0][1])
    rows.append([(Vector((co.x * base_inset, co.y * base_inset, 0.0)), bc) for co, _ in last])
    return grid(rows, True, True, True)


def rangeo(s, v, primaries, slant=1.0, secondaries=4, offset=True):
    """Rangeomorph pattern at (s across -1..1, v along 0..1). Returns (furrow 0..1, sec 0..1):
    primary branches climb obliquely out from the midline, alternating between the sides."""
    off = 0.5 if (offset and s < 0) else 0.0
    ph = v * primaries - abs(s) * slant + off
    t = ph % 1.0
    furrow = 1.0 - nh.smoothstep(0.0, 0.2, min(t, 1.0 - t))
    sec = 0.5 + 0.5 * math.cos(abs(s) * secondaries * math.tau + t * 1.5)
    return furrow, sec


def blade(length, width, wfn, relief, color, nv=40, nu=24, thick=0.02, cup=0.0, bend=None):
    """Leaf growing from z = 0 up +Z, flat in the XZ plane, its front face toward -Y.
    wfn(v): half-width fraction; relief(s, v, front) -> outward bump; color(s, v, front) -> rgb;
    cup: edges curl toward -Y by cup * half-width; bend(v) -> y offset of the midline."""
    rows = []
    for i in range(nv + 1):
        v = i / nv
        W = width * max(wfn(v), 0.004)
        row = []
        for k in range(nu):
            a = k / nu * math.tau
            s, f = math.cos(a), math.sin(a)
            front = f > 0
            lens = math.sqrt(max(0.0, 1 - s * s))
            y = -f * thick * 0.5 * (0.3 + 0.7 * lens)
            y += -relief(s, v, front) if front else relief(s, v, front) * 0.6
            y -= cup * W * s * s
            if bend:
                y += bend(v)
            co = Vector((s * W, y, v * length))
            row.append((co, color(s, v, front)))
        rows.append(row)
    return grid(rows, True, True, True)


def place(bm, x=0.0, y=0.0, yaw=0.0, lean=0.0, z=0.0, roll=0.0):
    m = (Matrix.Translation(Vector((x, y, z))) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
         @ Matrix.Rotation(math.radians(lean), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Y"))
    nh.transform(bm, m)
    return bm


def add(mb, part):
    bm, vcol = part
    nf.add_colored(mb, bm, vcol)


def mat(mb, radius, seed=(2.0, 5.0, 1.0), squash=0.88, light=SAND):
    """Low, wrinkled microbial-mat patch."""
    sv = Vector(seed)
    bm = nh.uv_ellipsoid((0.0, 0.0, -0.03), (radius, radius * squash, 0.05), 24, 6,
                         deform=lambda n: 1.0 + 0.08 * noise.noise(n * 4.0 + sv))

    def col(co, n):
        m = noise.noise(co * 5.0 + sv) * 0.5 + 0.5
        wrinkle = abs(noise.noise(co * 20.0 + sv))
        c = nh.lerp(MAT, MAT_LIGHT, 0.2 + 0.5 * m)
        c = nh.lerp(c, (0.22, 0.22, 0.15), nh.smoothstep(0.08, 0.0, wrinkle) * 0.5)
        return nh.lerp(c, light, nh.smoothstep(0.55, 0.95, math.hypot(co.x, co.y / squash) / radius))

    mb.add(bm, col)


def mottle(c, co, amount=0.07, scale=14.0):
    k = 1.0 + amount * noise.noise(Vector(co) * scale)
    return tuple(min(1.0, x * k) for x in c)


def finish(mb, name, fixed=True, roughness=0.7):
    obj = mb.to_object(name, roughness=roughness)
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    if fixed:
        for v in obj.data.vertices:
            v.co.z = max(v.co.z, -0.012)
        zmin = min(v.co.z for v in obj.data.vertices)
        obj.data.transform(Matrix.Translation((-mid.x, -mid.y, -zmin)))
    else:
        obj.data.transform(Matrix.Translation(-mid))
    return obj


def export(build, name, fixed=True, views=None):
    if views is None:
        views = ((30, 30), (0, 80), (-90, 8)) if fixed else ((0, 89), (30, 35), (-90, 10))
    if fixed:
        nh.run(build, name, ground=GROUND, background=SEA_BG, views=views)
    else:
        nh.run(build, name, background=SEA_BG, views=views)
