"""
Parametric early-tetrapod builder for the Permian batch (Edaphosaurus, Cotylorhynchus,
Ophiacodon, Varanops, Scutosaurus, Eryops, Diplocaulus, Seymouria, Moschops, Diictodon,
Gorgonops, Mesosaurus, Coelurosauravus...).

A Spec describes the animal as lofted sections plus four limbs:
  * torso: (y, z, half width, half height) rows from the neck to the tail tip (faces -Y,
    so the neck has the smallest y);
  * head:  the same rows for the skull, back to snout tip; jaw: optional lower jaw rows;
  * fore / hind: Limb() with joint position, sprawl and foot size.
Body, head, limbs and any `fused` extras are voxel-fused into one seamless skin, lightly
sculpted (scales / wrinkles), painted by a countershaded colour scheme plus a pattern,
then crisp details are added: eyes, nostrils, claws, teeth (Spec.teeth rows) and
whatever the species script adds in `crisp(mb, spec)`.

Species scripts build a Spec and call nh_per_tetra.main(spec).
Faces -Y; pivot on the ground (Spec.pivot = "ground") or at the body centre ("centre").
"""

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

V = Vector


# ---------------------------------------------------------------- geometry helpers

def loft(sections, sides=18, power=2.0, ref=V((0, 0, 1))):
    """Skin superelliptic rings along a path. sections: (center, half width, half height)."""
    bm = bmesh.new()
    pts = [V(s[0]) for s in sections]
    rings = []
    for i, (c, ra, rb) in enumerate(sections):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = fwd.cross(ref).normalized()
        up = side.cross(fwd).normalized()
        if ra <= 1e-6:
            rings.append([bm.verts.new(V(c))])
            continue
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ca, sa = math.cos(a), math.sin(a)
            x = math.copysign(abs(ca) ** (2.0 / power), ca) * ra
            y = math.copysign(abs(sa) ** (2.0 / power), sa) * rb
            ring.append(bm.verts.new(V(c) + side * x + up * y))
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


def densify(rows, steps):
    """Catmull-Rom resample of (y, z, hw, hh[, x]) rows -> loft sections."""
    vals = [(r[4] if len(r) > 4 else 0.0, r[0], r[1], r[2], r[3]) for r in rows]
    out = []

    def cr(a, b, c, d, t):
        t2, t3 = t * t, t * t * t
        return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
    for i in range(len(vals) - 1):
        p0, p1 = vals[max(0, i - 1)], vals[i]
        p2, p3 = vals[i + 1], vals[min(len(vals) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            x, y, z, a, b = (cr(p0[j], p1[j], p2[j], p3[j], t) for j in range(5))
            out.append(((x, y, z), max(0.0, a), max(0.0, b)))
    x, y, z, a, b = vals[-1]
    out.append(((x, y, z), a, b))
    return out


def rows_at(rows, y):
    """Linear (z, hw, hh, x) of a row table at y (tables may run either direction)."""
    rs = sorted(rows, key=lambda r: r[0])
    if y <= rs[0][0]:
        r = rs[0]
    elif y >= rs[-1][0]:
        r = rs[-1]
    else:
        for r0, r1 in zip(rs, rs[1:]):
            if r0[0] <= y <= r1[0]:
                k = (y - r0[0]) / max(r1[0] - r0[0], 1e-9)
                x0 = r0[4] if len(r0) > 4 else 0.0
                x1 = r1[4] if len(r1) > 4 else 0.0
                return (r0[1] + (r1[1] - r0[1]) * k, r0[2] + (r1[2] - r0[2]) * k,
                        r0[3] + (r1[3] - r0[3]) * k, x0 + (x1 - x0) * k)
    return r[1], r[2], r[3], (r[4] if len(r) > 4 else 0.0)


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=16, rings=10, deform=None):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(V(center)))
    return bm


def cone(base, tip, r, sides=6):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


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


