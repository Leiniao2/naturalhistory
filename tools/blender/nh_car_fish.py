"""
Parametric Carboniferous fish for the "car" batch (akmonistion_zangerli.py, falcatus_falcatus.py,
edestus_heinrichi.py, echinochimaera_meltoni.py, rhizodus_hibberti.py).

The body is lofted along Y (snout at -Y) from side-view key tables: the centre line z(y),
the half-height and the half-width at each station, so heterocercal tails can sweep up.
Fins are thick panels (median fins in the YZ plane, paired fins tilted out from the flank)
fused with the body into one surface. Painted procedurally (dark back, pale belly, optional
spots / bands), then crisp eyes, gill slits, teeth and species extras go on top.
Swimmers: faces -Y, pivot at the body centre.
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

PUPIL = (0.02, 0.02, 0.03)
TOOTH = (0.93, 0.91, 0.84)
GILL = (0.08, 0.07, 0.07)


def interp(key, y):
    if y <= key[0][0]:
        return key[0][1]
    for (y0, r0), (y1, r1) in zip(key, key[1:]):
        if y <= y1:
            t = (y - y0) / max(y1 - y0, 1e-6)
            t = t * t * (3 - 2 * t)
            return r0 + (r1 - r0) * t
    return key[-1][1]


@dataclass
class Spec:
    name: str
    y0: float = -0.6
    y1: float = 0.6
    mid: list = field(default_factory=lambda: [(-0.6, 0.0), (0.6, 0.0)])          # centre line z(y)
    height: list = field(default_factory=lambda: [(-0.6, 0.0), (-0.45, 0.08), (0.0, 0.1), (0.6, 0.01)])
    width: list = field(default_factory=lambda: [(-0.6, 0.0), (-0.45, 0.07), (0.0, 0.08), (0.6, 0.008)])
    fins: list = field(default_factory=list)      # median: ("mid", [(y, z), ...]); paired: ("pair", root, [(dx, dy, dz)...])
    fin_th: float = 0.016
    back: tuple = (0.25, 0.27, 0.30)
    flank: tuple = (0.40, 0.42, 0.44)
    belly: tuple = (0.82, 0.80, 0.74)
    fin_col: tuple = None
    pattern: str = "none"                        # none, spots, bands, mottle
    pattern_col: tuple = (0.12, 0.12, 0.14)
    pattern_scale: float = 1.0
    eye: tuple = (-0.45, 0.03, 0.03)             # y, z above centre line, radius
    iris: tuple = (0.55, 0.50, 0.30)
    gills: int = 5                               # gill slits per side (0 = none / operculum)
    gill_y: float = -0.36
    teeth: int = 0
    tooth_len: float = 0.02
    mouth_y: tuple = (-0.58, -0.44)              # mouth from snout to corner (teeth along it)
    mouth_z: float = -0.035                      # mouth height relative to centre line
    voxel: float = 0.007
    max_tris: int = 7000
    extra: list = field(default_factory=list)    # fn(spec, tree) -> [(bm, colour or fn)]
    fused_extra: list = field(default_factory=list)  # fn(spec) -> [bm] fused with the body


def zmid(sp, y):
    return interp(sp.mid, y)


def body(sp, stations=70, ring=22):
    bm = bmesh.new()
    rings = []
    for i in range(stations + 1):
        t = i / stations
        y = sp.y0 + (sp.y1 - sp.y0) * t
        h, w, zc = interp(sp.height, y), interp(sp.width, y), zmid(sp, y)
        if i == 0 or i == stations or h < 1e-4:
            rings.append([bm.verts.new((0, y, zc))])
            continue
        r = []
        for k in range(ring):
            a = k / ring * math.tau
            c, s = math.cos(a), math.sin(a)
            r.append(bm.verts.new((w * math.copysign(abs(c) ** 0.8, c), y, zc + h * s)))
        rings.append(r)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(ring):
                bm.faces.new([a[0], b[(k + 1) % ring], b[k]])
        elif len(b) == 1:
            for k in range(ring):
                bm.faces.new([a[k], a[(k + 1) % ring], b[0]])
        else:
            for k in range(ring):
                j = (k + 1) % ring
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def panel(points, normal, th):
    """Thick panel from a planar outline (3D points) offset +-th/2 along normal."""
    n = Vector(normal).normalized() * th * 0.5
    bm = bmesh.new()
    top = [bm.verts.new(Vector(p) + n) for p in points]
    bot = [bm.verts.new(Vector(p) - n) for p in points]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    m = len(points)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def fin_parts(sp):
    out = []
    for f in sp.fins:
        if f[0] == "mid":
            pts = [(0.0, y, z) for y, z in f[1]]
            out.append(panel(pts, (1, 0, 0), f[2] if len(f) > 2 else sp.fin_th))
        else:  # paired: root point (x, y, z) for the right side, outline offsets; mirrored to the left
            root, offs = Vector(f[1]), f[2]
            th = f[3] if len(f) > 3 else sp.fin_th
            for sx in (-1, 1):
                pts = [Vector((sx * (root.x + d[0]), root.y + d[1], root.z + d[2])) for d in offs]
                a, b, c = pts[0], pts[1], pts[2]
                nrm = (b - a).cross(c - a)
                if nrm.length < 1e-8:
                    nrm = Vector((0, 0, 1))
                out.append(panel(pts, nrm, th))
    return out


def make_paint(sp):
    fin_col = sp.fin_col or sp.back

    def paint(co, n):
        y = co.y
        h, w = max(interp(sp.height, y), 1e-3), max(interp(sp.width, y), 1e-3)
        up = (co.z - zmid(sp, y)) / h
        on_fin = abs(up) > 1.15 or abs(co.x) > w * 1.25
        coarse = noise.noise(co * 9.0 / sp.pattern_scale)
        if on_fin:
            c = nh.lerp(fin_col, sp.belly, 0.25 * nh.smoothstep(0.0, -1.0, n.z)) if abs(co.x) > w * 1.25 else fin_col
        else:
            c = nh.lerp(sp.flank, sp.back, nh.smoothstep(-0.15, 0.55, up + 0.1 * coarse))
            c = nh.lerp(c, sp.belly, nh.smoothstep(-0.1, -0.6, up))
            pat = 0.0
            if sp.pattern == "spots":
                pat = nh.smoothstep(0.38, 0.45, noise.noise(co * 32.0 / sp.pattern_scale)) * nh.smoothstep(-0.3, 0.2, up)
            elif sp.pattern == "bands":
                pat = (1.0 if (((y - sp.y0) / (0.1 * sp.pattern_scale)) % 1.0) < 0.35 else 0.0) * nh.smoothstep(-0.4, 0.2, up)
            elif sp.pattern == "mottle":
                pat = 0.7 * nh.smoothstep(0.1, 0.35, coarse) * nh.smoothstep(-0.3, 0.3, up)
            c = nh.lerp(c, sp.pattern_col, pat)
        k = 0.93 + 0.14 * (0.5 + 0.5 * noise.noise(co * 40.0))
        return (c[0] * k, c[1] * k, c[2] * k)
    return paint


def details(sp, tree):
    out = []
    ey, ez, er = sp.eye
    for sx in (-1, 1):
        z = zmid(sp, ey) + ez
        loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, ey, z)), Vector((-sx, 0, 0)))
        if loc is not None:
            look = Vector((sx, -0.25, 0.1)).normalized()
            c = loc - look * er * 0.4

            def eye_col(co, n, c=c, lk=look):
                k = (co - c).normalized().dot(lk)
                return PUPIL if k > 0.78 else (sp.iris if k > 0.45 else (0.08, 0.08, 0.08))
            out.append((nh.ellipsoid(c, (er, er, er), subdivisions=2), eye_col))
        for g in range(sp.gills):
            y = sp.gill_y + g * 0.022
            zc = zmid(sp, y)
            h = interp(sp.height, y)
            pts = []
            for k in range(5):
                z = zc + h * (0.25 - 0.6 * k / 4)
                loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, y, z)), Vector((-sx, 0, 0)))
                if loc is not None:
                    pts.append(loc + nrm * 0.001)
            if len(pts) >= 2:
                out.append((nh.tube(pts, [0.003] * len(pts), sides=4), GILL))
        for t in range(sp.teeth):
            y = sp.mouth_y[0] + (sp.mouth_y[1] - sp.mouth_y[0]) * (t + 0.5) / sp.teeth
            z = zmid(sp, y) + sp.mouth_z
            loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, y, z)), Vector((-sx, 0, 0)))
            if loc is None:
                continue
            L = sp.tooth_len * (1.5 if t % 3 == 0 else 1.0)
            b = loc + Vector((-sx * L * 0.3, 0, L * 0.25))
            out.append((nh.tube([b, b + Vector((sx * L * 0.15, 0, -L))], [L * 0.28, 0.0], sides=4), TOOTH))
    for fn in sp.extra:
        out += fn(sp, tree)
    return out


def build(sp):
    mb0 = nh.MeshBuilder()
    mb0.add(body(sp), sp.flank)
    for p in fin_parts(sp):
        mb0.add(p, sp.back)
    for fn in sp.fused_extra:
        for p in fn(sp):
            mb0.add(p, sp.back)
    fused = mb0.fuse(voxel=sp.voxel, smooth=3, smooth_factor=0.5, max_tris=sp.max_tris)
    fused.normal_update()
    tree = BVHTree.FromBMesh(fused)
    extra = details(sp, tree)
    mb = nh.MeshBuilder()
    mb.add(fused, color=make_paint(sp))
    for bm, col in extra:
        mb.add(bm, col, smooth=False)
    obj = mb.to_object(sp.name, roughness=0.45)
    vs = obj.data.vertices
    mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (mn + mx) / 2
    for v in vs:
        v.co -= c
    return obj


def run(sp):
    nh.run(lambda: build(sp), sp.name, background=(0.06, 0.18, 0.24), views=((35, 20), (-90, 5), (150, 55)))
