"""
Shared toolkit for the Jurassic batch (nh_jur_*.py modules and their species scripts).

Builds on nh_model. Provides:
  * Spine: a smooth path of control rings (centre, half width, half height) that is
    lofted into one tube (tail -> body -> neck -> head), with helpers to find points
    on its surface so plates, spikes, crests and feathers can be placed on the back.
  * limb() / bird_foot() / pillar_foot() / hand(): legs and feet.
  * blade(): thin flat plates in the YZ plane (stegosaur plates, crests, fins).
  * paint(): countershaded skin with optional stripes, spots and mottling.
  * eyes(), teeth(), cone(), decimate(), finish().

Conventions as in nh_model: faces -Y, Z up; Ground animals pivot on the ground, swimmers
and fliers at the body centre.
"""

import math

import bpy
import bmesh
from mathutils import Vector, Matrix, noise

import nh_model as nh

EYE = (0.80, 0.55, 0.12)
PUPIL = (0.03, 0.02, 0.02)
CLAW = (0.16, 0.14, 0.11)
TOOTH = (0.95, 0.92, 0.80)
MOUTH = (0.50, 0.15, 0.15)


# ---------------------------------------------------------------- curves

def catmull(vals, steps):
    """Catmull-Rom resample of a list of tuples of floats (all the same length)."""
    out = []
    n = len(vals)
    for i in range(n - 1):
        p0, p1, p2, p3 = vals[max(0, i - 1)], vals[i], vals[i + 1], vals[min(n - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(vals[-1]))
    return out


def loft(sections, sides=18, power=2.0, cap=True):
    """Skin rings along a path. sections: (centre, half width, half height); a zero width
    closes that end in a point. Rotation-minimising frames, so steep necks don't twist.
    power > 2 squares the cross-section off (boxy skulls)."""
    bm = bmesh.new()
    pts = [Vector(s[0]) for s in sections]
    rings = []
    side = None
    for i, (c, ra, rb) in enumerate(sections):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if side is None:
            side = fwd.cross(Vector((0, 0, 1)))
            if side.length < 1e-4:
                side = Vector((1, 0, 0))
            side.normalize()
        else:
            side = (side - fwd * side.dot(fwd)).normalized()
        up = side.cross(fwd).normalized()
        if up.z < 0:
            up = -up
        if ra <= 1e-6:
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
    if cap and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


class Spine:
    """A smooth tube through control rings [(x, y, z, half width, half height), ...].
    Densified with Catmull-Rom; s = 0..1 by arc length from the first ring."""

    def __init__(self, rows, steps=4):
        self.rows = catmull([tuple(r) for r in rows], steps)
        # keep the pointed ends pointed
        self.rows[0] = tuple(rows[0])
        self.rows[-1] = tuple(rows[-1])
        self.pts = [Vector(r[:3]) for r in self.rows]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def mesh(self, sides=18, power=2.0):
        secs = [((r[0], r[1], r[2]), max(0.0, r[3]), max(0.0, r[4])) for r in self.rows]
        return loft(secs, sides=sides, power=power)

    def at(self, s):
        """(centre, tangent, half width, half height) at arc-length fraction s."""
        d = max(0.0, min(1.0, s)) * self.length
        for i in range(len(self.cum) - 1):
            if self.cum[i + 1] >= d:
                seg = self.cum[i + 1] - self.cum[i]
                t = 0.0 if seg < 1e-9 else (d - self.cum[i]) / seg
                c = self.pts[i].lerp(self.pts[i + 1], t)
                tan = (self.pts[i + 1] - self.pts[i]).normalized()
                hw = self.rows[i][3] + (self.rows[i + 1][3] - self.rows[i][3]) * t
                hh = self.rows[i][4] + (self.rows[i + 1][4] - self.rows[i][4]) * t
                return c, tan, hw, hh
        r = self.rows[-1]
        return self.pts[-1], (self.pts[-1] - self.pts[-2]).normalized(), r[3], r[4]

    def top(self, s, inset=0.0):
        """Point on the dorsal midline at s (pushed in by inset * half height) and the local up."""
        c, tan, hw, hh = self.at(s)
        side = tan.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
        up = side.cross(tan).normalized()
        if up.z < 0:
            up = -up
        return c + up * hh * (1.0 - inset), up

    def side_pt(self, s, sx, height=0.0, inset=0.0):
        """Point on the flank at s: sx = +-1, height -1 (belly) .. 1 (back)."""
        c, tan, hw, hh = self.at(s)
        side = tan.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
        up = side.cross(tan).normalized()
        if up.z < 0:
            up = -up
        a = math.asin(max(-1.0, min(1.0, height)))
        return c + side * (sx * math.cos(a) * hw * (1 - inset)) + up * (math.sin(a) * hh * (1 - inset))

    def s_at_y(self, y):
        """Arc-length fraction of the first point whose y passes y (for mostly horizontal paths)."""
        best, bd = 0.0, 1e9
        for i, p in enumerate(self.pts):
            if abs(p.y - y) < bd:
                bd, best = abs(p.y - y), self.cum[i] / self.length
        return best


# ---------------------------------------------------------------- parts

def cone(base, tip, r, sides=5):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


def limb(points, radii, sides=12, steps=3):
    """Smooth tapering limb through points."""
    vals = [tuple(p) + (r,) for p, r in zip(points, radii)]
    rows = catmull(vals, steps)
    return nh.tube([r[:3] for r in rows], [max(0.0, r[3]) for r in rows], sides=sides)


def bird_foot(ball, sx, toe_len, toe_r, spread=0.42, fwd=Vector((0, -1, 0)), claw=True, hallux=True):
    """Three forward toes (and a small hallux) from the ball of a theropod foot.
    Returns (fused parts, crisp claws as (base, tip, r))."""
    parts, claws = [], []
    ball = Vector(ball)
    for k, ang in enumerate((-spread, 0.0, spread)):
        d = Matrix.Rotation(ang * -sx, 3, "Z") @ fwd
        ln = toe_len * (1.0 if k == 1 else 0.8)
        p1 = Vector((ball.x, ball.y, toe_r * 0.9)) + d * ln * 0.5
        p2 = Vector((ball.x, ball.y, toe_r * 0.7)) + d * ln
        parts.append(nh.tube([ball, p1, p2], [toe_r * 1.2, toe_r, toe_r * 0.7], sides=8))
        if claw:
            claws.append((p2 - d * toe_r * 0.3 + Vector((0, 0, toe_r * 0.2)), p2 + d * toe_r * 2.2 + Vector((0, 0, -toe_r * 0.6)), toe_r * 0.6))
    if hallux:
        claws.append((ball + Vector((0, toe_r * 0.6, toe_r * 1.6)), ball + Vector((sx * toe_r * 0.5, toe_r * 2.8, toe_r * 0.4)), toe_r * 0.45))
    return parts, claws


def pillar_foot(center, r, sx, nails=3, fwd=Vector((0, -1, 0)), color_nails=True):
    """An elephantine pad (fused) plus a row of blunt nails (crisp)."""
    c = Vector(center)
    parts = [nh.ellipsoid((c.x, c.y - r * 0.15, r * 0.45), (r * 1.05, r * 1.15, r * 0.48), subdivisions=3)]
    claws = []
    for k in range(nails):
        a = (k - (nails - 1) / 2) * 0.45
        d = Matrix.Rotation(-a * sx, 3, "Z") @ fwd
        b = Vector((c.x, c.y, r * 0.3)) + d * r * 1.05
        claws.append((b - d * r * 0.15, b + d * r * 0.35 + Vector((0, 0, -r * 0.18)), r * 0.2))
    return parts, claws


def hand(wrist, sx, fingers, length, r, down=0.4, spread=0.35, fwd=Vector((0, -1, 0))):
    """Clawed fingers from a wrist: returns (finger tubes, claws)."""
    tubes, claws = [], []
    w = Vector(wrist)
    for k in range(fingers):
        a = (k - (fingers - 1) / 2) * spread
        d = (Matrix.Rotation(-a * sx, 3, "Z") @ fwd + Vector((0, 0, -down))).normalized()
        tip = w + d * length * (1.0 if k == fingers // 2 else 0.85)
        tubes.append(nh.tube([w, tip], [r, r * 0.7], sides=6))
        claws.append((tip, tip + d * r * 2.5 + Vector((0, 0, -r * 1.2)), r * 0.7))
    return tubes, claws


def blade(outline_yz, thickness, x=0.0, center=None, up=None):
    """Thin slab in the YZ plane (plates, crests, sails) from a closed outline [(y, z), ...],
    centred on x. Optionally rotated so its +Z points along `up` about `center`."""
    bm = bmesh.new()
    left = [bm.verts.new((x - thickness * 0.5, y, z)) for y, z in outline_yz]
    right = [bm.verts.new((x + thickness * 0.5, y, z)) for y, z in outline_yz]
    bm.faces.new(left)
    bm.faces.new(list(reversed(right)))
    n = len(outline_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([left[i], left[j], right[j], right[i]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if up is not None and center is not None:
        q = Vector((0, 0, 1)).rotation_difference(Vector(up))
        nh.transform(bm, Matrix.Translation(Vector(center)) @ q.to_matrix().to_4x4() @ Matrix.Translation(-Vector(center)))
    return bm


def plate(base, height, length, thickness, up=Vector((0, 0, 1)), lean=0.0, shape="kite", sx=0.0):
    """A dorsal plate standing on `base`: kite (stegosaur), round or spike-ish outline.
    lean tilts it back (+) along +Y; sx tilts it outward to one side."""
    b = Vector(base)
    if shape == "kite":
        out = [(-length * 0.5, 0.0), (-length * 0.42, height * 0.45), (-length * 0.05, height),
               (length * 0.3, height * 0.6), (length * 0.5, 0.0)]
    elif shape == "round":
        out = [(math.cos(a) * length * 0.5, max(0.0, math.sin(a)) * height)
               for a in [math.pi * k / 10 for k in range(11)]]
        out = list(reversed(out))
        out = [(y, z) for y, z in out]
    else:  # tall narrow spike plate
        out = [(-length * 0.5, 0.0), (-length * 0.1, height), (length * 0.5, 0.0)]
    out = [(y + lean * z, z - height * 0.12) for y, z in out]  # sink the base in
    bm = blade(out, thickness)
    d = Vector(up).normalized()
    if sx:
        d = (d + Vector((sx, 0, 0))).normalized()
    q = Vector((0, 0, 1)).rotation_difference(d)
    nh.transform(bm, Matrix.Translation(b) @ q.to_matrix().to_4x4())
    return bm


def eyes(mb, center, r, sx_list=(1, -1), iris=EYE, pupil=PUPIL, out=0.55):
    c = Vector(center)
    for sx in sx_list:
        e = Vector((sx * abs(c.x), c.y, c.z))
        mb.add(nh.ellipsoid(e, (r, r * 1.1, r), subdivisions=2), iris)
        mb.add(nh.ellipsoid(e + Vector((sx * r * out, -r * 0.2, 0)), (r * 0.5, r * 0.5, r * 0.75), subdivisions=2), pupil)


def teeth(mb, rows, color=TOOTH, sides=4):
    """rows: [(base, tip, r), ...]"""
    for base, tip, r in rows:
        mb.add(cone(base, tip, r, sides=sides), color, smooth=False)


def claws(mb, lst, color=CLAW, sides=5):
    for base, tip, r in lst:
        mb.add(cone(base, tip, r, sides=sides), color, smooth=False)


# ---------------------------------------------------------------- colour

def paint(back, flank, belly, stripe=None, freq=0.0, y_range=(-9, 9), stripe_amt=0.7, stripe_sharp=(0.6, 0.9),
          spots=None, spot_scale=8.0, spot_amt=0.6, mottle=0.12, mottle_scale=14.0, extra=None, axis="y"):
    """Countershaded skin colour function (co, n) -> rgb. Stripes run across the body along
    `axis` (bands at sin(coord * freq)); spots are cellular blotches on the back and flanks.
    extra(co, n, c) -> rgb lets a species add its own markings on top."""
    def fn(co, n):
        c = nh.lerp(belly, flank, nh.smoothstep(-0.6, -0.1, n.z))
        c = nh.lerp(c, back, nh.smoothstep(0.1, 0.8, n.z))
        top = nh.smoothstep(-0.3, 0.5, n.z)
        coord = co.y if axis == "y" else co.z
        if stripe is not None and freq and y_range[0] < co.y < y_range[1]:
            s = 0.5 + 0.5 * math.sin(coord * freq + abs(co.x) * 3.0)
            c = nh.lerp(c, stripe, stripe_amt * nh.smoothstep(*stripe_sharp, s) * top)
        if spots is not None:
            cell = noise.cell(co * spot_scale)
            c = nh.lerp(c, spots, spot_amt * (1.0 - nh.smoothstep(0.08, 0.2, cell)) * top)
        if extra is not None:
            c = extra(co, n, c)
        if mottle:
            m = noise.noise(co * mottle_scale)
            c = tuple(max(0.0, min(1.0, v * (1.0 + mottle * m))) for v in c)
        return c
    return fn


def pebble(bm, amount=0.002, scale=40.0):
    """Light pebbly scale displacement along the normals."""
    bm.normal_update()
    offs = [(v, v.normal * (amount * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(v.co * scale))))) for v in bm.verts]
    for v, o in offs:
        v.co += o
    bm.normal_update()
    return bm


# ---------------------------------------------------------------- finishing

def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def fuse_parts(parts, voxel, max_tris, smooth=5, color=(0.5, 0.5, 0.5)):
    """Fuse a list of bmeshes (or (bmesh, colour) pairs) into one surface."""
    b = nh.MeshBuilder()
    for p in parts:
        if isinstance(p, tuple):
            b.add(p[0], p[1])
        else:
            b.add(p, color)
    return b.fuse(voxel=voxel, smooth=smooth, smooth_factor=0.5, max_tris=max_tris)


def finish(mb, name, pivot="ground", roughness=0.65):
    """MeshBuilder -> object. pivot: 'ground' (lowest point at z = 0), 'center' (bounds centre at the origin) or 'none' (as modelled, e.g. a waterline at z = 0)."""
    obj = mb.to_object(name, roughness=roughness)
    if pivot == "ground":
        nh.ground_to_zero(obj)
    elif pivot == "center":
        vs = obj.data.vertices
        lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
        hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
        c = (lo + hi) * 0.5
        for v in vs:
            v.co -= c
    return obj