def membrane(outline, thickness=0.006):
    """Thin double-sided panel from a closed polygon in any plane (wings, sails, fins)."""
    pts = [V(p) for p in outline]
    c = sum(pts, V()) / len(pts)
    nrm = V()
    for a, b in zip(pts, pts[1:] + pts[:1]):
        nrm += (a - c).cross(b - c)
    nrm = nrm.normalized() if nrm.length > 1e-9 else V((0, 0, 1))
    bm = bmesh.new()
    top = [bm.verts.new(p + nrm * thickness * 0.5) for p in pts]
    bot = [bm.verts.new(p - nrm * thickness * 0.5) for p in pts]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- spec

@dataclass
class Limb:
    y: float                 # shoulder / hip y
    z: float                 # joint height
    x: float                 # joint distance from the midline
    upper: float             # humerus / femur length
    lower: float             # forearm / shin length (elbow to wrist)
    sprawl: float = 0.8      # 1 = upper limb horizontal (sprawling), 0 = straight down
    swing: float = 0.0       # fore/aft offset of the elbow/knee (+ = backward)
    r: float = 0.05          # upper limb radius (lower tapers from it)
    foot: tuple = (0.05, 0.06, 0.02)   # half sizes of the hand / foot pad
    toes: int = 5
    toe_len: float = 0.04
    toe_r: float = 0.010
    toe_fan: float = 90.0    # degrees between outer toes
    toe_yaw: float = 10.0    # toes turned outwards
    muscle: float = 1.0      # size of the shoulder / thigh mass
    claw: float = 1.0        # claw length factor (0 = none)
    paddle: bool = False     # webbed paddle instead of separate toes
    grounded: bool = True    # False: swimmers / gliders - the limb sweeps back, foot not on the ground


@dataclass
class Spec:
    name: str
    torso: list
    head: list
    jaw: Optional[list] = None
    fore: Optional[Limb] = None
    hind: Optional[Limb] = None
    eye: tuple = (0.05, -0.6, 0.4, 0.02)          # x, y, z, radius (mirrored)
    eye_col: tuple = (0.70, 0.52, 0.15)
    nostril: Optional[tuple] = None                # x, y, z (mirrored)
    back: tuple = (0.35, 0.28, 0.20)
    flank: tuple = (0.50, 0.40, 0.28)
    belly: tuple = (0.78, 0.70, 0.55)
    leg: Optional[tuple] = None
    mark: tuple = (0.18, 0.13, 0.09)
    pattern: str = "bands"                         # bands, spots, stripes, mottle, none
    pattern_freq: float = 20.0
    pattern_amount: float = 0.55
    claw_col: tuple = (0.12, 0.10, 0.08)
    tooth_col: tuple = (0.93, 0.89, 0.76)
    teeth: list = field(default_factory=list)      # (y0, y1, count, length, radius, upper?) rows
    fangs: list = field(default_factory=list)      # (x, y, z, length, radius, dy) crisp fangs (mirrored)
    fused: Optional[Callable] = None               # fused(b, spec): extra parts merged into the skin
    crisp: Optional[Callable] = None               # crisp(mb, spec): extra separate parts
    paint: Optional[Callable] = None               # paint(co, n, c) -> c   final colour tweak
    sculpt: Optional[Callable] = None              # sculpt(co, n) -> extra displacement
    scale_bumps: float = 1.0
    voxel: float = 0.009
    max_tris: int = 12000
    pivot: str = "ground"
    torso_power: float = 2.1
    head_power: float = 2.4
    mouth_col: tuple = (0.20, 0.09, 0.08)
    preview: dict = field(default_factory=dict)
    roughness: float = 0.65
    drop: float = 0.0        # lower the whole body by this much (legs get shorter): quick stance tuning
    _claws: list = field(default_factory=list)


# ---------------------------------------------------------------- limbs

