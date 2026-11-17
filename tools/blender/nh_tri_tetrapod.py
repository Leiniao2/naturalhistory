"""
Shared parametric builder for the Triassic reptile / synapsid / amphibian models
(plateosaurus_engelhardti.py, coelophysis_bauri.py, desmatosuchus_spurensis.py,
nothosaurus_mirabilis.py, proganochelys_quenstedti.py ... see the tri_* species scripts).

A TetrapodSpec describes one animal:

  * axis: the main body as a list of sections (y, z, half width, half height[, x]) from the
    snout tip (-Y) through neck and trunk to the tail tip (+Y). It is Catmull-Rom
    resampled and skinned with superelliptic rings (nh_model conventions: faces -Y).
  * lofts: extra lofted parts in the same format (a separate skull, a crest, a beak...).
  * blobs: ellipsoids (centre, radii, pitch, yaw, roll) for muscles, cheeks, jowls.
  * limbs: right-side Limb chains (hip/shoulder -> knee -> ankle -> sole) with toes or a
    flat paddle; mirrored to the left with an opposite stride swing.
  * pre(b, spec): hook to add any further shells before fusing.
Everything above is fused into one seamless surface (MeshBuilder.fuse), decimated, given
a little pebbly-scale displacement plus an optional mouth groove, and painted by
spec.paint (or the default countershading with optional bands / spots / stripe).
Crisp details go on top: eyes, teeth along the mouth line, claws, dorsal plates /
spikes / knobs (plates), and post(mb, surf, spec) for anything special (shells, plumes,
membranes, tusks).

Pivot: "ground" (z = 0 at the feet, Ground style) or "centre" (bounding-box centre, Swim /
Swarm). Model about 2 units long.
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

import bpy
import bmesh
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

TOOTH = (0.93, 0.90, 0.80)
CLAW = (0.12, 0.10, 0.08)
PUPIL = (0.02, 0.02, 0.02)
MOUTH_LINE = (0.16, 0.11, 0.09)


# ---------------------------------------------------------------- geometry helpers

def loft(sections, sides=18, power=2.0, ref=Vector((0, 0, 1))):
    """Skin superelliptic rings along a path. sections: (center, half width, half height)."""
    bm = bmesh.new()
    pts = [Vector(s[0]) for s in sections]
    rings = []
    for i, (c, ra, rb) in enumerate(sections):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        if fwd.length < 1e-9:
            fwd = Vector((0, 1, 0))
        fwd.normalize()
        r = ref if abs(fwd.dot(ref)) < 0.95 else Vector((1, 0, 0))
        side = fwd.cross(r).normalized()
        up = side.cross(fwd).normalized()
        if ra <= 1e-6 or rb <= 1e-6:
            rings.append([bm.verts.new(Vector(c))])
            continue
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ca, sa = math.cos(a), math.sin(a)
            x = math.copysign(abs(ca) ** (2.0 / power), ca) * ra
            y = math.copysign(abs(sa) ** (2.0 / power), sa) * rb
            ring.append(bm.verts.new(Vector(c) + side * x + up * y))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[k], b[(k + 1) % sides]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def densify(sections, steps):
    """Catmull-Rom resample of (center, a, b) sections."""
    vals = [(Vector(c), a, b) for c, a, b in sections]
    out = []
    for i in range(len(vals) - 1):
        p0, p1 = vals[max(0, i - 1)], vals[i]
        p2, p3 = vals[i + 1], vals[min(len(vals) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t

            def cr(a, b, c, d):
                return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
            ra = max(0.0, cr(p0[1], p1[1], p2[1], p3[1]))
            rb = max(0.0, cr(p0[2], p1[2], p2[2], p3[2]))
            if i == 0 and k == 0:
                ra, rb = p1[1], p1[2]
            out.append((tuple(cr(p0[0], p1[0], p2[0], p3[0])), ra, rb))
    out.append((tuple(vals[-1][0]), vals[-1][1], vals[-1][2]))
    return out


def sections(axis):
    """(y, z, hw, hh[, x]) rows -> (center, hw, hh)."""
    out = []
    for row in axis:
        y, z, hw, hh = row[:4]
        x = row[4] if len(row) > 4 else 0.0
        out.append(((x, y, z), hw, hh))
    return out


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=16, rings=10):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def cone(base, tip, r, sides=6):
    return nh.tube([Vector(base), Vector(tip)], [r, 0.0], sides=sides)


def curved_spike(base, direction, length, r, bend=Vector((0, 0, 0)), sides=7):
    """Tapered horn from base along direction, curving toward bend at the tip."""
    d = Vector(direction).normalized()
    b = Vector(base)
    pts = [b, b + d * length * 0.4 + Vector(bend) * 0.1 * length,
           b + d * length * 0.75 + Vector(bend) * 0.35 * length, b + d * length + Vector(bend) * 0.7 * length]
    return nh.tube(pts, [r, r * 0.72, r * 0.4, 0.0], sides=sides)


def panel(points, thickness):
    """Thin slab through an arbitrary planar-ish closed 3D outline (fan triangulated)."""
    bm = bmesh.new()
    P = [Vector(p) for p in points]
    c = sum(P, Vector()) / len(P)
    nrm = Vector()
    for i in range(len(P)):
        nrm += (P[i] - c).cross(P[(i + 1) % len(P)] - c)
    nrm.normalize()
    off = nrm * thickness * 0.5
    top = [bm.verts.new(p + off) for p in P]
    bot = [bm.verts.new(p - off) for p in P]
    ct, cb = bm.verts.new(c + off), bm.verts.new(c - off)
    n = len(P)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ct, top[i], top[j]])
        bm.faces.new([cb, bot[j], bot[i]])
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def ribbon(points, half_widths, wdir, thickness):
    """Flat strap along points; wdir: Vector (or fn(i) -> Vector) across the strap's width."""
    bm = bmesh.new()
    P = [Vector(p) for p in points]
    rings = []
    for i, (p, w) in enumerate(zip(P, half_widths)):
        fwd = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        wd = Vector(wdir(i) if callable(wdir) else wdir)
        wd = (wd - fwd * wd.dot(fwd)).normalized()
        nd = fwd.cross(wd).normalized() * thickness * 0.5
        w = max(w, 1e-4)
        rings.append([bm.verts.new(p + wd * w + nd), bm.verts.new(p - wd * w + nd),
                      bm.verts.new(p - wd * w - nd), bm.verts.new(p + wd * w - nd)])
    for a, b in zip(rings, rings[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def dome(center, rx, ry, rz_top, rz_bot, power=2.0, segments=40, rings=20, ridge=None):
    """Superelliptic shell (carapace): plan outline |x/rx|^p + |y/ry|^p = 1, domed top, flat-ish
    bottom. ridge(x, y) -> extra height (keels, bumps), in model units."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    c = Vector(center)
    for v in bm.verts:
        n = v.co.normalized()
        rho = math.hypot(n.x, n.y)
        if rho > 1e-6:
            ca, sa = n.x / rho, n.y / rho
            k = (abs(ca) ** power + abs(sa) ** power) ** (-1.0 / power)
            ux, uy = ca * k * rho, sa * k * rho
        else:
            ux = uy = 0.0
        z = n.z * (rz_top if n.z > 0 else rz_bot)
        x, y = ux * rx, uy * ry
        if ridge and n.z > 0:
            z += ridge(x, y) * n.z
        v.co = c + Vector((x, y, z))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def voronoi_edge(p, centres, width):
    """1 near the boundary between the two nearest centres (2D, x/y), else 0."""
    d = sorted(((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5 for cx, cy in centres)
    return 1.0 - nh.smoothstep(width * 0.5, width, d[1] - d[0])


class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal

    def nearest(self, p):
        loc, normal, _i, _d = self.tree.find_nearest(Vector(p))
        return loc, normal


# ---------------------------------------------------------------- spec

@dataclass
class Limb:
    pts: list                       # right side: root (hip/shoulder) ... sole/palm centre
    radii: list                     # one per point
    toes: int = 4
    toe_len: float = 0.05
    toe_r: float = 0.012
    toe_spread: float = 50.0        # total fan, degrees
    toe_yaw: float = 0.0            # fan direction: 0 = forward (-Y), +90 = outward
    toe_drop: float = 0.006         # how far the toe tips curl down
    claws: bool = True
    claw_len: float = 0.022
    sole: tuple = None              # radii of a flat sole/palm ellipsoid at the last point
    paddle: tuple = None            # (length, width, yaw deg, pitch deg) flat paddle instead of toes
    stride: float = 0.0             # swing (deg) about the root, +right / -left
    color: tuple = None             # None = paint like the body


@dataclass
class TetrapodSpec:
    name: str
    axis: list                                  # (y, z, hw, hh[, x]) snout -> tail tip
    sides: int = 22
    power: float = 2.1
    steps: int = 3
    lofts: list = field(default_factory=list)   # [(axis rows, power)]
    blobs: list = field(default_factory=list)   # (centre, radii[, pitch, yaw, roll]) mirrored if x != 0
    limbs: list = field(default_factory=list)
    voxel: float = 0.011
    max_tris: int = 11000
    pivot: str = "ground"                       # "ground" | "centre"
    # ---- surface
    scale_bump: float = 0.0016
    scale_freq: float = 50.0
    # mouth: (y tip, y gape, z tip, z gape, depth) the groove along the side of the head
    mouth: tuple = None
    mouth_min_x: float = 0.25                   # only where |n.x| exceeds this (sides of the head)
    teeth: tuple = None                         # (count, length, radius, y0, y1) upper teeth
    lower_teeth: bool = False
    eyes: tuple = None                          # (y, z, radius, iris colour)
    eye_bulge: float = 0.55                     # how far the eyeball pokes out (fraction of r)
    nostrils: tuple = None                      # (y, z, x?) -> small dark pits
    plates: list = field(default_factory=list)  # dicts, see add_plates
    # ---- colour
    back: tuple = (0.30, 0.26, 0.20)
    flank: tuple = (0.55, 0.47, 0.34)
    belly: tuple = (0.82, 0.76, 0.62)
    limb_col: tuple = None
    pattern: tuple = None   # ("bands", colour, freq, strength, y0, y1) | ("spots", colour, freq, strength)
    pattern2: tuple = None
    head: tuple = None      # (colour, y_back, strength) tint of the head in front of y_back
    shade_lo: float = -0.55
    shade_hi: float = 0.55
    paint: Optional[Callable] = None            # custom paint(co, n, spec) -> rgb (replaces default)
    paint_extra: Optional[Callable] = None      # paint_extra(co, n, c, spec) -> rgb after the default
    pre: Optional[Callable] = None
    post: Optional[Callable] = None
    roughness: float = 0.65
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- body

def _rot_about(p, root, ang):
    m = Matrix.Translation(root) @ Matrix.Rotation(math.radians(ang), 4, "X") @ Matrix.Translation(-root)
    return m @ p


def limb_chain(limb, side):
    root = Vector((limb.pts[0][0] * side, limb.pts[0][1], limb.pts[0][2]))
    ang = limb.stride * side
    pts = []
    for p in limb.pts:
        v = Vector((p[0] * side, p[1], p[2]))
        pts.append(_rot_about(v, root, ang))
    return pts


def add_limbs(b, spec, toe_tips):
    for limb in spec.limbs:
        col = limb.color or spec.limb_col or spec.flank
        for side in (1, -1):
            pts = limb_chain(limb, side)
            b.add(nh.tube(pts, limb.radii, sides=12), col)
            for p, r in zip(pts[1:-1], limb.radii[1:-1]):
                b.add(nh.ellipsoid(p, (r * 1.02,) * 3, subdivisions=2), col)
            sole = pts[-1]
            if limb.paddle:
                ln, wd, yaw, pitch = limb.paddle
                yawr = math.radians(yaw)
                d = Vector((side * math.sin(yawr), -math.cos(yawr), 0.0))
                d = (d + Vector((0, 0, math.sin(math.radians(pitch))))).normalized()
                pad = nh.uv_ellipsoid((0, 0, 0), (wd, ln, wd * 0.18), segments=14, rings=8)
                rot = Vector((0, -1, 0)).rotation_difference(d).to_matrix().to_4x4()
                nh.transform(pad, rot)
                nh.transform(pad, Matrix.Translation(sole + d * ln * 0.8))
                b.add(pad, col)
                continue
            if limb.sole:
                b.add(nh.uv_ellipsoid(sole, limb.sole, segments=12, rings=8), col)
            for k in range(limb.toes):
                t = 0.5 if limb.toes == 1 else k / (limb.toes - 1)
                a = math.radians(limb.toe_yaw + (t - 0.5) * limb.toe_spread)
                d = Vector((side * math.sin(a), -math.cos(a), 0.0))
                ln = limb.toe_len * (0.75 + 0.25 * math.sin(math.pi * t)) if limb.toes > 2 else limb.toe_len
                base = sole + d * limb.toe_r * 0.8
                tip = base + d * ln + Vector((0, 0, -limb.toe_drop))
                b.add(nh.tube([base, base + d * ln * 0.55, tip], [limb.toe_r, limb.toe_r * 0.85, limb.toe_r * 0.6],
                              sides=7), col)
                if limb.claws:
                    toe_tips.append((tip, d, limb.toe_r, limb.claw_len))


def build_body(spec):
    b = nh.MeshBuilder()
    b.add(loft(densify(sections(spec.axis), spec.steps), sides=spec.sides, power=spec.power), spec.flank)
    for rows, pw in spec.lofts:
        b.add(loft(densify(sections(rows), spec.steps), sides=max(12, spec.sides - 4), power=pw), spec.flank)
    for bl in spec.blobs:
        c, r = bl[0], bl[1]
        ang = list(bl[2:5]) + [0.0] * (3 - len(bl[2:5]))
        for side in ((1, -1) if abs(c[0]) > 1e-6 else (1,)):
            b.add(oriented((c[0] * side, c[1], c[2]), r, pitch=ang[0], yaw=ang[1] * side, roll=ang[2] * side),
                  spec.flank)
    tips = []
    add_limbs(b, spec, tips)
    if spec.pre:
        spec.pre(b, spec)
    fused = b.fuse(voxel=spec.voxel, smooth=5, smooth_factor=0.5)
    sculpt(fused, spec)
    fused = decimate(fused, spec.max_tris)
    return fused, tips


def mouth_z(spec, y):
    y0, y1, z0, z1 = spec.mouth[:4]
    t = max(0.0, min(1.0, (y - y0) / (y1 - y0)))
    return z0 + (z1 - z0) * t


def mouth_k(spec, co, n):
    """1 on the mouth line, 0 away from it."""
    if not spec.mouth:
        return 0.0
    y0, y1 = spec.mouth[0], spec.mouth[1]
    if co.y < y0 - 0.01 or co.y > y1:
        return 0.0
    if abs(n.x) < spec.mouth_min_x and co.y > y0 + 0.02:
        return 0.0
    d = abs(co.z - mouth_z(spec, co.y))
    fade = nh.smoothstep(y1, y1 - 0.03, co.y)
    return (1.0 - nh.smoothstep(0.003, 0.008, d)) * fade


def sculpt(bm, spec):
    bm.normal_update()
    moves = []
    depth = spec.mouth[4] if spec.mouth and len(spec.mouth) > 4 else 0.005
    for v in bm.verts:
        co, n = v.co, v.normal
        d = spec.scale_bump * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * spec.scale_freq)))
        d += spec.scale_bump * 0.6 * noise.noise(co * 22.0)
        d -= depth * mouth_k(spec, co, n)
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def default_paint(co, n, spec):
    c = nh.lerp(spec.belly, spec.flank, nh.smoothstep(spec.shade_lo, 0.0, n.z))
    c = nh.lerp(c, spec.back, nh.smoothstep(0.1, spec.shade_hi + 0.3, n.z))
    for pat in (spec.pattern, spec.pattern2):
        if not pat:
            continue
        kind = pat[0]
        if kind == "bands":
            _k, pc, freq, st = pat[:4]
            y0, y1 = (pat[4], pat[5]) if len(pat) > 5 else (-9, 9)
            if y0 < co.y < y1:
                wob = noise.noise(co * 4.0) * 1.0
                band = 0.5 + 0.5 * math.sin(co.y * freq + wob)
                upper = nh.smoothstep(-0.3, 0.3, n.z)
                c = nh.lerp(c, pc, st * nh.smoothstep(0.62, 0.85, band) * upper)
        elif kind == "spots":
            _k, pc, freq, st = pat[:4]
            s = 1.0 - nh.smoothstep(0.12, 0.3, noise.cell(co * freq))
            c = nh.lerp(c, pc, st * s * nh.smoothstep(-0.4, 0.2, n.z))
        elif kind == "stripe":       # lengthwise flank stripe at normal height nz
            _k, pc, nz, wdt, st = pat[:5]
            y0, y1 = (pat[5], pat[6]) if len(pat) > 6 else (-9, 9)
            if y0 < co.y < y1:
                c = nh.lerp(c, pc, st * (1.0 - nh.smoothstep(wdt * 0.5, wdt, abs(n.z - nz))))
        elif kind == "mottle":
            _k, pc, freq, st = pat[:4]
            m = nh.smoothstep(0.1, 0.5, noise.noise(co * freq))
            c = nh.lerp(c, pc, st * m)
    if spec.head:
        hc, yb, st = spec.head
        c = nh.lerp(c, hc, st * nh.smoothstep(yb, yb - 0.06, co.y) * nh.smoothstep(-0.6, 0.0, n.z))
    if spec.paint_extra:
        c = spec.paint_extra(co, n, c, spec)
    return c


def paint(co, n, spec):
    c = spec.paint(co, n, spec) if spec.paint else default_paint(co, n, spec)
    c = nh.lerp(c, MOUTH_LINE, 0.85 * mouth_k(spec, co, n))
    m = noise.noise(co * 13.0)
    k = (1.0 + 0.07 * m) * (0.95 + 0.07 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * spec.scale_freq))))
    return tuple(min(1.0, max(0.0, x * k)) for x in c)


# ---------------------------------------------------------------- crisp details

def add_eyes(mb, surf, spec):
    if not spec.eyes:
        return
    y, z, r, iris = spec.eyes[:4]
    top_x = spec.eyes[4] if len(spec.eyes) > 4 else None   # eyes on top of the head at |x|
    for sx in (1, -1):
        if top_x is None:
            loc, nrm = surf.hit((sx * 3.0, y, z), (-sx, 0, 0))
        else:
            loc, nrm = surf.hit((sx * top_x, y, z + 3.0), (0, 0, -1))
        if loc is None:
            continue
        c = loc - nrm * r * (1.0 - spec.eye_bulge)
        mb.add(nh.ellipsoid(c, (r, r * 1.1, r), subdivisions=2), iris)
        mb.add(nh.ellipsoid(c + nrm * r * 0.72, (r * 0.42, r * 0.5, r * 0.42), subdivisions=1), PUPIL)


def add_nostrils(mb, surf, spec):
    if not spec.nostrils:
        return
    y, z = spec.nostrils[:2]
    xo = spec.nostrils[2] if len(spec.nostrils) > 2 else None
    for sx in (1, -1):
        if xo is None:
            loc, nrm = surf.hit((sx * 3.0, y, z), (-sx, 0, 0))
        else:
            loc, nrm = surf.hit((sx * xo, y, z + 2.0), (0, 0, -1))
        if loc is None:
            continue
        mb.add(nh.ellipsoid(loc, (0.006, 0.009, 0.006), subdivisions=1), PUPIL)


def add_teeth(mb, surf, spec):
    if not spec.teeth or not spec.mouth:
        return
    count, ln, r, ya, yb = spec.teeth
    for i in range(count):
        t = (i + 0.5) / count
        y = ya + (yb - ya) * t
        z = mouth_z(spec, y)
        for sx in (1, -1):
            loc, nrm = surf.hit((sx * 3.0, y, z + 0.004), (-sx, 0, 0))
            if loc is None:
                continue
            base = loc - nrm * r * 0.6 + Vector((0, 0, 0.004))
            l2 = ln * (0.7 + 0.3 * math.sin(math.pi * min(1.0, t * 1.6)))
            mb.add(nh.tube([base, base + Vector((0, 0.1 * l2, -0.6 * l2)), base + Vector((0, 0.25 * l2, -l2))],
                           [r, r * 0.65, 0.0], sides=6), TOOTH, smooth=False)
            if spec.lower_teeth and i % 2 == 0:
                b2 = loc - nrm * r * 0.6 + Vector((0, 0.01, -0.005))
                mb.add(cone(b2, b2 + Vector((0, -0.1 * l2, 0.8 * l2)), r * 0.8), TOOTH, smooth=False)


def add_claws(mb, tips):
    for tip, d, r, cl in tips:
        base = tip - d * 0.004 + Vector((0, 0, 0.003))
        end = tip + d * cl + Vector((0, 0, -cl * 0.45))
        mb.add(nh.tube([base, base + d * cl * 0.45, end], [r * 0.7, r * 0.5, 0.0], sides=6), CLAW)


def add_plates(mb, surf, spec):
    """plates: dict(xs=(x offsets), y0, y1, step, size, kind='plate'|'knob'|'spike', height,
    col, keel_col, taper, follow=callable y->x (tail sway), shrink)"""
    for pd in spec.plates:
        y = pd["y0"]
        follow = pd.get("follow", lambda yy: 0.0)
        while y <= pd["y1"]:
            t = (y - pd["y0"]) / max(pd["y1"] - pd["y0"], 1e-6)
            size = pd["size"] * (1.0 - pd.get("taper", 0.5) * t)
            for x0 in pd["xs"]:
                x = follow(y) + x0
                loc, n = surf.hit((x, y, 5.0), (0, 0, -1))
                if loc is None:
                    continue
                kind = pd.get("kind", "plate")
                col = pd.get("col", (0.2, 0.17, 0.13))
                kc = pd.get("keel_col", col)
                if kind == "spike":
                    h = pd.get("height", 3.0) * size
                    out = (n + Vector((math.copysign(pd.get("splay", 0.0), x0) if x0 else 0, 0.25, 0))).normalized()
                    mb.add(cone(loc - n * size * 0.2, loc + out * h, size * 0.55, sides=7),
                           lambda co, nn, l=loc, h=h: nh.lerp(col, kc, min(1.0, (co - l).length / h)))
                    continue
                if kind == "knob":
                    mb.add(nh.ellipsoid(loc, (size, size, size * pd.get("height", 0.6)), subdivisions=2), col)
                    continue
                rx = size * pd.get("wide", 1.0)
                ry, rz = size, size * 0.18
                plate = nh.uv_ellipsoid((0, 0, 0), (1, 1, 1), segments=10, rings=6)
                kh = pd.get("height", 1.4)
                for v in plate.verts:
                    ux, uy, uz = v.co
                    v.co = Vector((math.copysign(abs(ux) ** 0.55, ux) * rx, math.copysign(abs(uy) ** 0.55, uy) * ry,
                                   uz * rz + max(0.0, uz) * rz * kh * max(0.0, 1.0 - abs(ux) * 2.2)))
                rot = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
                nh.transform(plate, rot)
                nh.transform(plate, Matrix.Translation(loc + n * rz * 0.3))

                def pc(co, _nn, c=loc, up=n.copy(), k=size):
                    return nh.lerp(col, kc, nh.smoothstep(0.18 * k, 0.36 * k, (co - c).dot(up)))
                mb.add(plate, pc)
            y += pd["step"] * (1.0 - pd.get("shrink", 0.0) * t)


def build(spec):
    fused, tips = build_body(spec)
    surf = Surface(fused)
    mb = nh.MeshBuilder()
    mb.add(fused, lambda co, n: paint(co, n, spec))
    add_eyes(mb, surf, spec)
    add_nostrils(mb, surf, spec)
    add_teeth(mb, surf, spec)
    add_claws(mb, tips)
    add_plates(mb, surf, spec)
    if spec.post:
        spec.post(mb, surf, spec)
    obj = mb.to_object(spec.name, roughness=spec.roughness)
    if spec.pivot == "ground":
        nh.ground_to_zero(obj)
    else:
        corners = [Vector(c) for c in obj.bound_box]
        centre = sum(corners, Vector()) / 8
        for v in obj.data.vertices:
            v.co -= centre
    zs = [v.co.z for v in obj.data.vertices]
    print(f"  {spec.name}: height {max(zs) - min(zs):.3f}")
    return obj


VIEWS_GROUND = ((35, 22), (-90, 6), (25, 65))
VIEWS_SWIM = ((35, 22), (-90, 6), (20, 70))


def run(spec, ground=(0.48, 0.40, 0.30), views=None, background=None):
    kw = {}
    if spec.pivot == "ground":
        kw["ground"] = ground
        kw["views"] = views or VIEWS_GROUND
    else:
        kw["views"] = views or VIEWS_SWIM
        kw["background"] = background or (0.05, 0.18, 0.24)
    nh.run(lambda: build(spec), spec.name, **kw)