def limb(b, L, s, col):
    """One sprawling/upright limb. Returns nothing; claw tips go to L._tips."""
    sh = V((s * L.x, L.y, L.z))
    ang = math.radians(90.0 * (1.0 - L.sprawl) + 8.0 * L.sprawl)    # angle below horizontal
    el = sh + V((s * L.upper * math.cos(ang), L.swing, -L.upper * math.sin(ang)))
    fx, fy, fz = L.foot
    if L.grounded:
        wr = V((el.x + s * 0.15 * L.lower * L.sprawl, el.y - 0.05 * L.lower, max(fz * 1.4, el.z - L.lower)))
    else:
        wr = el + V((s * L.lower * 0.55, L.lower * 0.8, -L.lower * 0.15))
    r0 = L.r
    b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [r0, r0 * 0.85, r0 * 0.72], sides=12), col)
    b.add(oriented(sh.lerp(el, 0.2) + V((0, 0, r0 * 0.1)), (r0 * 1.1 * L.muscle, r0 * 1.1 * L.muscle,
                                                            r0 * 1.05 * L.muscle)), col)
    b.add(oriented(el, (r0 * 0.75,) * 3, segments=10, rings=8), col)
    b.add(nh.tube([el, el.lerp(wr, 0.5), wr], [r0 * 0.70, r0 * 0.60, r0 * 0.52], sides=12), col)
    foot_c = V((wr.x + s * fx * 0.15, wr.y - fy * 0.35, fz)) if L.grounded else wr + V((s * fx * 0.5, fy * 0.3, 0))
    b.add(oriented(foot_c, (fx, fy, fz), yaw=-s * L.toe_yaw), col)
    tips = []
    if L.paddle:
        fwd = -1 if L.grounded else 1
        b.add(oriented(foot_c + V((s * fx * 0.3, fwd * fy * 0.9, -fz * 0.3)), (fx * 1.3, fy * 1.2, fz * 0.45),
                       yaw=-s * L.toe_yaw), col)
        return tips
    for k in range(L.toes):
        t = k / max(L.toes - 1, 1)
        a = math.radians(-L.toe_fan / 2 + L.toe_fan * t + L.toe_yaw)
        d = V((s * math.sin(a), -math.cos(a) if L.grounded else math.cos(a), 0.0))
        ln = L.toe_len * (0.7 + 0.3 * math.sin(math.pi * (0.25 + 0.6 * t)))
        base = foot_c + d * fy * 0.55
        tip = base + d * ln + V((0, 0, -fz * 0.35 if L.grounded else 0.0))
        b.add(nh.tube([base, base + d * ln * 0.5, tip], [L.toe_r, L.toe_r * 0.85, L.toe_r * 0.65], sides=8), col)
        tips.append((tip, d, L.toe_r * 0.8 * L.claw))
    return tips


# ---------------------------------------------------------------- paint / sculpt

def head_y(spec):
    return max(r[0] for r in spec.head)


def default_paint(spec):
    leg = spec.leg or spec.flank

    def paint(co, n):
        c = nh.lerp(spec.belly, spec.flank, nh.smoothstep(-0.6, -0.1, n.z))
        c = nh.lerp(c, spec.back, nh.smoothstep(0.1, 0.8, n.z))
        z, hw, hh, _x = rows_at(spec.torso, co.y)
        below = z - hh * 0.6
        if co.z < below and abs(co.x) > hw * 0.5:
            c = nh.lerp(leg, c, nh.smoothstep(below - 0.08, below, co.z))
        p = spec.pattern
        amt = 0.0
        if p == "bands":
            v = 0.5 + 0.5 * math.sin(co.y * spec.pattern_freq + noise.noise(co * 5.0) * 1.5)
            amt = nh.smoothstep(0.62, 0.9, v) * nh.smoothstep(-0.3, 0.4, n.z)
        elif p == "spots":
            v = noise.cell(co * spec.pattern_freq)
            amt = nh.smoothstep(0.70, 0.88, v) * nh.smoothstep(-0.4, 0.3, n.z)
        elif p == "stripes":
            v = 0.5 + 0.5 * math.sin(co.z * spec.pattern_freq + noise.noise(co * 4.0))
            amt = nh.smoothstep(0.65, 0.9, v) * nh.smoothstep(-0.5, 0.2, n.z)
        elif p == "mottle":
            v = noise.noise(co * spec.pattern_freq)
            amt = nh.smoothstep(0.15, 0.45, v) * nh.smoothstep(-0.4, 0.4, n.z)
        c = nh.lerp(c, spec.mark, spec.pattern_amount * amt)
        if spec.paint:
            c = spec.paint(co, n, c)
        k = 1.0 + 0.08 * noise.noise(co * 22.0)
        return tuple(max(0.0, min(1.0, x * k)) for x in c)
    return paint


def sculpt(spec, bm):
    bm.normal_update()
    moves = []
    s = spec.scale_bumps
    for v in bm.verts:
        co, n = v.co, v.normal
        d = s * 0.0016 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 55.0)))
        d += s * 0.0010 * noise.noise(co * 80.0)
        if spec.sculpt:
            d += spec.sculpt(co, n)
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def repaint(spec, bm):
    """Paint the fused skin; parts that were added in a colour other than the flank / leg
    colour (horns, bosses, crests...) keep their own colour."""
    paint = default_paint(spec)
    col = bm.loops.layers.color.get("Col")
    plain = [V(spec.flank), V(spec.leg or spec.flank)]
    bm.normal_update()
    for f in bm.faces:
        for l in f.loops:
            o = V(l[col][:3])
            c = paint(l.vert.co, l.vert.normal)
            k = nh.smoothstep(0.03, 0.10, min((o - p).length for p in plain))
            if k > 0:
                j = 1.0 + 0.07 * noise.noise(l.vert.co * 30.0)
                c = nh.lerp(c, tuple(x * j for x in o), k)
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        from mathutils.bvhtree import BVHTree
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(V(origin), V(direction).normalized())
        return loc, normal


def add_teeth(mb, spec, surf):
    for y0, y1, count, ln, r, upper in spec.teeth:
        rows = spec.head if upper or not spec.jaw else spec.jaw
        for i in range(count):
            y = y0 + (y1 - y0) * (i + 0.5) / count
            z, hw, hh, _x = rows_at(rows, y)
            for sx in (1, -1):
                if upper:
                    o, d = V((sx * hw * 0.78, y, z - hh - 0.2)), V((0, 0, 1))
                else:
                    o, d = V((sx * hw * 0.70, y, z + hh + 0.2)), V((0, 0, -1))
                loc, _n = surf.hit(o, d)
                if loc is None or abs(loc.z - (z - hh if upper else z + hh)) > hh * 0.8 + 0.02:
                    continue
                base = loc + d * -0.0 + V((0, 0, 0.004 if upper else -0.004))
                tip = loc + V((0, 0, -ln if upper else ln))
                mb.add(cone(base, tip, r, sides=5), spec.tooth_col, smooth=False)


def details(mb, spec, surf):
    ex, ey, ez, er = spec.eye
    for sx in (1, -1):
        # put the eye on the skin by casting inward from the side
        loc, _n = surf.hit((sx * (ex + 0.3), ey, ez), (-sx, 0, 0))
        e = V((sx * ex, ey, ez)) if loc is None else loc + V((-sx * er * 0.45, 0, 0))
        mb.add(nh.ellipsoid(e, (er, er * 1.1, er), subdivisions=2), spec.eye_col)
        mb.add(nh.ellipsoid(e + V((sx * er * 0.7, -er * 0.15, 0)), (er * 0.38, er * 0.5, er * 0.62),
                            subdivisions=1), (0.02, 0.02, 0.02))
        if spec.nostril:
            nx, ny, nz = spec.nostril
            mb.add(nh.ellipsoid((sx * nx, ny, nz), (er * 0.3, er * 0.35, er * 0.25), subdivisions=1),
                   (0.03, 0.02, 0.02))
    for x, y, z, ln, r, dy in spec.fangs:
        for sx in (1, -1):
            base = V((sx * x, y, z))
            mid = base + V((0, dy * 0.4, -ln * 0.55))
            tip = base + V((0, dy, -ln)) if ln > 0 else base + V((0, dy, -ln))
            mb.add(nh.tube([base + V((0, 0, 0.01 * math.copysign(1, ln))), mid, tip], [r, r * 0.8, 0.0], sides=8),
                   spec.tooth_col, smooth=False)
    for tip, d, r in spec._claws:
        if r <= 0:
            continue
        base = tip - d * 0.004 + V((0, 0, r * 0.4))
        end = tip + d * r * 2.8 + V((0, 0, -r * 0.8))
        mb.add(nh.tube([base, base + d * r * 1.4, end], [r, r * 0.7, 0.0], sides=6), spec.claw_col)


# ---------------------------------------------------------------- build

def apply_drop(spec):
    d = spec.drop
    if not d:
        return
    spec.drop = 0.0
    shift = lambda rows: [(r[0], r[1] - d) + tuple(r[2:]) for r in rows]  # noqa: E731
    spec.torso, spec.head = shift(spec.torso), shift(spec.head)
    if spec.jaw:
        spec.jaw = shift(spec.jaw)
    for L in (spec.fore, spec.hind):
        if L:
            L.z -= d
            L.lower -= d
    x, y, z, r = spec.eye
    spec.eye = (x, y, z - d, r)
    if spec.nostril:
        x, y, z = spec.nostril
        spec.nostril = (x, y, z - d)
    spec.fangs = [(f[0], f[1], f[2] - d) + tuple(f[3:]) for f in spec.fangs]


def build_fn(spec):
    def build():
        apply_drop(spec)
        spec._claws.clear()
        b = nh.MeshBuilder()
        b.add(loft(densify(spec.torso, 4), sides=24, power=spec.torso_power), spec.flank)
        b.add(loft(densify(spec.head, 3), sides=22, power=spec.head_power), spec.flank)
        if spec.jaw:
            b.add(loft(densify(spec.jaw, 3), sides=16, power=2.2), spec.flank)
        leg = spec.leg or spec.flank
        for s in (-1, 1):
            if spec.fore:
                spec._claws += limb(b, spec.fore, s, leg)
            if spec.hind:
                spec._claws += limb(b, spec.hind, s, leg)
        if spec.fused:
            spec.fused(b, spec)
        fused = b.fuse(voxel=spec.voxel, smooth=5, smooth_factor=0.5)
        sculpt(spec, fused)
        fused = decimate(fused, spec.max_tris)
        surf = Surface(fused)
        mb = nh.MeshBuilder()
        add_teeth(mb, spec, surf)
        details(mb, spec, surf)
        if spec.crisp:
            spec.crisp(mb, spec)
        mb.add(repaint(spec, fused), None)
        obj = mb.to_object(spec.name, roughness=spec.roughness)
        if spec.pivot == "ground":
            nh.ground_to_zero(obj)
        else:
            corners = [V(c) for c in obj.bound_box]
            centre = sum(corners, V()) / 8
            for v in obj.data.vertices:
                v.co -= centre
        return obj
    return build


def main(spec):
    preview = dict(ground=(0.42, 0.36, 0.26), views=((35, 22), (-90, 6), (25, 65)))
    if spec.pivot != "ground":
        preview = dict(background=(0.04, 0.10, 0.13), views=((35, 22), (-90, 6), (25, 65)))
    preview.update(spec.preview)
    nh.run(build_fn(spec), spec.name, **preview)
